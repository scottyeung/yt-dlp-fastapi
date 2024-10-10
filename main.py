import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from yt_dlp import YoutubeDL
import redis
from uuid import uuid4

from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="/tmp"), name="static")

# Initialize Redis client
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, password=os.getenv('REDIS_PASS', ''), db=0)

class VideoRequest(BaseModel):
    url: HttpUrl

class TaskStatus(BaseModel):
    task_id: str
    status: str
    download_url: Optional[str] = None

async def download_and_convert(url: str, task_id: str):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'max_filesize': 1024 * 1024 * 1024,  # 1GB max file size
            'outtmpl': f'/tmp/{task_id}.%(ext)s',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get('duration', 0)

            if duration > 7200:  # 2 hours in seconds
                raise Exception("Video is longer than 2 hours")

            if info.get('is_live', False):
                raise Exception("Livestreams are not supported")

            redis_client.set(task_id, "PROCESSING")
            ydl.download([url])

        file_path = f'/tmp/{task_id}.mp3'
        redis_client.set(f"{task_id}:file_path", file_path)
        redis_client.set(task_id, "DONE")
    except Exception as e:
        redis_client.set(task_id, f"FAILED: {str(e)}")

@app.post("/submit", response_model=TaskStatus)
async def submit_video(video: VideoRequest):
    task_id = str(uuid4())
    redis_client.set(task_id, "PENDING")
    asyncio.create_task(download_and_convert(str(video.url), task_id))
    return TaskStatus(task_id=task_id, status="PENDING")

@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    status = redis_client.get(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskStatus(task_id=task_id, status=status.decode('utf-8'))

@app.get("/")
async def root():
    return {"message": "YouTube to MP3 Converter API"}

@app.get("/download/{task_id}", response_model=TaskStatus)
async def get_download_url(task_id: str):
    status = redis_client.get(task_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = status.decode('utf-8')
    if status != "DONE":
        return TaskStatus(task_id=task_id, status=status)
    
    file_path = redis_client.get(f"{task_id}:file_path")
    if file_path is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_path.decode('utf-8')
    download_url = f"/static/{os.path.basename(file_path)}"
    return TaskStatus(task_id=task_id, status=status, download_url=download_url)
