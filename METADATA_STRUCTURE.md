# Metadata and File Structure Documentation

## Overview

This document explains the new file organization and metadata format for downloaded YouTube audio files.

## File Structure

### Directory Organization

Each video is stored in its own directory named by the video ID:

```
downloads/
├── Jq7llIkbJeA/                 # Video ID directory
│   ├── Jq7llIkbJeA.wav          # Audio file
│   └── Jq7llIkbJeA.json         # Metadata file
├── dQw4w9WgXcQ/
│   ├── dQw4w9WgXcQ.wav
│   └── dQw4w9WgXcQ.json
└── xvFZjo5PgG0/
    ├── xvFZjo5PgG0.wav
    └── xvFZjo5PgG0.json
```

### Why This Structure?

**Benefits:**
- ✅ Easy to track: Each video ID maps to one folder
- ✅ Clean organization: Audio + metadata in same location
- ✅ Prevents conflicts: No filename collisions
- ✅ Traceable: Video ID is universally unique
- ✅ Portable: Can move folders independently

## Metadata Format

### JSON Structure

Each `{video_id}.json` file contains:

```json
{
  "video_id": "Jq7llIkbJeA",
  "channel_url": "https://www.youtube.com/@joeman",
  "channel_id": "UCyBpimFKmJc4o_OwQq8JtQg",
  "channel_name": "Joe嬌",
  "title": "我被綁架到北韓拍片！？",
  "description": "Video description text...",
  "upload_date": "20231115",
  "duration_sec": 512.23,
  "view_count": 1234567,
  "like_count": 89012,
  "webpage_url": "https://www.youtube.com/watch?v=Jq7llIkbJeA",

  "audio": {
    "codec": "wav",
    "sample_rate": 48000,
    "channels": 1,
    "original_codec": "opus",
    "original_sample_rate": 48000,
    "original_bitrate": 160000,
    "file_name": "Jq7llIkbJeA.wav",
    "file_size": 32123442,
    "file_path": "Jq7llIkbJeA/Jq7llIkbJeA.wav"
  }
}
```

### Field Descriptions

#### Video Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `video_id` | string | Unique YouTube video ID | `"Jq7llIkbJeA"` |
| `channel_url` | string | Original channel URL | `"https://www.youtube.com/@joeman"` |
| `channel_id` | string | Unique channel ID | `"UCyBp..."` |
| `channel_name` | string | Channel display name | `"Joe嬌"` |
| `title` | string | Video title | `"我被綁架到北韓拍片！？"` |
| `description` | string | Full video description | `"Video desc..."` |
| `upload_date` | string | Upload date (YYYYMMDD) | `"20231115"` |
| `duration_sec` | number | Video length in seconds | `512.23` |
| `view_count` | number | Total views | `1234567` |
| `like_count` | number | Total likes | `89012` |
| `webpage_url` | string | Full video URL | `"https://..."` |

#### Audio Metadata

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `codec` | string | Output audio codec | `"wav"` |
| `sample_rate` | number | Output sample rate (Hz) | `48000` |
| `channels` | number | Number of audio channels | `1` (mono) |
| `original_codec` | string | YouTube's original codec | `"opus"` |
| `original_sample_rate` | number | Original sample rate | `48000` |
| `original_bitrate` | number | Original bitrate (bps) | `160000` |
| `file_name` | string | Audio filename | `"Jq7llIkbJeA.wav"` |
| `file_size` | number | File size in bytes | `32123442` |
| `file_path` | string | Relative path | `"Jq7llIkbJeA/..."` |

## Audio File Specifications

### Format Requirements

According to the project requirements:

#### ✅ **Mandatory Requirements**

1. **Sample Rate ≥ 16 kHz**
   - Current: **48 kHz** ✅
   - Exceeds minimum requirement

2. **Mono Audio**
   - Current: **1 channel (mono)** ✅
   - Converted from stereo if needed

3. **Filename = Video ID**
   - Current: **`{video_id}.wav`** ✅
   - Easy to match with metadata

#### 🎯 **Preferred Settings**

1. **Uncompressed/Lossless Format**
   - Current: **WAV (uncompressed)** ✅
   - Alternative: FLAC (lossless compression)

2. **High Sample Rate**
   - Current: **48 kHz** ✅
   - Options: 44.1 kHz, 48 kHz

### Changing Audio Format

#### To Use FLAC Instead of WAV

Edit `tasks.py` line 69:

```python
# Change from:
'preferredcodec': 'wav',

# To:
'preferredcodec': 'flac',
```

**Benefits of FLAC:**
- Lossless compression (same quality as WAV)
- Smaller file size (~50-60% of WAV)
- Preserves all audio information

**When to use WAV:**
- Maximum compatibility
- No processing overhead
- Some tools don't support FLAC

#### To Adjust Sample Rate

Edit `tasks.py` line 87:

```python
# Current (48 kHz):
'-ar', '48000',

# For 44.1 kHz:
'-ar', '44100',

# For 16 kHz (minimum):
'-ar', '16000',
```

**Recommended:** Stick with 48 kHz for maximum quality.

#### To Keep Stereo (Not Convert to Mono)

Edit `tasks.py` line 88:

```python
# Current (mono):
'-ac', '1',

# For stereo:
'-ac', '2',

# To keep original channels (auto):
# Remove this line entirely
```

⚠️ **Note:** The requirement says convert to mono **unless** the multi-channel is speaker-separated tracks. YouTube typically doesn't provide separate speaker tracks, so mono is correct.

## Using the Metadata

### Example: Load Metadata in Python

