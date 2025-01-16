from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# import pandas as pd
import time
from tqdm import tqdm
from typing import List
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("YOUTUBE_API_KEY")


class YouTube:
    def __init__(self, context: str, keywords: List[str]) -> None:

        self.youtube = build("youtube", "v3", developerKey=API_KEY)
        self.context = context
        self.keywords = keywords

    def build_queries(self):
        logging.info(self.keywords)
        query_set = set()
        for keyword in self.keywords:
            query_set.add(f'{self.context} + "{keyword}"')
        logging.info(query_set)
        return query_set

    def search_youtube(self):
        video_info = {}
        queries = self.build_queries()
        for q in tqdm(queries, total=len(queries), desc="Fetching queries"):
            request = self.youtube.search().list(
                part="snippet",
                q=q,
                type="video",
                order="relevance",
                maxResults=5,
            )
            response = request.execute()
            for item in response["items"]:
                video_id = item["id"]["videoId"]
                title = item["snippet"].get("title", "")
                if video_id not in video_info:
                    video_info[video_id] = title
            time.sleep(1)
        return video_info

    def fetch_data(self, required_comments: bool = False) -> List[dict]:
        videos = self.search_youtube()
        video_list = []
        logs = {}

        for id, title in tqdm(
            videos.items(), total=len(videos), desc="Extracting transcripts"
        ):
            video_url = f"https://www.youtube.com/watch?v={id}"
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id=id, languages=["en"]
                )
                text_formatted = ""
                for i in transcript:
                    text_formatted += " " + i["text"]

                if required_comments:
                    try:
                        # Fetch comments
                        comments = []
                        response = self.youtube.commentThreads().list(
                            part='snippet',
                            videoId=id,
                            textFormat='plainText',
                            maxResults=500,
                        ).execute()
                        if response['items']:
                            for index, item in enumerate(response['items']):
                                top = item['snippet']['topLevelComment']
                                comment = top['snippet']['textDisplay']
                                comments.append(f"{index}: {comment}")
                    except Exception as e:
                        logging.error(e)
                        comments.append("Comments disabled")

                # Fixed: Access dictionary values correctly
                db_item = {
                    "video_id": str(id),
                    "title": str(title),
                    "url": str(video_url),
                    "transcript": text_formatted,
                    "comments": comments
                }
                if not isinstance(db_item, dict):
                    logging.error(f"Invalid item: {db_item}")
                    continue
                logging.info(f"Processed video: {id}")
                video_list.append(db_item)

            except Exception as e:
                logs[id] = {"error_message": str(e)}
                pass

        return video_list
