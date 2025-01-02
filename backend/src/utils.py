
import os
import dspy
import logging
from src.global_settings import SMALL_LLM, OPENAI_API_BASE

from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")


class Punctuation(dspy.Signature):
    """Fix the punctuations and capitalizations of the text without changing
    the text."""

    text: str = dspy.InputField()
    output: str = dspy.OutputField()


def fix_punctuations(text: str) -> str:
    lm = dspy.LM(
        model=f"openai/{SMALL_LLM}",
        api_key=os.environ.get("GROQ_API_KEY"),
        api_base=OPENAI_API_BASE,
        temperature=0,
    )
    dspy.configure(lm=lm)
    try:
        predict = dspy.Predict(Punctuation)
        result = predict(text=text)
        return result.output
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        return "Error"
