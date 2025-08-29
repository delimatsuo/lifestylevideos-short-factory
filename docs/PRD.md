<context>
# Overview  
"Shorts Factory" is an automated system designed to solve the problem of manual, time-consuming short-form video content creation for platforms like YouTube Shorts. The system transforms ideas into engaging, ready-to-publish videos through a fully autonomous content engine, enabling rapid scaling of multiple content channels. It addresses the challenge of consistently producing high-volume content needed to engage social media algorithms while maintaining budgetary control and operational efficiency.

# Core Features  
## Automated Content Ideation
- **What it does:** Generates 10-20 daily content ideas from Gemini API (Career/Self-Help/Management topics) and Reddit API (trending stories from specific subreddits)
- **Why it's important:** Ensures continuous supply of fresh content ideas without manual brainstorming
- **How it works:** Python script runs on daily schedule, populates Google Sheets dashboard with new ideas marked as "Pending Approval"

## Human-in-the-Loop Approval System
- **What it does:** Provides Google Sheets dashboard for manual review and approval of AI-generated ideas
- **Why it's important:** Maintains content quality control while minimizing operator effort
- **How it works:** Channel operator reviews ideas and updates status to "Approved" to trigger video creation pipeline

## Automated Script Generation & Narration
- **What it does:** Converts approved ideas into ~160-word scripts optimized for shorts format, then generates natural-sounding MP3 narration
- **Why it's important:** Eliminates manual scriptwriting and voice recording while maintaining professional quality
- **How it works:** Gemini API generates scripts, ElevenLabs API creates MP3 audio files

## Intelligent Video Assembly
- **What it does:** Automatically sources and combines visual content with narration and synchronized captions
- **Why it's important:** Removes manual video editing bottleneck while ensuring professional presentation
- **How it works:** Uses Pexels API for stock videos (niche content) or pre-downloaded loops (Reddit stories), FFmpeg for compilation, caption burning, and 9:16 aspect ratio rendering

## Automated YouTube Distribution
- **What it does:** Generates optimized metadata and uploads finished videos directly to YouTube
- **Why it's important:** Completes the automation pipeline from idea to published content
- **How it works:** Gemini API generates titles/descriptions/tags, YouTube Data API v3 handles upload and publishing

# User Experience  
## User Personas
- **Channel Operator:** Content creator focused on scaling YouTube presence, values time efficiency and consistent output over manual creative control
- **System Administrator:** Technical user responsible for system maintenance, API key management, and troubleshooting

## Key User Flows
### Daily Content Management Flow:
1. Operator receives notification of new ideas in Google Sheets
2. Reviews generated ideas (estimated 10-15 minutes daily)
3. Approves desired content by changing cell status
4. System automatically processes approved content throughout the day
5. Operator monitors completion status and published video URLs

### System Monitoring Flow:
1. Check daily output metrics (target: 5+ videos/day)
2. Review error logs for failed processes
3. Monitor API cost dashboard (budget: <$100/month)
4. Verify video upload success and metadata accuracy

## UI/UX Considerations
- Google Sheets interface provides familiar, accessible dashboard
- Clear status indicators: Pending Approval → Approved → In Progress → Complete/Failed
- Error messages logged directly in spreadsheet for easy troubleshooting
- Minimal learning curve leveraging existing Google Sheets expertise
</context>

<PRD>
# Technical Architecture  
## System Components
- **Orchestration Layer:** Python 3.x application with daily scheduled execution
- **Content Management:** Google Sheets API v4 integration for dashboard and status tracking
- **AI Services Integration:** Google Gemini 2.5 Pro for content generation, ElevenLabs API for text-to-speech
- **Media Processing:** FFmpeg command-line tool for video assembly, caption burning, and format optimization
- **Content Sourcing:** Reddit API for trending stories, Pexels API for stock video content
- **Distribution:** YouTube Data API v3 for automated upload and publishing

