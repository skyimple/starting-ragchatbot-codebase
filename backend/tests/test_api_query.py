"""
Tests for the /api/query endpoint.

These tests cover:
- Successful query responses
- Session creation for new queries
- Session reuse for existing sessions
- Error handling
- Request validation
"""

import pytest
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock


@pytest.mark.api
async def test_query_success(async_client: AsyncClient, mock_rag_system: Mock):
    """Test successful query returns expected response structure."""
    mock_rag_system.query = AsyncMock(return_value=(
        "Backpropagation is an algorithm for training neural networks by computing gradients...",
        ["Deep Learning Specialization - Lesson 3"]
    ))

    response = await async_client.post(
        "/api/query",
        json={"query": "What is backpropagation?"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "session_id" in data
    assert isinstance(data["sources"], list)
    assert data["answer"] == "Backpropagation is an algorithm for training neural networks by computing gradients..."


@pytest.mark.api
async def test_query_creates_session_when_not_provided(
    async_client: AsyncClient,
    mock_rag_system: Mock,
    mock_session_manager: Mock
):
    """Test that a new session is created when session_id is not provided."""
    mock_session_manager.create_session = Mock(return_value="new_session_456")
    mock_rag_system.query = AsyncMock(return_value=(
        "Response text",
        []
    ))

    response = await async_client.post(
        "/api/query",
        json={"query": "Test question"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "new_session_456"
    mock_session_manager.create_session.assert_called_once()


@pytest.mark.api
async def test_query_reuses_existing_session(
    async_client: AsyncClient,
    mock_rag_system: Mock,
    mock_session_manager: Mock
):
    """Test that an existing session_id is reused when provided."""
    mock_rag_system.query = AsyncMock(return_value=(
        "Response text",
        ["Source 1"]
    ))

    response = await async_client.post(
        "/api/query",
        json={
            "query": "Test question",
            "session_id": "existing_session_123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "existing_session_123"
    mock_session_manager.create_session.assert_not_called()


@pytest.mark.api
async def test_query_includes_sources(async_client: AsyncClient, mock_rag_system: Mock):
    """Test that query response includes source information."""
    expected_sources = [
        "Deep Learning Specialization - Lesson 3: Neural Networks",
        "Deep Learning Specialization - Lesson 4: Optimization"
    ]
    mock_rag_system.query = AsyncMock(return_value=(
        "Gradient descent is an optimization algorithm...",
        expected_sources
    ))

    response = await async_client.post(
        "/api/query",
        json={"query": "Explain gradient descent"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == expected_sources


@pytest.mark.api
async def test_query_passes_session_to_rag_system(
    async_client: AsyncClient,
    mock_rag_system: Mock
):
    """Test that session_id is properly passed to RAG system query method."""
    mock_rag_system.query = AsyncMock(return_value=(
        "Response",
        []
    ))

    await async_client.post(
        "/api/query",
        json={
            "query": "Test question",
            "session_id": "test_session_abc"
        }
    )

    mock_rag_system.query.assert_called_once_with("Test question", "test_session_abc")


@pytest.mark.api
async def test_query_missing_query_field(async_client: AsyncClient):
    """Test that request without query field returns validation error."""
    response = await async_client.post(
        "/api/query",
        json={"session_id": "test_123"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.api
async def test_query_empty_query_string(async_client: AsyncClient):
    """Test that empty query string is handled (validation)."""
    response = await async_client.post(
        "/api/query",
        json={"query": ""}
    )

    # Empty string may pass validation but should be handled by the app
    # Accepting 200 or 422 depending on implementation
    assert response.status_code in (200, 422)


@pytest.mark.api
async def test_query_rag_system_error_handling(
    async_client: AsyncClient,
    mock_rag_system: Mock
):
    """Test that RAG system exceptions are properly caught and returned as 500."""
    mock_rag_system.query = AsyncMock(side_effect=Exception("Database connection failed"))

    response = await async_client.post(
        "/api/query",
        json={"query": "Test question"}
    )

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Database connection failed" in data["detail"]


@pytest.mark.api
async def test_query_with_session_id_none(
    async_client: AsyncClient,
    mock_rag_system: Mock,
    mock_session_manager: Mock
):
    """Test that explicit null session_id creates new session."""
    mock_session_manager.create_session = Mock(return_value="created_session_789")
    mock_rag_system.query = AsyncMock(return_value=(
        "Response",
        []
    ))

    response = await async_client.post(
        "/api/query",
        json={
            "query": "Test",
            "session_id": None
        }
    )

    assert response.status_code == 200
    mock_session_manager.create_session.assert_called_once()


@pytest.mark.api
async def test_query_conversation_history_maintained(
    async_client: AsyncClient,
    mock_rag_system: Mock,
    mock_session_manager: Mock
):
    """Test that conversation history is maintained within a session."""
    session_id = "conversation_session"
    mock_session_manager.get_conversation_history = Mock(return_value=(
        "User: First question\nAssistant: First answer"
    ))
    mock_rag_system.query = AsyncMock(return_value=(
        "Second answer with context",
        ["Source"]
    ))

    response = await async_client.post(
        "/api/query",
        json={
            "query": "Follow up question",
            "session_id": session_id
        }
    )

    assert response.status_code == 200
    mock_session_manager.get_conversation_history.assert_called_once_with(session_id)
    mock_session_manager.add_exchange.assert_called_once()


@pytest.mark.api
async def test_query_without_conversation_history(
    async_client: AsyncClient,
    mock_rag_system: Mock,
    mock_session_manager: Mock
):
    """Test query when session has no prior history."""
    mock_session_manager.get_conversation_history = Mock(return_value=None)
    mock_rag_system.query = AsyncMock(return_value=(
        "Answer without context",
        []
    ))

    response = await async_client.post(
        "/api/query",
        json={
            "query": "First question",
            "session_id": "new_session"
        }
    )

    assert response.status_code == 200
    mock_session_manager.get_conversation_history.assert_called_once()


@pytest.mark.api
async def test_query_accepts_only_post(async_client: AsyncClient):
    """Test that query endpoint rejects GET requests."""
    response = await async_client.get("/api/query")

    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.api
async def test_query_response_json_content_type(async_client: AsyncClient, mock_rag_system: Mock):
    """Test that query endpoint returns JSON content type."""
    mock_rag_system.query = AsyncMock(return_value=("Answer", []))

    response = await async_client.post(
        "/api/query",
        json={"query": "Test"}
    )

    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.api
async def test_query_special_characters_in_input(async_client: AsyncClient, mock_rag_system: Mock):
    """Test handling of special characters in query text."""
    special_query = "What about <script>alert('xss')</script> and &amp; entities?"
    mock_rag_system.query = AsyncMock(return_value=(
        "Safe response",
        []
    ))

    response = await async_client.post(
        "/api/query",
        json={"query": special_query}
    )

    assert response.status_code == 200
    mock_rag_system.query.assert_called_once()
