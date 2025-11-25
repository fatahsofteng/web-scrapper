
import os
import random
import json
import time
from pathlib import Path
from celery import Celery
import yt_dlp

celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'  # Enable result backend
)

# --- DECODO PROXY CONFIGURATION ---
DECODO_USER = os.environ.get('DECODO_USER')
DECODO_PASS = os.environ.get('DECODO_PASS')
DECODO_HOST = "gate.decodo.com"
DECODO_PORT = "7000"

# --- COOKIE AUTHENTICATION CONFIGURATION ---
# For bypassing YouTube bot detection (proven to work in Colab testing)
# Set environment variable YOUTUBE_COOKIES_FILE to path of cookies file
# Export cookies from browser: https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
YOUTUBE_COOKIES_FILE = os.environ.get('YOUTUBE_COOKIES_FILE')


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


# --- RATE LIMITING CONFIGURATION ---
# These settings help avoid 403 bans from YouTube by slowing down requests
# Conservative settings for free tier (no proxy/IP rotator)
SLEEP_BETWEEN_VIDEOS = 15  # seconds to sleep between each video download
SLEEP_INTERVAL_MIN = 10    # minimum random sleep between requests (seconds)
SLEEP_INTERVAL_MAX = 20    # maximum random sleep between requests (seconds)
MAX_DOWNLOADS_PER_HOUR = 30  # Very conservative limit to avoid detection
RATE_LIMIT = '200K'        # Limit download speed to 200KB/s (very conservative)




