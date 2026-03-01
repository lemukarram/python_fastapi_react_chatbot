# RSG Tender BOT

A full-stack AI-powered chatbot assistant specialized for the **Saudi Arabian Tendering and Contracting market**. It helps contractors and businesses navigate the Etimad platform, comply with Saudi Government Procurement Law, and prepare competitive bids — all powered by Google Gemini and a RAG (Retrieval-Augmented Generation) knowledge base.

> Built by **Mukarram Hussain** — Tech with Muk | Jeddah, KSA

---

## Features

- **AI Chat** — Powered by Gemini 2.5 Flash with expert system instructions for the KSA tender market
- **RAG Knowledge Base** — Admins add tender laws, procedures, and regulations; the bot retrieves relevant context before every answer
- **Persistent Chat History** — Every conversation is saved per user and reloaded on login
- **JWT Authentication** — Secure register/login with token-based auth via FastAPI Users
- **Vector Search** — pgvector + Gemini embeddings (768-dim) for semantic similarity search
- **Admin Panel** — Superuser dashboard to manage users, view all chats, and control the knowledge base
- **Knowledge Base Management** — Admins can add text chunks, upload `.txt`/`.pdf` files, and delete entries
- **Database Migrations** — Alembic manages all schema changes automatically on startup
- **Unit Tests** — 12 pytest tests covering auth, all API endpoints, and all admin endpoints
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
| **PDF Parsing** | PyMuPDF (fitz) |
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
│   │   │   ├── chat.py         # Chat, history endpoints (ingest: admin only)
│   │   │   └── admin.py        # Admin-only endpoints (users, chats, knowledge base)
│   │   ├── core/
│   │   │   ├── auth.py         # JWT strategy, current_active_user, current_superuser
│   │   │   ├── config.py       # Pydantic settings from .env
│   │   │   └── db.py           # Async engine and session factory
│   │   ├── models/
│   │   │   └── models.py       # User, ChatMessage, KnowledgeBase tables
│   │   ├── providers/
│   │   │   ├── base.py         # Abstract AI provider interface
│   │   │   └── gemini.py       # Gemini client (singleton)
│   │   ├── schemas/
│   │   │   ├── admin.py        # Admin request/response schemas
│   │   │   ├── chat.py         # Chat request/response schemas
│   │   │   └── user.py         # User schemas
│   │   ├── services/
│   │   │   ├── chat_service.py # Core chat logic + history
│   │   │   └── rag_service.py  # Embedding + vector search (singleton)
│   │   └── main.py             # FastAPI app entrypoint
│   ├── alembic/                # Database migrations
│   │   ├── versions/
│   │   │   └── 20250228_0001_initial_schema.py
│   │   └── env.py
│   ├── tests/
│   │   ├── conftest.py         # Shared fixtures (in-memory DB, mocked AI, superuser)
│   │   ├── test_auth.py        # Register and login tests
│   │   ├── test_api.py         # History, message, and ingest tests
│   │   └── test_admin.py       # All admin endpoint tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── example.env
│
└── bot-ui/                     # React Frontend
    ├── src/
    │   └── App.jsx             # Full chat UI + admin panel (single file)
    └── Dockerfile
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Register a new user | No |
| `POST` | `/auth/jwt/login` | Login and receive JWT token | No |
| `GET` | `/users/me` | Get current user profile + superuser status | Yes |

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

### Chat (Regular Users)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/v1/history` | Get full chat history for logged-in user | User |
| `POST` | `/api/v1/message` | Send a message and get an AI reply with sources | User |

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

---

### Admin Endpoints (Superuser Only)

