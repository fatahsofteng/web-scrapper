# YouTube crawler automates audio file downloading (Youtube爬蟲自動化下載音檔)

## 1. Task Introduction:

- Please follow the channel list file to download all the videos in each channel, and record the metadata of the videos, so that we can carry out the subsequent ASR correction and training process.

## **1.1 Task Overview**

 The purpose of this task is to **automate** the process of **capturing audio and metadata of all the videos in batches from multiple YouTube channels** for subsequent **ASR calibration, audio dataset creation, TTS/VC training, and data cleansing**.

 In the end, the system will automatically list all the public videos of the channel according to the channel URL in the "Channel List File":

1.  List all public videos of the channel
2.  Download the audio file of each movie
3.  Record complete metadata
4.  Apply audio formatting specifications
5.  Save files to a clean, traceable folder structure.

## 2. Task **Reference** Steps:

1.  Find a way to download the audio file of a specific movie from youtube (or just download the movie and convert it to just the audio file).
2.  Record the metadata of the movie, if necessary:
    1.  Movie ID, e.g. Jq7llIkbJeA ( https://www.youtube.com/watch?v=Jq7llIkbJeA)
    2.  The channel from which the movie originated from in the channel list file, e.g.: @joeman ( Jq7llIkbJeA from https://www.youtube.com/@joeman)
    3.  Audio file metadata, e.g. Codec, Sample Rate, Bit Rate, Channels, Duration, File Size.
3.  Save the audio file and name it Video ID for easy tracking and management of the audio file, and save the metadata as {Video ID}.json for easy tracking.
4.  Please make sure to follow the below principles for audio file format:
    1.  Try to download uncompressed audio file format (but not mandatory because YT has already compressed it once), such as: WAV, FLAC, etc.
    2.  Sample Rate should be at least 16k.
    3.  If the number of channels is not mono, convert to Mono and save the file (if the multichannel is a separate track with a speaker, then please don't convert to Mono and keep the multichannel format).

### Resources:

1.  11/18 Provided by: v1 Channel List
    
    [創用CC_50個YT頻道.txt](attachment:3ce6d930-dab6-4436-b505-3e9d96508d91:創用CC_50個YT頻道.txt)
    
2.  3rd party API + google official streaming download link demo code:
    
    https://drive.google.com/file/d/1AFsZEdUBo5h48Crm3kfikb6l_tt8Ke5B/view?usp=sharing
    
3.  Calculate the number of channel movies:
    
    [創用CC_50個YT頻道.csv](attachment:27d696d7-c489-42fb-8f6c-cc01021c142e:創用CC_50個YT頻道.csv)
    

## **3. 🎯 Core Tasks**

### **###**

### **3.1 Downloading audio files (Audio Download)**

 ✔ Follow each video URL

 ✔ Prioritize downloads in high quality, uncompressed formats (if provided by the platform)

 ✔ If only compressed audio files are available, download the highest bit rate version

 ✔ Audio file format must be m4a, sample rate = 44kHz

 Select a tool (choose one):

| **Tools** | **Pros** | **DISADVANTAGES** |
| --- | --- | --- |
| **yt-dlp (recommended)** |  Stable, high speed, flexible format selection, cookies support, automatic sound quality optimization |  No official API |
|  YouTube API + yt-dlp |  API for more reliable information |  API quota limit |
|  puppeteer / playwright + yt-dlp |  Crawls cloaked channels |  Most complex |
|  3rd party API + google official streaming download link |  API is more reliable to get information |  To be tested |

### The tool is available for testing:

1.  3rd party API + google official streaming download link:
    
    https://drive.google.com/file/d/1AFsZEdUBo5h48Crm3kfikb6l_tt8Ke5B/view?usp=sharing
    

---

## **3.2 📦 Metadata recording specification (video + audio)**

 One output per movie:

```
{video_id}.json
```

 Contents include:

### **① video metadata (Video Metadata)**

```
{
  "video_id": "Jq7llIkbJeA",
  "channel_url": "https://www.youtube.com/@joeman",
  ...
}
```

### **② audio metadata (Audio Metadata)**

```
{
  "codec": "opus",
  "sample_rate": 48000,
  "bit_rate": 160000,
  "channels": 2,
  "duration_sec": 512.23,
  "file_size": 32_123_442
}
```

---

## **① Video Metadata ② Audio Metadata ① Video Metadata ① Audio Metadata ① Audio Metadata**

## **3.3 Audio Format Requirements**

### **⭕ Compulsory (mandatory)**

1. **Sample Rate == 44 kHz (44k or 48k recommended)**
2. **If the non-speaker is separated from the multi-track, convert all to Mono.**

**Output filename = video ID, e.g.:**

```
Jq7llIkbJeA.m4a
```

### **⭕ not mandatory, but preferred**

- If available in **uncompressed format (WAV) or lossless (FLAC)** → select the highest quality.
- If you can only download Opus/AAC → download the highest bit rate version (but do not download too high quality files, try to **have a Sample Rate < 48 kHz** ).

---

## Select the direction of practice and follow-up:

1.  yt-dlp (@Rispal Gibar & @Fatahillah in progress...)
    
     1.1. Cost calculation:
    
    - One IP can crawl and download 30 audio files . 10857 audio files in total. 362 IPs are needed.
    - How much would it cost to buy IP VAT for three sites?
        - https://decodo.com/proxies/isp-proxies/pricing
            
             (IP will not repeat) **Dedicated:**200*2.5+100*2.6+50*2.7+10*2.9+3*3.33 = **933.99 $USD**
            
            **Pay per IP:**100*0.35*3+50*0.4+10*0.47*2 = **134.4 $USD**
            
        - https://oxylabs.io/pricing/isp-proxies
            
             (IP may repeat) ISP Proxies: 200*1.3+100*1.3+50*1.45+10*1.6*2 = 494.5 $USD
            
             (IP may not be duplicated) Dedicated: contact sales
            
        - https://brightdata.com/products/web-scraper
            - Billing by number of requests Assuming one request per audio file.
            
            (IP may repeat) Pay as you go: 10857/1000*1.5 = 16.2855 $USD(no additional VAT charge for requests, additional charge if over 100GB using monthly fee)
            
    
     1.2 Download rate:
    
    - **yt-dlp**  need to be evaluated in Fatah please!
    
2.  google official streaming URL download method (Hoan test demo code, can provide movie URL for batch auto download audio files)
    - Looks like the official streaming download method for Android VR.
    
     2.1. Cost calculation:
    
    - https://turboscribe.ai/zh-TW/downloader get google official streaming download link need to pay account unlimited use: 20 $USD/month ⇒ free users have IP lock, one day to get a limited number (test about 100)
    
     2.2 Download rate:
    
    - Calculation formula:
        - google official streaming download link: 3 lines about 70 KB/s, 12 lines about 164 KB/s, fluctuating but with a basic speed limit
        - 12-line efficiency about download 12 audio files (total length audio file seconds 2240 seconds)/238 (seconds) = `9.4111 audio file length / 1 second`, the test is about **`6.7532 Duration/s`~**`9.4111 **Duration/s`** between
    - Download a file time:
        - (The length of the audio file varies from channel to channel, this is only a preliminary calculation of the length of the audio file in the three channels) about  `**38.83s`,`20.14s`,`19.83s`,`31.26s`to do the average calculation = 110.06 ÷ 4 = 27.52s**
    - Time to download all audio files from all 50 channels of  ****:
        - **27.52s(assuming each audio file download time) ×** 10857 audio files (number of all movies on 50 channels) = **298784.64s (83 hours == 3.46 days)**