from fastapi import APIRouter
from app.models.chat import ChatRequest, ChatResponse
from app.agent.core import build_graph
from app.utils.exceptions import AgentError
from starlette.concurrency import run_in_threadpool

router = APIRouter()
graph = build_graph()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        state = {"messages": [msg.model_dump() for msg in req.messages]}
        output = await run_in_threadpool(graph.invoke, state)
        print("Graph output:", output)
        last_message = output["messages"][-1]
        # Defensive: ensure string
        llm_response = str(getattr(last_message, "content", ""))
        print("LLM Response:", llm_response)
        return ChatResponse(response=llm_response)
    except Exception as e:
        print("Exception in endpoint:", e)
        raise AgentError(str(e))