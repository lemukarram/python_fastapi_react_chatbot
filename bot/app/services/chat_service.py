from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import ChatMessage
from app.services.rag_service import RAGService
from app.providers.gemini import GeminiProvider

class ChatService:
    def __init__(self, db: AsyncSession):
        
        self.db = db
        # Initialize RAG for tender searching
        self.rag = RAGService()
        # Initialize Gemini AI
        self.ai = GeminiProvider()

    async def get_history(self, user_id):
        """
        Fetches all previous messages for a user to show in the UI.
        """
        
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in messages]

    async def chat(self, user_id, message: str):
        """
        Handles the conversation, saves history, and cleans the AI response.
        """

        # 1. Search RAG context
        sources = await self.rag.search_context(self.db, message)
        
        # 2. Join them for the AI to read as context
        context = "\n".join(sources) if sources else "No specific context found."


        try:
            # 2. Get last 5 messages for AI context
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(5)
            )
            res = await self.db.execute(stmt)
            db_history = res.scalars().all()
            history = [{"role": m.role, "content": m.content} for m in db_history[::-1]]
            
            # 3. Get AI Response
            enhanced_prompt = f"Context:\n{context}\n\nUser Question: {message}"
            raw_reply = await self.ai.get_response(enhanced_prompt, history=history)
            
            # 4. Clean formatting (remove asterisks)
            reply = raw_reply.replace("*", "")

            # 5. Save to database
            user_msg = ChatMessage(user_id=user_id, role="user", content=message)
            bot_msg = ChatMessage(user_id=user_id, role="bot", content=reply)
            
            self.db.add_all([user_msg, bot_msg])
            await self.db.commit()

            # We return both the reply and the original sources list
            return {
                "reply": reply,
                "sources": sources
            }
        
        except Exception as e:
            print(f"message error: {e}")
            return {
                "reply": "No Reply",
                "sources": []
                
            }