import os
import dspy
import logging
from typing import Literal
from typing import Dict, Optional
from src.global_settings import BASE_LLM, OPENAI_API_BASE

from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")


class Sentiment(dspy.Signature):
    """YouTube video transcript sentiment."""

    text: str = dspy.InputField()
    prediction: Literal["Positive", "Negative", "Neutral"] = dspy.OutputField()
    confidence: float = dspy.OutputField()


class VideoRelevance(dspy.Signature):
    """Classify whether the YouTube transcript text is related to the topic."""

    topic: str = dspy.InputField()
    text: str = dspy.InputField()
    prediction: Literal["Related", "Not Related"] = dspy.OutputField()
    confidence: float = dspy.OutputField()


class Classify:
    """
    A class to handle different types of text classification using DSPy.

    This class provides functionality to classify text using different models
    like sentiment analysis and video relevance checking.
    """

    def __init__(self) -> None:
        """Initialize the classifier with language model configuration."""
        self.lm = dspy.LM(
            model=f"openai/{BASE_LLM}",
            api_key=os.environ.get("GROQ_API_KEY"),
            api_base=OPENAI_API_BASE,
            temperature=0,
        )
        dspy.configure(lm=self.lm)

        self.mode = {
            "sentiments": Sentiment,
            "video_relevance": VideoRelevance,
        }

    def classifier(
        self,
        text: str,
        type: str,
        topic: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Classify text based on specified type and optional topic.

        Args:
            text: The text to classify.
            type: Classification type ["sentiments", "video_relevance"].
            topic: The topic for classification. Required when type
            is "video_relevance".

        Returns:
            A dictionary containing:
                - reasoning: The reasoning behind the classification
                - prediction: The classification result
                - confidence: The confidence score of the classification

        Raises:
            KeyError: If an invalid classification type is provided.
            ValueError: If topic is not provided for relevance classification.
        """
        if type not in self.mode:
            modes = list(self.mode.keys())
            raise KeyError(
                f"Invalid classification type. Must be one of {modes}")

        if type == "video_relevance" and topic is None:
            message = "Topic is required for video_relevance classification"
            raise ValueError(message)

        classify = dspy.ChainOfThought(self.mode[type])

        try:
            if type == "video_relevance":
                result = classify(topic=topic, text=text)
            else:
                result = classify(text=text)

            return {
                "reasoning": result.reasoning,
                "prediction": result.prediction,
                "confidence": result.confidence,
            }

        except Exception as e:
            logging.error(f"Classification failed: {str(e)}", exc_info=True)
            return {
                "reasoning": "Not available",
                "prediction": "Not available",
                "confidence": "Not available",
            }
