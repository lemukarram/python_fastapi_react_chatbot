from google.genai import types
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import KnowledgeBase
from app.core.config import settings
from app.providers.gemini import GeminiClientManager

class RAGService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Create the object only if it does not exist.
            cls._instance = super(RAGService, cls).__new__(cls)
            cls._instance._init_rag_service()
            
        return cls._instance
    
    def _init_rag_service(self):
        """
        Internal initialization for the singleton.
        Runs only once when the first RAGService object is created.
        """
        self.client = GeminiClientManager.get_client()

    async def get_embedding(self, text_to_embed: str):
        try:
            print(f"===== before embedding 400 ====")
            # New method for generating embeddings
            result = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text_to_embed,
                config=types.EmbedContentConfig(output_dimensionality=768)
            )
            print(f"===== after embedding 400 ====")
            if result and result.embeddings:
                return result.embeddings[0].values
            
            return None
        
        except Exception as e:
            print(f"Embedding error: {e}")
            return None

    async def search_context(self, db: AsyncSession, query_text: str, limit: int = 3) -> str:
        query_embedding = await self.get_embedding(query_text)
        print(f" ------- gemini emdeding-100------")
        if not query_embedding:
            print(f" ------- gemini emdeding-0------")
            return []
        try:
            # Using the vector distance search in Postgres
            stmt = (
                select(KnowledgeBase.content)
                .order_by(KnowledgeBase.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )

            # Execute using the session passed from the caller
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            # This will tell you if the 'vector' type is missing in the DB 
            # or if the dimensions (768) don't match.
            print(f"Database Execution Error in RAG: {e}")
            return []