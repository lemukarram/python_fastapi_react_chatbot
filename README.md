
# RSG Tender Chat BOT

An advanced AI-powered assistant designed specifically for the Saudi Arabian tendering and contracting market. This tool helps users navigate the Etimad platform and understand the Government Tendering and Procurement Law using Gemini 2.5 Flash and Retrieval-Augmented Generation (RAG).

## Project Overview

The RSG Tender Chat BOT is a full-stack application. It uses a FastAPI backend and a React frontend. It stores tender-related documents in a PostgreSQL database using the pgvector extension. This allows the bot to provide accurate advice based on your specific documents.

## System Requirements

Before you start, make sure your computer has these tools installed.

. Python 3.10 or higher.
. Node.js and npm (for the frontend).
. PostgreSQL 14 or higher.
. An API key from Google AI Studio (Gemini).

## Step 1. Database Setup

The bot needs a special extension called pgvector to handle AI data.

1. Install PostgreSQL on your system.
2. Open your terminal and install pgvector. If you are on a Mac with Homebrew, you can use the command: brew install pgvector.
3. Create a new database named bot_db.
4. Open your database tool or terminal and run this command: CREATE EXTENSION IF NOT EXISTS vector. This is very important for the AI features.

## Step 2. Backend Installation (Python)

Follow these steps to set up the server logic.

1. Open your terminal and go to the bot folder.
2. Create a virtual environment. This keeps the project files separate from your computer system. Run: python3 -m venv venv.
3. Activate the environment. On Mac, use: source venv/bin/activate. On Windows, use: venv\Scripts\activate.
4. Install all the required Python packages. Run: pip install -r requirements.txt.
5. Create a file named .env in the bot folder. This is where you will save your private keys.

## Step 3. How to Connect the Database

Inside your .env file, you need to tell the bot how to find your database. Use this format.

. DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@localhost:5432/bot_db.

Replace USERNAME and PASSWORD with your actual PostgreSQL credentials. Also, add your Gemini key in the same file as: GEMINI_API_KEY=your_key_here.

## Step 4. Frontend Setup (React)

This is the part that creates the chat screen.

1. Open a new terminal window and go to the bot-ui folder.
2. Install the necessary packages. Run: npm install.
3. This may take a minute. Once it is finished, you are ready to start.

## Step 5. How to Use the Bot

1. Start the backend. In the bot folder terminal, run: fastapi dev app/main.py.
2. The terminal will show that the server is running on http://127.0.0.1:8000.
3. Start the frontend. In the bot-ui folder terminal, run: npm run dev.
4. Open the link shown in the terminal (usually http://localhost:5173).
5. Register a new account, log in, and start asking questions about Saudi tenders.

## Technical Stack

. Backend. FastAPI (Python).
. Frontend. React.js.
. Database. PostgreSQL with pgvector.
. AI Model. Gemini 2.5 Flash.
. Authentication. JWT (JSON Web Tokens).

## License

This project is developed for professional use in the KSA contracting market.
