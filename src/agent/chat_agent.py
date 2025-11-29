#src/agent/chat_agent.py
import asyncio
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode, tools_condition

from src.utils.memory import (
    get_user, set_user, get_cached_response, set_cached_response
)

from src.utils.metrics import (
    LLM_API_CALLS, MCP_TOOL_CALLS, CACHE_HITS, CACHE_MISSES
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_agent(session_id: str):

    client = MultiServerMCPClient({
        "expenses": {
            "transport": "stdio",
            "command": "python3",
            "args": ["src/mcp_servers/expense_tracker.py"]
        }
    })

    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-5", temperature=0)
    llm_tools = llm.bind_tools(tools)

    async def chat_node(state):

        last_msg = state["messages"][-1].content
        user = get_user(session_id)

        # First Time: Ask name
        if user is None:
            set_user(session_id, "PENDING")
            return {"messages": [HumanMessage(content="Please enter your name:")]}

        # Second message: Save name
        if user == "PENDING":
            set_user(session_id, last_msg)
            return {"messages": [
                HumanMessage(content=f"Welcome {last_msg}! How can I help you today?")
            ]}

        # Check cache
        cached = get_cached_response(user, last_msg)
        if cached:
            CACHE_HITS.inc()
            return {"messages": [HumanMessage(content=cached)]}
        else:
            CACHE_MISSES.inc()

        # Add user context
        state["messages"][-1].content = f"{last_msg} (user={user})"

        # LLM call
        LLM_API_CALLS.inc()
        response = await llm_tools.ainvoke(state["messages"])

        # Detect tool call
        try:
            if hasattr(response, "tool_calls") and response.tool_calls:
                MCP_TOOL_CALLS.inc()
        except:
            pass

        set_cached_response(user, last_msg, response.content)
        return {"messages": [response]}

    graph = StateGraph(ChatState)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    return graph.compile()

async def run_agent(session_id: str, msg: str):
    agent = await build_agent(session_id)
    output = await agent.ainvoke({"messages": [HumanMessage(content=msg)]})
    final_message = output["messages"][-1].content
    return final_message
