
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import time
from tqdm.notebook import tqdm_notebook
from typing import List
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("YOUTUBE_API_KEY")


class YouTube:
    def __init__(self,
                 keywords: List[str],
                 filename: str) -> None:

        self.youtube = build('youtube', 'v3', developerKey=API_KEY)
        self.keywords = keywords
        self.csv_path = os.path.join(BASE_DATA_PATH, f'{filename}.csv')

    def build_queries(self):
        query_set = set()
        for keyword in self.keywords:
            query_set.add(f'"AI" OR "artifical intelligence" + "{keyword}"')
        return query_set

    def search_youtube(self):
        video_info = {}
        queries = self.build_queries()
        for q in tqdm_notebook(queries,
                               total=len(queries),
                               desc="Fetching queries"):
            request = self.youtube.search().list(
                part='snippet',
                q=q,
                type='video',
                order='relevance',
                maxResults=50,
            )
            response = request.execute()
            for item in response['items']:
                video_id = item['id']['videoId']
                title = item['snippet']['title']
                thumbnail = item['snippet']['thumbnails']['url']
                if video_id not in video_info:
                    video_info[video_id] = {
                        'title': title,
                        'thumbnail': thumbnail}
            time.sleep(1)
        return video_info

    def get_transcript(self):
        video_info = self.search_youtube()
        video_df_list = []
        logs = {}

        for id, item in tqdm_notebook(video_info.items(),
                                      total=len(video_info),
                                      desc="Extracting transcripts"):

            video_url = f"https://www.youtube.com/watch?v={id}"
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id=id,
                    languages=["en", "fr", "de", "es", "it"])
                text_formatted = ""
                for i in transcript:
                    text_formatted += ' ' + i['text']

                # Adding data to the pandas dataframe
                df_item = {
                    'video_id': id,
                    'title': item.title,
                    'url': video_url,
                    'thumbnail': item.thumbnail,
                    'transcript': text_formatted,
                    }
                video_df_list.append(df_item)

            except Exception as e:
                logs[id] = {
                    'error_message': str(e)
                }
                pass

        # Save youtube data to a csv file
        df = pd.DataFrame(video_df_list)
        df.to_csv(self.csv_path, index=False)
        print("Completed")