All admin endpoints require a superuser JWT token. Regular users receive `403 Forbidden`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/admin/users` | List all users with message counts |
| `GET` | `/api/v1/admin/chats` | List all chat messages across all users |
| `GET` | `/api/v1/admin/knowledge` | List all knowledge base entries (200-char preview) |
| `POST` | `/api/v1/admin/knowledge/upload` | Upload a `.txt` or `.pdf` file to the knowledge base |
| `DELETE` | `/api/v1/admin/knowledge/{id}` | Delete a knowledge base entry by ID |
| `POST` | `/api/v1/ingest` | Add text chunks directly to the knowledge base |

**POST /api/v1/ingest — Request:**
```json
{
  "texts": [
    "Etimad platform requires CR registration before bidding.",
    "Bid security must be between 1% and 2% of the total tender value."
  ]
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

```bash
cp bot/example.env bot/.env
```

Edit `bot/.env` and fill in your values:

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
| **API Health Check** | http://localhost:8000 |

---

## Admin Setup

### Creating an Admin Account

The `/auth/register` endpoint always creates regular users. To promote a user to admin:

**1. Register normally** via the UI at `http://localhost:3000`

**2. Promote to superuser** via the database:

```bash
docker exec -it tender_db psql -U myuser -d bot_db
```

```sql
UPDATE "user" SET is_superuser = true WHERE email = 'your@email.com';
\q
```

Or in a single command:

```bash
docker exec -it tender_db psql -U myuser -d bot_db -c "UPDATE \"user\" SET is_superuser = true WHERE email = 'your@email.com';"
```

**3. Log in** — the **Admin Panel** button (🛡) will appear in the top-right of the chat UI.

---

### Admin Panel Features

| Tab | Capabilities |
|---|---|
| **Users** | View all registered users, active status, role, message count |
| **Chats** | Monitor all conversations across all users (newest first) |
| **Knowledge Base** | Add text chunks, upload `.txt`/`.pdf` files, view and delete entries |

---

## Running Tests

Tests use an **in-memory SQLite database** — no real Postgres or Gemini API calls are made.

### From your Mac terminal (Docker must be running)

```bash
docker exec tender_backend pytest --tb=short -v
```

### From Docker Desktop UI

1. Open **Docker Desktop** → click `tender_backend` container → **Exec** tab
2. Type: `pytest --tb=short -v`

### Run specific test files

```bash
# Auth tests only
docker exec tender_backend pytest tests/test_auth.py -v

# API (chat) tests only
docker exec tender_backend pytest tests/test_api.py -v

# Admin endpoint tests only
docker exec tender_backend pytest tests/test_admin.py -v
```

### Expected output

```
collected 12 items

tests/test_admin.py::test_admin_requires_superuser         PASSED  [  8%]
tests/test_admin.py::test_admin_list_users                 PASSED  [ 16%]
tests/test_admin.py::test_admin_list_chats                 PASSED  [ 25%]
tests/test_admin.py::test_admin_list_knowledge             PASSED  [ 33%]
tests/test_admin.py::test_admin_upload_txt_file            PASSED  [ 41%]
tests/test_admin.py::test_admin_delete_knowledge_entry     PASSED  [ 50%]
tests/test_api.py::test_get_history_empty_for_new_user     PASSED  [ 58%]
tests/test_api.py::test_send_message_returns_reply         PASSED  [ 66%]
tests/test_api.py::test_ingest_requires_superuser          PASSED  [ 75%]
tests/test_api.py::test_ingest_documents                   PASSED  [ 83%]
tests/test_auth.py::test_register_success                  PASSED  [ 91%]
tests/test_auth.py::test_login_success                     PASSED  [100%]

12 passed in 1.34s
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

## Database Access (pgAdmin / psql)

### Connect with pgAdmin 4

| Field | Value |
|---|---|
| Host | `127.0.0.1` |
| Port | `5432` |
| Database | `bot_db` |
| Username | `myuser` |
| Password | `mypassword` |

> Use `127.0.0.1` not `localhost` to ensure pgAdmin connects to the Docker container, not your local Postgres.

### Direct psql access

```bash
docker exec -it tender_db psql -U myuser -d bot_db
```

### Key tables

| Table | Contents |
|---|---|
| `user` | Registered accounts — set `is_superuser = true` to promote admins |
| `chat_messages` | All conversation history per user |
| `knowledge_base` | RAG text chunks with 768-dim vector embeddings |

---

## Stopping the Project

```bash
# Stop all containers (data preserved)
docker compose down

# Stop and delete all data including the database volume
docker compose down -v
```

---

## Troubleshooting

**Port 8000 or 3000 already in use**
```bash
lsof -i :8000   # find what's using the port
kill -9 <PID>
```

**Backend keeps restarting**
```bash
docker logs tender_backend
```

**Alembic migration issues**
```bash
# Check current migration version
docker exec tender_backend alembic current

# Apply pending migrations
docker exec tender_backend alembic upgrade head
```

**pgAdmin connecting to wrong database**

Use `127.0.0.1` as the host (not `localhost`) and make sure no local Postgres is running on port 5432:
```bash
brew services stop postgresql   # macOS
```

---

## Credits

Created by **Mukarram Hussain** — Tech with Muk
Professional AI assistant for the KSA Contracting and Tender market.
Built with FastAPI, Gemini, pgvector, React, and Docker.
