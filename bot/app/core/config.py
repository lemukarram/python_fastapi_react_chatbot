import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # These must match the names in your .env file
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Secret key for JWT and Auth logic
    # In a real project, put a long random string in your .env
    SECRET_KEY: str = "SUPER_SECRET_KEY_FOR_JWT_TOKEN"
    
    # Project Info
    PROJECT_NAME: str = "AI Chatbot Pro"
    
    # Tell Pydantic to read from the .env file in the bot folder
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# We create one instance to use across the whole app
settings = Settings()