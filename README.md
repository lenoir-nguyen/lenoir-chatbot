# Lenoir Chatbot

A multilingual AI-powered chatbot built with Next.js, FastAPI, and OpenAI's GPT-4o. Supports English, French, and Vietnamese with real-time responses.

**Live Demo:** [https://lenoir-chatbot.vercel.app](https://lenoir-chatbot.vercel.app)

## Quick Start

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- OpenAI API key

### Local Development

**Backend (FastAPI):**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
uvicorn main:app --reload
```

**Frontend (Next.js):**
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local and add NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:3000` and start chatting.

## Documentation

- **[VERSIONS.md](docs/VERSIONS.md)** — Release notes for each version
- **[SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** — Detailed setup instructions
- **[PROJECT_DETAILS.md](docs/PROJECT_DETAILS.md)** — Tech stack and architecture
- **[IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** — How the app works
- **[PROMPT.md](docs/PROMPT.md)** — Original project prompt
- **[REUSABLE_SKILLS.md](docs/REUSABLE_SKILLS.md)** — Reusable patterns and best practices

## Project Structure

```
lenoir-chatbot/
├── frontend/          # Next.js 14 application
├── backend/           # FastAPI application
├── docs/              # Documentation
└── README.md          # This file
```

## Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python 3.11, Uvicorn
- **API:** OpenAI GPT-4o
- **Deployment:** Vercel (frontend), Railway (backend)

## Features (v1)

- ✅ Real-time chat with GPT-4o
- ✅ Multilingual support (English, French, Vietnamese)
- ✅ Language switching mid-conversation
- ✅ Conversation history
- ✅ Responsive design

## License

MIT
