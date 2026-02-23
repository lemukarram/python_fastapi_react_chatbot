from google import genai
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import KnowledgeBase
from app.core.config import settings

class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def get_embedding(self, text_to_embed: str):
        try:
            # New method for generating embeddings
            result = self.client.models.embed_content(
                model="text-embedding-004",
                contents=text_to_embed
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Embedding error: {e}")
            return None

    async def search_context(self, query_text: str, limit: int = 3) -> str:
        query_embedding = await self.get_embedding(query_text)
        if not query_embedding:
            return ""

        # Using the vector distance search in Postgres
        stmt = (
            select(KnowledgeBase.content)
            .order_by(KnowledgeBase.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return "\n".join(rows) if rows else ""