import os

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv(override=True)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = None
try:
    client = MultiServerMCPClient(
        {
            "tavily": {
                "transport": "streamable_http",
                "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
            }
        }
    )
except Exception as exc:
    print(f"Tavily MCP client initialization failed: {exc}")

search_tool = None


async def initialize_mcp():
    global search_tool
    if search_tool is not None:
        return

    if client is None:
        raise RuntimeError("Tavily MCP client is unavailable. Check TAVILY_API_KEY.")

    tools = await client.get_tools()
    search_tool = next(
        (tool for tool in tools if tool.name == "tavily_search"),
        None,
    )
    if search_tool is None:
        raise RuntimeError("Tavily MCP search tool is unavailable")


async def tavily_mcp_search(query: str):
    try:
        await initialize_mcp()
        return await search_tool.ainvoke({"query": query})
    except Exception as exc:
        return f"Tavily search unavailable: {exc}"