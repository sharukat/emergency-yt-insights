import os

# import re
import logging
from typing import List
from dotenv import load_dotenv

from src.global_settings import EMBED_MODEL
from langchain_cohere import CohereRerank
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain.retrievers import contextual_compression
from langchain_ollama import OllamaEmbeddings
# from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_core.output_parsers import StrOutputParser
# BaseOutputParser

# Load environmental variables
load_dotenv(dotenv_path=".env")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_ENDPOINT")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["COHERE_API_KEY"] = os.getenv("COHERE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO)


class Chat:
    def __init__(self, model: str) -> None:
        self.model_name = os.getenv("LLM")
        self.model = ChatGroq(
            model=self.model_name,
            temperature=0,
        )
        self.dense_embeddings = OllamaEmbeddings(
            model=EMBED_MODEL, base_url=os.getenv("OLLAMA_SERVICE")
        )
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.types = {
            0: "Disaster and Emergency Management",
            1: "Health, Safety and Environment (HSE)",
        }
        self.db_collection = {
            0: "yt_dem",
            1: "yt_hse",
        }

        # self.multi_query_llm = ChatGroq(model="llama-3.1-8b-instant")

    def get_hyde_model(self, max_tokens=None):
        model = ChatGroq(
            model=self.model_name,
            temperature=0,
            max_tokens=max_tokens
        )
        return model

    def classifier(self, question: str) -> int:
        return self.classify.predict(question)

    def hyde_generation(self, question: str, type: int):
        prompt = PromptTemplate.from_template(
            """
            You are an expert in providing information on AI applications
            and technologies for `{`query_type}`.

            Provide a detailed explanation for the below user question.

            Question:
            `{question}`.
            """
        )

        chain = prompt | self.get_hyde_model(max_tokens=512)
        response = chain.invoke({
            "query_type": self.types[type],
            "question": question})
        return response

    def retriever(self, question: str):

        # Output parser will split the LLM result into a list of queries
        # class LineListOutputParser(BaseOutputParser[List[str]]):
        #     """Output parser for a list of lines."""

        #     def parse(self, text: str) -> List[str]:
        #         lines = text.strip().split("\n")
        #         return list(filter(None, lines))  # Remove empty lines

        # output_parser = LineListOutputParser()

        # QUERY_PROMPT = PromptTemplate(
        #     input_variables=["question"],
        #     template="""You are an AI language model assistant. Your task is
        #     to generate five different versions of the given user question
        #     to retrieve relevant documents from a vector database. By
        #     generating multiple perspectives on the user question, your goal
        #     is to help the user overcome some of the limitations of the
        #     distance-based similarity search. Provide these alternative
        #     questions separated by newlines.
        #     Original question: {question}""",
        # )

        # llm_chain = QUERY_PROMPT | self.multi_query_llm | output_parser

        # retriever = MultiQueryRetriever(
        #     retriever=self.vectordb.as_retriever(
        #         search_type="mmr", search_kwargs={"k": 10, "fetch_k": 20}
        #     ),
        #     llm_chain=llm_chain,
        #     parser_key="lines",
        # )

        type = self.classifier(question=question)
        vectordb = QdrantVectorStore.from_existing_collection(
            embedding=self.dense_embeddings,
            sparse_embedding=self.sparse_embeddings,
            collection_name=self.db_collection[type],
            url=os.getenv("QDRANT_SERVICE"),
            retrieval_mode=RetrievalMode.HYBRID,
        )
        retriever = vectordb.as_retriever(search_kwargs={"k": 5})

        compressor = CohereRerank(model="rerank-v3.5", top_n=5)
        c_retriever = contextual_compression.ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        reranked_docs = c_retriever.invoke(question)
        # docs = []
        # if reranked_docs:
        #     for doc in reranked_docs:
        #         if doc.metadata['relevance_score'] > 0.5:
        #             docs.append(doc)
        # docs = retriever_from_llm.invoke(question)
        return reranked_docs

    def repacking(self, documents: List[Document]) -> List[Document]:
        try:
            sorted_docs = sorted(
                documents,
                key=lambda doc: doc["metadata"]["relevance_score"],
                reverse=False,
            )
            return sorted_docs
        except Exception as e:
            logging.info(e)
            raise ValueError

    def generate(self, question: str, language: str):
        urls_set = set()
        metadata_list = []
        context = []
        docs = self.retriever(question=question)
        docs = self.repacking(docs)

        for doc in docs:
            url = doc.metadata["url"]
            if url not in urls_set:
                urls_set.add(url)
                metadata_list.append(
                    {
                        "urls": url,
                        "title": doc.metadata["title"],
                        "video_id": doc.metadata["video_id"],
                    }
                )
            context.append(doc.page_content)

        context = "\n\n".join(context)

        prompt = PromptTemplate.from_template(
            """You are an expert in providing information on AI applications
            and technologies for `{query_type}`.

            First, lets think step by step. - Provide a detailed and
            descriptive explanation in `{language}` based ONLY on the
            context given below, adopting a formal tone.

            Context:
            `{context}`

            Question:
            `{question}`."""
        )

        chain = prompt | self.model | StrOutputParser()

        response = chain.invoke({
            "context": context,
            "language": language,
            "question": question})
        return {"response": response, "meta_data": metadata_list}
