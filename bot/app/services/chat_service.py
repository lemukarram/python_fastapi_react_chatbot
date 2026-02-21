from app.providers.factory import AIProviderFactory

class ChatService:
    def __init__(self):
        # We use the factory to get the default provider.
        # You could also pull the provider name from your config/env.
        self.provider = AIProviderFactory.get_provider("gemini")

    async def chat_with_ai(self, user_message: str):
        # This remains the central hub for your logic.
        # When you add RAG, you will fetch embeddings here.
        return await self.provider.get_response(user_message)