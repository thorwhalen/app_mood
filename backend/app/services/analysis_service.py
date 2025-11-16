"""Service for text analysis."""
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Analysis
from ..config import settings
import logging
import pickle
import random

logger = logging.getLogger(__name__)


def analyze_text(model_path: str, text: str) -> float:
    """
    Analyze a text using a trained model.

    Args:
        model_path: Path to the model file
        text: Text to analyze

    Returns:
        Sentiment score between 0 and 1
    """
    try:
        # TODO: Load actual model and perform analysis
        # For now, return mock score
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        # Mock analysis - replace with actual mood library integration
        score = random.uniform(0, 1)
        logger.info(f"Analyzed text (length {len(text)}): score={score:.3f}")
        return score

    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise


def analyze_batch_task(mood_id: str, model_id: str, texts: list[str]):
    """
    Background task to analyze multiple texts.

    Args:
        mood_id: ID of the mood
        model_id: ID of the model to use
        texts: List of texts to analyze
    """
    db = SessionLocal()
    try:
        from ..models import MLModel

        model = db.query(MLModel).filter(MLModel.id == model_id).first()
        if not model:
            logger.error(f"Model {model_id} not found")
            return

        logger.info(f"Batch analyzing {len(texts)} texts with model {model_id}")

        for text in texts:
            try:
                score = analyze_text(model.file_path, text)

                analysis = Analysis(
                    mood_id=mood_id,
                    model_id=model_id,
                    input_text=text,
                    score=score,
                )
                db.add(analysis)
            except Exception as e:
                logger.error(f"Error analyzing text in batch: {str(e)}")

        db.commit()
        logger.info(f"Batch analysis completed for {len(texts)} texts")

    except Exception as e:
        logger.error(f"Error in batch analysis task: {str(e)}")
    finally:
        db.close()


def get_financial_headlines():
    """
    Get and analyze current financial headlines using mood's quick-start feature.

    Returns:
        List of headline analysis results
    """
    # TODO: Integrate with mood library's headline analysis feature
    # For now, return mock data
    mock_headlines = [
        {"headline": "Markets surge on positive economic data", "sentiment_score": 8.5, "source": "Reuters"},
        {"headline": "Tech stocks face regulatory concerns", "sentiment_score": -3.2, "source": "Bloomberg"},
        {"headline": "Federal Reserve maintains interest rates", "sentiment_score": 0.5, "source": "CNBC"},
        {"headline": "Energy sector shows strong growth", "sentiment_score": 6.8, "source": "WSJ"},
        {"headline": "Inflation concerns weigh on consumer stocks", "sentiment_score": -5.1, "source": "Financial Times"},
    ]

    logger.info(f"Retrieved {len(mock_headlines)} financial headlines")
    return mock_headlines
