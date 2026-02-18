from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "Hello API"
    version: str = "0.1"

settings = Settings()
