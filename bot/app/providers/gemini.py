from google import genai
from google.genai import types
from app.providers.base import BaseAIProvider
from app.core.config import settings

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        # We use the new client with your API key
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_id = "gemini-2.5-flash"
        self.system_instruction = (
            "You are a helpful and very concise AI assistant. "
            "Always give short, accurate, and direct answers. "
            "Do not use long explanations unless asked."
        )

    async def get_response(self, prompt: str, history: list = None) -> str:
        """
        Communicates with Gemini using the new SDK.
        Fixed the 'Extra inputs' error by moving history out of the config block.
        """
        try:
            # We map our database history to the format Gemini expects
            formatted_history = []
            if history:
                for entry in history:
                    role = "user" if entry["role"] == "user" else "model"
                    formatted_history.append({
                        "role": role, 
                        "parts": [{"text": entry["content"]}]
                    })

            # The 'history' parameter must be passed directly to create(), 
            # NOT inside GenerateContentConfig.
            chat = self.client.chats.create(
                model=self.model_id,
                history=formatted_history,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )
            )

            # Send the new message with the context
            response = chat.send_message(prompt)
            
            if response and response.text:
                return response.text
            
            return "I received an empty response. Please try again."

        except Exception as e:
            # This will help you debug during your 'Tech with muk' sessions
            return f"Gemini Error: {str(e)}"