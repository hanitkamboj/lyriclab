# LyricLab - AI-Powered Lyrics Video Creator

> **Non-profit project** - Create beautiful lyric videos like 7clouds automatically.

## Architecture

```
lyriclab/
├── frontend/          # Next.js Dashboard (TypeScript)
│   ├── pages/         # Routes: login, dashboard, projects, chat, settings, trending, bulk, create, project
│   ├── components/    # Layout, UI components
│   ├── lib/           # Firebase config, API client, Zustand store
│   └── styles/        # Tailwind CSS
├── backend/           # FastAPI Python Backend
│   ├── app/
│   │   ├── api/       # REST endpoints
│   │   ├── agents/    # Research, Lyrics, Orchestrator agents
│   │   ├── services/  # Audio, Lyrics, Background, Render, YouTube, Firebase
│   │   └── models/    # Pydantic schemas
│   └── requirements.txt
├── agent/             # Standalone CLI agent
│   ├── crawler/       # YouTube channel crawler
│   ├── processor/     # Audio/video processing utilities
│   └── standalone_agent.py
├── docker-compose.yml # Full stack deployment
└── vercel.json        # Vercel deployment config
```

## Features

### Core
- **7clouds-style lyric videos** - Same style as popular channels
- **Auto research** - Crawls YouTube, Billboard for trending songs
- **Multi-source lyrics** - LRCLib, AZLyrics, any URL
- **Smart backgrounds** - Pexels videos/images, generated gradients, particle effects
- **Preview first** - Quick preview before full render
- **High quality** - 60 FPS, 1080p-4K, high bitrate
- **Timeline verification** - Ensures lyrics match audio duration

### YouTube Publishing
- **OAuth 2.0 integration** - Google sign-in for upload
- **Auto SEO** - Title, description, tags optimization
- **Thumbnail generation** - Auto-created thumbnails
- **Multiple channel support** - Connect multiple YouTube channels
- **Bulk upload** - Process and upload multiple videos

### Agent System
- **Chat interface** - Natural language control
- **Auto mode** - Continuous discover → create → render → upload
- **Bulk processing** - Handle multiple songs at once
- **Style analysis** - Learn from existing lyric videos

### AI Integration
- **Ollama support** - Use your own AI models
- **Cloudflare tunnel** - Connect Kaggle-hosted models
- **Custom model selection** - Choose any Ollama model

## Quick Start

### Prerequisites
```bash
# System dependencies
sudo apt-get update
sudo apt-get install -y ffmpeg python3-pip nodejs npm

# Python packages
pip install -r backend/requirements.txt
pip install yt-dlp

# Node packages
cd frontend && npm install
```

### Run Locally

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Or both at once:
npm run dev
```

### Using Docker
```bash
docker-compose up -d
```

### Standalone Agent (CLI)
```bash
python agent/standalone_agent.py research
python agent/standalone_agent.py create
python agent/standalone_agent.py auto
python agent/standalone_agent.py bulk songs.json
```

## Dashboard Pages

| Route | Description |
|-------|-------------|
| `/` | Login/Signup (Google + Email) |
| `/dashboard` | Stats, quick actions, recent projects |
| `/projects` | All projects with filters |
| `/create` | New project form (4 steps) |
| `/project?id=X` | Detail view with preview, render, upload |
| `/chat` | Agent chat interface |
| `/trending` | Discover trending songs |
| `/bulk` | Bulk processing & auto mode |
| `/settings` | YouTube channels, Ollama config |

## Agent Commands

In the chat interface or CLI, use these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `research` | Find trending songs | `research` |
| `create` | New project | `create title=Hello artist=Adele song_url=https://...` |
| `preview` | Generate preview | `preview project_id=xxx` |
| `render` | Full render | `render project_id=xxx` |
| `upload` | Upload to YouTube | `upload project_id=xxx privacy=public` |
| `bulk` | Batch process | `bulk auto_mode=true` |
| `auto` | Auto mode | `auto` |
| `status` | Check progress | `status` |
| `analyze` | Analyze video style | `analyze video_id=xxx` |
| `help` | Show all commands | `help` |

## Configuration

The system is pre-configured with:
- **Firebase** (Auth, DB, Storage) - sonifall project
- **YouTube Data API v3** - lyriclab-497417 project
- **Pexels API** - For backgrounds
- **GitHub Token** - For repo management

## Deploy to Vercel

```bash
npm i -g vercel
vercel
```

The frontend will be deployed with all API rewrites. Note: Video processing requires the backend with FFmpeg.

## API Endpoints

### Projects
- `GET /api/projects/?user_id=X` - List projects
- `POST /api/projects/` - Create project
- `POST /api/projects/process` - Process audio/lyrics/bg
- `POST /api/projects/preview` - Generate preview
- `POST /api/projects/render` - Full render
- `POST /api/projects/upload` - Upload to YouTube

### Chat
- `POST /api/chat/` - Send command
- `GET /api/chat/history/X` - Get chat history

### Trending
- `GET /api/trending/` - Get trending songs
- `GET /api/trending/discover` - Auto discover

### YouTube
- `GET /api/youtube/auth-url` - OAuth URL
- `POST /api/youtube/connect` - Connect channel
- `GET /api/youtube/channels/X` - List channels

### Ollama
- `POST /api/ollama/chat` - Chat with Ollama model
- `POST /api/ollama/config` - Save config
- `GET /api/ollama/configs/X` - List configs

## License

MIT - Non-profit project for creating lyric videos.
