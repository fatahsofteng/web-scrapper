# Cookie Authentication Setup (Local Project)

## 🎉 Breakthrough: Cookie Auth Works!

Testing in Google Colab shows **100% success rate** with cookie authentication:
- ✅ 3/3 videos downloaded successfully
- ✅ 0 bot detection errors
- ✅ 0 forbidden errors
- 💰 **Saves $494-933 USD** (no need for paid IP rotator)

## 📋 Setup Instructions

### Step 1: Export YouTube Cookies

**Chrome (Recommended):**
1. Install extension: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to https://www.youtube.com and **login**
3. Click extension icon → Export
4. Save as `youtube_cookies.txt` in project directory

**Firefox:**
1. Install: [cookies.txt extension](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Go to https://www.youtube.com and **login**
3. Export cookies
4. Save as `youtube_cookies.txt`

**Important:**
- ⚠️ Must be logged in to YouTube when exporting
- ⚠️ Cookies expire every few hours/days (need refresh)
- ⚠️ Keep cookies file secure (contains your session)

---

### Step 2: Configure Environment Variable

Set the path to your cookies file:

**Option A: Export in terminal (temporary)**
```bash
export YOUTUBE_COOKIES_FILE="./youtube_cookies.txt"
```

**Option B: Add to `.env` file (recommended)**
```bash
# Create .env file
echo "YOUTUBE_COOKIES_FILE=./youtube_cookies.txt" >> .env
```

Then load in your shell:
```bash
source .env
```

**Option C: Add to shell profile (permanent)**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export YOUTUBE_COOKIES_FILE="/absolute/path/to/youtube_cookies.txt"' >> ~/.zshrc
source ~/.zshrc
```

---

### Step 3: Verify Setup

Check if cookie file is detected:

```bash
# Start Python
python3

>>> import os
>>> from pathlib import Path
>>> cookie_file = os.environ.get('YOUTUBE_COOKIES_FILE')
>>> print(f"Cookie file: {cookie_file}")
>>> print(f"Exists: {Path(cookie_file).exists() if cookie_file else False}")
```

Should output:
```
Cookie file: ./youtube_cookies.txt
Exists: True
```

---

### Step 4: Test with Single Video

```bash
# Make sure Redis is running
redis-server &

# Start Celery worker
celery -A tasks worker --loglevel=info &

# In Python console
python3
```

```python
from tasks import download_video

# Test single video
result = download_video.delay(
    "https://www.youtube.com/watch?v=VIDEO_ID"
)

# Check result
print(result.get())
```

**Expected output:**
```
Using cookie authentication from: ./youtube_cookies.txt
Downloading https://www.youtube.com/watch?v=...
✅ Downloaded successfully
```

---

### Step 5: Test with Channel

```python
from tasks import scrape_channel_videos

# Test channel scraping
result = scrape_channel_videos.delay(
    "https://www.youtube.com/channel/CHANNEL_ID"
)
```

---

## 🔍 Troubleshooting

### Problem: "Cookies are no longer valid"

**Solution:**
```bash
# 1. Logout from YouTube in browser
# 2. Clear YouTube cookies
# 3. Login again
# 4. Browse a few videos (activate session)
# 5. Export fresh cookies
# 6. Replace youtube_cookies.txt
```

### Problem: "File not found"

**Solution:**
```bash
# Check environment variable
echo $YOUTUBE_COOKIES_FILE

# Check file exists
ls -la youtube_cookies.txt

# Use absolute path
export YOUTUBE_COOKIES_FILE="/full/path/to/youtube_cookies.txt"
```

### Problem: Still getting 403 errors

**Possible causes:**
1. **Cookies expired** → Export fresh cookies
2. **Local IP banned** → Wait 24h or use different network
3. **Cookies not from logged-in session** → Ensure logged in when exporting

**Test with Colab first:**
If local still fails but Colab works → Local IP may be banned
- Try different network (mobile hotspot, VPN, etc.)
- Or use Colab for production

---

## 📊 Comparison: Local vs Colab

| Aspect | Local + Cookies | Colab + Cookies |
|--------|-----------------|-----------------|
| **Cost** | $0 | $0 |
| **Setup** | Medium | Easy |
| **IP Issues** | Possible (if banned) | Less likely |
| **Speed** | Faster (local network) | Slower (Colab limits) |
| **Scalability** | High (own hardware) | Limited (Colab quotas) |
| **Cookie Management** | Manual refresh | Manual refresh |

**Recommendation:**
- **Development/Testing:** Use Colab (proven to work)
- **Production (if local IP clean):** Use local + cookies
- **Production (if local IP banned):** Use Colab or wait 24h

---

## 🔄 Cookie Refresh Strategy

Cookies typically expire every **2-6 hours** (YouTube security measure).

**For Production:**

**Option 1: Manual refresh (simple)**
- Export fresh cookies every 4 hours
- Replace `youtube_cookies.txt`
- Restart celery workers

**Option 2: Automated refresh (advanced)**
- Use browser automation (Selenium/Puppeteer)
- Auto-export cookies every 2 hours
- Requires headless browser setup

**Option 3: Multiple accounts (rotation)**
- Use multiple YouTube accounts
- Rotate cookies from different accounts
- Reduces refresh frequency

---

## 📈 Scale Testing Plan

Before production with 50 channels:

**Phase 1: Small scale (done ✅)**
- 1 channel, 3 videos
- Result: 100% success

**Phase 2: Medium scale (next)**
- 1 channel, 10-20 videos
- Monitor: cookie expiry, success rate

**Phase 3: Multi-channel**
- 3-5 channels, 5 videos each
- Monitor: rate limiting, bans

**Phase 4: Full scale**
- All 50 channels
- Monitor: stability over time

---

## ✅ Success Indicators

Cookie authentication is working if:
- ✅ Log shows: "Using cookie authentication from: ..."
- ✅ No "Sign in to confirm you're not a bot" errors
- ✅ No 403 Forbidden errors
- ✅ Downloads complete successfully
- ✅ .m4a and .json files created

---

## 🎯 Next Steps

1. **Export fresh cookies** → Test locally
2. **If local works** → Proceed with scale testing
3. **If local still fails** → Use Colab for production
4. **Report results** → Share with team

**Goal:** Validate free tier (cookies only) before considering paid IP rotator.

---

## 📝 Notes

- **Security:** Keep `youtube_cookies.txt` in `.gitignore`
- **Privacy:** Don't commit cookies to repository
- **Rotation:** Refresh cookies regularly (every 4-6 hours)
- **Backup plan:** Paid IP rotator if cookies don't scale

**Cost savings if successful:** $494-933 USD (100%)
