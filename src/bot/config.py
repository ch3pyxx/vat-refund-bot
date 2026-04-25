from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    TOKEN: str

    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()
