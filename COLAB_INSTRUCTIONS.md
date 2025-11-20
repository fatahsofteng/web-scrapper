# Google Colab Testing Instructions

## Quick Start

1. **Open the notebook in Google Colab:**
   - Go to https://colab.research.google.com/
   - Click "File" → "Upload notebook"
   - Upload `youtube_audio_crawler_colab.ipynb` from this repository

   OR

   - Use this direct link (if repository is public):
   ```
   https://colab.research.google.com/github/fatahsofteng/web-scrapper/blob/claude/youtube-audio-crawler-016dbwPE9fcnRDVWZydnZ3PZ/youtube_audio_crawler_colab.ipynb
   ```

2. **Run the notebook:**
   - Click "Runtime" → "Run all"
   - Or run cells one by one with Shift+Enter

3. **Configure channels (Step 4):**
   - Edit the `CHANNELS` list with your YouTube channel URLs
   - Set `MAX_VIDEOS_PER_CHANNEL` (default: 5 for testing)

4. **Monitor progress:**
   - Watch the output for download status
   - Check statistics at the end

5. **Download files:**
   - Click folder icon 📁 in left sidebar
   - Navigate to `downloads/` folder
   - Right-click files → Download
   - Or run Step 7 to create a ZIP file

## Why Google Colab?

- **Different IP address**: Colab uses Google's infrastructure, potentially avoiding 403 bans
- **No local setup**: No need for Python, FFmpeg, or dependencies
- **Easy testing**: Quick to test without infrastructure setup
- **Free compute**: No cost for testing

## Testing Configuration

The notebook is configured with conservative rate limiting:
- 15 seconds sleep between videos
- 10-20 seconds random delay before each download
- 200KB/s download speed limit
- Maximum 5 videos per channel (for initial testing)

## Expected Results

If successful:
- ✅ Downloads will complete with .m4a and .json files
- ✅ Statistics will show success rate > 0%

If YouTube still blocks:
- ❌ 403 Forbidden errors will appear
- ❌ Success rate = 0%

## Output Format

Each video creates a folder structure:
```
downloads/
  └─ {video_id}/
      ├─ {video_id}.m4a     # Audio file (44kHz, mono, M4A)
      └─ {video_id}.json    # Metadata
```

## Audio Specifications

- **Format**: M4A (AAC codec)
- **Sample Rate**: 44000 Hz (exact)
- **Channels**: Mono (1 channel)
- **Bitrate**: 192 kbps

## Troubleshooting

**If you still get 403 errors:**
- YouTube may be blocking Colab IPs as well
- Try reducing `MAX_VIDEOS_PER_CHANNEL` to 1-2
- Try increasing sleep times
- May still require paid IP rotator solution

**If FFmpeg errors:**
- FFmpeg is pre-installed in Colab
- Should work automatically
- Check the output of Step 1 for confirmation

## Report Results to Team

After testing, share:
1. Success rate (from Step 5 final statistics)
2. Number of 403 errors
3. Any successful downloads
4. Screenshot of final statistics

This will help determine if Colab is a viable alternative or if paid IP rotator is still needed.
