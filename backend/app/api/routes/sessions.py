from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.graph import get_graph
from app.core.text import extract_text
from app.memory.sessions import delete_session, list_sessions

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("")
async def get_sessions():
    return {"sessions": list_sessions()}


@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str):
    graph = get_graph()
    config = {"configurable": {"thread_id": session_id}}

    state = await graph.aget_state(config)
    if not state or not state.values.get("messages"):
        raise HTTPException(status_code=404, detail="Session not found or empty.")

    messages = []
    for msg in state.values["messages"]:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            continue  # skip system/tool messages, frontend only renders user/assistant

        text = extract_text(msg.content)
        if not text:
            continue  # e.g. an AIMessage that was purely a tool call, no visible text
        messages.append({"role": role, "content": text})

    return {"session_id": session_id, "messages": messages}


@router.delete("/{session_id}")
async def remove_session(session_id: str):
    deleted = delete_session(session_id)
    return {"deleted": deleted}
