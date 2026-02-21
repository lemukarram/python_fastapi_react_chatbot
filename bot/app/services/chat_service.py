from app.providers.factory import AIProviderFactory

class ChatService:
    def __init__(self):
        self.provider = AIProviderFactory.get_provider("gemini")

    async def chat_with_ai(self, user_message: str, session_id: str = "default"):
        # We now pass the session_id to the provider to maintain context
        return await self.provider.get_response(user_message, session_id=session_id)