from google import genai
from google.genai import types
from app.providers.base import BaseAIProvider
from app.core.config import settings

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        # Using the new SDK client
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.0-flash"
        self.system_instruction = (
            "You are a helpful and very concise AI assistant. "
            "Always give short, accurate, and direct answers. "
            "Do not use long explanations unless asked."
        )

    async def get_response(self, prompt: str, history: list = None) -> str:
        try:
            # We convert the history to the new SDK format
            formatted_history = []
            if history:
                for entry in history:
                    role = "user" if entry["role"] == "user" else "model"
                    formatted_history.append(
                        types.Content(role=role, parts=[types.Part(text=entry["content"])])
                    )

            # Creating the chat session
            chat = self.client.chats.create(
                model=self.model_id,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    history=formatted_history
                )
            )

            response = chat.send_message(prompt)
            return response.text

        except Exception as e:
            return f"Gemini Error: {str(e)}"