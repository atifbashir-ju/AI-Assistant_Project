from functools import lru_cache

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.tools.registry import get_active_tools
from app.llm.factory import get_llm
from app.memory.checkpointer import get_checkpointer

SYSTEM_PROMPT = """You are a helpful, general-purpose AI assistant.

Answer clearly and directly. If you have access to tools (web search,
knowledge base search, etc.), use them when they would give a better or
more up-to-date answer than you could give from memory alone. Otherwise,
just answer from your own knowledge."""


def _build_agent_node():
    """Returns the `agent` node function, with the LLM (+ tools) bound once."""
    llm = get_llm()
    tools = get_active_tools()
    llm_with_tools = llm.bind_tools(tools) if tools else llm

    def agent_node(state: AgentState) -> dict:
        messages = state["messages"]
        # Prepend the system prompt if it's not already the first message.
        from langchain_core.messages import SystemMessage

        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    return agent_node


@lru_cache
def get_graph():
    """Builds and compiles the graph once per process."""
    tools = get_active_tools()

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("agent", _build_agent_node())

    if tools:
        graph_builder.add_node("tools", ToolNode(tools))
        graph_builder.add_conditional_edges(
            "agent",
            tools_condition,  # routes to "tools" if the last message has tool calls, else END
            {"tools": "tools", END: END},
        )
        graph_builder.add_edge("tools", "agent")
    else:
        graph_builder.add_edge("agent", END)

    graph_builder.add_edge(START, "agent")

    return graph_builder.compile(checkpointer=get_checkpointer())
