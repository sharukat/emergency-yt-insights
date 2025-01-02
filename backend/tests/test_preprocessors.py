from src.utils import fix_punctuations


def test_punctuations():
    texts = [
        "Hello world how are you today?",
        "This is a test sentence without punctuation",
    ]

    expected_texts = [
        "Hello, world! How are you today?",
        "This is a test sentence without punctuation.",
    ]

    for text, expected in zip(texts, expected_texts):
        result = fix_punctuations(text)
        print(f"Expected: {expected}\nResult: {result}\n")
        assert result == expected, f"Expected {expected}, but got {result}"

    texts = [
        "This is Wrong!",
        "Multiple     spaces   and   dots.",
    ]

    expected_texts = [
        "This is wrong!",
        "Multiple spaces and dots."
    ]

    for text, expected in zip(texts, expected_texts):
        result = fix_punctuations(text)
        print(f"Expected: {expected}\nResult: {result}\n")
        assert result == expected, f"Expected {expected}, but got {result}"
