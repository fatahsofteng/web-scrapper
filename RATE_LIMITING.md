# Rate Limiting Configuration for YouTube Audio Crawler

## Overview

This document explains the rate limiting and anti-ban measures implemented to avoid 403 errors when downloading from YouTube.

## Why Rate Limiting?

YouTube has anti-bot protection that can detect and block automated downloads. Without rate limiting, you may encounter:
- 403 Forbidden errors
- IP bans
- Temporary account restrictions

## Implemented Solutions

### 1. **Sleep Intervals Between Downloads**

Each video download now includes random sleep intervals to mimic human behavior:

```python
# In tasks.py
SLEEP_BETWEEN_VIDEOS = 5  # Base sleep time between videos (seconds)
SLEEP_INTERVAL_MIN = 3     # Minimum random sleep (seconds)
SLEEP_INTERVAL_MAX = 8     # Maximum random sleep (seconds)
```

**How it works:**
- Before each download, the system sleeps for 3-8 seconds (random)
- Between videos, it waits at least 5 seconds
- This creates irregular timing patterns that look more human

### 2. **Download Speed Limiting**

Downloads are throttled to avoid suspiciously fast transfer rates:

```python
RATE_LIMIT = '500K'  # 500KB/s download speed limit
```

**Benefit:** Slower downloads appear more like regular users watching videos.

### 3. **Request Throttling**

API requests to YouTube are spaced out:

```python
'sleep_interval_requests': 1  # 1 second between API requests
```

**Applied to:**
- Metadata extraction
- Video info requests
- Channel scraping

### 4. **Download Limits**

Conservative hourly limit to avoid detection:

```python
MAX_DOWNLOADS_PER_HOUR = 50  # Maximum 50 videos per hour
```

**Note:** This is currently a documentation guideline. For automatic enforcement, you can implement Celery rate limits.

### 5. **Retry Mechanism**

Failed downloads are retried automatically:

```python
'retries': 3,           # Retry failed downloads 3 times
'fragment_retries': 3,  # Retry failed fragments 3 times
```

## Configuration Options

### Adjusting Rate Limits

Edit these constants in `tasks.py` (lines 35-41) to tune the rate limiting:

```python
# --- RATE LIMITING CONFIGURATION ---
SLEEP_BETWEEN_VIDEOS = 5  # Increase for more conservative crawling
SLEEP_INTERVAL_MIN = 3     # Minimum random sleep
SLEEP_INTERVAL_MAX = 8     # Maximum random sleep
MAX_DOWNLOADS_PER_HOUR = 50
RATE_LIMIT = '500K'        # Options: '100K', '500K', '1M', etc.
```

### Recommended Settings by Use Case

#### **Conservative (Safest - Avoid Bans)**
```python
SLEEP_BETWEEN_VIDEOS = 10
SLEEP_INTERVAL_MIN = 5
SLEEP_INTERVAL_MAX = 15
RATE_LIMIT = '300K'
MAX_DOWNLOADS_PER_HOUR = 30
```

#### **Moderate (Balanced)**
```python
SLEEP_BETWEEN_VIDEOS = 5
SLEEP_INTERVAL_MIN = 3
SLEEP_INTERVAL_MAX = 8
RATE_LIMIT = '500K'
MAX_DOWNLOADS_PER_HOUR = 50
```

#### **Aggressive (Faster, Higher Risk)**
```python
SLEEP_BETWEEN_VIDEOS = 2
SLEEP_INTERVAL_MIN = 1
SLEEP_INTERVAL_MAX = 3
RATE_LIMIT = '1M'
MAX_DOWNLOADS_PER_HOUR = 100
```

⚠️ **Warning:** Aggressive settings may trigger YouTube's anti-bot protection.

## Additional Recommendations

### 1. **Use Proxy Rotation (Already Implemented)**

The system uses Decodo proxy rotation:
- Each request gets a new IP via `gate.decodo.com`
- Reduces the risk of IP-based rate limiting
- Configure with environment variables:
  ```bash
  export DECODO_USER="your_username"
  export DECODO_PASS="your_password"
  ```

### 2. **Monitor Download Success Rate**

Watch for these warning signs:
- Increasing 403 errors
- Failed downloads
- Slow metadata extraction

**Action:** If you see these, increase sleep intervals.

### 3. **Schedule Downloads During Off-Peak Hours**

YouTube is less strict during off-peak hours:
- Late night (2 AM - 6 AM)
- Weekdays vs weekends

### 4. **Batch Processing Strategy**

Instead of downloading entire channels at once:
- Download 50 videos
- Wait 1-2 hours
- Download next batch