## Data Models
### Google Sheets Schema:
- **ID:** Unique identifier for each content item
- **Source:** Content category (Career/Self-Help/Management/Reddit)
- **Title/Concept:** Generated idea or Reddit post title
- **Status:** Pending Approval → Approved → In Progress → Complete/Failed
- **Script:** Generated 160-word script content
- **Audio_File:** Local path to generated MP3 narration
- **Video_File:** Local path to final rendered MP4
- **YouTube_URL:** Published video link
- **Error_Log:** Detailed error messages for failed processes
- **Created_Date:** Timestamp for tracking and analytics

### File System Structure:
```
/working_directory/
  ├── audio/ (MP3 narration files)
  ├── video_clips/ (downloaded stock videos)
  ├── final_videos/ (rendered MP4 outputs)
  ├── background_loops/ (pre-downloaded Reddit story backgrounds)
  └── logs/ (system execution logs)
```

## APIs and Integrations
| Service | Purpose | Endpoint | Rate Limits |
|---------|---------|----------|-------------|
| Google Gemini 2.5 Pro | Content ideation, script generation, metadata creation | generateContent | 60 requests/minute |
| Google Sheets API v4 | Dashboard management, status tracking | spreadsheets.values.get/.update | 300 requests/100 seconds |
| ElevenLabs API | Text-to-speech narration | v1/text-to-speech | Varies by plan |
| Reddit API | Trending story sourcing | /r/{subreddit}/hot | 60 requests/minute |
| Pexels API | Stock video sourcing | v1/videos/search | 200 requests/hour |
| YouTube Data API v3 | Video upload and publishing | videos.insert | 10,000 units/day |

## Infrastructure Requirements
- **Compute:** Single server/VPS capable of running Python applications and FFmpeg processing
- **Storage:** 50GB+ for temporary media file storage (auto-cleanup after upload)
- **Network:** Stable internet connection for API calls and video uploads
- **Security:** Environment variable management for API keys, no hard-coded credentials
- **Monitoring:** Logging system for process tracking and error debugging

# Development Roadmap  
## Phase 1: Core Pipeline Foundation (MVP)
### Content Management System
- Implement Google Sheets API integration for dashboard creation
- Build basic status tracking and workflow management
- Create error logging and manual override capabilities

### Content Generation Engine
- Integrate Gemini API for ideation and script generation
- Implement Reddit API for story sourcing
- Build approval workflow with manual gates

### Basic Audio/Video Processing
- Integrate ElevenLabs API for narration generation
- Implement basic FFmpeg video assembly pipeline
- Create simple caption generation and burning system

## Phase 2: Advanced Media Processing
### Intelligent Visual Content
- Implement Pexels API integration with keyword extraction
- Build automated video selection and downloading system
- Create background video management for Reddit stories

### Professional Video Assembly
- Advanced FFmpeg scripting for seamless video stitching
- Synchronized caption timing and styling
- 9:16 aspect ratio optimization and quality control

### Automated Distribution
- YouTube Data API integration for upload automation
- Metadata generation and SEO optimization
- Publishing workflow with error handling

## Phase 3: Optimization and Scaling
### Performance Enhancements
- Parallel processing for multiple video creation
- Caching system for frequently used assets
- Optimized file management and cleanup

### Advanced Features
- Analytics integration for performance tracking
- Content performance feedback loop
- Multi-channel support and management

### Monitoring and Maintenance
- Comprehensive logging and alerting system
- Cost tracking and budget management
- Automated health checks and recovery

# Logical Dependency Chain
## Foundation Layer (Build First)
1. **Environment Setup:** Python environment, API key management, basic configuration
2. **Google Sheets Integration:** Dashboard creation, read/write operations, status tracking
3. **Basic Orchestration:** Daily scheduling, process management, error handling framework

## Content Generation Layer (Core Functionality)
4. **Content Ideation:** Gemini API integration for idea generation
5. **Reddit Integration:** API setup, subreddit monitoring, content extraction
6. **Script Generation:** Gemini-powered script creation with format optimization
7. **Approval Workflow:** Manual review system, status management

## Media Processing Layer (Getting to Working Frontend)
8. **Text-to-Speech:** ElevenLabs integration, audio file management
9. **Basic Video Assembly:** Simple FFmpeg operations, file handling
10. **Caption System:** Text extraction, timing, basic styling

