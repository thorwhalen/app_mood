"""Service for training ML models."""
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import MLModel, Dataset, DatasetExample
from ..models.model import ModelType
from ..config import settings
import logging
import os
import pickle
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def train_models_task(mood_id: str, dataset_id: str):
    """
    Background task to train multiple model types for a mood using mood library.

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

        if len(examples) < 5:
            raise ValueError(f"Need at least 5 examples to train models, got {len(examples)}")

        logger.info(f"Training models for mood {mood_id} with {len(examples)} examples")

        # Prepare training data
        texts = [ex.text for ex in examples]
        scores = [ex.score for ex in examples]

        # Compute embeddings using OpenAI
        try:
            from openai import OpenAI
            from ..config import settings

            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")

            client = OpenAI(api_key=settings.openai_api_key)

            logger.info("Computing embeddings for training texts...")
            embeddings = []
            batch_size = 100

            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = client.embeddings.create(
                    input=batch,
                    model="text-embedding-ada-002"
                )
                embeddings.extend([item.embedding for item in response.data])

            logger.info(f"Computed {len(embeddings)} embeddings")

        except Exception as e:
            logger.error(f"Error computing embeddings: {str(e)}")
            raise

        # Create DataFrame for training
        training_data = pd.DataFrame({
            'score': scores,
            'segment': texts,
            'embedding': embeddings
        })

        # Use mood library's MoodModelingManager
        try:
            from mood.mood_modeling import MoodModelingManager

            logger.info("Initializing MoodModelingManager...")
            manager = MoodModelingManager(
                df=training_data,
                embedding_col='embedding',
                score_col='score',
                verbose=1
            )

            # Train and evaluate models
            logger.info("Training models...")
            results = manager.train_and_evaluate()

            # Fit final models on all data
            logger.info("Fitting final models...")
            manager.fit_final_models()

            # Get model summary
            summary = manager.get_model_summary(use_cv=False)

            logger.info(f"Model training completed. Summary: {summary}")

        except Exception as e:
            logger.error(f"Error with mood library training: {str(e)}")
            raise

        # Save the trained manager and create model records
        storage_path = settings.storage_path
        os.makedirs(storage_path, exist_ok=True)

        # Save the entire manager object
        manager_filename = f"{mood_id}_manager.pkl"
        manager_path = os.path.join(storage_path, manager_filename)

        with open(manager_path, "wb") as f:
            pickle.dump(manager, f)

        logger.info(f"Saved manager to {manager_path}")

        # Create model records for each type in the summary
        model_type_mapping = {
            'regression': ModelType.NUMERICAL_REGRESSION,
            'classification': ModelType.BINARY_CLASSIFICATION,
            'ordinal': ModelType.ORDINAL_REGRESSION,
        }

        best_spearman = -1
        best_model_id = None

        for model_name, model_metrics in summary.items():
            # Determine model type from name
            model_type = ModelType.NUMERICAL_REGRESSION  # Default
            for key, mtype in model_type_mapping.items():
                if key in model_name.lower():
                    model_type = mtype
                    break

            # Extract metrics
            metrics = {
                "model_name": model_name,
            }

            # Add available metrics
            if isinstance(model_metrics, dict):
                for metric_name in ['spearman', 'mae', 'rmse', 'r2', 'f1', 'accuracy']:
                    if metric_name in model_metrics:
                        metrics[metric_name] = float(model_metrics[metric_name])
            elif isinstance(model_metrics, (int, float)):
                metrics["score"] = float(model_metrics)

            spearman_score = metrics.get('spearman', metrics.get('score', 0))

            ml_model = MLModel(
                mood_id=mood_id,
                model_type=model_type,
                metrics=metrics,
                file_path=manager_path,  # All models share the same manager file
                is_selected=False,
            )
            db.add(ml_model)
            db.flush()  # Get the ID

            # Track best model by Spearman correlation
            if spearman_score > best_spearman:
                best_spearman = spearman_score
                best_model_id = ml_model.id

        # Select the best model
        if best_model_id:
            db.query(MLModel).filter(MLModel.id == best_model_id).update({"is_selected": True})

        db.commit()
        logger.info(f"Models trained successfully for mood {mood_id}. Best Spearman: {best_spearman:.3f}")

    except Exception as e:
        logger.error(f"Error training models for mood {mood_id}: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
