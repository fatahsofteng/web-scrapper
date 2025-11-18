# YouTube Audio Crawler

Automated system for downloading audio and metadata from YouTube channels for ASR (Automatic Speech Recognition) training and audio dataset creation.

## 🎯 Features

- ✅ **Batch channel scraping** - Process multiple channels from a file
- ✅ **High-quality audio** - WAV format, 48kHz sample rate, mono
- ✅ **Complete metadata** - Video info + audio specs in JSON
- ✅ **Rate limiting** - Built-in protection against 403 bans
- ✅ **Proxy rotation** - Decodo integration for IP diversity
- ✅ **Distributed processing** - Celery + Redis for scalability
- ✅ **Organized storage** - One folder per video with ID-based naming

## 📋 Requirements

### System Requirements

```bash
# Python 3.8+
python --version

# FFmpeg (for audio processing)
ffmpeg -version

# Redis (for Celery task queue)
redis-server --version
```

### Python Dependencies

```bash
pip install -r requirements.txt
```

Requirements:
- fastapi
- uvicorn
- celery
- redis
- yt-dlp

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Proxy (Optional but Recommended)

Set environment variables for Decodo proxy:

```bash
export DECODO_USER="your_username"
export DECODO_PASS="your_password"
```

⚠️ **Note:** Without proxy, you may encounter rate limiting faster.

### 3. Start Redis

```bash
redis-server
```

### 4. Start Celery Worker

In a new terminal:

```bash
celery -A tasks worker --loglevel=info
```

### 5. Start FastAPI Server

In another terminal:

```bash
uvicorn main:app --reload
```

### 6. Start Downloading

#### Option A: From Channel List File

```bash
curl -X POST http://localhost:8000/start-jobs-from-file \
  -H "Content-Type: application/json" \
  -d '{"filename": "創用CC_50個YT頻道.txt"}'
```

#### Option B: Single Channel via API

Create a custom channel list file and use the endpoint above.

## 📂 Output Structure

```
downloads/
├── Jq7llIkbJeA/                 # Video ID directory
│   ├── Jq7llIkbJeA.wav          # Audio file (48kHz, mono, WAV)
│   └── Jq7llIkbJeA.json         # Metadata
├── dQw4w9WgXcQ/
│   ├── dQw4w9WgXcQ.wav
│   └── dQw4w9WgXcQ.json
└── ...
```

### Metadata Format

Each JSON file contains:

```json
{
  "video_id": "Jq7llIkbJeA",
  "channel_url": "https://www.youtube.com/@joeman",
  "title": "Video title",
  "duration_sec": 512.23,
  "upload_date": "20231115",
  "audio": {
    "codec": "wav",
    "sample_rate": 48000,
    "channels": 1,
    "file_size": 32123442
  }
}
```

## ⚙️ Rate Limiting Configuration

To avoid YouTube 403 bans, the system implements multiple rate limiting strategies:

### Default Settings (tasks.py:35-41)

```python
SLEEP_BETWEEN_VIDEOS = 5   # 5 seconds between videos
SLEEP_INTERVAL_MIN = 3      # Min random sleep
SLEEP_INTERVAL_MAX = 8      # Max random sleep
RATE_LIMIT = '500K'         # 500KB/s download speed
```

### Built-in Protections

1. **Random sleep intervals** - 3-8 seconds before each download
2. **Download speed limit** - Max 500KB/s to appear human
3. **Request throttling** - 1-2 seconds between API calls
4. **Automatic retries** - 3 attempts for failed downloads
5. **Proxy rotation** - New IP per request (with Decodo)

### Adjusting Rate Limits

Edit `tasks.py` constants for your needs:

#### Conservative (Safest)
```python
SLEEP_BETWEEN_VIDEOS = 10
SLEEP_INTERVAL_MIN = 5
SLEEP_INTERVAL_MAX = 15
RATE_LIMIT = '300K'
```

#### Aggressive (Faster, Higher Risk)
```python
SLEEP_BETWEEN_VIDEOS = 2
SLEEP_INTERVAL_MIN = 1
SLEEP_INTERVAL_MAX = 3
RATE_LIMIT = '1M'
```

📖 **Full Documentation:** See [RATE_LIMITING.md](RATE_LIMITING.md)

## 🎵 Audio Format Specifications

### Current Settings

- **Format:** WAV (uncompressed)
- **Sample Rate:** 48 kHz
- **Channels:** 1 (mono)
- **Bit Depth:** 16-bit
- **Filename:** `{video_id}.wav`

### Meets Requirements ✅

| Requirement | Setting | Status |
|-------------|---------|--------|
| Sample Rate ≥ 16 kHz | 48 kHz | ✅ |
| Mono audio | 1 channel | ✅ |
| Uncompressed format | WAV | ✅ |
| Filename = Video ID | `{video_id}.wav` | ✅ |

### Alternative: Use FLAC

To save storage space (~50-60% smaller, same quality):

Edit `tasks.py:69`:
```python
'preferredcodec': 'flac',  # Change from 'wav'
```

📖 **Full Documentation:** See [METADATA_STRUCTURE.md](METADATA_STRUCTURE.md)

## 🔍 Monitoring

### Check Celery Worker Status

```bash
celery -A tasks inspect active
```

### Check Task Queue Length

```bash
redis-cli LLEN celery
```

### View Worker Logs

```bash
celery -A tasks worker --loglevel=info
```

