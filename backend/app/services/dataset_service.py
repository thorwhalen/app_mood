"""Service for generating training datasets."""
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Dataset, DatasetExample
from ..config import settings
from ..utils.openai_client import openai_client
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


def generate_dataset_task(dataset_id: str, attribute_definition: str):
    """
    Background task to generate a training dataset using mood library.

    Args:
        dataset_id: ID of the dataset to generate
        attribute_definition: Semantic attribute definition
    """
    db = SessionLocal()
    dataset = None

    try:
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found")
            return

        dataset.status = "generating"
        db.commit()

        logger.info(f"Generating {dataset.num_examples} examples for dataset {dataset_id}")

        # Use OpenAI to generate training examples
        if not openai_client.is_available():
            raise ValueError("OpenAI API key not configured. Cannot generate dataset.")

        # Generate examples using OpenAI
        examples = openai_client.generate_training_examples(
            attribute_definition=attribute_definition,
            num_examples=dataset.num_examples,
            model=dataset.openai_model_used or "gpt-4"
        )

        # Store examples in database
        for example_data in examples:
            example = DatasetExample(
                dataset_id=dataset_id,
                text=example_data["text"],
                score=float(example_data["score"]),
            )
            db.add(example)

        dataset.status = "completed"
        db.commit()
        logger.info(f"Dataset {dataset_id} generation completed with {len(examples)} examples")

    except Exception as e:
        logger.error(f"Error generating dataset {dataset_id}: {str(e)}", exc_info=True)
        if dataset:
            dataset.status = "failed"
            dataset.error_message = str(e)
            db.commit()
    finally:
        db.close()
