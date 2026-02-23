from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ChatMessage
from app.services.rag_service import RAGService
from app.providers.gemini import GeminiProvider

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # We initialize the RAG service to search our Postgres vector data
        self.rag = RAGService(db)
        # We use our specific Gemini provider logic
        self.ai = GeminiProvider()

    async def chat(self, user_id, message: str):
        """
        Orchestrates the full AI response logic:
        1. Search RAG context
        2. Load user history from Postgres
        3. Get AI response from Gemini
        4. Save everything back to Postgres
        """
        
        # 1. Search for relevant context in the Knowledge Base (RAG)
        # This makes the AI answer based on your specific uploaded data
        context = await self.rag.search_context(message)
        
        # 2. Get the last 5 messages for this user to maintain conversation flow
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(5)
        )
        res = await self.db.execute(stmt)
        # We reverse the history so it's in chronological order for the AI
        db_history = res.scalars().all()
        history = [{"role": m.role, "content": m.content} for m in db_history[::-1]]
        
        # 3. Combine the RAG context with the user's current question
        # This tells the AI: "Use this info to answer this question"
        enhanced_prompt = f"Context from Knowledge Base:\n{context}\n\nUser Question: {message}"
        
        # 4. Get the response from Gemini
        raw_reply = await self.ai.get_response(enhanced_prompt, history=history)
        # remove the * from the response.
        reply = raw_reply.replace("*", "")

        # 5. Save the new exchange to the database history
        # We save both what the user said and what the bot replied
        user_msg = ChatMessage(user_id=user_id, role="user", content=message)
        bot_msg = ChatMessage(user_id=user_id, role="bot", content=reply)
        
        self.db.add_all([user_msg, bot_msg])
        await self.db.commit()

        return reply