## Advanced Assembly Layer (Building Upon Foundation)  
11. **Visual Content Sourcing:** Pexels API, keyword extraction, video downloading
12. **Advanced Video Processing:** Complex FFmpeg operations, quality optimization
13. **Professional Captions:** Advanced styling, synchronization, accessibility

## Distribution Layer (Completing the Pipeline)
14. **YouTube Integration:** API setup, authentication, basic upload
15. **Metadata Generation:** SEO-optimized titles, descriptions, tags
16. **Publishing Automation:** Scheduled releases, error recovery

## Optimization Layer (Iterative Improvements)
17. **Performance Monitoring:** Metrics collection, cost tracking
18. **Error Recovery:** Automated retry logic, failure notifications
19. **Scaling Features:** Multi-threading, batch processing, resource optimization

# Risks and Mitigations  
## Technical Challenges
### Risk: API Rate Limiting and Costs
- **Mitigation:** Implement intelligent request queuing, cost monitoring dashboard, fallback strategies for service failures
- **Contingency:** Manual override capabilities, alternative API providers

### Risk: Video Processing Reliability
- **Mitigation:** Robust error handling, file validation, automated cleanup processes
- **Contingency:** Manual processing workflow, video quality verification systems

### Risk: YouTube API Changes/Restrictions
- **Mitigation:** Stay updated with API documentation, implement flexible authentication, maintain API usage within limits
- **Contingency:** Alternative distribution methods, manual upload fallback

## MVP Scope and Build Strategy
### Risk: Over-engineering Initial Version
- **Mitigation:** Focus on core pipeline functionality first, prioritize end-to-end workflow over advanced features
- **MVP Focus:** Single content type, basic video assembly, manual approval gates

### Risk: Complex Dependencies
- **Mitigation:** Build modular components that can be tested independently, implement graceful degradation
- **Strategy:** Start with simplest video types (static background + narration), add complexity incrementally

## Resource Constraints
### Risk: Budget Overruns
- **Mitigation:** Implement real-time cost tracking, set API usage limits, optimize request efficiency
- **Target:** <$100/month operational costs with monitoring alerts at 75% threshold

### Risk: Processing Time Bottlenecks  
- **Mitigation:** Optimize FFmpeg operations, implement parallel processing where possible, cache frequently used assets
- **Target:** <15 minutes per video end-to-end processing time

### Risk: Content Quality Consistency
- **Mitigation:** Implement quality checks at each pipeline stage, maintain human oversight for initial rollout
- **Strategy:** Gradual automation increase as quality metrics prove reliable

# Appendix  
## Research Findings
### Content Performance Analysis
- Short-form video (60-90 seconds) shows highest engagement rates
- Captions increase retention by 40% across demographics
- Consistent posting schedule (5+ videos/day) significantly impacts algorithm preference
- Career/Self-help content averages 2.3x higher engagement than general entertainment

### Technical Feasibility Study
- FFmpeg processing time: ~3-5 minutes per video on standard hardware
- ElevenLabs API quality assessment: 95% natural-sounding narration
- YouTube API reliability: 99.2% successful upload rate with proper authentication
- Google Sheets API performance: Sufficient for <100 concurrent operations

## Technical Specifications
### Video Output Requirements
- **Resolution:** 1080x1920 (9:16 aspect ratio)
- **Frame Rate:** 30fps minimum for smooth playback
- **Audio Quality:** 44.1kHz, 16-bit minimum for clear narration
- **File Format:** MP4 with H.264 encoding for YouTube optimization
- **Caption Format:** Burned-in subtitles with high contrast styling

### System Performance Targets
- **Daily Output:** 5+ videos minimum, 20+ videos optimal
- **Processing Time:** <15 minutes per video end-to-end
- **Success Rate:** >95% completion without manual intervention  
- **Cost Efficiency:** <$20 per 100 videos produced
- **Uptime:** 99% availability during operating hours

### API Integration Details
- **Authentication:** OAuth 2.0 for Google services, API keys for third-party services
- **Error Handling:** Exponential backoff for rate limiting, circuit breaker for service failures
- **Data Validation:** Schema validation for all API responses, file integrity checks
- **Logging:** Comprehensive audit trail for debugging and performance optimization
</PRD>
