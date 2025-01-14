import uuid
import asyncio
import logging
from enum import Enum
from asyncio import Queue
from src.crud import MongoCrud
from src.youtube import YouTube
from src.utils import preprocess, chunking
from src.global_settings import StatusType
from src.api_utils import FetchRequest, status_stream
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


class ExtractionTaskStatus(str, Enum):
    EXTRACTING = "Extracting..."
    PREPROCESSING = "Preprocessing..."
    CLASSIFYING = "Classifying..."
    SAVING = "Saving..."
    CHUNKING = "Chunking..."
    COMPLETED = "Completed"
    ERROR = "Error"


active_tasks = {}


async def process_data(task_id: str, request: FetchRequest):
    task_result = active_tasks[task_id]
    try:
        await task_result.update_status(ExtractionTaskStatus.EXTRACTING)
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

        await task_result.update_status(ExtractionTaskStatus.SAVING)
        DB.insert_many("extract", request.collection_name, results)
        logging.info(task_result.status)

        await task_result.update_status(ExtractionTaskStatus.PREPROCESSING)
        processed_results = [
            {**item, "transcript": preprocess(item["transcript"])}
            for item in results
        ]
        logging.info(task_result.status)

        # Identify whether the vidoes are relevant - Binary classification
        await task_result.update_status(ExtractionTaskStatus.CLASSIFYING)
        classifier = Classify()
        relevant = [
            {**item, "related": "Yes"}
            for item in processed_results
            if classifier.classifier(
                text=item["transcript"],
                type="video_relevance",
                topic=request.context
            )["prediction"] == "Related"
        ]

        # Save preprocessed and classified data in the database
        await task_result.update_status(ExtractionTaskStatus.SAVING)
        DB.insert_many("processed", request.collection_name, relevant)

        # Chunk extracted video transcripts and identify chunks relevancy
        await task_result.update_status(ExtractionTaskStatus.CHUNKING)
        chunked = []
        for item in relevant:
            chunks = chunking(item, "transcript", request.context)
            chunked.extend(chunks)

        # Save chunks data in the 'chunked' database
        await task_result.update_status(ExtractionTaskStatus.SAVING)
        DB.insert_many("chunked", request.collection_name, chunked)

        await task_result.update_status(ExtractionTaskStatus.COMPLETED)
        logging.info(task_result.status)
        task_result.result = "Final results"

    except Exception as e:
        logging.error(f"Error processing task {task_id}: {str(e)}")
        await task_result.update_status(ExtractionTaskStatus.ERROR)
        task_result.error = str(e)


# *****************************************************************
# FastAPI Endpoints
# *****************************************************************


@app.post("/fetch")
async def fetch_data(request: FetchRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = TaskResult(
        ExtractionTaskStatus, ExtractionTaskStatus.EXTRACTING)

    # Start processing in the background
    background_tasks.add_task(process_data, task_id, request)
    return JSONResponse({"task_id": task_id, "status": "EXTRACTING"})


@app.get("/status/{task_id}")
async def stream_status(task_id: str):
    if task_id not in active_tasks:
        return JSONResponse(status_code=404,
                            content={"error": "Task not found"})
    return StreamingResponse(
        status_stream(task_id, active_tasks, ExtractionTaskStatus),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/collections")
def get_collections(db_name: str):
    return {"response": DB.get_collections(db_name=db_name)}
