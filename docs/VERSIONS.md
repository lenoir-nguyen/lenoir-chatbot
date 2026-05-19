# Version History

## v1.0.0 — Basic Chat SPA (2026-05-15)

**Status**: ✅ Complete & Deployed

**Features**:
- Text-based chat interface with real-time messaging
- Language selection (English, French, Vietnamese)
- GPT-4o model integration via OpenAI API
- Client-side message history (persisted in React state only)
- Auto-scroll to latest message
- Typing indicators ("Thinking...") during responses
- Responsive UI with message timestamps

**Files Created**:
- Backend: `main.py`, `config.py`, `routers/chat.py`, `requirements.txt`
- Frontend: `ChatWindow.tsx`, `MessageBubble.tsx`, `LanguageSelector.tsx`, `api.ts`
- Config: `package.json`, `tsconfig.json`, `next.config.js`, `.env.local.example`, `.env.example`

**Tech Stack**:
- Backend: FastAPI, Python 3.11+, OpenAI SDK
- Frontend: Next.js 14, React 18, TypeScript
- Deployment: Vercel (frontend), Railway (backend)

**Testing**: ✅ Local end-to-end working

---

## v2.0.0 — Voice Features (2026-05-19)

**Status**: ✅ Complete & Deployed

**Features**:
- Voice input: Speech-to-text (Whisper STT) via microphone
- Voice output: Text-to-speech (TTS) with per-message speaker button
- Transcription inserts into input field (user can edit before sending)
- Audio playback via speaker icon on assistant messages
- Language-aware TTS (responds in selected language)
- Graceful fallback if audio APIs fail

**New Components**:
- `VoiceButton.tsx` — Microphone recording button with visual feedback
- `backend/routers/voice.py` — Two endpoints: `/voice/transcribe` and `/voice/speak`
- `backend/tests/test_voice.py` — Comprehensive voice endpoint tests (TDD)

**API Changes**:
- New endpoints: `POST /voice/transcribe` (audio → text) and `POST /voice/speak` (text → audio)
- New config: `OPENAI_TTS_VOICE` (default: "nova")
- Frontend API functions: `transcribeAudio()` and `speakText()`

**Tech Stack Additions**:
- MediaRecorder API (native browser, no packages needed)
- OpenAI Whisper model (`whisper-1`)
- OpenAI TTS model (`tts-1`)

**Testing**: 
- Backend unit tests: 4 test cases (transcribe success/missing/empty, speak success/empty/missing)
- Frontend: VoiceButton component with microphone permission handling
- E2E: Mic recording → transcription → input → chat → TTS playback

**Key Design Decisions**:
- TTS is optional (speaker button, not auto-play) — respects user preferences
- Transcription shows in input field — user can verify/edit before sending
- Separate endpoints (not combined) — follows DRY principle
- No session ID persistence in v2 — stays in v4 with database

---

## v3.0.0 — Authentication (Planned)

**Planned Features**:
- Passphrase: "I am Lenoir"
- PIN protection with bcrypt hashing
- Owner vs. Stranger conversation modes
- Session management

---

## v4.0.0 — LangChain & Database (Planned)

**Planned Features**:
- PostgreSQL integration via Railway
- Persistent conversation memory
- LangChain orchestration
- ConversationBufferWindowMemory (last 10 messages for owner, 5 for stranger)
- System prompts with personalization

---

## v5.0.0 — RAG System (Planned)

**Planned Features**:
- pgvector for semantic search
- OpenAI embeddings
- Personal facts knowledge base
- Context-aware responses
- Retrieval-augmented generation

---
