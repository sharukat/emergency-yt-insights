import os
import re
import dspy
import logging
from typing import List
from transformers import AutoTokenizer
from langchain_ollama import OllamaEmbeddings
from src.text_splitter import SemanticChunker
from src.classifiers import Classify
from src.global_settings import SMALL_LLM, EMBED_MODEL

from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")

classifier = Classify()
tokenizer = AutoTokenizer.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    token=os.environ.get("HF_TOKEN"),
    trust_remote_code=True)

# Initialize embedding model
embeddings = OllamaEmbeddings(
    model=EMBED_MODEL, base_url=os.getenv("OLLAMA_SERVICE")
)

# Initialize the semantic chunker
chunker = SemanticChunker(
    embeddings=embeddings, breakpoint_threshold_type="percentile"
)

# Initialize LLM
lm = dspy.LM(
        model=f"ollama_chat/{SMALL_LLM}",
        api_key="",
        api_base=os.getenv("OLLAMA_SERVICE"),
        temperature=0,
    )
dspy.configure(lm=lm)


class Punctuation(dspy.Signature):
    """Fix the punctuations and capitalizations
    of the text without changing the text."""

    text: str = dspy.InputField()
    output: str = dspy.OutputField()


def remove_fillers_transcript_specific_words(text) -> str:
    try:
        if text is not None:
            fillers = [
                "um", "uh", "hmm", "mhm", "uh-huh", "ah", "huh", "hm", "m"
                ]
            pattern = r'\b(?:' + '|'.join(
                re.escape(filler) for filler in fillers) + r')\b'
            cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

            # Remove [Music], [Applause], [ __ ], and new lines (\n)
            cleaned_text = re.sub(
                r'\[(Music|Applause|\xa0__\xa0)\]', '', cleaned_text)
            cleaned_text = cleaned_text.replace("\n", " ")
            return cleaned_text
    except Exception as e:
        logging.info(e)
        return "Not available"


def preprocess(text: str) -> str:
    text = remove_fillers_transcript_specific_words(text)
    try:
        if text != "Not available":
            predict = dspy.Predict(Punctuation)
            result = predict(text=text)
            return result.output
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        return "Error"


def count_tokens(text: str) -> int:
    tokens = tokenizer.encode(text)
    return len(tokens)


def chunking(data_record: dict, item_name: str, context: str) -> List[dict]:
    chunks = chunker.create_documents([data_record[item_name]])

    classified_chunks = []
    for chunk in chunks:
        text = chunk.page_content
        size = count_tokens(text)
        if size >= 100:
            pred = classifier.classifier(
                text=text,
                type="video_relevance",
                topic=context)["prediction"]

            result = {
                "video_id": data_record["video_id"],
                "title": data_record["title"],
                "url": data_record["url"],
                "text": text,
                "comments": data_record["comments"],
                "related": pred
            }
            classified_chunks.append(result)
    return classified_chunks
