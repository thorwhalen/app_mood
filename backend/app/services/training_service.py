"""Service for training ML models."""
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import MLModel, Dataset, DatasetExample
from ..models.model import ModelType
from ..config import settings
import logging
import os
import pickle

logger = logging.getLogger(__name__)


def train_models_task(mood_id: str, dataset_id: str):
    """
    Background task to train multiple model types for a mood.

    Args:
        mood_id: ID of the mood
        dataset_id: ID of the training dataset
    """
    db = SessionLocal()
    try:
        # Get dataset and examples
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found")
            return

        examples = db.query(DatasetExample).filter(
            DatasetExample.dataset_id == dataset_id
        ).all()

        if not examples:
            logger.error(f"No examples found for dataset {dataset_id}")
            return

        logger.info(f"Training models for mood {mood_id} with {len(examples)} examples")

        # Prepare training data
        texts = [ex.text for ex in examples]
        scores = [ex.score for ex in examples]

        # TODO: Integrate with mood library for actual training
        # For now, create mock models
        model_types = [
            ModelType.NUMERICAL_REGRESSION,
            ModelType.BINARY_CLASSIFICATION,
            ModelType.ORDINAL_REGRESSION,
        ]

        storage_path = settings.storage_path
        os.makedirs(storage_path, exist_ok=True)

        for model_type in model_types:
            # Mock model creation
            model_data = {
                "type": model_type.value,
                "trained_on": len(examples),
                "mock": True,
            }

            # Save mock model
            model_filename = f"{mood_id}_{model_type.value}.pkl"
            model_path = os.path.join(storage_path, model_filename)

            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)

            # Create model record
            import random
            metrics = {
                "spearman": random.uniform(0.7, 0.95),
                "mae": random.uniform(0.1, 0.5),
            }

            ml_model = MLModel(
                mood_id=mood_id,
                model_type=model_type,
                metrics=metrics,
                file_path=model_path,
                is_selected=(model_type == ModelType.NUMERICAL_REGRESSION),  # Select first by default
            )
            db.add(ml_model)

        db.commit()
        logger.info(f"Models trained successfully for mood {mood_id}")

    except Exception as e:
        logger.error(f"Error training models for mood {mood_id}: {str(e)}")
    finally:
        db.close()