@celery_app.task(name="download_video")
def download_video(video_url: str, channel_url: str = None):
    """
    Downloads a SINGLE video with rate limiting to avoid 403 bans.
    Saves audio file and metadata in a folder named by video ID.

    Args:
        video_url: URL of the video to download
        channel_url: Original channel URL (for metadata)
    """
    # Sleep before starting download to avoid rate limiting
    sleep_time = random.uniform(SLEEP_INTERVAL_MIN, SLEEP_INTERVAL_MAX)
    print(f"Sleeping for {sleep_time:.1f} seconds before downloading {video_url}...")
    time.sleep(sleep_time)

    proxy_url = get_decodo_proxy_url()

    # Configure yt-dlp with rate limiting and proper audio format
    ydl_opts = {
        # Audio format: M4A with 44kHz sample rate (strict requirement)
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',  # M4A format (AAC codec)
            'preferredquality': '192',   # Good quality bitrate
        }, {
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        }],

        # Output: downloads/{video_id}/{video_id}.{ext}
        'outtmpl': './downloads/%(id)s/%(id)s.%(ext)s',

        # Rate limiting to avoid 403 bans (yt-dlp built-in features)
        'sleep_interval': SLEEP_BETWEEN_VIDEOS,
        'max_sleep_interval': SLEEP_INTERVAL_MAX,
        'sleep_interval_requests': 1,  # Sleep 1 second between API requests
        # NOTE: ratelimit removed - caused type error, cookies handle throttling naturally

        # Audio processing
        'postprocessor_args': [
            '-ar', '44000',  # Sample rate: 44kHz exact (strict requirement)
            '-ac', '1',      # Convert to mono (1 channel)
        ],

        # Additional settings
        'ignoreerrors': False,  # Don't ignore errors - we want to know if something fails
        'no_warnings': False,
        'extract_flat': False,  # We need full metadata
        'writeinfojson': False, # We'll write JSON manually with custom format
        'retries': 3,          # Retry failed downloads
        'fragment_retries': 3,
    }

    if proxy_url:
        ydl_opts['proxy'] = proxy_url
        print(f"Downloading {video_url} via Decodo proxy...")
    else:
        print(f"Downloading {video_url} without proxy...")

    # Add cookie authentication if available
    if YOUTUBE_COOKIES_FILE and Path(YOUTUBE_COOKIES_FILE).exists():
        ydl_opts['cookiefile'] = YOUTUBE_COOKIES_FILE
        print(f"Using cookie authentication from: {YOUTUBE_COOKIES_FILE}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First, extract info without downloading to get metadata
            print(f"Extracting metadata for {video_url}...")
            info = ydl.extract_info(video_url, download=False)

            if not info:
                return f"Failed: Could not extract info for {video_url}"

            video_id = info.get('id')

            # Create directory for this video
            video_dir = Path(f'./downloads/{video_id}')
            video_dir.mkdir(parents=True, exist_ok=True)

            # Download the video
            print(f"Downloading audio for video ID: {video_id}...")
            ydl.download([video_url])

            # Prepare metadata according to specification
            metadata = {
                # Video Metadata
                "video_id": video_id,
                "channel_url": channel_url or info.get('channel_url', ''),
                "channel_id": info.get('channel_id', ''),
                "channel_name": info.get('uploader', ''),
                "title": info.get('title', ''),
                "description": info.get('description', ''),
                "upload_date": info.get('upload_date', ''),
                "duration_sec": info.get('duration', 0),
                "view_count": info.get('view_count', 0),
                "like_count": info.get('like_count', 0),
                "webpage_url": info.get('webpage_url', ''),

                # Audio Metadata (will be updated after download)
                "audio": {
                    "codec": "m4a",
                    "sample_rate": 44000,  # 44kHz exact (strict requirement)
                    "channels": 1,         # Mono
                    "original_codec": info.get('acodec', ''),
                    "original_sample_rate": info.get('asr', 0),
                    "original_bitrate": info.get('abr', 0),
                }
            }

            # Find the downloaded audio file and get its actual size
            audio_files = list(video_dir.glob(f'{video_id}.*'))
            if audio_files:
                audio_file = audio_files[0]
                metadata['audio']['file_name'] = audio_file.name
                metadata['audio']['file_size'] = audio_file.stat().st_size
                metadata['audio']['file_path'] = str(audio_file.relative_to('./downloads'))

            # Save metadata as JSON
            metadata_path = video_dir / f'{video_id}.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"✓ Successfully downloaded and saved metadata for {video_id}")
            return f"Success: {video_url} -> {video_id}"

    except Exception as e:
        error_msg = f"Failed: {video_url} - Error: {str(e)}"
        print(error_msg)
        return error_msg



@celery_app.task(name="scrape_channel_videos")
def scrape_channel_videos(channel_url: str):
    """
    Scrapes all videos from a channel with rate limiting.
    Queues download tasks for each video with delays to avoid bans.

    Args:
        channel_url: YouTube channel URL to scrape
    """
    proxy_url = get_decodo_proxy_url()

    ydl_opts = {
        'extract_flat': True,
        'skip_download': True,
        'ignoreerrors': True,
        'sleep_interval_requests': 2,  # Sleep between API requests when scraping
    }

    if proxy_url:
        ydl_opts['proxy'] = proxy_url
        print(f"Scraping channel {channel_url} via Decodo proxy...")
    else:
        print(f"Scraping channel {channel_url} without proxy...")

    # Add cookie authentication if available
    if YOUTUBE_COOKIES_FILE and Path(YOUTUBE_COOKIES_FILE).exists():
        ydl_opts['cookiefile'] = YOUTUBE_COOKIES_FILE
        print(f"Using cookie authentication from: {YOUTUBE_COOKIES_FILE}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Extracting video list from {channel_url}...")
            result = ydl.extract_info(channel_url, download=False)

            if 'entries' in result:
                video_urls = [entry['url'] for entry in result['entries'] if entry]

                print(f"Found {len(video_urls)} videos. Queueing download tasks...")

                # Queue download tasks with delays to avoid overwhelming the system
                for idx, url in enumerate(video_urls):
                    # Pass channel_url to download_video for metadata
                    download_video.delay(url, channel_url)

                    # Add small delay between queueing to spread out the load
                    if (idx + 1) % 10 == 0:  # Every 10 videos
                        print(f"Queued {idx + 1}/{len(video_urls)} videos...")
                        time.sleep(2)  # Brief pause

                return f"✓ Queued {len(video_urls)} video download tasks for channel: {channel_url}"
            else:
                return f"No video entries found for: {channel_url}"

    except Exception as e:
        error_msg = f"Failed to scrape channel: {channel_url} - Error: {str(e)}"
        print(error_msg)
        return error_msg