import uuid
import asyncio
import logging
from enum import Enum
from tqdm import tqdm
from asyncio import Queue
from src.crud import MongoCrud
from src.youtube import YouTube
from src.utils import preprocess, chunking
from src.global_settings import StatusType
from src.topic_modeling import BertTopic
from src.api_utils import FetchRequest, AnalyzeRequest, status_stream
from src.classifiers import Classify
from typing import Generic
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize MongoDB client
DB = MongoCrud()


class TaskResult(Generic[StatusType]):
    def __init__(self,
                 status_struct: type[StatusType],
                 init_status: StatusType):
        self.status_struct = status_struct
        self.status = init_status
        self.result = None
        self.error = None
        self.status_queue = Queue()

    async def update_status(self, new_status: type[StatusType]):
        self.status = new_status
        await self.status_queue.put(new_status)
        await asyncio.sleep(1)


class TaskStatus(str, Enum):
    EXTRACTING = "Extracting..."
    PREPROCESSING = "Preprocessing..."
    CLASSIFYING = "Classifying..."
    SAVING = "Saving..."
    CHUNKING = "Chunking..."
    COMPLETED = "Completed"
    ERROR = "Error"
    TOPICMODEL = "Topic modeling in progress..."
    SENTIMENTS = "Sentiment analysis in progress..."


# active_tasks = {}
# active_analyze_tasks = {}

active_tasks = {"extraction": {}, "analysis": {}}


async def process_data(task_id: str, request: FetchRequest):
    task_result = active_tasks["extraction"][task_id]
    try:
        await task_result.update_status(TaskStatus.EXTRACTING)
        YT = YouTube(context=request.context, keywords=request.keywords)
        results = YT.fetch_data(required_comments=request.comments_required)

        COLL_STATUS = "ADDING DATA TO A NEW COLLECTION"
        if request.is_existing_collection:
            COLL_STATUS = "ADDING DATA TO AN EXISTING COLLECTION"
            existing_ids = DB.get_ids("extract", request.collection_name)
            new_results = [
                item
                for item in results
                if item["video_id"] not in existing_ids
            ]
            logging.info(f"{len(new_results)} out of {len(results)} are new.")
            results = new_results
        logging.info(COLL_STATUS)
        logging.info(task_result.status)

        await task_result.update_status(TaskStatus.SAVING)
        DB.insert_many("extract", request.collection_name, results)
        logging.info(task_result.status)

        await task_result.update_status(TaskStatus.PREPROCESSING)
        processed_results = [
            {**item, "transcript": preprocess(item["transcript"])}
            for item in results
        ]
        logging.info(task_result.status)

        # Identify whether the vidoes are relevant - Binary classification
        await task_result.update_status(TaskStatus.CLASSIFYING)
        classifier = Classify()
        relevant = [
            {**item, "related": "Yes"}
            for item in processed_results
            if classifier.classifier(
                text=item["transcript"],
                type="video_relevance",
                topic=request.context
            )["prediction"]
            == "Related"
        ]

        # Save preprocessed and classified data in the database
        await task_result.update_status(TaskStatus.SAVING)
        DB.insert_many("processed", request.collection_name, relevant)

        # Chunk extracted video transcripts and identify chunks relevancy
        await task_result.update_status(TaskStatus.CHUNKING)
        chunked = []
        for item in relevant:
            chunks = chunking(item, "transcript", request.context)
            chunked.extend(chunks)

        # Save chunks data in the 'chunked' database
        await task_result.update_status(TaskStatus.SAVING)
        DB.insert_many("chunked", request.collection_name, chunked)

        await task_result.update_status(TaskStatus.COMPLETED)
        logging.info(task_result.status)
        task_result.result = "Final results"

    except Exception as e:
        logging.error(f"Error processing task {task_id}: {str(e)}")
        await task_result.update_status(TaskStatus.ERROR)
        task_result.error = str(e)


async def analyze_data(task_id: str, request: AnalyzeRequest):
    task_result = active_tasks["analysis"][task_id]
    try:
        if "topic-model" in request.analysis_types:
            await task_result.update_status(TaskStatus.TOPICMODEL)
            docs = DB.get_text("chunked", request.collection_name, "text")
            BT = BertTopic(zero_shot_topics=request.topics)
            topics = BT.get_topics(paragraphs=docs)

            await task_result.update_status(TaskStatus.SAVING)
            documents = [{"topic": topic} for topic in topics]
            DB.insert_many("topics", request.collection_name, documents)

            await task_result.update_status(TaskStatus.COMPLETED)
            logging.info(task_result.status)
            task_result.result = "Final results"

        if "sentiments" in request.analysis_types:
            await task_result.update_status(TaskStatus.SENTIMENTS)
            items = list(DB.get_all("processed", request.collection_name))
            classifier = Classify()
            for item in tqdm(items, total=len(items)):
                item.pop('_id', None)
                result = classifier.classifier(
                    text=item['transcript'], type="sentiments")
                item["sentiment"] = result["prediction"]

            await task_result.update_status(TaskStatus.SAVING)
            DB.insert_many("sentiments", request.collection_name, items)

            await task_result.update_status(TaskStatus.COMPLETED)
            logging.info(task_result.status)
            task_result.result = "Final results"

    except Exception as e:
        logging.error(f"Error processing task {task_id}: {str(e)}")
        await task_result.update_status(TaskStatus.ERROR)
        task_result.error = str(e)


# *****************************************************************
# FastAPI Endpoints
# *****************************************************************


@app.post("/fetch")
async def fetch_data(request: FetchRequest, background_tasks: BackgroundTasks):
    logging.info(f"The request is: {request}")
    task_id = str(uuid.uuid4())
    active_tasks["extraction"][task_id] = TaskResult(
        TaskStatus,
        TaskStatus.EXTRACTING
        )

    # Start processing in the background
    background_tasks.add_task(process_data, task_id, request)
    return JSONResponse({"task_id": task_id, "status": "EXTRACTING"})


@app.get("/status/{task_type}/{task_id}")
async def stream_status(task_id: str, task_type: str):
    if task_id not in active_tasks[task_type]:
        return JSONResponse(
            status_code=404, content={"error": "Task not found"})
    return StreamingResponse(
        status_stream(task_id, active_tasks[task_type], TaskStatus),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/collections")
def get_collections(db_name: str):
    return {"response": DB.get_collections(db_name=db_name)}


@app.get("/topics/{collection_name}")
def get_topics(collection_name: str):
    topics = DB.get_text("topics", collection_name, "topic")
    if topics:
        return JSONResponse({"response": topics})
    return JSONResponse(status_code=404, content={"error": "No content"})


@app.post("/analyze")
def analyze(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    logging.info(f"The request is: {request}")
    task_id = str(uuid.uuid4())
    active_tasks["analysis"][task_id] = TaskResult(
        TaskStatus, TaskStatus.TOPICMODEL)
    background_tasks.add_task(analyze_data, task_id, request)
    return JSONResponse(
        {"task_id": task_id, "status": "Topic modeling in progress..."})
