
import json
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.agent.graph import get_graph
from app.core.errors import friendly_error_message
from app.core.text import extract_text
from app.llm.factory import get_llm
from app.memory.sessions import register_or_touch_session
from app.schemas.chat import ChatRequest, ChatResponse, SuggestionsRequest, SuggestionsResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _build_message_content(request: ChatRequest):
    """Plain text, or a multimodal content list if an image was attached."""
    if request.image_base64:
        mime = request.image_mime_type or "image/jpeg"
        return [
            {"type": "text", "text": request.message},
            {"type": "image_url", "image_url": f"data:{mime};base64,{request.image_base64}"},
        ]
    return request.message


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    graph = get_graph()
    register_or_touch_session(session_id, request.message)

    config = {"configurable": {"thread_id": session_id}}
    try:
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=_build_message_content(request))]},
            config=config,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=friendly_error_message(exc))

    reply = extract_text(result["messages"][-1].content)
    return ChatResponse(reply=reply, session_id=session_id)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    graph = get_graph()
    register_or_touch_session(session_id, request.message)
    config = {"configurable": {"thread_id": session_id}}

    async def event_generator():
        yield f"event: session\ndata: {json.dumps({'session_id': session_id})}\n\n"

        try:
            async for event in graph.astream_events(
                {"messages": [HumanMessage(content=_build_message_content(request))]},
                config=config,
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    text = extract_text(getattr(chunk, "content", ""))
                    if text:
                        yield f"event: token\ndata: {json.dumps({'text': text})}\n\n"

                elif kind == "on_tool_start":
                    tool_name = event.get("name", "tool")
                    yield f"event: tool_start\ndata: {json.dumps({'tool': tool_name})}\n\n"

                elif kind == "on_tool_end":
                    tool_name = event.get("name", "tool")
                    yield f"event: tool_end\ndata: {json.dumps({'tool': tool_name})}\n\n"

            yield "event: done\ndata: {}\n\n"
        except Exception as exc:
            message = friendly_error_message(exc)
            yield f"event: error\ndata: {json.dumps({'message': message})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/suggestions", response_model=SuggestionsResponse)
async def suggestions(request: SuggestionsRequest) -> SuggestionsResponse:
    """Generate 2-3 short, clickable follow-up questions based on the most
    recent exchange in a session. Best-effort: returns an empty list rather
    than erroring if anything goes wrong, since this is a "nice to have" UI
    feature, not core functionality."""
    graph = get_graph()
    config = {"configurable": {"thread_id": request.session_id}}

    try:
        state = await graph.aget_state(config)
        messages = state.values.get("messages", []) if state else []
        if not messages:
            return SuggestionsResponse(suggestions=[])

        recent = messages[-4:]
        transcript = "\n".join(
            f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {extract_text(m.content)}"
            for m in recent
        )

        llm = get_llm()
        prompt = (
            "Based on this conversation snippet, suggest exactly 3 short, "
            "natural follow-up questions the user might want to ask next. "
            "One per line, no numbering, no quotes, no extra commentary.\n\n"
            f"{transcript}"
        )
        response = await llm.ainvoke(prompt)
        text = extract_text(response.content)
        lines = [line.strip("-•* ").strip() for line in text.splitlines() if line.strip()]
        return SuggestionsResponse(suggestions=lines[:3])
    except Exception:
        return SuggestionsResponse(suggestions=[])
