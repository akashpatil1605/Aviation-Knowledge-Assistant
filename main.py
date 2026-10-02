
# Two-Agent Study Assistant: Tavily Search and FAA Maintenance RAG

from typing import TypedDict
import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage

from langchain_groq import ChatGroq
from maintenance_rag import is_faa_query, retrieve_maintenance_context

from mcp_client import tavily_mcp_search


from dotenv import load_dotenv
load_dotenv(override=True)

# LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b"
)

# State
class AssistantState(TypedDict):
    user_query: str
    tavily_results: str
    maintenance_results: str


def tavily_agent(state: AssistantState):
    query = state["user_query"]
    search_results = asyncio.run(tavily_mcp_search(query))
    prompt = f"""
    Answer the user's question using the Tavily search results below.
    Be concise, distinguish sourced facts from uncertainty, and cite source URLs
    when they are present. If search failed or returned no useful evidence, say so.

    User question:
    {query}

    Tavily search results:
    {search_results}
    """
    response = llm.invoke([
        SystemMessage(content="You are a web research assistant grounded in Tavily results."),
        HumanMessage(content=prompt),
    ])

    return {
        "tavily_results": response.content,
    }


def faa_maintenance_agent(state: AssistantState):
    sources = retrieve_maintenance_context(state["user_query"])

    if not sources:
        answer = "I don't know."
    else:
        answer = "\n\n".join(
            f"Source: {source['source']}, page {source['page']}\n{source['content']}"
            for source in sources
        )

    return {
        "maintenance_results": answer,
    }


def route_query(state: AssistantState) -> str:
    if is_faa_query(state["user_query"]):
        return "faa_maintenance_agent"
    return "tavily_agent"


graph = StateGraph(AssistantState)

graph.add_node("tavily_agent", tavily_agent)
graph.add_node("faa_maintenance_agent", faa_maintenance_agent)


graph.add_conditional_edges(
    START,
    route_query,
    {
        "tavily_agent": "tavily_agent",
        "faa_maintenance_agent": "faa_maintenance_agent",
    },
)
graph.add_edge("tavily_agent", END)
graph.add_edge("faa_maintenance_agent", END)


app = graph.compile()


if __name__ == "__main__":
    user_input = input("Ask a general or FAA maintenance question: ")
    result = app.invoke(
        {
            "user_query": user_input,
            "tavily_results": "",
            "maintenance_results": "",
        },
    )
    answer_key = (
        "maintenance_results"
        if is_faa_query(user_input)
        else "tavily_results"
    )
    print(f"\nANSWER:\n{result[answer_key]}")
