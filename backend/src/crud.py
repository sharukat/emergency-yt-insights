#!/usr/bin/env python3
import os
import json
import logging as log
from typing import List
from bson import json_util
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(dotenv_path=".env")
USERNAME = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
PORT = os.environ.get("MONGO_INITDB_ROOT_PORT")


class MongoCrud:
    def __init__(self):
        host = f"mongodb://{USERNAME}:{PASSWORD}@mongo:{PORT}/"
        self.client = MongoClient(host)
        self.db_extracted = self.client.extract
        self.db_processed = self.client.processed
        self.db_analyzed = self.client.analyzed

        self.dbs = {
            "extract": self.db_extracted,
            "processed": self.db_processed,
            "analyzed": self.db_analyzed,
        }

    def insert_many(
        self, db_name: str, collection_name: str, documents: List[dict]
    ) -> None:
        try:
            collection_list = self.dbs[db_name].list_collection_names()
            if collection_name not in collection_list:
                self.dbs[db_name].create_collection(name=collection_name)

            collection = self.dbs[db_name][collection_name]
            docs = [json.loads(json_util.dumps(doc)) for doc in documents]
            if docs:
                collection.insert_many(docs)
                log.info(f"Added {len(docs)} records into {collection_name}")

        except Exception as e:
            log.error(f"Error inserting documents: {str(e)}")
            raise

    def get_collections(self, db_name: str) -> List[str]:
        return self.dbs[db_name].list_collection_names()

    def get_ids(self, db_name: str, collection_name: str):
        ids = self.dbs[db_name][collection_name].distinct("video_id")
        return set(ids) if ids else set()