```python
import json
from pathlib import Path

# Load metadata
video_id = "Jq7llIkbJeA"
metadata_path = Path(f"downloads/{video_id}/{video_id}.json")

with open(metadata_path, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Access fields
print(f"Title: {metadata['title']}")
print(f"Duration: {metadata['duration_sec']} seconds")
print(f"Sample Rate: {metadata['audio']['sample_rate']} Hz")
print(f"File Size: {metadata['audio']['file_size']} bytes")
```

### Example: Find All Videos from a Channel

```python
import json
from pathlib import Path

channel_url = "https://www.youtube.com/@joeman"
downloads_dir = Path("downloads")

# Find all videos from this channel
channel_videos = []

for video_dir in downloads_dir.iterdir():
    if video_dir.is_dir():
        metadata_file = video_dir / f"{video_dir.name}.json"

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            if metadata.get('channel_url') == channel_url:
                channel_videos.append(metadata)

print(f"Found {len(channel_videos)} videos from {channel_url}")
```

### Example: Calculate Total Duration

```python
import json
from pathlib import Path

total_seconds = 0
total_files = 0

for video_dir in Path("downloads").iterdir():
    if video_dir.is_dir():
        metadata_file = video_dir / f"{video_dir.name}.json"

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            total_seconds += metadata.get('duration_sec', 0)
            total_files += 1

hours = total_seconds / 3600
print(f"Total: {total_files} files, {hours:.2f} hours of audio")
```

### Example: Generate Dataset CSV

```python
import json
import csv
from pathlib import Path

# Create CSV for ASR training
with open('dataset.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['video_id', 'audio_path', 'duration', 'sample_rate', 'title'])

    for video_dir in Path("downloads").iterdir():
        if video_dir.is_dir():
            metadata_file = video_dir / f"{video_dir.name}.json"

            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                audio_path = f"downloads/{metadata['audio']['file_path']}"

                writer.writerow([
                    metadata['video_id'],
                    audio_path,
                    metadata['duration_sec'],
                    metadata['audio']['sample_rate'],
                    metadata['title']
                ])

print("Generated dataset.csv")
```

## Data Validation

### Validate Metadata Completeness

```python
import json
from pathlib import Path

required_fields = [
    'video_id', 'channel_url', 'title',
    'duration_sec', 'upload_date'
]

required_audio_fields = [
    'codec', 'sample_rate', 'channels',
    'file_size', 'file_name'
]

def validate_metadata(metadata):
    """Check if metadata has all required fields"""

    # Check video fields
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            return False, f"Missing or empty: {field}"

    # Check audio fields
    if 'audio' not in metadata:
        return False, "Missing audio metadata"

    for field in required_audio_fields:
        if field not in metadata['audio'] or not metadata['audio'][field]:
            return False, f"Missing or empty: audio.{field}"

    # Validate sample rate
    if metadata['audio']['sample_rate'] < 16000:
        return False, f"Sample rate too low: {metadata['audio']['sample_rate']}"

    # Validate channels
    if metadata['audio']['channels'] not in [1, 2]:
        return False, f"Invalid channels: {metadata['audio']['channels']}"

    return True, "Valid"

# Validate all metadata files
for video_dir in Path("downloads").iterdir():
    if video_dir.is_dir():
        metadata_file = video_dir / f"{video_dir.name}.json"

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            is_valid, message = validate_metadata(metadata)

            if not is_valid:
                print(f"❌ {video_dir.name}: {message}")
            else:
                print(f"✅ {video_dir.name}: {message}")
```

## File Naming Convention

### Video ID Format

YouTube video IDs are:
- 11 characters long
- Alphanumeric + `-` and `_`
- Example: `Jq7llIkbJeA`, `dQw4w9WgXcQ`

### Audio File Extensions

| Extension | Format | Compression | Quality |
|-----------|--------|-------------|---------|
| `.wav` | WAV | None | Lossless ✅ |
| `.flac` | FLAC | Lossless | Lossless ✅ |
| `.m4a` | AAC | Lossy | High |
| `.opus` | Opus | Lossy | High |
| `.mp3` | MP3 | Lossy | Medium |

**Current Default:** `.wav` (uncompressed)

## Troubleshooting

### Problem: Metadata File Not Created

**Check:**
1. Video downloaded successfully?
   ```bash
   ls downloads/{video_id}/
   ```

2. Check logs for errors:
   ```bash
   celery -A tasks worker --loglevel=info
   ```

**Solution:** Ensure `download_video` task completes without errors.

### Problem: Audio File Different Extension

**Reason:** yt-dlp may use different format based on availability.

**Solution:** The metadata JSON records the actual filename:
```python
metadata['audio']['file_name']  # e.g., "Jq7llIkbJeA.wav"
```

### Problem: File Size Too Large

**Solution:** Switch to FLAC for compression:
```python
# In tasks.py line 69
'preferredcodec': 'flac',
```

FLAC provides same quality at ~50-60% file size.

### Problem: Missing Fields in Metadata

**Reason:** YouTube doesn't always provide all fields (like count, description).

**Solution:** Metadata uses `.get()` with defaults:
```python
metadata['like_count']  # May be 0 if unavailable
```

## Summary

✅ **File Organization:**
- Each video: separate folder
- Folder name: video ID
- Contains: audio + metadata JSON

✅ **Metadata Format:**
- Complete video information
- Detailed audio specifications
- Easy to parse and validate

✅ **Audio Requirements Met:**
- Sample rate: 48 kHz (≥16 kHz ✓)
- Channels: Mono (1 channel ✓)
- Format: WAV (uncompressed ✓)
- Filename: Video ID ✓

🎯 **Ready for:**
- ASR calibration
- Audio dataset creation
- TTS/VC training
- Data cleansing
