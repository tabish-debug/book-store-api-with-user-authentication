from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str
    FILE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    CLIENT_ORIGIN: str
    
    class Config:
        env_file = './.env'


settings = Settings()