Look for these messages:
```
Sleeping for 5.3 seconds before downloading...
Extracting metadata for https://youtube.com/watch?v=...
✓ Successfully downloaded and saved metadata for {video_id}
```

## 🐛 Troubleshooting

### Problem: 403 Forbidden Errors

**Cause:** YouTube rate limiting detected

**Solution:**
1. Increase sleep intervals in `tasks.py`
2. Enable proxy (set DECODO credentials)
3. Reduce download speed limit

### Problem: Downloads Failing

**Check:**
```bash
# Test yt-dlp directly
yt-dlp --print title "https://youtube.com/watch?v=VIDEO_ID"

# Test FFmpeg
ffmpeg -version
```

### Problem: Celery Not Processing Tasks

**Check:**
```bash
# Redis running?
redis-cli ping  # Should return "PONG"

# Celery worker running?
celery -A tasks inspect active
```

### Problem: Proxy Not Working

**Test:**
```bash
curl -x http://$DECODO_USER:$DECODO_PASS@gate.decodo.com:7000 https://youtube.com
```

## 📊 Channel List Format

Create a text file with channels (CSV format):

```
頻道名稱,頻道網址
Joe嬌,https://www.youtube.com/@joeman
阿滴英文,https://www.youtube.com/@RayDuEnglish
志祺七七,https://www.youtube.com/@chihchiseven
```

Requirements:
- First line can be header (will be filtered)
- Format: `name,URL`
- Only YouTube channel URLs processed
- Supports `@username` and `channel/ID` formats

## 🔧 API Endpoints

### POST /start-jobs-from-file

Start scraping jobs from a channel list file.

**Request:**
```json
{
  "filename": "創用CC_50個YT頻道.txt"
}
```

**Response:**
```json
{
  "message": "Started jobs for 50 channels",
  "channels_processed": 50
}
```

### GET /

Health check endpoint.

**Response:**
```json
{
  "status": "YouTube Audio Crawler API is running"
}
```

## 📈 Performance Considerations

### Download Speed

With default rate limiting:
- ~50 videos per hour
- ~1 video per 70-80 seconds (including sleep)
- For 1000 videos: ~20 hours

### Storage Requirements

Estimate:
- Average video: 10 minutes
- WAV @ 48kHz mono: ~30 MB per 10 minutes
- 1000 videos: ~30 GB

Use FLAC to reduce by 40-50%.

### Scaling

**Horizontal Scaling:**
```bash
# Run multiple Celery workers
celery -A tasks worker --concurrency=4 &
celery -A tasks worker --concurrency=4 &
```

**Rate Limit Warning:** More workers = higher rate limit risk. Adjust sleep intervals accordingly.

## 📚 Documentation

- [RATE_LIMITING.md](RATE_LIMITING.md) - Comprehensive rate limiting guide
- [METADATA_STRUCTURE.md](METADATA_STRUCTURE.md) - Metadata format and usage examples
- [tasks.py](tasks.py) - Source code with inline comments

## 🔐 Privacy & Legal

### Important Notes

1. **Respect YouTube Terms of Service**
2. **Use for authorized purposes only** (research, education, fair use)
3. **Do not redistribute** downloaded content without permission
4. **Check video licenses** - Prioritize Creative Commons content

### Provided Channel List

The included "創用CC_50個YT頻道.txt" contains channels that publish Creative Commons content.

## 🛠️ Technology Stack

- **FastAPI** - REST API framework
- **Celery** - Distributed task queue
- **Redis** - Message broker
- **yt-dlp** - YouTube download library
- **FFmpeg** - Audio processing
- **Decodo** - Proxy rotation service (optional)

## 📝 Task Workflow

```
1. User uploads channel list → FastAPI endpoint
2. FastAPI queues scrape_channel_videos tasks → Celery
3. Celery worker scrapes channel → Gets video URLs
4. For each video, queues download_video task → Celery
5. Celery worker downloads video with rate limiting
6. Saves audio (WAV) + metadata (JSON) to disk
```

## 🔄 Recent Updates

### v2.0 - Rate Limiting & Metadata Enhancement

**Changes:**
- ✅ Added comprehensive rate limiting (sleep intervals, speed limits)
- ✅ Implemented proper metadata storage (1 folder per video)
- ✅ Upgraded audio format (WAV, 48kHz, mono)
- ✅ Added retry mechanism for failed downloads
- ✅ Enhanced logging and error handling

**Migration from v1:**
- Old: `downloads/{uploader}/{title}.mp3`
- New: `downloads/{video_id}/{video_id}.wav`

## 🤝 Contributing

### Reporting Issues

1. Check existing issues first
2. Provide full error logs
3. Include `tasks.py` configuration
4. Specify yt-dlp version: `yt-dlp --version`

### Suggested Improvements

- [ ] Automatic rate limit adjustment based on 403 errors
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Web dashboard for monitoring
- [ ] Resume interrupted downloads
- [ ] Duplicate detection
- [ ] Quality validation

## 📞 Support

For issues or questions:
1. Check documentation (RATE_LIMITING.md, METADATA_STRUCTURE.md)
2. Review Celery logs for error messages
3. Test with single video first before batch processing
4. Ensure all dependencies installed correctly

## 📄 License

This project is for educational and research purposes. Respect YouTube's Terms of Service and applicable laws in your jurisdiction.

---

**Happy Crawling! 🎵🤖**
