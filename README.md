# Lifestylevideos Shorts Factory

Automated YouTube Shorts content creation pipeline for the Lifestylevideos project.

## 🎯 Project Overview

Shorts Factory is a fully autonomous content engine that transforms ideas into engaging, ready-to-publish short-form videos through a 4-phase automated pipeline.

## ✅ Current Progress - Task #1 COMPLETE

### **Task #1: Core Orchestration & Google Sheets Integration** ✅
- **Status:** COMPLETED ✅
- **Google Cloud Project:** `Lifestylevideos` (lifestylevideos-470516)  
- **Service Account:** `lifestyle-videos-service`
- **Dashboard:** [Lifestylevideos Shorts Factory Dashboard](https://docs.google.com/spreadsheets/d/1uAu0yBPzjAvvNn4GjVpnwa3P2wdpF9P69K1-anNqSZU/edit)

#### What's Working:
- ✅ **Python Project Structure** - Complete application framework
- ✅ **Configuration Management** - Secure environment variable handling  
- ✅ **Google Sheets Integration** - Full API integration with dashboard
- ✅ **Logging System** - Colored console + detailed file logging
- ✅ **Main Orchestration** - Pipeline framework with scheduler
- ✅ **Error Handling** - Graceful failure and detailed error messages
- ✅ **Working Directories** - Media processing folder structure

#### Test Results:
```
🎉 All tests passed! Your Google Sheets integration is working!
✅ Google Sheets connection successful!
✅ Dashboard headers created!
✅ Test content added with ID: 1
```

## 📊 Dashboard Schema

The Google Sheets dashboard tracks content through the pipeline with 11 columns:

| Column | Purpose | Example |
|--------|---------|---------|
| ID | Unique identifier | 1, 2, 3... |
| Source | Content origin | Gemini, Reddit |  
| Title/Concept | Content idea | "5 Career Tips for Success" |
| Status | Processing stage | Pending Approval → In Progress → Complete |
| Script | Generated script text | ~160 word script |
| Audio File | Narration file path | /audio/video_001.mp3 |
| Video File | Final video path | /final_videos/video_001.mp4 |
| YouTube URL | Published video link | https://youtu.be/... |
| Error Log | Debug information | Error messages if any |
| Created Date | When idea was added | 2024-08-29 12:00:00 |
| Updated Date | Last modification | 2024-08-29 12:30:00 |

## 🏗️ Project Structure

```
lifestylevideos/
├── shorts_factory/          # Main application ✅
│   ├── src/
│   │   ├── core/           # Configuration management ✅
│   │   ├── integrations/   # Google Sheets API ✅ 
│   │   ├── utils/          # Logging system ✅
│   │   └── main.py         # Main orchestration ✅
│   ├── working_directory/  # Media processing folders ✅
│   ├── config/            
│   │   └── credentials/    # Google service account ✅
│   ├── requirements.txt    # Dependencies ✅
│   ├── setup.py           # Installation script ✅
│   ├── test_sheets.py     # Google Sheets test ✅
│   └── README.md          # Application docs ✅
├── .taskmaster/           # Task management ✅
├── docs/                  # Project documentation ✅
└── memory/               # AI agent memory ✅
```

## 🚀 Next Phase - Task #2

**Next:** Implement Content Ideation Engine (Gemini & Reddit)
- Priority: High
- Complexity: Medium (6/10)
- Dependencies: ✅ Complete (Task #1)

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Google Cloud Project with Sheets API enabled
- Service account credentials

### Installation
```bash
cd shorts_factory
python setup.py
python test_sheets.py
```

### Testing
```bash
python src/main.py test
python src/main.py run-once
```

## 📈 Success Metrics

- **System Health:** >95% successful job completion
- **Output:** Average 5+ videos published per day  
- **Budget:** Monthly API spend <$100
- **Performance:** <15 minutes per video end-to-end

## 🔗 Resources

- **Project Dashboard:** [Google Sheets](https://docs.google.com/spreadsheets/d/1uAu0yBPzjAvvNn4GjVpnwa3P2wdpF9P69K1-anNqSZU/edit)
- **Google Cloud Console:** [Lifestylevideos Project](https://console.cloud.google.com/home/dashboard?project=lifestylevideos-470516)
- **Task Management:** Task-Master CLI

---

**Last Updated:** August 29, 2025  
**Status:** Task #1 Complete ✅ | Ready for Task #2 🚀
