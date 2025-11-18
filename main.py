# main.py

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tasks import scrape_channel_videos

app = FastAPI()


class FileRequest(BaseModel):
    filename: str = "創用CC_50個YT頻道.txt"


@app.get("/")
def home():
    return {"status": "API is running. POST to /start-jobs-from-file to begin."}


@app.post("/start-jobs-from-file")
def add_jobs_from_file(request: FileRequest):
    """
    Reads the provided text file, parses each line for a channel URL,
    and adds a 'scrape_channel_videos' job to the Celery queue for each.
    """

    if not os.path.exists(request.filename):
        raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")

    job_count = 0
    channel_urls_added = []

    try:
        with open(request.filename, 'r', encoding='utf-8') as f:
            for line in f:
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue


                parts = cleaned_line.split(',')


                if len(parts) >= 2:
                    channel_url = parts[1].strip()
                    if "youtube.com/channel/" in channel_url:
                        scrape_channel_videos.delay(channel_url)
                        job_count += 1
                        channel_urls_added.append(channel_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

    return {
        "message": f"Successfully added {job_count} channel scraping jobs to the queue.",
        "file_processed": request.filename
    }