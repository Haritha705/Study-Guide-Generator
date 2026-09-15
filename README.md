# 📚 Study Guide Generator

**Study Guide Generator** is an AI-powered learning platform that converts lecture PDFs into a structured and personalized study pack.

Upload a PDF and the application uses **Google Gemini 3.6 Flash** to generate study materials such as summaries, MCQs, short-answer questions, answers, glossary, and flashcards. Students can also take quizzes, track their performance, identify weak topics, and use adaptive quizzes for better preparation.

---

## 🤖 AI Model Used

The primary AI model used in this project is:

**Google Gemini 3.6 Flash**

It is used for:

* Summarizing study material
* Generating MCQs
* Generating short-answer questions
* Generating model answers
* Creating glossary terms
* Generating flashcards
* RAG-based question answering
* Quiz generation
* AI tutoring

The project integrates Gemini through **LangChain**.

A fallback LLM is also configured in the backend for cases where the primary model is unavailable.

---

# ⚡ How to Run

## 1. Clone the Repository

```bash
git clone https://github.com/Haritha705/Study-Guide-Generator.git
cd Study-Guide-Generator
```

---

## 2. Backend Setup

Open a terminal:

```powershell
cd Backend
```

Create a Python virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file inside the backend and add your required credentials:

```env
MONGODB_URL=your_mongodb_connection_string
DB_NAME=Study

GEMINI_API_KEY=your_gemini_api_key

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
FRONTEND_URL=http://localhost:3000
```

Start the FastAPI backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

Swagger API documentation:

```text
http://localhost:8000/docs
```

---

## 3. Frontend Setup

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the Next.js application:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:3000
```

### Local Setup

Both servers should be running:

```text
Frontend
http://localhost:3000
       │
       ▼
Backend
http://localhost:8000
       │
       ├── Gemini
       ├── MongoDB
       ├── RAG
       └── MCP
```

**Port 3000 → Next.js frontend**

**Port 8000 → FastAPI backend**

---

# 📖 What Does the Application Do?

The application follows this workflow:

```text
Upload Lecture PDF
        ↓
Extract Text
        ↓
Process & Split Documents
        ↓
Create Embeddings
        ↓
Store in Vector Store
        ↓
Retrieve Relevant Content
        ↓
RAG + Gemini
        ↓
Generate Study Pack
        ↓
Take Quiz
        ↓
Analyze Performance
        ↓
Identify Weak Topics
        ↓
Adaptive Learning
```

---

# ✨ Main Features

### 📄 PDF Study Material Processing

Students can upload lecture notes and other educational PDFs.

The application extracts and processes the content before sending relevant information to the AI pipeline.

### 📝 AI Study Pack Generation

The application generates:

* Topic summaries
* Important concepts
* MCQs
* MCQ explanations
* Short-answer questions
* Model answers
* Glossary
* Flashcards
* Suggested study order

### 🧠 RAG

Retrieval-Augmented Generation is used to retrieve relevant information from the uploaded study material before generating AI responses.

```text
PDF
 ↓
Chunks
 ↓
Embeddings
 ↓
Vector Store
 ↓
Relevant Context
 ↓
Gemini
 ↓
Grounded Response
```

### 🧪 Quiz System

Students can take quizzes generated from their study material.

The system evaluates answers and calculates performance.

### 📊 Performance Analytics

The application analyzes quiz results and identifies topics where the student needs more revision.

### 🔄 Adaptive Quiz

Quiz difficulty can adapt based on student performance.

```text
Easy
 ↓
Good Performance
 ↓
Medium
 ↓
Good Performance
 ↓
Hard
```

The system can also focus on weaker topics.

### 📚 External Learning Resources

The project integrates external educational resources such as:

* Google Books API
* YouTube Data API

These can be used to discover additional books and educational videos.

---

# 🔌 LangChain

**LangChain** is used as the main LLM application framework.

It handles:

* Gemini integration
* Prompt management
* Document processing
* Embeddings
* Retrieval
* Vector stores
* RAG
* Tool calling
* AI workflows

---

# 🔀 LangGraph

**LangGraph** is used to build stateful AI workflows.

The project is designed around a supervisor-based multi-agent architecture.

```text
                 Supervisor Agent
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
     Drive Agent     RAG Agent     Quiz Agent
          │             │             │
          ↓             ↓             ↓
     Google Drive    Vector DB     Quiz Engine
         MCP
