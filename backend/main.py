import json
import uuid
import asyncio
import logging
from enum import Enum
from typing import List
from src.crud import MongoCrud
from src.youtube import YouTube
from src.utils import preprocess
# from src.classifiers import Classify
from pydantic import BaseModel, Field
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


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    PREPROCESSING = "PREPROCESSING"
    CLASSIFYING = "CLASSIFYING"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"
    DATABASE = "SAVING TO THE DATABASE"


class TaskResult:
    def __init__(self):
        self.status = TaskStatus.EXTRACTING
        self.result = None
        self.error = None


active_tasks = {}
status_updates = {}


class FetchRequest(BaseModel):
    # ... emphasize that the field is required (must be provided)
    context: str = Field(..., description="Context for data fetching")
    keywords: List[str] = Field(..., description="List of keywords to search")
    collection_name: str = Field(..., description="MongoDB collection name")
    is_existing_collection: bool = Field(False)


async def process_data(task_id: str, request: FetchRequest):
    task_result = active_tasks[task_id]
    try:
        task_result.status = TaskStatus.EXTRACTING
        YT = YouTube(context=request.context, keywords=request.keywords)
        results = YT.fetch_data()
        STATUS = "ADDING DATA TO A NEW COLLECTION"
        if request.is_existing_collection:
            STATUS = "ADDING DATA TO AN EXISTING COLLECTION"
            existing_ids = DB.get_ids("extract", request.collection_name)
            new_results = [
                item
                for item in results
                if item['video_id'] not in existing_ids
            ]
            logging.info(f"{len(new_results)} out of {len(results)} are new.")
            results = new_results
        logging.info(STATUS)

        task_result.status = TaskStatus.DATABASE
        DB.insert_many("extract", request.collection_name, results)

        task_result.status = TaskStatus.PREPROCESSING
        processed_results = [
            {**item, "transcript": preprocess(item["transcript"])}
            for item in results
        ]

        # task_result.status = TaskStatus.CLASSIFYING
        # classifier = Classify()
        # relevant = [
        #     {**item, "related": "Yes"}
        #     for item in processed_results
        #     if classifier.classifier(
        #         text=item["transcript"],
        #         type="video_relevance",
        #         topic=request.context
        #     ).prediction == "Related"
        # ]
        DB.insert_many("processed", request.collection_name, processed_results)

        task_result.status = TaskStatus.COMPLETED
        task_result.result = "Final results"

    except Exception as e:
        logging.error(f"Error processing task {task_id}: {str(e)}")
        task_result.status = TaskStatus.ERROR
        task_result.error = str(e)


async def status_stream(task_id: str):
    """Stream status updates for a specific task"""
    task_result = active_tasks[task_id]
    previous_status = None

    while True:
        current_status = task_result.status
        if current_status != previous_status:
            data = {"status": current_status, "task_id": task_id}
            if current_status == TaskStatus.COMPLETED:
                data["result"] = task_result.result
            elif current_status == TaskStatus.ERROR:
                data["error"] = task_result.error

            yield f"data: {json.dumps(data)}\n\n"
            previous_status = current_status

            # Exit the loop if we've reached a terminal state
            if current_status in [TaskStatus.COMPLETED, TaskStatus.ERROR]:
                break

        await asyncio.sleep(0.5)


@app.post("/fetch")
async def fetch_data(request: FetchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = TaskResult()

    # Start processing in the background
    background_tasks.add_task(process_data, task_id, request)
    return JSONResponse({"task_id": task_id, "status": "EXTRACTING"})


@app.get("/status/{task_id}")
async def stream_status(task_id: str):
    if task_id not in active_tasks:
        return JSONResponse(
            status_code=404, content={"error": "Task not found"})
    return StreamingResponse(
        status_stream(task_id), media_type="text/event-stream")


@app.get("/collections")
def get_collections(db_name: str):
    return {"response": DB.get_collections(db_name=db_name)}
