import os
import torch
from torch import bfloat16
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig
)
import pandas as pd
from typing import List
from bertopic import BERTopic
from bertopic.representation import TextGeneration
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from src.global_settings import EMBED_MODEL

from dotenv import load_dotenv
load_dotenv(dotenv_path="./.env")


class BertTopic:
    def __init__(self) -> None:
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.embedding_model = None
        self.pool = None
        self.generator = None
        self.zero_shot_topics = [
            "AI applications for Disaster and Emergency Management",
            "AI technologies for Disaster and Emergency Management",
        ]

    def start_pool(self):
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(EMBED_MODEL)
            self.pool = self.embedding_model.start_multi_process_pool()

    def cleanup(self):
        if self.pool is not None:
            self.embedding_model.stop_multi_process_pool(self.pool)
            self.pool = None
        torch.cuda.empty_cache()

    def get_representation_models(self) -> str:
        system_prompt = """
            <s>[INST] <<SYS>>
            You are a helpful, respectful and honest assistant for labeling
            topics.
            <</SYS>>
        """

        oneshot_prompt = """
            [INST]
            I have a topic that contains the following documents:
            - Traditional diets in most cultures were primarily plant-based
              with a little meat on top, but with the rise of industrial style
              meat production & factory farming, meat has become a staple food.
            - Especially beef, is the word food in terms of emissions.
            - Eating meat doesn't make you a bad person, not eating meat
              doesn't make you a good one.

            The topic is described by the following keywords: 'meat, beef,
            eating, emissions, food'.

            Based on the information about the topic above, please create a
            short label of this topic. Make sure you to only return the label
            and nothing more.
            [/INST] Environmental impacts of eating meat
        """

        main_prompt = """
            [INST]
            I have a topic that contains the following documents:
            [DOCUMENTS]

            The topic is described by the following keywords: '[KEYWORDS]'.

            Based on the information about the topic above, please create
            a short english label of this topic. Make sure you to only return
            the label and nothing more.
            [/INST]
        """
        prompt = system_prompt + oneshot_prompt + main_prompt
        llama = TextGeneration(self.generator, prompt=prompt, diversity=0.1)
        return {"llama": llama}

    def create_topic_model(self):
        # LLM for topic generation using keywords
        model_id = "meta-llama/Llama-3.1-8B-Instruct"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=bfloat16
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            device_map="auto",
            quantization_config=bnb_config,
        )
        self.generator = pipeline(
            model=model,
            tokenizer=tokenizer,
            task="text-generation",
            temperature=0.1,
            max_new_tokens=500,
            repetition_penalty=1.1,
        )
        vectorizer = CountVectorizer(stop_words="english")

        # Few-shot topic modeling
        topic_model = BERTopic(
            min_topic_size=10,
            embedding_model=self.embedding_model,
            vectorizer_model=vectorizer,
            zeroshot_topic_list=self.zero_shot_topics,
            zeroshot_min_similarity=0.9,
            representation_model=self.get_representation_models(),
            verbose=True,
        )
        return topic_model

    def create_dataframe(self, llama_labels, filename: str) -> None:
        df = pd.DataFrame(llama_labels, columns=['topics'])
        df.to_csv(f"data/{filename}.csv", index=False)

    def save_models(self,
                    topic_model: BERTopic,
                    model_name: str) -> None:
        topic_model.save(
            f"topic_models/{model_name}",
            serialization="safetensors",
            save_embedding_model=False,
        )
        print("Model saved successfully.")

    def get_topics(self, paragraphs: List[str], filename: str):
        self.start_pool()
        embed = self.embedding_model.encode_multi_process(
            paragraphs, pool=self.pool,
            show_progress_bar=True
        )
        self.cleanup()

        topic_model = self.create_topic_model()
        topics, _ = topic_model.fit_transform(paragraphs, embed)
        topics = topic_model.get_topics(full=True)["llama"].values()
        llama_labels = [label[0][0].split("\n")[0] for label in topics]
        self.create_dataframe(llama_labels, filename)
        self.save_models(topic_model, model_name="model-v1")
        return llama_labels

    def predict_topics(self, model_name: str, dataset: pd.DataFrame, col: str):
        model_path = f"topic_models/{model_name}"
        loaded_model = BERTopic.load(model_path)

        docs = [row[col] for _, row in dataset.iterrows()]
        embed = self.embedding_model.encode_multi_process(
            docs, pool=self.pool, show_progress_bar=True
        )
        topics, _ = loaded_model.transform(docs, embeddings=embed)

        topics_for_passages = []
        for id in topics:
            topic = loaded_model.get_topic(id, full=True)["llama"]
            topic = topic[0][0]
            topic = topic.split("\n\n[INST]")[0]
            topics_for_passages.append(topic)
        dataset["topic"] = topics_for_passages
        dataset.to_csv(f"data/{model_name}.csv", index=False)
        return dataset
