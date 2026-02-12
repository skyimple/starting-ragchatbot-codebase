"""
Tests for the /api/courses endpoint.

These tests cover:
- Successful course listing
- Empty course catalog
- Error handling
- Response structure validation
"""

import pytest
from httpx import AsyncClient
from unittest.mock import Mock


@pytest.mark.api
async def test_courses_success(async_client: AsyncClient, mock_rag_system: Mock):
    """Test successful retrieval of course statistics."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 3,
        "course_titles": [
            "Deep Learning Specialization",
            "NLP with Deep Learning",
            "Computer Vision Fundamentals"
        ]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert "total_courses" in data
    assert "course_titles" in data
    assert data["total_courses"] == 3
    assert len(data["course_titles"]) == 3
    assert "Deep Learning Specialization" in data["course_titles"]


@pytest.mark.api
async def test_courses_empty_catalog(async_client: AsyncClient, mock_rag_system: Mock):
    """Test response when no courses are available."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 0,
        "course_titles": []
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert data["total_courses"] == 0
    assert data["course_titles"] == []


@pytest.mark.api
async def test_courses_single_course(async_client: AsyncClient, mock_rag_system: Mock):
    """Test response when only one course is available."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 1,
        "course_titles": ["Introduction to Machine Learning"]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert data["total_courses"] == 1
    assert len(data["course_titles"]) == 1


@pytest.mark.api
async def test_courses_response_structure(async_client: AsyncClient, mock_rag_system: Mock):
    """Test that courses endpoint returns correct JSON structure."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 2,
        "course_titles": ["Course A", "Course B"]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()

    # Verify top-level keys
    assert set(data.keys()) == {"total_courses", "course_titles"}

    # Verify types
    assert isinstance(data["total_courses"], int)
    assert isinstance(data["course_titles"], list)

    # Verify all titles are strings
    assert all(isinstance(title, str) for title in data["course_titles"])


@pytest.mark.api
async def test_courses_rag_system_error_handling(
    async_client: AsyncClient,
    mock_rag_system: Mock
):
    """Test that RAG system exceptions are properly caught and returned as 500."""
    mock_rag_system.get_course_analytics = Mock(
        side_effect=Exception("Vector store unavailable")
    )

    response = await async_client.get("/api/courses")

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Vector store unavailable" in data["detail"]


@pytest.mark.api
async def test_courses_accepts_only_get(async_client: AsyncClient):
    """Test that courses endpoint rejects POST requests."""
    response = await async_client.post("/api/courses", json={})

    assert response.status_code == 405  # Method Not Allowed


@pytest.mark.api
async def test_courses_no_query_params(async_client: AsyncClient, mock_rag_system: Mock):
    """Test that courses endpoint works without query parameters."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 5,
        "course_titles": [f"Course {i}" for i in range(5)]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    mock_rag_system.get_course_analytics.assert_called_once()


@pytest.mark.api
async def test_courses_with_query_params_ignored(
    async_client: AsyncClient,
    mock_rag_system: Mock
):
    """Test that query parameters are ignored (endpoint doesn't use them)."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 2,
        "course_titles": ["Course A", "Course B"]
    })

    response = await async_client.get("/api/courses?limit=10&offset=5")

    assert response.status_code == 200
    mock_rag_system.get_course_analytics.assert_called_once()


@pytest.mark.api
async def test_courses_response_json_content_type(async_client: AsyncClient, mock_rag_system: Mock):
    """Test that courses endpoint returns JSON content type."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 1,
        "course_titles": ["Test Course"]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")


@pytest.mark.api
async def test_courses_call_analytics_method(async_client: AsyncClient, mock_rag_system: Mock):
    """Test that endpoint calls get_course_analytics method."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 0,
        "course_titles": []
    })

    await async_client.get("/api/courses")

    mock_rag_system.get_course_analytics.assert_called_once()


@pytest.mark.api
async def test_courses_unicode_in_titles(async_client: AsyncClient, mock_rag_system: Mock):
    """Test handling of unicode characters in course titles."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 2,
        "course_titles": [
            "Deep Learning: 深度学习",
            "Méthodes de Apprentissage"
        ]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert "深度学习" in data["course_titles"][0]
    assert "Apprentissage" in data["course_titles"][1]


@pytest.mark.api
async def test_courses_large_catalog(async_client: AsyncClient, mock_rag_system: Mock):
    """Test handling of large course catalog."""
    large_catalog = [f"Course {i}: Advanced Topics" for i in range(100)]
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 100,
        "course_titles": large_catalog
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert data["total_courses"] == 100
    assert len(data["course_titles"]) == 100


@pytest.mark.api
async def test_courses_special_characters_in_titles(async_client: AsyncClient, mock_rag_system: Mock):
    """Test handling of special characters in course titles."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 2,
        "course_titles": [
            "C++ Programming & Algorithms",
            "AI/ML: <Advanced> Techniques"
        ]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert "C++" in data["course_titles"][0]
    assert "<Advanced>" in data["course_titles"][1]


@pytest.mark.api
async def test_courses_duplicate_titles(async_client: AsyncClient, mock_rag_system: Mock):
    """Test response when duplicate course titles exist."""
    mock_rag_system.get_course_analytics = Mock(return_value={
        "total_courses": 3,
        "course_titles": [
            "Introduction to Python",
            "Introduction to Python",
            "Advanced Python"
        ]
    })

    response = await async_client.get("/api/courses")

    assert response.status_code == 200
    data = response.json()
    assert data["total_courses"] == 3
    # Duplicates are preserved as returned by the system
    assert data["course_titles"].count("Introduction to Python") == 2
