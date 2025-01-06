
import os
import dspy
import logging
import pandas as pd
from typing import List
from transformers import AutoTokenizer
from tqdm.notebook import tqdm_notebook
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


def count_tokens(dataframe: pd.DataFrame) -> List[int]:
    tokenizer = AutoTokenizer.from_pretrained(
        'meta-llama/Llama-3.1-8B-Instruct',
        token=os.environ.get("HF_TOKEN"),
        trust_remote_code=True)
    lengths = []
    for row in tqdm_notebook(dataframe.itertuples(index=True),
                             total=dataframe.shape[0]):
        tokens = tokenizer.encode(row.page_content)
        lengths.append(len(tokens))
    return lengths
