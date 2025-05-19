import os
import traceback
from dotenv import load_dotenv
from langgraph.graph import START, StateGraph, MessagesState
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader, ArxivLoader
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

load_dotenv()

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@tool
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b

@tool
def divide(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

@tool
def modulus(a: int, b: int) -> int:
    """Get the modulus of two numbers."""
    return a % b

@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for a query and return maximum 2 results."""
    try:
        search_docs = WikipediaLoader(query=query, load_max_docs=2).load()
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
                for doc in search_docs
            ])
        return {"wiki_results": formatted_search_docs}
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[wiki_search] Error: {e}\n{tb}")
        return {"wiki_results": f"ERROR: Wikipedia search failed for '{query}'. Reason: {e}"}

Tavily_api_key = os.environ.get("TAVILY_API_KEY")

@tool
def web_search(query: str) -> str:
    """Search Tavily for a query and return maximum 3 results."""
    try:
        search_docs = TavilySearchResults(api_key=Tavily_api_key, max_results=3).invoke({"query": query})
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.get("source", "")}" page="{doc.get("page", "")}"/>\n{doc.get("content", "")}\n</Document>'
                for doc in search_docs
            ])
        return {"web_results": formatted_search_docs}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[web_search] Error: {e}\n{tb}")
        return {"web_results": f"ERROR: Web search failed for '{query}'. Reason: {e}"}

@tool
def arxiv_search(query: str) -> str:
    """Search Arxiv for a query and return maximum 3 results."""
    try:
        search_docs = ArxivLoader(query=query, load_max_docs=3).load()
        formatted_search_docs = "\n\n---\n\n".join(
            [
                f'<Document source="{doc.metadata.get("source", "")}" page="{doc.metadata.get("page", "")}"/>\n{getattr(doc, "page_content", "")[:1000]}\n</Document>'
                for doc in search_docs
            ])
        return {"arxiv_results": formatted_search_docs}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[arxiv_search] Error: {e}\n{tb}")
        return {"arxiv_results": f"ERROR: Arxiv search failed for '{query}'. Reason: {e}"}

# Load the system prompt from file
with open("app/agent/system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

sys_msg = SystemMessage(content=system_prompt)

tools = [
    multiply,
    add,
    subtract,
    divide,
    modulus,
    wiki_search,
    web_search,
    arxiv_search,
]

# Build graph function
def build_graph():
    """Build the graph with Google Gemini only."""
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY in environment variables or .env file.")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-04-17",
        temperature=0,
        google_api_key=api_key
    )


    llm_with_tools = llm.bind_tools(tools)

    def assistant(state: MessagesState):
        """Assistant node"""
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile()