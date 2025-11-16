"""OpenAI API client wrapper."""
from openai import OpenAI
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for OpenAI API interactions."""

    def __init__(self):
        """Initialize OpenAI client."""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.openai_api_key)

    def is_available(self) -> bool:
        """Check if OpenAI client is available."""
        return self.client is not None

    def generate_training_examples(
        self, attribute_definition: str, num_examples: int = 20, model: str = "gpt-4"
    ) -> list[dict]:
        """
        Generate training examples for a semantic attribute.

        Args:
            attribute_definition: Definition of the semantic attribute
            num_examples: Number of examples to generate
            model: OpenAI model to use

        Returns:
            List of dictionaries with 'text' and 'score' keys
        """
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")

        prompt = f"""Generate {num_examples} financial text examples that vary in how much they express this attribute:

Attribute: {attribute_definition}

For each example, provide:
1. A text snippet (1-3 sentences)
2. A score from 0 to 5, where:
   - 0 = completely lacks the attribute
   - 5 = maximally expresses the attribute

Format your response as a JSON array with objects containing 'text' and 'score' fields.
Example: [{{"text": "...", "score": 3.5}}, ...]
"""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in financial sentiment analysis. Generate diverse training examples.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                response_format={"type": "json_object"},
            )

            import json

            result = json.loads(response.choices[0].message.content)

            # Handle different response formats
            if isinstance(result, dict) and "examples" in result:
                examples = result["examples"]
            elif isinstance(result, list):
                examples = result
            else:
                examples = [result]

            logger.info(f"Generated {len(examples)} training examples")
            return examples

        except Exception as e:
            logger.error(f"Error generating training examples: {str(e)}")
            raise

    def analyze_financial_headlines(self) -> list[dict]:
        """
        Analyze current financial headlines with sentiment scores.

        Returns:
            List of dictionaries with 'headline', 'sentiment_score', and 'source' keys
        """
        if not self.is_available():
            raise ValueError("OpenAI API key not configured")

        prompt = """Provide 5 recent financial headlines (or realistic examples) with sentiment scores from -10 to +10.

Format as JSON array: [{{"headline": "...", "sentiment_score": 5.5, "source": "Reuters"}}, ...]
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial news analyst. Provide realistic financial headlines with sentiment analysis.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            import json

            result = json.loads(response.choices[0].message.content)

            # Handle different response formats
            if isinstance(result, dict) and "headlines" in result:
                headlines = result["headlines"]
            elif isinstance(result, list):
                headlines = result
            else:
                headlines = [result]

            logger.info(f"Retrieved {len(headlines)} financial headlines")
            return headlines

        except Exception as e:
            logger.error(f"Error analyzing headlines: {str(e)}")
            raise


# Singleton instance
openai_client = OpenAIClient()
