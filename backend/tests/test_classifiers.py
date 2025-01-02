import pytest
from src.classifiers import Classify


@pytest.fixture
def classifier():
    """Fixture to initialize the classifier models."""
    return Classify()


def test_sentiment_classification(classifier):
    """Test sentiment classification with a positive text."""

    text = "I am excited to start my new job"
    classification_type = "sentiments"

    result = classifier.classifier(text=text, type=classification_type)
    print(result)

    assert isinstance(result, dict)
    assert all(key in result for key in [
        "reasoning", "prediction", "confidence"])
    assert result["prediction"] != "Not available"
    assert result["reasoning"] != "Not available"
    assert result["confidence"] != "Not available"


def test_invalid_classification_type(classifier):
    """Test classifier with invalid classification type."""
    with pytest.raises(KeyError) as exc_info:
        classifier.classifier(text="Some text", type="invalid_type")
    assert "Invalid classification type" in str(exc_info.value)


def test_video_relevance_without_topic(classifier):
    """Test video relevance classification without required topic."""
    with pytest.raises(ValueError) as exc_info:
        classifier.classifier(
            text="Video content about programming",
            type="video_relevance"
        )
    assert "Topic is required" in str(exc_info.value)


def test_video_relevance_classification(classifier):
    """Test video relevance classification with valid inputs."""

    text = "This video explains Python programming basics"
    classification_type = "video_relevance"
    topic = "Python programming"

    result = classifier.classifier(
        text=text,
        type=classification_type,
        topic=topic
    )
    print(result)

    assert isinstance(result, dict)
    assert all(key in result for key in [
        "reasoning", "prediction", "confidence"])
    assert result["prediction"] != "Not available"
    assert result["reasoning"] != "Not available"
    assert result["confidence"] != "Not available"
