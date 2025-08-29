# Shorts Factory v1.0

Automated YouTube Shorts content creation pipeline that transforms ideas into engaging, ready-to-publish videos.

## 🎯 Overview

Shorts Factory is a fully autonomous content engine that:
- Sources content ideas from Gemini AI and Reddit
- Generates optimized scripts for short-form videos  
- Creates natural-sounding narration using ElevenLabs
- Assembles videos with stock footage and synchronized captions
- Publishes directly to YouTube with optimized metadata

## 🏗️ Architecture

```
shorts_factory/
├── src/
│   ├── core/           # Core configuration and utilities
│   ├── integrations/   # External API integrations
│   └── utils/          # Utility functions
├── working_directory/  # Temporary files and media
├── config/            # Configuration files
└── tests/             # Unit tests
```

## 🚀 Quick Start

### 1. Installation

```bash
cd shorts_factory
python setup.py
```

### 2. Configuration

Edit the `.env` file with your API keys:

```bash
# Required API Keys
GOOGLE_SHEETS_API_KEY=your_key_here
GOOGLE_GEMINI_API_KEY=your_key_here  
ELEVENLABS_API_KEY=your_key_here
YOUTUBE_API_KEY=your_key_here
# ... and more
```

### 3. Test the System

```bash
python src/main.py test
```

### 4. Run the Pipeline

```bash
# Run once
python src/main.py run-once

# Start scheduler (daily execution)
python src/main.py schedule
```

## 📊 Dashboard Schema

The Google Sheets dashboard tracks content through the pipeline:

| Column | Purpose | Example |
|--------|---------|---------|
| ID | Unique identifier | 1, 2, 3... |
| Source | Content origin | Gemini, Reddit |  
| Title/Concept | Content idea | "5 Career Tips for Success" |
| Status | Processing stage | Pending Approval, In Progress, Complete |
| Script | Generated script text | ~160 word script |
| Audio File | Narration file path | /audio/video_001.mp3 |
| Video File | Final video path | /final_videos/video_001.mp4 |
| YouTube URL | Published video link | https://youtu.be/... |
| Error Log | Debug information | Error messages if any |
| Created Date | When idea was added | 2024-08-29 12:00:00 |
| Updated Date | Last modification | 2024-08-29 12:30:00 |

## 🔄 Content Pipeline

### Phase 1: Ideation
- Gemini AI generates career/self-help topics
- Reddit API pulls trending stories
- Ideas populate Google Sheets as "Pending Approval"

### Phase 2: Approval & Processing  
- Manual review and approval via Google Sheets
- Status change to "Approved" triggers processing
- Scripts generated via Gemini API
- Audio created via ElevenLabs API

### Phase 3: Video Assembly
- Stock footage sourced from Pexels API
- FFmpeg assembles video with narration
- Synchronized captions burned onto video
- 9:16 aspect ratio output (1080x1920)

### Phase 4: Distribution
- YouTube metadata generated via Gemini
- Automated upload via YouTube Data API v3
- Final URL and status updated in dashboard

## 🛠️ Commands

```bash
# Test all functionality
python src/main.py test

# Run pipeline once  
python src/main.py run-once

# Start scheduled daily execution
python src/main.py schedule
```

## 📝 Requirements

- Python 3.8+
- Google Sheets API access
- Google Gemini API key
- ElevenLabs API key
- YouTube Data API v3 access
- Pexels API key (optional)
- Reddit API credentials (optional)
- FFmpeg installed on system

## 🎛️ Configuration

Key settings in `.env`:

```bash
# Execution schedule
DAILY_EXECUTION_TIME=09:00

# Cost management  
MAX_API_COST_PER_MONTH=100.0

# Logging
LOG_LEVEL=INFO

# Working directory
WORKING_DIRECTORY=./working_directory
```

## 📈 Success Metrics

- **System Health:** >95% successful job completion
- **Output:** Average 5+ videos published per day  
- **Budget:** Monthly API spend <$100
- **Performance:** <15 minutes per video end-to-end

## 🔧 Troubleshooting

### Common Issues

1. **API Authentication Errors**
   - Verify all API keys in `.env` file
   - Check Google credentials file path
   - Ensure OAuth consent screen is configured

2. **Google Sheets Access**
   - Verify spreadsheet ID is correct
   - Check sharing permissions on spreadsheet
   - Ensure service account has edit access

3. **FFmpeg Not Found**
   - Install FFmpeg: `brew install ffmpeg` (macOS)
   - Verify installation: `ffmpeg -version`

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python src/main.py test
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Support

For issues and questions, check the logs in `working_directory/logs/` or run with DEBUG logging enabled.
