
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.v1 import chat

app = FastAPI(title="AI Chatbot")

app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

@app.get("/")
def read_root():
    return {"status": "AI Chatbot is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allows everything. 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)