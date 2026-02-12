"""
Shared fixtures and test configuration for RAG system API tests.

This module provides:
- Mock RAGSystem components for isolated testing
- Test data fixtures for requests and responses
- Test FastAPI app without static file mounting
- Async HTTP client for endpoint testing
"""

import os
import sys
from pathlib import Path
from typing import List, Generator, Any
from unittest.mock import AsyncMock, MagicMock, Mock
import pytest
from httpx import AsyncClient, ASGITransport

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_course_data() -> dict:
    """Sample course data for testing."""
    return {
        "total_courses": 2,
        "course_titles": ["Deep Learning Specialization", "NLP with Deep Learning"]
    }


@pytest.fixture
def sample_query_request() -> dict:
    """Sample query request payload."""
    return {
        "query": "What is backpropagation?",
        "session_id": None
    }


@pytest.fixture
def sample_query_request_with_session() -> dict:
    """Sample query request with existing session ID."""
    return {
        "query": "Explain gradient descent",
        "session_id": "test_session_123"
    }


@pytest.fixture
def sample_query_response() -> dict:
    """Sample query response data."""
    return {
        "answer": "Backpropagation is an algorithm for training neural networks...",
        "sources": ["Lesson 3: Neural Networks", "Lesson 4: Optimization"],
        "session_id": "test_session_123"
    }


@pytest.fixture
def sample_session_id() -> str:
    """Sample session ID."""
    return "test_session_abc123"


# =============================================================================
# Mock Component Fixtures
# =============================================================================

@pytest.fixture
def mock_session_manager() -> Mock:
    """Mock SessionManager for testing."""
    manager = Mock()
    manager.create_session = Mock(return_value="test_session_123")
    manager.get_conversation_history = Mock(return_value=None)
    manager.add_exchange = Mock()
    return manager


@pytest.fixture
def mock_vector_store() -> Mock:
    """Mock VectorStore for testing."""
    store = Mock()
    store.search = Mock(return_value=[
        {
            "content": "Backpropagation computes gradients...",
            "metadata": {"course": "Deep Learning", "lesson": 3}
        }
    ])
    store.get_course_count = Mock(return_value=2)
    store.get_existing_course_titles = Mock(return_value=[
        "Deep Learning Specialization",
        "NLP with Deep Learning"
    ])
    return store


@pytest.fixture
def mock_ai_generator() -> Mock:
    """Mock AIGenerator for testing."""
    generator = Mock()
    generator.generate_response = AsyncMock(return_value=(
        "Backpropagation is an algorithm for training neural networks by computing gradients...",
        []
    ))
    return generator


@pytest.fixture
def mock_tool_manager() -> Mock:
    """Mock ToolManager for testing."""
    manager = Mock()
    manager.get_tool_definitions = Mock(return_value=[
        {
            "name": "search_course_content",
            "description": "Search course content",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        }
    ])
    manager.get_last_sources = Mock(return_value=[
        "Deep Learning Specialization - Lesson 3: Neural Networks"
    ])
    manager.reset_sources = Mock()
    return manager


@pytest.fixture
def mock_rag_system(
    mock_session_manager: Mock,
    mock_vector_store: Mock,
    mock_ai_generator: Mock,
    mock_tool_manager: Mock
) -> Mock:
    """Mock RAGSystem with all components mocked."""
    rag_system = Mock()
    rag_system.session_manager = mock_session_manager
    rag_system.query = AsyncMock(return_value=(
        "Backpropagation is an algorithm...",
        ["Deep Learning - Lesson 3"]
    ))
    rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 2,
        "course_titles": ["Deep Learning Specialization", "NLP with Deep Learning"]
    })
    return rag_system


# =============================================================================
# Test App Fixtures
# =============================================================================

@pytest.fixture
def test_app(monkeypatch: Any, mock_rag_system: Mock):
    """
    Create a test FastAPI app without static file mounting.

    This fixture creates a minimal FastAPI app with only the API endpoints
    needed for testing, avoiding the static file mount that causes issues
    in test environments.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    # Import models
    class QueryRequest(BaseModel):
        query: str
        session_id: Optional[str] = None

    class QueryResponse(BaseModel):
        answer: str
        sources: List[str]
        session_id: str

    class CourseStats(BaseModel):
        total_courses: int
        course_titles: List[str]

    # Create minimal test app
    app = FastAPI(title="Test RAG System")

    # Setup CORS
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mock RAG system at module level (not actually used since we use mock_rag_system directly in endpoints)
    # The mock is passed via closure to the endpoint functions

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        """Process a query and return response with sources."""
        try:
            # Create session if not provided
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()

            # Get conversation history if session exists (simulates RAG system behavior)
            if session_id:
                mock_rag_system.session_manager.get_conversation_history(session_id)

            # Process query using mocked RAG system
            answer, sources = await mock_rag_system.query(request.query, session_id)

            # Add exchange to conversation history (simulates RAG system behavior)
            if session_id:
                mock_rag_system.session_manager.add_exchange(session_id, request.query, answer)

            return QueryResponse(
                answer=answer,
                sources=sources,
                session_id=session_id
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        """Get course analytics and statistics."""
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


@pytest.fixture
async def async_client(test_app) -> AsyncClient:
    """
    Async HTTP client for testing FastAPI endpoints.

    Uses ASGITransport to call the FastAPI app directly without
    running a server.
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# =============================================================================
# Helper Fixtures
# =============================================================================

@pytest.fixture
def temp_chroma_path(tmp_path: Path) -> str:
    """Temporary path for ChromaDB testing."""
    chroma_path = tmp_path / "test_chroma_db"
    chroma_path.mkdir(exist_ok=True)
    return str(chroma_path)


@pytest.fixture
def mock_env_vars(monkeypatch: Any) -> dict:
    """Mock environment variables for testing."""
    env_vars = {
        "ANTHROPIC_API_KEY": "test-api-key-12345"
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars
