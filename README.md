Simple AI Chatbot (Gemini 2.5 + FastAPI + React)A modular, future-proof AI chatbot built with a FastAPI backend and a React frontend. This project is architected using the Service-Repository and Factory patterns, making it easy to scale or add RAG (Retrieval-Augmented Generation) in the future.Project Structurersg/ (Main Git Root)
├── bot/                # FastAPI Backend (Python)
│   ├── app/            # Application logic
│   ├── .env            # Environment variables (API Keys)
│   └── requirements.txt
└── bot-ui/             # React Frontend (Vite)
    ├── src/            # React components & logic
    └── package.json
FeaturesFastAPI Backend: High-performance Python API.Service-Provider Architecture: Decoupled logic for easy scaling.Gemini 2.5 Integration: Uses the gemini-1.5-flash model for fast responses.Clean UI: Responsive chat interface built with React and custom CSS.CORS Enabled: Pre-configured for local cross-origin communication.Setup Instructions1. Backend Setup (bot/)Go to the backend folder:cd bot
Create and activate a virtual environment:python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:pip install -r requirements.txt
pip install --upgrade google-generativeai
Create a .env file in the bot/ folder and add your key:GEMINI_API_KEY=your_google_ai_studio_key
Run the server:fastapi dev app/main.py
2. Frontend Setup (bot-ui/)Go to the frontend folder:cd bot-ui
Install Node dependencies:npm install
Run the development server:npm run dev
How to UseStart the backend (Port 8000).Start the frontend (Port 5173).Open http://localhost:5173 in your browser.Future Roadmap[ ] RAG Support: Adding vector database integration.[ ] Multi-Agent Factory: Support for OpenAI and Claude.[ ] History: Implementing session-based persistent chat history.Developed by Mukarram Hussain (Tech with muk)
