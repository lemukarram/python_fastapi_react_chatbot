# RSG Tender BOT

A full-stack AI-powered chatbot assistant specialized for the **Saudi Arabian Tendering and Contracting market**. It helps contractors and businesses navigate the Etimad platform, comply with Saudi Government Procurement Law, and prepare competitive bids — all powered by Google Gemini and a RAG (Retrieval-Augmented Generation) knowledge base.

> Built by **Mukarram Hussain** — Tech with Muk | Jeddah, KSA

---

## Features

- **AI Chat** — Powered by Gemini 2.5 Flash with expert system instructions for KSA tender market
- **RAG Knowledge Base** — Add tender laws, procedures, and regulations; the bot retrieves relevant context before every answer
- **Persistent Chat History** — Every conversation is saved per user and reloaded on login
- **JWT Authentication** — Secure register/login with token-based auth via FastAPI Users
- **Vector Search** — pgvector + Gemini embeddings (768-dim) for semantic similarity search
- **Database Migrations** — Alembic manages all schema changes automatically on startup
- **Unit Tests** — 5 pytest tests covering auth and all API endpoints
- **Fully Dockerized** — One command to run everything: DB, backend, frontend

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite |
| **Backend** | FastAPI, Python 3.11 |
| **AI Model** | Google Gemini 2.5 Flash |
| **Embeddings** | Gemini Embedding 001 (768 dimensions) |
| **Database** | PostgreSQL 15 + pgvector extension |
| **ORM** | SQLAlchemy (async) |
| **Migrations** | Alembic |
| **Auth** | FastAPI Users + JWT (Bearer Token) |
| **Testing** | pytest, pytest-asyncio, httpx, aiosqlite |
| **Containers** | Docker, Docker Compose |

---

## Project Structure

```
tander-bot/
├── docker-compose.yml          # Orchestrates all 3 services
│
├── bot/                        # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   └── chat.py         # Chat, history, and ingest endpoints
│   │   ├── core/
│   │   │   ├── auth.py         # JWT strategy and FastAPI Users setup
│   │   │   ├── config.py       # Pydantic settings from .env
│   │   │   └── db.py           # Async engine and session factory
│   │   ├── models/
│   │   │   └── models.py       # User, ChatMessage, KnowledgeBase tables
│   │   ├── providers/
│   │   │   ├── base.py         # Abstract AI provider interface
│   │   │   ├── factory.py      # Provider factory (swap AI models easily)
│   │   │   └── gemini.py       # Gemini client (singleton)
│   │   ├── schemas/
│   │   │   ├── chat.py         # Request/Response schemas
│   │   │   └── user.py         # User schemas
│   │   ├── services/
│   │   │   ├── chat_service.py # Core chat logic + history
│   │   │   └── rag_service.py  # Embedding + vector search (singleton)
│   │   └── main.py             # FastAPI app entrypoint
│   ├── alembic/                # Database migrations
│   │   ├── versions/
│   │   │   └── 20250228_0001_initial_schema.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── tests/
│   │   ├── conftest.py         # Shared fixtures (in-memory DB, mocked AI)
│   │   ├── test_auth.py        # Register and login tests
│   │   └── test_api.py         # History, message, and ingest tests
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── example.env
│
└── bot-ui/                     # React Frontend
    ├── src/
    │   └── App.jsx             # Full chat UI with knowledge base panel
    └── Dockerfile
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/jwt/login` | Login and receive JWT token | No |

**Register body:**
```json
{
  "email": "user@example.com",
  "password": "YourPassword123!"
}
```

**Login body** (form-urlencoded):
```
username=user@example.com&password=YourPassword123!
```

**Login response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

---

### Chat

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/v1/history` | Get full chat history for logged-in user | Yes |
| `POST` | `/api/v1/message` | Send a message and get an AI reply | Yes |
| `POST` | `/api/v1/ingest` | Add text chunks to the knowledge base | Yes |

**POST /api/v1/message — Request:**
```json
{
  "message": "What are the bid security requirements on Etimad?"
}
```

**POST /api/v1/message — Response:**
```json
{
  "reply": "Bid security is typically required at 1% to 2% of the total tender value...",
  "sources": [
    "Bid security must be between 1% and 2% of the total tender value.",
    "Etimad platform requires CR registration before submitting any bid."
  ]
}
```

**POST /api/v1/ingest — Request:**
```json
{
  "texts": [
    "Etimad platform requires CR registration before bidding.",
    "Bid security must be between 1% and 2% of the total tender value.",
    "LCGPA requires a minimum 30% Saudi workforce for compliance."
  ]
}
```

**POST /api/v1/ingest — Response:**
```json
{
  "inserted": 3,
  "message": "Successfully inserted 3 of 3 chunk(s) into the knowledge base."
}
```

---

### System

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/docs` | Interactive Swagger UI |

