from pydantic import BaseSettings

class Settings(BaseSettings):
    google_api_key: str
    tavily_api_key: str = ""
    

    class Config:
        env_file = ".env"

settings = Settings()