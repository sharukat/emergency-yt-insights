from pydantic import BaseModel
from typing import List
from fastapi import FastAPI
from src.youtube import YouTube
import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()


class FetchRequest(BaseModel):
    context: str
    keywords: List[str]


@app.post("/fetch")
def fetch_data(request: FetchRequest):
    YT = YouTube(context=request.context, keywords=request.keywords)
    results = YT.fetch_data()
    YT.mongodb_add(
        db_name='extract',
        collection_name='planecrash',
        documents=results)
    return {"results": results}
