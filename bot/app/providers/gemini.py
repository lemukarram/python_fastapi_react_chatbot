import google.generativeai as genai
from app.providers.base import BaseAIProvider
from app.core.config import settings

class GeminiProvider(BaseAIProvider):
    def __init__(self):
        # Configure the SDK
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Use the specific model identifier. 
        # If 'gemini-1.5-flash' still fails, try 'models/gemini-1.5-flash'
        self.model_name = 'gemini-2.5-flash'
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction="You are a helpful but very concise AI assistant. "
                               "Give short, accurate, and to-the-point answers. "
                               "Avoid long explanations unless specifically asked."
        )
        # This dictionary will store chat sessions in memory
        # Key: session_id, Value: ChatSession object
        self.sessions = {}

    async def get_response(self, prompt: str, session_id: str = "default") -> str:
        try:
            # If the session doesn't exist, start a new chat
            if session_id not in self.sessions:
                self.sessions[session_id] = self.model.start_chat(history=[])
            
            chat_session = self.sessions[session_id]
            
            # send_message automatically updates the history inside the session object
            response = chat_session.send_message(prompt)
            
            if response and response.text:
                return response.text
            
            return "I received an empty response. Please try again."
            
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"