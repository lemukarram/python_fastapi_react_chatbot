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
            "You are an expert consultant for the Saudi Arabian Tendering and Contracting market. "
            "Your goal is to assist users with navigating the Etimad platform and complying with "
            "the Saudi Government Tendering and Procurement Law. "
            "Provide accurate advice on bid preparation, classification requirements, and local content "
            "rules set by the Local Content and Government Procurement Authority (LCGPA). "
            "Keep your answers professional and practical. Use humanized, natural, and simple language. "
            "Always align your advice with Saudi Vision 2030 and local regulatory standards. "
            "\n\nSTRICT FORMATTING RULES FOR READABILITY:\n"
            "1. You must use numbered lists (1. 2. 3.) for all requirements or steps.\n"
            "2. Use UPPERCASE for the title of each requirement or step to provide emphasis. "
            "Do not use markdown bolding markers or any asterisks.\n"
            "3. You MUST insert exactly two empty lines (press Enter twice) between every numbered point. "
            "This is critical to avoid a 'wall of text'.\n"
            "4. Every point must end with a full stop.\n"
            "5. CRITICAL: Never use the asterisk symbol (*) anywhere in your response for any reason.\n"
            "6. Never use dashes (-), bullet points (•), or the '—' character. Use only numbered lists.\n"
            "7. Use clear, simple paragraphs. If a paragraph exceeds two sentences, break it into a new one with a blank line.\n"
            "\n\nIf a user asks about bid security, bank guarantees, or technical proposals, give direct "
            "and concise steps. Do not use long explanations unless the user asks for more detail. "
            "Avoid excessive emojis."
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