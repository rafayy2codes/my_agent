from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as v1_router
from app.utils.exceptions import add_exception_handlers
from app.api.v1 import endpoints

app = FastAPI()
app.include_router(endpoints.router, prefix="/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


add_exception_handlers(app)

@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint to verify the server is running.
    """
    return {"message": "Everything is working fine"}