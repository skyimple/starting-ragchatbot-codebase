# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Retrieval-Augmented Generation (RAG) system that answers questions about course materials using ChromaDB for semantic search and Anthropic Claude for AI-powered responses. Full-stack web app with FastAPI backend and vanilla HTML/CSS/JS frontend.

## Commands

```bash
# Install dependencies (always use uv - never pip)
uv sync

# Start development server (always use uv run)
cd backend && uv run uvicorn app:app --reload --port 8000

# Or use the provided script
./run.sh
```

## Architecture

```
Frontend (static/) → FastAPI (backend/app.py) → RAGSystem (backend/rag_system.py)
                                              ├→ VectorStore → ChromaDB
                                              ├→ AIGenerator → Anthropic Claude
                                              └→ DocumentProcessor → docs/*.txt
```

### Key Components

| File | Responsibility |
|------|----------------|
| `backend/rag_system.py` | Core orchestration - coordinates query flow |
| `backend/vector_store.py` | ChromaDB wrapper for semantic search |
| `backend/ai_generator.py` | Claude API calls with tool execution |
| `backend/document_processor.py` | Parses docs/*.txt into chunks |
| `backend/session_manager.py` | Conversation history management |
| `backend/search_tools.py` | Tool abstraction for Claude to search content |
| `backend/config.py` | All configuration (models, chunk sizes, API keys) |

### Data Flow

1. On startup: `DocumentProcessor` parses `docs/*.txt` files and stores chunks in ChromaDB
2. Query: `POST /api/query` → `RAGSystem.query()` → Claude with `search_course_content` tool
3. Tool: `VectorStore.search()` returns semantically similar chunks
4. Response: Claude generates answer with sources

### API Endpoints

- `POST /api/query` - Send a question, returns answer with sources
- `GET /api/courses` - List available courses
- `GET /` - Serve frontend SPA

## Configuration

All settings in `backend/config.py`:
- `ANTHROPIC_MODEL`: "claude-sonnet-4-20250514"
- `EMBEDDING_MODEL`: "all-MiniLM-L6-v2"
- `CHUNK_SIZE`: 800 characters
- `CHUNK_OVERLAP`: 100 characters
- `CHROMA_PATH`: "./chroma_db"

## Document Format

Files in `docs/` follow this structure:
```
Course Title: [Name]
Course Link: [URL]
Course Instructor: [Name]

Lesson 1: [Title]
Lesson Link: [URL]
[Lesson content...]
```

## Tech Stack

- Python 3.13, FastAPI, ChromaDB, Anthropic SDK, sentence-transformers, uvicorn, python-dotenv
