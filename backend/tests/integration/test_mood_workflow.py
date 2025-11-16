"""Integration tests for complete mood workflow."""
import pytest
from fastapi import status


def test_complete_mood_workflow(client):
    """Test the complete workflow: create mood -> generate dataset -> train model -> analyze."""

    # 1. Create a mood
    mood_data = {
        "name": "Market Optimism",
        "description": "Positive outlook on market conditions",
        "attribute_definition": "Text expressing confidence in market growth",
    }
    mood_response = client.post("/api/v1/moods/", json=mood_data)
    assert mood_response.status_code == status.HTTP_201_CREATED
    mood_id = mood_response.json()["id"]

    # 2. Generate a dataset (this will use background tasks in production)
    dataset_data = {
        "num_examples": 10,
        "openai_model": "gpt-4",
    }
    dataset_response = client.post(
        f"/api/v1/datasets/{mood_id}/generate",
        json=dataset_data,
    )
    assert dataset_response.status_code == status.HTTP_202_ACCEPTED
    dataset_id = dataset_response.json()["id"]

    # 3. Check datasets for the mood
    datasets_response = client.get(f"/api/v1/datasets/mood/{mood_id}")
    assert datasets_response.status_code == status.HTTP_200_OK
    datasets = datasets_response.json()
    assert len(datasets) >= 1

    # 4. Get dataset details
    dataset_detail = client.get(f"/api/v1/datasets/{dataset_id}")
    assert dataset_detail.status_code == status.HTTP_200_OK

    # Note: In real tests with actual background tasks, you would:
    # - Wait for dataset generation to complete
    # - Train models using the dataset
    # - Select a model
    # - Perform analysis
    #
    # For unit tests with mock data, we're just testing the API endpoints work
