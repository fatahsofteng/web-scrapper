
import os
import random
from celery import Celery
import yt_dlp

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

# --- DECODO PROXY CONFIGURATION ---
DECODO_USER = os.environ.get('DECODO_USER')
DECODO_PASS = os.environ.get('DECODO_PASS')
DECODO_HOST = "gate.decodo.com"
DECODO_PORT = "7000"


def get_decodo_proxy_url():
    """
    Formats the proxy URL string for Decodo.
    Using the rotating endpoint gateway (gate.decodo.com) means
    Decodo will assign a new IP for each request.
    """
    if not DECODO_USER or not DECODO_PASS:

        return None

    return (
        f"http://{DECODO_USER}:{DECODO_PASS}"
        f"@{DECODO_HOST}:{DECODO_PORT}"
    )




@celery_app.task(name="download_video")
def download_video(video_url: str):
    """
    This task downloads a SINGLE video, using a single, unique proxy IP
    provided by Decodo's rotating gateway.
    """
    proxy_url = get_decodo_proxy_url()

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': './downloads/%(uploader)s/%(title)s.%(ext)s',
        'ignoreerrors': True,
    }

    if proxy_url:
        ydl_opts['proxy'] = proxy_url
        print(f"Downloading {video_url} via Decodo proxy...")
    else:
        print(f"Downloading {video_url} without proxy...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return f"Success: {video_url}"
    except Exception as e:
        return f"Failed: {video_url} - Error: {e}"



@celery_app.task(name="scrape_channel_videos")
def scrape_channel_videos(channel_url: str):
    """
    This task does NOT download. It uses a Decodo proxy to
    get all video URLs from a channel and queues them.
    """
    proxy_url = get_decodo_proxy_url()

    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'ignoreerrors': True,
    }

    if proxy_url:
        ydl_opts['proxy'] = proxy_url

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)

            if 'entries' in result:
                video_urls = [entry['url'] for entry in result['entries'] if entry]

                for url in video_urls:
                    download_video.delay(url)

                return f"Added {len(video_urls)} video jobs for channel: {channel_url}"
            else:
                return f"No video entries found for: {channel_url}"
    except Exception as e:
        return f"Failed to scrape channel: {channel_url} - Error: {e}"