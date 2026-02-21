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
        self.model = genai.GenerativeModel(self.model_name)

    async def get_response(self, prompt: str, history: list = None) -> str:
        try:
            # Generate content from the model
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text
            
            return "The AI returned an empty response. Please check your prompt."
            
        except Exception as e:
            # If you see 404 here, it usually means the SDK version is old 
            # or the model name has a regional restriction.
            error_msg = str(e)
            if "404" in error_msg:
                return f"Model Error: {self.model_name} not found. Try running 'pip install --upgrade google-generativeai' in your terminal."
            return f"Error calling Gemini API: {error_msg}"