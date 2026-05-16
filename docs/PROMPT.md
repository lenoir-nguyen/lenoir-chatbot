I want to build a multilingual AI chatbot SPA that supports English, French, and Vietnamese conversations. It should use GPT-4o on the backend and be built with Next.js 14 for the frontend and FastAPI for the backend. Both should be deployed to Vercel and Railway with auto-deploy on every push to main.

I'm planning to roll this out in 5 versions:

**v1** (Done): Start with basic text chat. Add a language selector so users can pick between English, French, or Vietnamese. Keep all message history on the client side for now—no database yet.

**v2** (Planned): Add voice capabilities. Users should be able to input voice using Whisper and hear responses back as speech with TTS.

**v3** (Planned): Add authentication with a passphrase and PIN. Also implement different modes—owner mode vs stranger mode—so the chatbot can behave differently depending on who's talking.

**v4** (Planned): Move conversation memory to a real database using PostgreSQL. Integrate LangChain to handle conversation orchestration and memory persistence.

**v5** (Planned): Build a RAG system on top. Use pgvector for embeddings and let the chatbot learn personal facts about the user for more personalized responses.
