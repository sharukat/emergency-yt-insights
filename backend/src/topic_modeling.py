import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import pandas as pd
from umap import UMAP
from typing import List
from bertopic import BERTopic
from hdbscan import HDBSCAN
from bertopic.representation import TextGeneration
from bertopic.representation import KeyBERTInspired
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer


class BertTopic:
    def __init__(self, is_train: bool = True) -> None:
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        # Embedding model with multi-processing
        self.embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
        self.pool = None

        if is_train:
            # LLM for topic generation using keywords
            model_id = "meta-llama/Llama-3.1-8B-Instruct"
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                trust_remote_code=True,
                device_map="auto"
            )
            self.generator = pipeline(
                model=self.model,
                tokenizer=self.tokenizer,
                task="text-generation",
                temperature=0.1,
                max_new_tokens=500,
                repetition_penalty=1.1,
            )
            self.vectorizer = CountVectorizer(stop_words="english")
            self.umap_model = UMAP(
                n_neighbors=15,
                n_components=5,
                min_dist=0.0,
                metric="cosine",
                random_state=42,
            )
            self.hdbscan_model = HDBSCAN(
                min_cluster_size=150,
                metric="euclidean",
                cluster_selection_method="eom",
                prediction_data=True,
            )
            self.zero_shot_topics = {
                "dem": [
                    "AI applications for Disaster and Emergency Management",
                    "AI technologies for Disaster and Emergency Management",
                ],
                "hse": [
                    "AI applications for Health, Safety & Environment (HSE)",
                    "AI technologies for Health, Safety & Environment (HSE)",
                ],
            }

    def start_pool(self):
        if self.pool is None:
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

        keybert = KeyBERTInspired()
        llama = TextGeneration(self.generator, prompt=prompt, diversity=0.1)
        return {"KeyBERT": keybert, "llama": llama}

    def create_topic_model(self, is_few_shot: bool, topics_type: any):
        if is_few_shot and topics_type is not None:
            # Few-shot topic modeling
            topic_model = BERTopic(
                min_topic_size=10,
                embedding_model=self.embedding_model,
                vectorizer_model=self.vectorizer,
                zeroshot_topic_list=self.zero_shot_topics[topics_type],
                zeroshot_min_similarity=0.9,
                representation_model=self.get_representation_models(),
                verbose=True,
            )
        else:
            # Conventional
            topic_model = BERTopic(
                umap_model=self.umap_model,
                hdbscan_model=self.hdbscan_model,
                embedding_model=self.embedding_model,
                vectorizer_model=self.vectorizer,
                representation_model=self.get_representation_models(),
                top_n_words=15,
                min_topic_size=10,
                verbose=True,
            )
        return topic_model

    def create_dataframe(
        self, keyBERT_data, llama_labels, filename: str
    ) -> pd.DataFrame:
        prepared_data = {"Number": [], "Keywords": [], "Scores": []}
        for num, entries in keyBERT_data.items():
            keywords, scores = zip(*entries)  # Unpack keywords and scores
            prepared_data["Number"].append(num)
            prepared_data["Keywords"].append(list(keywords))
            prepared_data["Scores"].append(list(scores))
        df = pd.DataFrame(prepared_data)
        df["topics"] = llama_labels
        df.to_csv(f"data/{filename}.csv", index=False)
        return df

    def save_models(self, topic_model, model_name: str) -> None:
        topic_model.save(
            f"topic_models/{model_name}",
            serialization="safetensors",
            save_ctfidf=False,
            save_embedding_model=False,
        )
        print("Model saved successfully.")

    def get_topics(
        self,
        paragraphs: List[str],
        filename: str,
        is_few_shot: bool = False,
        topics_type=None,
    ):
        self.start_pool()
        embed = self.embedding_model.encode_multi_process(
            paragraphs, pool=self.pool, show_progress_bar=True
        )
        self.cleanup()

        topic_model = self.create_topic_model(
            is_few_shot=is_few_shot, topics_type=topics_type
        )
        topics, _ = topic_model.fit_transform(paragraphs, embed)

        keyBERT_data = topic_model.get_topics(full=True)["KeyBERT"]
        topics = topic_model.get_topics(full=True)["llama"].values()
        llama_labels = [label[0][0].split("\n")[0] for label in topics]
        df = self.create_dataframe(keyBERT_data, llama_labels, filename)

        self.save_models(topic_model, model_name="conventional_dem")
        return df

    def predict_topics(self, model_name: str, dataset: pd.DataFrame, col: str):
        model_path = f"topic_models/{model_name}"
        loaded_model = BERTopic.load(model_path)

        docs = []
        for _, row in dataset.iterrows():
            docs.append(row[col])
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
