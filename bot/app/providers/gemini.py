from google import genai
from google.genai import types
from app.providers.base import BaseAIProvider
from app.core.config import settings

class GeminiClientManager:
    """
    Singleton manager for the Gemini client.
    This ensures we only create one client instance for the entire application lifecycle.
    """
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            # Initialize the client only if it hasn't been created yet
            cls._client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())
            
        return cls._client

class GeminiProvider(BaseAIProvider):
    """
    Singleton implementation of the Gemini Provider.
    This ensures that the system instructions and AI settings are consistent.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Create the instance only if it does not exist
            cls._instance = super(GeminiProvider, cls).__new__(cls)
            # Run the initialization logic only once
            cls._instance._init_provider()
        return cls._instance

    def _init_provider(self):
        """
        Internal initialization method for the singleton instance.
        """
        self.model_id = settings.gemini_ai_model
        # We fetch the singleton client from the manager
        self.client = None
        
        # Expert Tender Assistant Instructions
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
        Uses the managed singleton client instance to avoid initialization errors.
        """
        try:
            formatted_history = []
            if history:
                for entry in history:
                    role = "user" if entry["role"] == "user" else "model"
                    formatted_history.append({
                        "role": role, 
                        "parts": [{"text": entry["content"]}]
                    })

            if self.client is None:
                self.client = GeminiClientManager.get_client()

            # Create the chat session using the managed client
            chat = self.client.chats.create(
                model=self.model_id,
                history=formatted_history,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction
                )
            )

            response = chat.send_message(prompt)
            
            if response and response.text:
                return response.text
            
            return "The AI assistant could not generate a reply. Please try again."

        except Exception as e:
            # We log the error on the server for you to see in Docker.
            print(f"Internal AI Error: {str(e)}")
            # Instead of returning the error string to the user, we raise it.
            # This triggers the generic error message in your ChatService or Router.
            raise e