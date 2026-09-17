# StudyPack Project Architecture

This document outlines the high-level architecture of the StudyPack application.

## System Architecture Diagram

```mermaid
flowchart TD
    App[StudyPack App]
    
    subgraph Frontend [Frontend - Next.js]
        UI[React Components & Tailwind CSS]
        State[Zustand Store]
        Auth[Clerk Authentication]
        Routes[App Router]
        
        Routes --> Dashboard[/dashboard]
        Routes --> CreatePack[/create]
        Routes --> StudyView[/study-pack/:id]
        Routes --> QuizMode[/quiz]
        Routes --> AITutor[/tutor]
        Routes --> Analytics[/analytics]
    end
    
    subgraph Backend [Backend - FastAPI]
        API[REST API Endpoints /api/v1]
        
        API --> Extraction[/extract]
        API --> Generation[/generate]
        API --> QuizEngine[/quiz]
        API --> Tutor[/tutor]
        API --> Export[/export]
        API --> StudyPacks[/study-pack]
        
        Core[Core Services]
        Core --> AIPipeline[AI Pipeline - LangChain/LangGraph]
        Core --> AnalyticsEngine[Analytics Engine]
        Core --> ProgressiveQuiz[Progressive Quiz Logic]
        Core --> RevisionEngine[Spaced Repetition]
        Core --> RAG[RAG Service]
        
        DataIO[Data Processors]
        DataIO --> PDFParser[PDF Parser]
        DataIO --> Exporters[PDF & CSV Exporters]
        DataIO --> MCPClient[MCP Client - GitHub/Drive]
    end
    
    subgraph Database [Database Layer]
        Primary[(SQLite/aiosqlite)]
        Document[(MongoDB/Motor)]
    end
    
    subgraph External [External Services]
        LLMs[LLM Providers]
        LLMs --> Gemini[Google GenAI]
        LLMs --> Anthropic[Claude]
        LLMs --> Mistral[Mistral AI]
        
        Cloud[Integrations]
        Cloud --> Drive[Google Drive]
        Cloud --> GitHub[GitHub]
    end

    App --> Frontend
    App --> Backend
    Frontend --> Backend
    Backend --> Database
    Backend --> External
```

## Explanation

The StudyPack application follows a modern decoupled client-server architecture.

### 1. Frontend (Next.js & React)
- **Framework**: Built with Next.js using the App Router for seamless server-side rendering and static generation.
- **Styling & UI**: Tailwind CSS is used for utility-first styling, complemented by Framer Motion for animations.
- **State Management**: Zustand handles global state, providing a lightweight alternative to Redux.
- **Authentication**: Handled via Clerk, providing secure routes like `/sign-in` and `/sign-up`.
- **Key Modules**:
  - Dashboard: Overview of user's study packs.
  - Create: Interface to upload documents or connect integrations to generate study materials.
  - Quiz & Tutor: Interactive interfaces for testing knowledge and chatting with the AI.

### 2. Backend (FastAPI & Python)
- **Framework**: FastAPI provides high-performance, asynchronous REST API endpoints.
- **AI Core**: LangChain and LangGraph orchestrate the AI pipelines. The system is model-agnostic, supporting Gemini, Anthropic, and Mistral.
- **Services**:
  - **Extraction**: Parses text from PDFs.
  - **Generation**: Uses LLMs to generate study notes, summaries, and flashcards.
  - **Quiz Engine**: A progressive quiz engine that adapts to user performance.
  - **Tutor**: Conversational AI utilizing Retrieval-Augmented Generation (RAG) against study materials.
  - **MCP Client**: Interacts with External systems (Google Drive, GitHub) to pull in contextual data.
  - **Exporters**: Allows downloading materials as PDFs or CSVs.

### 3. Database Layer
- **SQLite (via aiosqlite)**: Handles structured data such as user metadata, study pack schemas, and quiz scores.
- **MongoDB (via Motor)**: Handles unstructured document data, vector embeddings for RAG, and extensive AI chat logs.

### 4. External Services
- **LLM APIs**: Core intelligence layer for generating content.
- **Context Providers**: Integrations with GitHub and Google Drive allow users to build study packs from existing repos and cloud documents.
