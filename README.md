# 🎬 Colab Video Generator - Complete Guide

**AI-powered content-to-video automation tool with Wav2Lip & Video Diffusion**

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Features](#features)
4. [Usage Guide](#usage-guide)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## 🚀 Getting Started

### What is Colab Video Generator?

Colab Video Generator is an **AI-powered automation tool** that converts articles and URLs into professional videos with:

- 🌍 **Multi-language support** (15+ languages)
- 🎤 **Natural Text-to-Speech** (Edge-TTS)
- 🤖 **AI Summarization** (Google Gemini)
- 🎥 **Video Generation** (Stable Video Diffusion)
- 👄 **Lip Sync** (Wav2Lip)
- 📝 **Auto Subtitles**
- ⚡ **GPU Optimized** for Colab T4

### Prerequisites

- ✅ Google Account (for Colab & Drive)
- ✅ Gemini API Key (free from https://makersuite.google.com/app/apikeys)
- ✅ 15+ GB free storage on Google Drive

---

## 📦 Installation

### Step 1: Open Google Colab

Option A - Direct Link:
```
https://colab.research.google.com/github/trankhoa1214/colab-video-generator/blob/main/video_automation_tool.ipynb
```

Option B - Upload Notebook:
1. Go to https://colab.research.google.com
2. Click "Upload" → Select `video_automation_tool.ipynb`

### Step 2: Set Up Gemini API Key

1. Visit https://makersuite.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key
4. In Colab sidebar → Click "🔑 Secrets"
5. Create new secret: `GEMINI_API_KEY` = paste your key

### Step 3: Run Installation Cell

```python
# This will install all dependencies (takes ~3-5 minutes)
!pip install -q torch torchvision torchaudio
!pip install -q trafilatura google-generativeai edge-tts
!pip install -q moviepy opencv-python gradio
# ... (full list in notebook)
```

### Step 4: Verify Setup

```python
# Test Gemini API
import google.generativeai as genai
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("Hello")
print(response.text)  # Should print a response
```

---

## ✨ Features

### 🌐 Multi-Language Support

| Language | TTS | Lip Sync | Status |
|----------|-----|---------|--------|
| Vietnamese | ✅ | ✅ | ⭐ Optimized |
| English | ✅ | ✅ | ⭐ Optimized |
| Chinese (Simplified) | ✅ | ✅ | ✅ |
| Chinese (Traditional) | ✅ | ✅ | ✅ |
| Japanese | ✅ | ✅ | ✅ |
| Korean | ✅ | ✅ | ✅ |
| Spanish | ✅ | ✅ | ✅ |
| French | ✅ | ✅ | ✅ |
| German | ✅ | ✅ | ✅ |
| Russian | ✅ | ✅ | ✅ |
| Arabic | ✅ | ⚠️ | ✅ |
| Portuguese | ✅ | ✅ | ✅ |
| Italian | ✅ | ✅ | ✅ |
| Polish | ✅ | ✅ | ✅ |
| Turkish | ✅ | ✅ | ✅ |

### 🎤 Available Voices

**Vietnamese:**
- Male: `vi-VN-NhanNeural`
- Female: `vi-VN-HoaiMyNeural`

**English:**
- US Female: `en-US-AriaNeural`
- US Male: `en-US-GuyNeural`
- UK Female: `en-GB-SoniaNeural`
- UK Male: `en-GB-RyanNeural`

**Other Languages:** Chinese, Japanese, Korean, Spanish, French, German, etc.

---

## 📖 Usage Guide

### Method 1: Using Gradio Web Interface (Easiest)

```python
# Run notebook cells in order:
# Cell 1-3: Setup & Dependencies
# Cell 4-6: Define functions
# Cell 7: Run Gradio interface
```

Then:
1. Paste URLs (one per line)
2. Select Language
3. Select Voice
4. Click "🚀 Generate Videos"
5. Wait for results

**Expected Time:** 7-18 minutes per URL

### Method 2: Manual Python Script

```python
from video_automation import process_url

# Process single URL
result = process_url(
    url="https://example.com/article",
    language="vi",  # Vietnamese
    voice="vi-VN-NhanNeural",
    output_dir="/content/drive/MyDrive/videos"
)

print(f"✅ Video: {result['output_video']}")
print(f"✅ Metadata: {result['metadata']}")
```

### Method 3: Batch Processing

```python
from video_automation import process_batch_urls

urls = [
    "https://vnexpress.net/...",
    "https://thanhnien.vn/...",
    "https://bbc.com/news/..."
]

results = process_batch_urls(
    urls=urls,
    language="vi",
    voice="vi-VN-NhanNeural",
    output_dir="/content/drive/MyDrive/videos"
)

# Auto-checkpoint: If interrupted, run again to continue from last URL
```

### Method 4: Advanced - Using Wav2Lip

```python
from wav2lip_processor import Wav2LipProcessor

processor = Wav2LipProcessor()

# Apply lip sync to video
video_with_lipsync = processor.process_video_with_lipsync(
    video_path="video.mp4",
    audio_path="audio.mp3",
    output_path="video_lipsync.mp4"
)
```

### Method 5: Advanced - Video Diffusion

```python
from video_diffusion_processor import VideoDiffusionProcessor

processor = VideoDiffusionProcessor()

# Generate video from text prompt
video = processor.generate_video_from_prompt(
    prompt="Professional businessman giving a presentation in modern office",
    output_path="generated_video.mp4",
    use_placeholder=True  # False requires more VRAM
)
```

---

## 🔧 Advanced Features

### Checkpoint Recovery

If your session gets disconnected:

```python
# Simply run batch processing again - it will resume from where it left off
results = process_batch_urls(urls, language="vi")

# Check checkpoint status
checkpoint_file = '/content/drive/MyDrive/colab-video-generator/videos/batch_checkpoint.json'
with open(checkpoint_file) as f:
    checkpoint = json.load(f)
    print(f"Processed: {len(checkpoint['processed'])} URLs")
    print(f"Completed: {checkpoint['completed']}")
    print(f"Failed: {checkpoint['failed']}")
```

### Custom Configuration

Edit `config.json`:

```json
{
  "processing_settings": {
    "max_video_duration_seconds": 600,
    "video_fps": 24,
    "video_resolution": "1080p",
    "audio_sample_rate": 22050,
    "vram_optimization": true
  }
}
```

### VRAM Optimization

```python
# Automatic VRAM management
torch.cuda.empty_cache()  # Clear GPU cache

# Disable Lip Sync if low VRAM (saves 8GB)
result = process_url(
    url="...",
    skip_lipsync=True
)

# Use placeholder images instead of Video Diffusion (saves 24GB)
video_path = processor.generate_video_from_prompt(
    prompt="...",
    use_placeholder=True  # Faster, uses <1GB VRAM
)
```

### Save to Google Drive

```python
# Automatic - videos saved to:
# /My Drive/colab-video-generator/videos/

# Manual upload
from shutil import copy
copy('output_video.mp4', '/content/drive/MyDrive/my_videos/')
```

---

## 🎯 Step-by-Step Workflow

### Example: Convert News Article to Video

```python
# Step 1: Input URL
url = "https://vnexpress.net/tin-tuc-...-12345678.html"
language = "vi"
voice = "vi-VN-NhanNeural"

# Step 2: Scrape Content
# 🔍 Tool extracts article title, text, images

# Step 3: Summarize with Gemini
# 📝 AI creates 3-5 video scenes with scripts

# Step 4: Generate Voice-Over
# 🎤 Text-to-Speech creates audio for each scene

# Step 5: Create Video Frames
# 🎨 Generate visual frames for each scene

# Step 6: Merge & Lip Sync
# 👄 Wav2Lip aligns lip movements with audio

# Step 7: Add Subtitles
# 📄 Auto-generated subtitles overlay

# Step 8: Final Output
# ✅ Complete video saved to Google Drive
```

---

## 🐛 Troubleshooting

### Error: "Out of Memory (OOM)"

```python
# Solution 1: Clear cache
torch.cuda.empty_cache()
import gc
gc.collect()

# Solution 2: Process fewer URLs at once
urls = urls[:5]  # Process only 5 URLs

# Solution 3: Disable Lip Sync
skip_lipsync = True

# Solution 4: Use placeholder images
use_placeholder = True
```

### Error: "API Key Invalid"

```python
# Test API key
import google.generativeai as genai
genai.configure(api_key="YOUR_KEY")
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content("test")  # Should work

# If fails: Get new key from https://makersuite.google.com/app/apikeys
```

### Error: "No faces detected in video"

```python
# Lip Sync requires visible faces
# Solution: Video will proceed without lip sync
# You can disable it to save time:
skip_lipsync = True
```

### Error: "CUDA out of memory on Stable Video Diffusion"

```python
# Video Diffusion requires 24GB VRAM (T4 has 16GB)
# Solution: Use placeholder images instead

from video_diffusion_processor import VideoDiffusionProcessor
processor = VideoDiffusionProcessor()
video = processor.generate_video_from_prompt(
    prompt="...",
    use_placeholder=True  # Use placeholder (saves VRAM)
)
```

### Error: "Connection timeout"

```python
# Colab session disconnected
# Solution: Run batch processing again
# It will resume from checkpoint automatically
```

### Check GPU Status

```python
# Monitor GPU usage
!nvidia-smi

# Check PyTorch setup
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

---

## 📊 Performance Estimates

### Processing Time per URL

| Step | Time | Notes |
|------|------|-------|
| Web Scraping | 5-10s | Depends on page size |
| Summarization | 10-20s | Gemini API |
| Voice-Over | 30-60s | Depends on script length |
| Video Generation | 2-5m | Placeholder: fast, Diffusion: slow |
| Lip Sync | 3-10m | Wav2Lip processing |
| Merging & Subtitles | 1-2m | MoviePy |
| **Total** | **7-18 min** | Per URL |

### GPU Memory Usage

- **Scraping & Summarization:** < 1GB
- **TTS (Edge-TTS):** < 1GB
- **Video Generation (Placeholder):** < 1GB
- **Video Generation (Diffusion):** 24GB (not recommended on T4)
- **Lip Sync (Wav2Lip):** 8GB
- **Total (with Lip Sync):** ~10GB

---

## 🔗 API Reference

### Main Functions

#### `process_url()`

```python
def process_url(
    url: str,
    language: str = 'vi',
    voice: str = None,
    output_dir: str = None,
    skip_lipsync: bool = False
) -> Dict
```

**Returns:**
```python
{
    'status': 'completed',
    'output_video': '/path/to/video.mp4',
    'metadata': '/path/to/metadata.json',
    'steps': {
        'scraping': {...},
        'summary': {...},
        'final': {...}
    }
}
```

#### `process_batch_urls()`

```python
def process_batch_urls(
    urls: List[str],
    language: str = 'vi',
    voice: str = None,
    output_dir: str = None
) -> List[Dict]
```

#### `apply_wav2lip_to_video()`

```python
from wav2lip_processor import apply_wav2lip_to_video

video = apply_wav2lip_to_video(
    video_path="video.mp4",
    audio_path="audio.mp3",
    output_path="output.mp4"
)
```

#### `generate_video_from_text()`

```python
from video_diffusion_processor import generate_video_from_text

video = generate_video_from_text(
    prompt="Description of video",
    output_path="output.mp4",
    use_placeholder=True
)
```

---

## 📁 Output Structure

```
Google Drive/colab-video-generator/
├── videos/
│   ├── final_video_20240613_123456.mp4
│   ├── final_video_with_subs_20240613_123456.mp4
│   ├── metadata_20240613_123456.json
│   ├── voiceover_scene_1.mp3
│   ├── scene_1.mp4
│   └── frames_scene_1/
│       ├── frame_000.png
│       ├── frame_001.png
│       └── ...
├── checkpoints/
│   └── batch_checkpoint.json
└── logs/
    └── processing.log
```

---

## 🔐 Privacy & Security

- ✅ **Your data stays on your Google Drive**
- ✅ **No uploads to external servers** (except Google APIs)
- ✅ **API keys stored securely** in Colab Secrets
- ✅ **Delete videos anytime** from Google Drive

---

## 📞 Support & Resources

- **Gemini API Docs:** https://ai.google.dev/
- **Edge-TTS GitHub:** https://github.com/rany2/edge-tts
- **MoviePy Docs:** https://zulko.github.io/moviepy/
- **Wav2Lip GitHub:** https://github.com/Rudrabha/Wav2Lip
- **Colab Tips:** https://colab.research.google.com/notebooks/basic_features_overview.ipynb

---

## 💡 Pro Tips

1. **Start with Placeholder Images** - Faster, uses less VRAM
2. **Use Checkpoint Recovery** - Never lose progress on batch jobs
3. **Monitor GPU Usage** - Run `!nvidia-smi` to check memory
4. **Process at Night** - Colab is faster when load is lower
5. **Save Locally First** - Download videos before Drive fills up
6. **Test with One URL** - Verify setup before batch processing

---

## 🎓 Learning Resources

- [Gemini AI Prompting Guide](https://ai.google.dev/docs)
- [Text-to-Speech with Edge-TTS](https://github.com/rany2/edge-tts#documentation)
- [Video Processing with MoviePy](https://zulko.github.io/moviepy/getting_started/getting_started.html)
- [Deep Learning on Colab GPU](https://colab.research.google.com/notebooks/gpu.ipynb)

---

## 📝 License

MIT License - Free to use, modify, and distribute

---

## ⭐ If This Helped You

Consider starring the repository! It helps others discover this tool.

**GitHub:** https://github.com/trankhoa1214/colab-video-generator

---

**Happy Video Creating! 🎬✨**

*Last Updated: June 13, 2024*
