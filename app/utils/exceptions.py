from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

class AgentError(Exception):
    def __init__(self, message: str):
        self.message = message

def add_exception_handlers(app):
    @app.exception_handler(AgentError)
    async def agent_exception_handler(request: Request, exc: AgentError):
        return JSONResponse(
            status_code=400,
            content={"error": exc.message}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
     
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error."}
        )