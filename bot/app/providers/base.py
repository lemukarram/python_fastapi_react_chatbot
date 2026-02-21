from abc import ABC, abstractmethod

class BaseAIProvider(ABC):
    @abstractmethod
    async def get_response(self, prompt: str, history: list = None) -> str:
        pass