```

The Supervisor decides which specialized agent should process a particular request.

---

# 🤖 Multi-Agent System

The project uses specialized agents for different responsibilities.

### Supervisor Agent

Routes tasks to the appropriate agent.

### Drive Agent

Handles study-material retrieval from Google Drive through MCP.

### RAG Agent

Retrieves relevant information from the uploaded study material and provides context to the LLM.

### Quiz Agent

Handles quiz generation, evaluation, adaptive difficulty, and performance-related operations.

---

# 🔌 MCP Integration

The project uses **Model Context Protocol (MCP)** to connect AI agents with external tools.

Current MCP integration includes:

### Google Drive MCP

Students can connect their own Google Drive.

The intended architecture is:

```text
Student
   ↓
Google OAuth
   ↓
FastAPI
   ↓
User-specific credentials
   ↓
Google Drive MCP
   ↓
Student's Google Drive
```

This allows different users to connect their own Google accounts rather than using one shared Drive account.

---

# 🛠️ Technology Stack

| Category        | Technology              |
| --------------- | ----------------------- |
| Frontend        | Next.js, React          |
| Backend         | Python, FastAPI         |
| AI Model        | Google Gemini 3.6 Flash |
| AI Framework    | LangChain               |
| Agent Workflow  | LangGraph               |
| Architecture    | RAG + Multi-Agent       |
| Protocol        | MCP                     |
| Database        | MongoDB                 |
| Vector Store    | In-Memory Vector Store  |
| Books           | Google Books API        |
| Videos          | YouTube Data API        |
| API Server      | Uvicorn                 |
| Version Control | Git + GitHub            |

---

# 🏗️ Architecture

```text
                         STUDY GUIDE GENERATOR
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ Next.js Frontend│
                         │  Port 3000      │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │ FastAPI Backend │
                         │  Port 8000      │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
                 Gemini       MongoDB          MCP
                    │                           │
                    ▼                           ▼
               LangChain                 External Tools
                    │
                    ▼
                LangGraph
                    │
             ┌──────┼──────┐
             ▼      ▼      ▼
          Drive    RAG    Quiz
          Agent   Agent   Agent
             │      │      │
             ▼      ▼      ▼
           Drive  Vector  Quiz
            MCP    DB    Engine
```

---

# 📁 Project Structure

```text
Study-APP/
│
├── Backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── extract.py
│   │   │       ├── generation.py
│   │   │       ├── quiz.py
│   │   │       ├── tutor.py
│   │   │       └── export.py
│   │   │
│   │   ├── services/
│   │   │   ├── ai_pipeline.py
│   │   │   ├── progressive_quiz.py
│   │   │   ├── analytics_engine.py
│   │   │   └── mcp_client.py
│   │   │
│   │   └── schemas/
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── README.md
└── .gitignore
```

---

# 🔐 Environment & Security

Keep API keys and credentials in `.env`.

Never commit:

```text
.env
```

to GitHub.

Do not expose:

* Gemini API keys
* Google OAuth client secrets
* Google access tokens
* Google refresh tokens
* MongoDB credentials

---

# 🔗 API Documentation

Once the backend is running, FastAPI provides interactive API documentation:

```text
http://localhost:8000/docs
```

This can be used to test and understand the backend APIs.

---

# 🚧 Project Status

### Implemented

* PDF upload
* PDF text extraction
* AI study-pack generation
* Gemini integration
* LangChain pipeline
* RAG architecture
* Vector store
* MCQ generation
* Quiz evaluation
* Performance analytics
* Adaptive quiz logic
* FastAPI backend
* Next.js frontend
* MongoDB integration
* Google Books API
* YouTube Data API
* MCP client architecture
* Google Drive MCP integration
* LangGraph workflow architecture
* Multi-agent architecture

### In Progress / Planned

* Complete Supervisor Agent routing
* Complete Drive Agent
* Complete RAG Agent
* Complete Quiz Agent
* Full multi-agent workflow
* Human-in-the-loop
* Production Google OAuth
* LangSmith tracing
* LangSmith evaluation
* Production deployment

---

# 🎯 Objective

The goal of Study Guide Generator is to transform traditional lecture material into an **AI-powered personalized learning experience**.

The project combines:

```text
Generative AI
+
RAG
+
LangChain
+
LangGraph
+
Multi-Agent Systems
+
MCP
+
Tool Calling
+
Adaptive Learning
```

to help students **learn, practice, analyze, and improve** from a single study material.

---

## 👩‍💻 Author

**Haritha B.**

B.Tech Information Technology
