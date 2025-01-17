from enum import Enum
from typing import TypeVar

# Task Status Generic Structure
StatusType = TypeVar('T', bound=Enum)

MAIN_LLM = "llama-3.3-70b-versatile"
BASE_LLM = "phi4"
SMALL_LLM = "qwen2.5:3b"
EMBED_MODEL = "nomic-embed-text:latest"
HF_EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"
OPENAI_API_BASE = "https://api.groq.com/openai/v1"
