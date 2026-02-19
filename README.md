# SAARTHI Backend Documentation

## Overview

This backend is built with FastAPI and SQLAlchemy, providing a robust API for an AI-powered interview preparation platform. It features user authentication, interview session management, question generation, answer evaluation, and subject management, with AI and embedding integrations.

---

## Project Structure

```
backend/
  alembic/                # Database migrations
  app/
    core/                 # Core authentication, config, security
    database/             # SQLAlchemy models and DB setup
    routes/               # All API endpoints (v1)
    schemas/              # Pydantic schemas
    services/             # AI, embeddings, question/answer logic
    main.py               # FastAPI app entrypoint
  requirements.txt        # Python dependencies
```

---

## Main Features & Functionalities

### 1. **Authentication & Authorization**

- **Signup/Login**: Email-based registration and login with JWT access/refresh tokens.
- **Role-based Access**: Admin and student roles enforced on endpoints.
- **Token Refresh**: Secure refresh endpoint for access tokens.

### 2. **Interview Sessions**

- **Start Session**: Begin a new interview session for a subject and mode.
- **Session Ownership**: Only session owners can interact with their sessions.
- **Session Status**: Tracks progress (in_progress, ended, etc).

### 3. **Questions**

- **List Questions**: Filter by Bloom level, difficulty, etc.
- **Generate Questions**: AI-powered, personalized question generation using LLMs and embeddings.

### 4. **Answers**

- **Submit Answer**: Submit and auto-evaluate answers using AI (LLM + context from embeddings).
- **Scoring & Feedback**: Returns score, explanation, and improvement feedback.

### 5. **Subjects**

- **List Subjects**: Get all available subjects.
- **Add/Update/Delete**: Admin-only endpoints for subject management.

### 6. **AI & Embeddings**

- **LLM Integration**: Uses Groq API (Llama 3) for question generation and answer evaluation.
- **Embeddings**: Uses Sentence Transformers and Pinecone for context and memory.

---

## API Routes

### **Auth** (`/v1/auth`)

- `POST /signup` — Register new user
- `POST /login` — Login and get tokens
- `POST /refresh` — Refresh access token

### **Interview Sessions** (`/v1/interview_sessions`)

- `POST /start` — Start a new session
- `GET /list` — List user sessions
- `POST /end` — End a session

### **Questions** (`/v1/questions`)

- `GET /list` — List questions (filterable)
- `POST /generate/{session_id}` — Generate questions for a session

### **Answers** (`/v1/answers`)

- `POST /submit` — Submit and auto-evaluate answer

### **Subjects** (`/v1/subjects`)

- `GET /list` — List all subjects
- `POST /add` — Add a subject (admin)
- `PUT /update` — Update a subject (admin)
- `DELETE /delete` — Delete a subject (admin)

---

## Key Services & Integrations

- **AI (LLM)**: Groq API (Llama 3) for question/answer logic
- **Embeddings**: Sentence Transformers for vectorization, Pinecone for storage/query
- **Database**: SQLAlchemy ORM, Alembic migrations
- **Security**: JWT tokens, OAuth2, role-based dependencies

---

## Database Models (Summary)

- **User**: id, name, email, password_hash, role, etc.
- **Subject**: id, name, description
- **Question**: id, question_text, sample_answer, bloom_level, difficulty, etc.
- **InterviewSession**: id, user_id, subject_id, mode, status, etc.
- **Answer**: (linked to session/question/user)

---

## How It Works (Flow)

1. **User registers/logins** → receives JWT tokens
2. **Starts interview session** (selects subject/mode)
3. **Questions generated** (AI, personalized)
4. **User submits answers** → evaluated by AI, feedback returned
5. **Admin manages subjects/questions**

---

## Requirements

- Python 3.10+
- FastAPI, SQLAlchemy, Pydantic
- Groq, Pinecone, Sentence Transformers

---

## Notes

- All endpoints require authentication unless public.
- Admin-only endpoints are protected by role checks.
- AI/embedding keys must be set in environment/config.

---

_For detailed code, see the respective files in each folder._
