
# RSG Tender Chat BOT

A specialized AI assistant built to help contractors and businesses navigate the Saudi Arabian tender market. It provides expert advice on the Etimad platform. local procurement laws. and bidding requirements.

## Project Overview

The RSG Tender Chat BOT uses Gemini 2.5 Flash to answer questions. It is a full-stack system that includes a database to remember your chat history and search through tender documents.

## Requirements

Before you start. make sure you have these installed on your computer.

1. Python 3.10 or higher.
2. Node.js (for the frontend).
3. PostgreSQL database.

---

## Step 1. Database Configuration

You must enable the vector extension in your database for the AI to work.

1. Create a new database in PostgreSQL named bot_db.
2. Open your terminal or a tool like pgAdmin.
3. Run this command: CREATE EXTENSION IF NOT EXISTS vector.

---

## Step 2. Backend Setup (Python)

Follow these steps to set up the server.

1. Open your terminal and go to the bot folder.
   . Command: cd bot

2. Create a virtual environment.
   . Command: python -m venv venv

3. Activate the virtual environment.
   . For Mac or Linux: source venv/bin/activate
   . For Windows: venv\\Scripts\\activate

4. Install all the necessary Python packages.
   . Command: pip install -r requirements.txt

5. Create a .env file.
   . Create a new file named .env in the bot folder.
   . Add your keys inside like this.
   . GEMINI_API_KEY=your_key_here
   . DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/bot_db
   . SECRET_KEY="RIYADH_TECH_WITH_MUK_SECURE_TOKEN_2024"
   . PROJECT_NAME="AI Chatbot Pro"

---

## Step 3. Frontend Setup (React)

Follow these steps to set up the chat screen.

1. Open a new terminal window.
2. Go to the UI folder.
   . Command: cd bot-ui

3. Install the dependencies.
   . Command: npm install

---

## Step 4. How to Run the Project

You must have two terminals open. one for the backend and one for the frontend.

1. Start the Backend.
   . Go to the bot folder.
   . Ensure the venv is active.
   . Command: fastapi dev app/main.py

2. Start the Frontend.
   . Go to the bot-ui folder.
   . Command: npm run dev

3. Open your browser.
   . Go to the link shown in the terminal (usually http://localhost:5173).

---

## Technical Details

. Backend. FastAPI.
. Frontend. React.
. AI Model. Gemini 2.5 Flash.
. Database. PostgreSQL with pgvector.
. Security. JWT Authentication.

## License

This software is for professional use in the KSA contracting and tender market.