## Implementation Details

### yt-dlp Built-in Rate Limiting Features

The implementation uses yt-dlp's native rate limiting options:

```python
ydl_opts = {
    # Rate limiting parameters
    'sleep_interval': SLEEP_BETWEEN_VIDEOS,
    'max_sleep_interval': SLEEP_INTERVAL_MAX,
    'sleep_interval_requests': 1,
    'ratelimit': RATE_LIMIT,

    # Retry parameters
    'retries': 3,
    'fragment_retries': 3,
}
```

### Additional Sleep Before Each Download

```python
# Random sleep before starting (in download_video function)
sleep_time = random.uniform(SLEEP_INTERVAL_MIN, SLEEP_INTERVAL_MAX)
time.sleep(sleep_time)
```

### Delay Between Queueing Tasks

```python
# In scrape_channel_videos function
for idx, url in enumerate(video_urls):
    download_video.delay(url, channel_url)

    if (idx + 1) % 10 == 0:  # Every 10 videos
        time.sleep(2)  # Brief pause
```

## Testing Rate Limiting

### Test with a Small Channel

```bash
# Start with a channel that has only 5-10 videos
curl -X POST http://localhost:8000/start-jobs-from-file \
  -H "Content-Type: application/json" \
  -d '{"filename": "test_channels.txt"}'
```

### Monitor Celery Logs

```bash
# Watch for sleep messages
celery -A tasks worker --loglevel=info
```

You should see:
```
Sleeping for 5.3 seconds before downloading...
Extracting metadata for https://youtube.com/watch?v=...
Downloading audio for video ID: Jq7llIkbJeA...
```

### Check for 403 Errors

If you see frequent 403 errors, **increase the sleep intervals**.

## Troubleshooting

### Problem: Still Getting 403 Errors

**Solution 1:** Increase sleep intervals
```python
SLEEP_BETWEEN_VIDEOS = 15
SLEEP_INTERVAL_MIN = 10
SLEEP_INTERVAL_MAX = 20
```

**Solution 2:** Reduce download speed
```python
RATE_LIMIT = '200K'
```

**Solution 3:** Check proxy status
```bash
# Test proxy connection
curl -x http://DECODO_USER:DECODO_PASS@gate.decodo.com:7000 https://youtube.com
```

### Problem: Downloads Too Slow

**Solution:** Adjust the balance between speed and safety
```python
SLEEP_BETWEEN_VIDEOS = 3
SLEEP_INTERVAL_MIN = 2
SLEEP_INTERVAL_MAX = 5
```

### Problem: Celery Workers Idle

**Solution:** Check if tasks are being queued
```bash
# Check Redis queue
redis-cli LLEN celery

# Check Celery worker status
celery -A tasks inspect active
```

## Future Enhancements

### 1. **Automatic Rate Limit Adjustment**

Detect 403 errors and automatically increase sleep intervals:

```python
# Pseudo-code
if error == 403:
    SLEEP_INTERVAL_MIN *= 1.5
    SLEEP_INTERVAL_MAX *= 1.5
```

### 2. **Celery Rate Limit**

Use Celery's built-in rate limiting:

```python
@celery_app.task(name="download_video", rate_limit='50/h')  # 50 per hour
def download_video(video_url: str, channel_url: str = None):
    # ...
```

### 3. **Priority Queue**

Download important videos first:

```python
download_video.apply_async(
    args=[url, channel_url],
    priority=9  # 0-9, higher = more priority
)
```

### 4. **Download Window**

Only download during specific hours:

```python
import datetime

current_hour = datetime.datetime.now().hour
if 2 <= current_hour <= 6:  # 2 AM - 6 AM only
    download_video.delay(url, channel_url)
else:
    # Schedule for later
    pass
```

## References

- [yt-dlp Rate Limiting Options](https://github.com/yt-dlp/yt-dlp#network-options)
- [Celery Rate Limits](https://docs.celeryq.dev/en/stable/userguide/tasks.html#rate-limits)
- [YouTube's Terms of Service](https://www.youtube.com/t/terms)

## Summary

✅ **Implemented Features:**
- Random sleep intervals (3-8 seconds)
- Download speed limiting (500KB/s)
- Request throttling (1 second between API calls)
- Automatic retries (3 attempts)
- Proxy rotation (Decodo)

⚠️ **Monitor and Adjust:**
- Start conservative, increase speed gradually
- Watch for 403 errors
- Adjust settings based on success rate

🎯 **Goal:**
Download all channel videos reliably while avoiding bans.
