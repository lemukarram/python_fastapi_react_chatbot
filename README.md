
# RSG Tender Chat BOT (AI Chatbot Pro)

A specialized AI assistant built to help contractors and businesses navigate the Saudi Arabian tender market. It provides expert advice on the Etimad platform, local procurement laws, and bidding requirements.

## Project Overview

The RSG Tender Chat BOT uses Gemini 2.5 Flash to answer questions. It is a full-stack system that includes a database to remember your chat history and search through tender documents using vector embeddings.

## Modern Setup with Docker (Recommended)

The easiest way to run this project is using Docker. This ensures that the database, pgvector extension, backend, and frontend all work together perfectly without manual configuration.

### Prerequisites
1. Docker Desktop installed on your computer.
2. Git to clone the repository.

---

### Step 1. Prepare your Environment
Create a file named .env in the root directory of the project and add your credentials.

GEMINI_API_KEY="AIzaSy-google-api-key"
SECRET_KEY="RIYADH_TECH_WITH_MUK_SECURE_TOKEN_2024"
PROJECT_NAME="AI Chatbot Pro"

# Database credentials for the container
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=bot_db
DATABASE_URL="postgresql+asyncpg://myuser:mypassword@db:5432/bot_db"

### Step 2. Run the Project
Open your terminal in the project root and run this command.

docker-compose up --build

This command will.
1. Set up a PostgreSQL database with pgvector pre-installed.
2. Build and start the FastAPI backend (with automatic reload).
3. Build and start the React frontend using the legacy-peer-deps fix for npm.

### Step 3. Access the Application
* Frontend. http://localhost:3000
* API Documentation. http://localhost:8000/docs
* Database Port. 5432 (Internal access via 'db' service)

---

## Troubleshooting

### Port 8000 already in use
If you see an error about port 8000 being allocated, another process is using it.
Fix. Run 'lsof -i :8000' to find the PID, then 'kill -9 PID' to stop it.

### Git Branch Name
If you cannot push to main, your local branch might be named master.
Fix. Run 'git branch -m master main' to rename it.

### NPM Install Errors
If you see dependency conflicts, the Dockerfile is configured to use '--legacy-peer-deps' to bypass these issues automatically.

---

## Technical Details

* Backend. FastAPI (Python 3.11).
* Frontend. React (Vite).
* AI Model. Gemini 2.5 Flash.
* Database. PostgreSQL with pgvector for vector search.
* Security. JWT Authentication via FastAPI Users.

## Project Structure
* /bot. FastAPI backend code.
* /bot-ui. React frontend code.
* docker-compose.yml. Orchestration for all services.

## Credits
Created by Mukarram Hussain (Tech with muk). Professional use for KSA Contracting & Tender Market.
