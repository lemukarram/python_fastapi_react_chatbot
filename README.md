
# Simple AI Chatbot (Gemini 2.5 + FastAPI + React)

This is a clean and modular AI chatbot project. It uses a FastAPI backend in Python and a React frontend. The architecture is designed so you can easily switch AI models or add more advanced features like RAG later.

## Project Structure

```text
rsg/ (Main Git Root)
├── bot/                # FastAPI Backend (Python)
│   ├── app/            # Application logic
│   ├── .env            # Private API Keys
│   └── requirements.txt
└── bot-ui/             # React Frontend (Vite)
    ├── src/            # Chat interface code
    └── package.json
```

## Main Features

* **FastAPI Backend.** High performance and easy to scale.
* **Modular Design.** Logic is separated from the AI provider.
* **Gemini 2.5.** Uses the latest gemini-1.5-flash model.
* **React UI.** A modern and responsive interface.
* **CORS Configured.** Ready for local development out of the box.

## Setup Instructions

### 1. Backend Setup (bot folder)

First, navigate into the backend directory.
```bash
cd bot
```

Create a virtual environment to keep your global Python clean.
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\\Scripts\\activate
```

Install the necessary packages.
```bash
pip install -r requirements.txt
pip install --upgrade google-generativeai
```

Create a file named `.env` in the bot folder and add your key.
```text
GEMINI_API_KEY=your_key_here
```

Start the FastAPI server.
```bash
fastapi dev app/main.py
```

### 2. Frontend Setup (bot-ui folder)

Open a new terminal and go to the frontend directory.
```bash
cd bot-ui
```

Install the Node.js dependencies.
```bash
npm install
```

Start the React development server.
```bash
npm run dev
```

## How to Use

1. Ensure your Python backend is running on port 8000.
2. Ensure your React app is running on port 5173.
3. Open `http://localhost:5173` in your browser.

## Future Roadmap

* Add RAG support for custom data.
* Add support for OpenAI and Claude.
* Implement database storage for chat history.

Developed by Mukarram Hussain (Tech with muk)
"""
