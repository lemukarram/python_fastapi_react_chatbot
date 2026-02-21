from typing import Dict, Type
from app.providers.base import BaseAIProvider
from app.providers.gemini import GeminiProvider

class AIProviderFactory:
    """
    Factory class to handle different AI agents.
    This makes it easy to switch from Gemini to OpenAI or others.
    """
    _providers: Dict[str, Type[BaseAIProvider]] = {
        "gemini": GeminiProvider,
        # "openai": OpenAIProvider,  <-- Easy to add later
    }

    @classmethod
    def get_provider(cls, provider_name: str = "gemini") -> BaseAIProvider:
        provider_class = cls._providers.get(provider_name.lower())
        
        if not provider_class:
            raise ValueError(f"Provider '{provider_name}' is not supported yet.")
            
        return provider_class()