---

## Installation & Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A **Google Gemini API Key** — get one free at [aistudio.google.com](https://aistudio.google.com)
- Git

---

### Step 1 — Clone the repository

```bash
git clone <your-repo-url>
cd tander-bot
```

---

### Step 2 — Create the environment file

Create a `.env` file inside the `bot/` folder:

```bash
cp bot/example.env bot/.env
```

Then open `bot/.env` and fill in your values:

```env
GEMINI_API_KEY="your-gemini-api-key-here"
SECRET_KEY="your-random-secret-key-min-32-chars"
PROJECT_NAME="RSG Tender BOT"
DATABASE_URL="postgresql+asyncpg://myuser:mypassword@db:5432/bot_db"
```

> **Tip:** Generate a strong secret key with:
> ```bash
> openssl rand -hex 32
> ```

---

### Step 3 — Run the project

```bash
docker compose up --build
```

This single command will:
1. Start **PostgreSQL + pgvector** database
2. Run **Alembic migrations** to create all tables automatically
3. Start the **FastAPI backend** on port `8000`
4. Start the **React frontend** on port `3000`

---

### Step 4 — Access the application

| Service | URL |
|---|---|
| **Chat UI** | http://localhost:3000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Root / Health** | http://localhost:8000 |

---

### Step 5 — Add your first knowledge base entries

Once logged in, click the **`+ Knowledge Base`** button in the top-right corner of the chat UI.

Paste your tender knowledge — separate each entry with a **blank line**:

```
Etimad platform requires CR registration before submitting any bid.

Bid security must be between 1% and 2% of the total tender value.

LCGPA requires a minimum 30% Saudi workforce for compliance with local content rules.

Technical proposals must be submitted separately from financial proposals on Etimad.
```

Click **Save to Knowledge Base**. The bot will now use these as sources when answering related questions.

---

## Running Tests

Tests run inside the Docker container using an **in-memory SQLite database** — no real Postgres or Gemini API calls are made.

### Option 1 — From your terminal (Docker must be running)

```bash
docker exec tender_backend pytest --tb=short -v
```

### Option 2 — From Docker Desktop UI

1. Open **Docker Desktop**
2. Click on the **`tender_backend`** container
3. Click the **`>_ Exec`** tab
4. Type: `pytest --tb=short -v`

### Run specific test files

```bash
# Auth tests only
docker exec tender_backend pytest tests/test_auth.py -v

# API tests only
docker exec tender_backend pytest tests/test_api.py -v
```

### Expected output

```
collected 5 items

tests/test_api.py::test_get_history_empty_for_new_user PASSED   [ 20%]
tests/test_api.py::test_send_message_returns_reply PASSED        [ 40%]
tests/test_api.py::test_ingest_documents PASSED                  [ 60%]
tests/test_auth.py::test_register_success PASSED                 [ 80%]
tests/test_auth.py::test_login_success PASSED                    [100%]

5 passed in 1.10s
```

---

## How the RAG Pipeline Works

```
User sends a message
        │
        ▼
Embed the message using Gemini gemini-embedding-001 (768 dims)
        │
        ▼
Cosine similarity search against knowledge_base table (pgvector)
        │
        ▼
Top 3 matching chunks retrieved as context
        │
        ▼
Build prompt:  [Context] + [Last 5 messages] + [User message]
        │
        ▼
Send to Gemini 2.5 Flash with system instructions
        │
        ▼
Return reply + sources to the frontend
```

---

## Stopping the Project

```bash
# Stop all containers
docker compose down

# Stop and delete all data (including the database volume)
docker compose down -v
```

---

## Troubleshooting

**Port 8000 or 3000 already in use**
```bash
# Find what's using the port
lsof -i :8000
# Kill it
kill -9 <PID>
```

**Backend keeps restarting**
```bash
# Check backend logs
docker logs tender_backend
```

**"alembic_version" table issues after schema changes**
```bash
# Check current migration version in DB
docker exec tender_backend alembic current

# Apply any pending migrations
docker exec tender_backend alembic upgrade head
```

---

## Credits

Created by **Mukarram Hussain** — Tech with Muk
Professional AI assistant for the KSA Contracting and Tender market.
Built with FastAPI, Gemini, pgvector, React, and Docker.
