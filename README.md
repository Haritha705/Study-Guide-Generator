# StudyPack AI (Study Guide Generator)

## Overview
StudyPack AI is an intelligent study material generator and dynamic quiz engine. It transforms unstructured PDFs or syllabi into progressive quizzes, structured notes, glossaries, and provides weak-topic analytics.

## Core Features
- **Input System**: Drag-and-drop PDF upload or raw text paste.
- **AI Notes**: Topic-wise notes with highlights and callouts.
- **Progressive 20-MCQ Bank**: Distributed cognitive depth (Easy, Medium, Hard).
- **Short Answer Questions (SAQs)**: With model answers.
- **Glossary**: Core terminology extraction.
- **Interactive Quiz & Analytics**: Auto-grading, difficulty breakdown, and weak-topic detection.
- **RAG AI Tutor**: Context-bounded chat sidebar grounded in the uploaded material.
- **Revision Mode**: Isolates callouts, definitions, and missed questions.
- **Exports**: PDF and CSV export pipelines.

## AI Models & Selection
- **Claude API (claude-3-5-sonnet)**: Primary reasoning model used for complex conceptual synthesis, generating progressive MCQs, and grounded tutoring. Chosen for superior structured instruction-following.
- **Mistral API (mistral-large / mistral-small)**: Secondary model used for fast text processing, glossary extraction, and preliminary RAG chunk processing. Chosen for high-throughput and cost-efficiency.

## Architecture Stack
- **Frontend**: Next.js (App Router, TypeScript, Tailwind CSS, Shadcn UI)
- **Backend/AI Processing**: LangChain, LangGraph, LangSmith, MCP (Model Context Protocol), RAG Engine
- **Orchestration**: LangGraph manages complex workflow loops (e.g., PDF -> Chunking -> Extraction -> Evaluation).
- **Observability**: LangSmith traces API calls and monitors latency.

## How to Run Locally

### Step 1: Clone Repository
```bash
git clone https://github.com/Haritha705/Study-Guide-Generator.git
cd Study-APP
```

### Step 2: Install Dependencies
For the Backend:
```bash
cd Backend
pip install -r requirements.txt
```

For the Frontend:
```bash
cd Frontend
npm install
```

### Step 3: Configure Environment
Create a `.env` file in the appropriate directories with the following keys:
```env
# Anthropic Claude API Key (Primary Reasoning Model)
ANTHROPIC_API_KEY=your_claude_api_key_here

# Mistral AI API Key (Extraction & Fast Summarization)
MISTRAL_API_KEY=your_mistral_api_key_here

# LangSmith Observability
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT="studypack-ai"

# Vector Store / RAG Configuration
VECTOR_STORE_PROVIDER=memory
```

### Step 4: Run Servers
Backend:
```bash
cd Backend
python server.py (or appropriate command)
```

Frontend:
```bash
cd Frontend
npm run dev
```
