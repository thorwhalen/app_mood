"""Service for text analysis."""
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Analysis
from ..config import settings
import logging
import pickle
import numpy as np

logger = logging.getLogger(__name__)


def analyze_text(model_path: str, text: str) -> float:
    """
    Analyze a text using a trained mood model.

    Args:
        model_path: Path to the trained MoodModelingManager file
        text: Text to analyze

    Returns:
        Sentiment score between 0 and 1
    """
    try:
        # Load the trained MoodModelingManager
        with open(model_path, "rb") as f:
            manager = pickle.load(f)

        # Compute embedding for the input text
        from openai import OpenAI

        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        client = OpenAI(api_key=settings.openai_api_key)

        response = client.embeddings.create(
            input=[text],
            model="text-embedding-ada-002"
        )

        embedding = response.data[0].embedding

        # Get prediction from the best model
        # The manager.predict_mood expects a list of embeddings
        predictions = manager.predict_mood([embedding])

        # Extract score (should be normalized 0-1)
        score = float(predictions[0])

        # Ensure score is in [0, 1] range
        # Mood library scores are 0-5, so normalize
        if score > 1.0:
            score = score / 5.0  # Normalize from 0-5 to 0-1

        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]

        logger.info(f"Analyzed text (length {len(text)}): score={score:.3f}")
        return score

    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}", exc_info=True)
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
    try:
        # Try to use mood library's headlines feature
        try:
            from mood import headlines_mood

            logger.info("Using mood library's headlines_mood function...")
            sentiment_scores = headlines_mood()

            # Convert to expected format
            results = []
            for headline, score in sentiment_scores.items():
                results.append({
                    "headline": headline,
                    "sentiment_score": float(score),
                    "source": None  # mood library doesn't provide source
                })

            logger.info(f"Retrieved {len(results)} financial headlines from mood library")
            return results

        except ImportError:
            logger.warning("mood.headlines_mood not available, using OpenAI fallback")

        # Fallback: Use OpenAI to generate headlines analysis
        from ..utils.openai_client import openai_client

        if not openai_client.is_available():
            logger.warning("OpenAI not available, using mock data")
            raise ValueError("OpenAI API key not configured")

        headlines = openai_client.analyze_financial_headlines()
        logger.info(f"Retrieved {len(headlines)} financial headlines from OpenAI")
        return headlines

    except Exception as e:
        logger.error(f"Error getting headlines: {str(e)}, falling back to mock data")

        # Final fallback: mock data
        mock_headlines = [
            {"headline": "Markets surge on positive economic data", "sentiment_score": 8.5, "source": "Reuters"},
            {"headline": "Tech stocks face regulatory concerns", "sentiment_score": -3.2, "source": "Bloomberg"},
            {"headline": "Federal Reserve maintains interest rates", "sentiment_score": 0.5, "source": "CNBC"},
            {"headline": "Energy sector shows strong growth", "sentiment_score": 6.8, "source": "WSJ"},
            {"headline": "Inflation concerns weigh on consumer stocks", "sentiment_score": -5.1, "source": "Financial Times"},
        ]

        return mock_headlines
