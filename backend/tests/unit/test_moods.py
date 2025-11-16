"""Unit tests for mood endpoints."""
import pytest
from fastapi import status


def test_create_mood(client):
    """Test creating a mood."""
    mood_data = {
        "name": "Bullish Sentiment",
        "description": "Optimistic market outlook",
        "attribute_definition": "Text expressing positive expectations about market performance",
    }

    response = client.post("/api/v1/moods/", json=mood_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == mood_data["name"]
    assert data["description"] == mood_data["description"]
    assert "id" in data
    assert "created_at" in data


def test_list_moods(client):
    """Test listing moods."""
    # Create a mood first
    mood_data = {
        "name": "Test Mood",
        "description": "Test description",
        "attribute_definition": "Test attribute",
    }
    client.post("/api/v1/moods/", json=mood_data)

    # List moods
    response = client.get("/api/v1/moods/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == mood_data["name"]


def test_get_mood(client):
    """Test getting a specific mood."""
    # Create a mood
    mood_data = {
        "name": "Test Mood",
        "description": "Test description",
        "attribute_definition": "Test attribute",
    }
    create_response = client.post("/api/v1/moods/", json=mood_data)
    mood_id = create_response.json()["id"]

    # Get the mood
    response = client.get(f"/api/v1/moods/{mood_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == mood_id
    assert data["name"] == mood_data["name"]


def test_update_mood(client):
    """Test updating a mood."""
    # Create a mood
    mood_data = {
        "name": "Original Name",
        "description": "Original description",
        "attribute_definition": "Original attribute",
    }
    create_response = client.post("/api/v1/moods/", json=mood_data)
    mood_id = create_response.json()["id"]

    # Update the mood
    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/v1/moods/{mood_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == mood_data["description"]  # Unchanged


def test_delete_mood(client):
    """Test deleting a mood."""
    # Create a mood
    mood_data = {
        "name": "Test Mood",
        "description": "Test description",
        "attribute_definition": "Test attribute",
    }
    create_response = client.post("/api/v1/moods/", json=mood_data)
    mood_id = create_response.json()["id"]

    # Delete the mood
    response = client.delete(f"/api/v1/moods/{mood_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(f"/api/v1/moods/{mood_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
