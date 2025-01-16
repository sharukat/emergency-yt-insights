import json
import asyncio
import logging
from typing import List
from pydantic import BaseModel, Field

# *****************************************************************
# Requsets Pydantic Structures
# *****************************************************************


class FetchRequest(BaseModel):
    # ... emphasize that the field is required (must be provided)
    context: str = Field(..., description="Context for data fetching")
    keywords: List[str] = Field(..., description="List of keywords to search")
    collection_name: str = Field(..., description="MongoDB collection name")
    is_existing_collection: bool = Field(False)
    comments_required: bool = Field(False)


class AnalyzeRequest(BaseModel):
    collection_name: str = Field(..., description="MongoDB collection name")
    topics: List[str] = Field([], description="List of topics")
    analysis_types: List[str] = Field(..., description="Type of the analysis")

# *****************************************************************
# Helper Classes and Funtions for Streaming Backend Status
# *****************************************************************


async def status_stream(task_id: str, active_tasks: dict, status_struct: type):
    """Stream status updates for a specific task"""
    task_result = active_tasks[task_id]
    while True:
        try:
            # Wait for the next status update
            current_status = await task_result.status_queue.get()
            data = {
                "status": current_status,
                "task_id": task_id
            }

            if current_status == status_struct.COMPLETED:
                data["result"] = task_result.result
            elif current_status == status_struct.ERROR:
                data["error"] = task_result.error

            yield f"data: {json.dumps(data)}\n\n"
            await asyncio.sleep(0.1)

            if current_status in [status_struct.COMPLETED,
                                  status_struct.ERROR]:
                break

        except Exception as e:
            logging.error(f"Error in status stream: {str(e)}")
            break
