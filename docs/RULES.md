# Lenoir Chatbot Project Rules

**Last Updated:** 2026-05-19
**Version:** 1.0.0+
**Scope:** All development for Lenoir Chatbot
**Reference:** See `../../guidelines/RULES.md` for universal rules

---

## 📋 Overview

This file contains **project-specific rules** that override or extend the universal rules.
All universal rules from `guidelines/RULES.md` apply unless superseded here.

---

## Version-Based Development

### Architecture
Lenoir Chatbot is built incrementally:

| Version | Focus | Database | Memory | Tests |
|---------|-------|----------|--------|-------|
| **v1** | Basic chat (text, multilingual, GPT-4o) | ❌ None | ❌ Client-side state only | ✅ Required |
| **v2** | Voice (Whisper STT + TTS) | ❌ None | ❌ Client-side state only | ✅ Required |
| **v3** | Authentication (passphrase + PIN) | ❌ None | ❌ Client-side state only | ✅ Required |
| **v4** | Conversation persistence (PostgreSQL + LangChain) | ✅ PostgreSQL | ✅ LangChain memory | ✅ Required |
| **v5** | RAG (pgvector, embeddings, personal facts) | ✅ PostgreSQL | ✅ RAG + structured facts | ✅ Required |

### Git Branching for Versions
```bash
# Create version branch
git checkout -b v2/voice-features
git commit -m "feat: add Whisper STT integration"
git push origin v2/voice-features

# When version is ready, merge to main
git checkout main
git merge v2/voice-features
git tag -a v2.0.0 -m "Version 2.0.0 - Voice features"
git push origin main --tags
```

---

## Testing Requirements (CRITICAL)

### Before ANY Push to GitHub:

**1. Unit Tests (Backend):**
```bash
# All new/modified functions must have tests
pytest --cov=backend tests/
# Minimum 85% coverage of changed code
```

**2. Unit Tests (Frontend):**
```bash
# All new/modified components must have tests
npm test -- --coverage
# Minimum 85% coverage of changed code
```

**3. Integration Tests:**
- Backend endpoints tested via HTTP requests
- Frontend components tested with user interactions
- Example: Chat message → API call → Response display

**4. E2E Testing (Manual):**
```bash
docker-compose up
# Test in browser:
# [ ] Send message in English
# [ ] Switch to French, send message
# [ ] Switch to Vietnamese, send message
# [ ] Check API /health returns correct status
# [ ] Verify Docker Desktop shows services running
```

**5. Deployment Verification:**
```bash
# After pushing to GitHub, verify:
# [ ] Railway build succeeds (check build logs)
# [ ] Vercel deploy succeeds (check deploy logs)
# [ ] Live app works end-to-end
# [ ] Health endpoint returns {"status": "ok", "redis": ...}
# [ ] Chat endpoint responds with GPT-4o
```

### Test File Naming
```
backend/
├── tests/
│   ├── test_chat.py
│   ├── test_cache.py
│   └── test_api_integration.py

frontend/
├── __tests__/
│   ├── ChatWindow.test.tsx
│   ├── LanguageSelector.test.tsx
│   └── api.test.ts
```

### NO EXCEPTIONS
- ❌ "I'll test this later"
- ❌ "This is a small change"
- ❌ "The tests will fail but that's okay"
- ❌ "I tested manually, that's enough"

**ALL changes require passing tests before push.**

---

## Documentation Updates

### When Making ANY Change:
Update related documentation:

| Change Type | Update |
|------------|--------|
| New chat endpoint | `docs/PROJECT_DETAILS.md` API section |
| New environment variable | `.env.example` + `docs/SETUP_GUIDE.md` |
| New feature in version | `docs/VERSIONS.md` for that version |
| Architecture change | `docs/IMPLEMENTATION_SUMMARY.md` |
| Code pattern discovered | `guidelines/REUSABLE_SKILLS.md` |
| New rule discovered | This file |
| Backend dependency added | `backend/requirements.txt` |
| Frontend dependency added | `frontend/package.json` |

### Example: Adding New Feature
```
1. Write feature code
2. Write tests (TDD)
3. Update:
   - docs/VERSIONS.md (add to current version)
   - docs/PROJECT_DETAILS.md (if architecture affects it)
   - docs/SETUP_GUIDE.md (if setup changes)
   - docs/IMPLEMENTATION_SUMMARY.md (document new code)
4. Commit: git commit -m "feat: add voice input with tests and docs"
5. Push: git push
```

---

## Code Quality Standards (Project-Specific)

### Lenoir-Specific Comment Standards

**Always Document:**
- Why a tool was chosen (Redis vs alternatives)
- Why a pattern was used (session caching strategy)
- Architecture decisions (client-side v1, server-side v4+)
- Integration points (OpenAI API usage)
- Edge cases (what happens if Redis is down)

**Example:**
```python
async def get_or_create_session(session_id: str = None, language: str = "en"):
    """
    Manage user session with Redis caching.
    
    Design rationale:
    - v1 has no database, so session is ephemeral
    - v4+ will persist to PostgreSQL instead
    - Redis allows fast language preference lookup (1ms vs 100ms DB)
    - Graceful fallback: if Redis down, uses request language
    
    Args:
        session_id: User session identifier (UUID if not provided)
        language: Requested language (en, fr, vi)
    
    Returns:
        Tuple of (session_id, resolved_language)
    """
```

### DRY Principle for Lenoir

**Before Writing Code:**
- [ ] Can this logic be extracted to a reusable function?
- [ ] Is a similar pattern used elsewhere?
- [ ] Should this go in `services/`, `utils/`, or `cache.py`?

**Bad (Repeated 3x):**
```python
# In chat.py
session = await cache_get(f"session:{session_id}")
language = session.get("language") if session else "en"

# In feedback.py (same code)
session = await cache_get(f"session:{session_id}")
language = session.get("language") if session else "en"

# In preferences.py (same code again)
session = await cache_get(f"session:{session_id}")
language = session.get("language") if session else "en"
```

**Good (Reusable function):**
```python
# In routers/utils.py or services/session.py
async def get_user_language(session_id: str) -> str:
    session = await cache_get(f"session:{session_id}")
    return session.get("language", "en") if session else "en"

# Used everywhere
language = await get_user_language(session_id)
```

---

## Docker & Deployment

### Local Development with Docker

**Checkpoint Before Major Work:**
```bash
# Tag stable version
git tag -a v1.0.0-stable -m "Stable checkpoint before v2"
git push origin v1.0.0-stable
```

**Docker Compose Workflow:**
```bash
# Start all services
docker-compose up --build

# If you change requirements.txt or Dockerfile
docker-compose down
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f redis
```

**Never Deploy Without:**
- [ ] Local docker-compose up works
- [ ] All tests pass
- [ ] Manual E2E testing complete
- [ ] No secrets in code
- [ ] REDIS_INTEGRATION.md updated if Redis logic changed
- [ ] docs updated

### Railway Deployment (Backend)
```bash
# After push to GitHub:
1. Check Railway build logs: ✅ Success
2. Check deploy logs: ✅ No errors
3. Visit /health endpoint: ✅ {"status": "ok", "redis": ...}
4. Test /chat/message: ✅ Response from GPT-4o
```

### Vercel Deployment (Frontend)
```bash
# After push to GitHub:
1. Check Vercel build: ✅ No TypeScript errors
2. Check deploy: ✅ Live
3. Visit live URL: ✅ Chat works end-to-end
```

---

## Rule Discovery During Development

### IMPORTANT: Bring Up New Rules Immediately

**During Development, If You Notice:**
- A pattern that should be standardized
- A practice that works really well
- A decision that affects future versions
- A Docker/testing/deployment practice worth documenting
- A new skill/pattern useful for other projects

**Do This:**
1. **PAUSE work**
2. **Discuss with me** (even mid-feature)
3. **Document the decision** once agreed
4. **Update RULES.md** or `guidelines/REUSABLE_SKILLS.md`

**Example Conversations That Should Happen:**
- "We keep querying facts before every chat message. Should we add caching in v5?"
- "The Docker compose health check for Redis is useful. Should this be in guidelines?"
- "I noticed we're handling errors with try-except everywhere. Should we create a decorator?"
- "Testing the language switching works better with a specific pattern. Should this be a reusable test?"

**These will be captured and documented.**

---

## Git Workflow for Lenoir

### Daily Workflow
```bash
# Start of day
git pull origin main

# Create feature branch for today's task
git checkout -b feature/descriptive-name

# During day: commit frequently
git commit -m "feat: partial progress on X"
git commit -m "test: add tests for X"
git commit -m "docs: update docs for X"

# End of day: push branch
git push origin feature/descriptive-name
```

### Before Pushing to Main
```bash
# 1. Sync with latest
git pull origin main

# 2. Run all tests
pytest --cov=backend tests/
npm test -- --coverage

# 3. Manual E2E testing
docker-compose up --build
# Test in browser...
docker-compose down

# 4. Clear commit history if needed
git rebase -i main  # Clean up WIP commits

# 5. Push
git push origin feature/descriptive-name

# 6. Create PR or merge manually
git checkout main
git merge feature/descriptive-name
git push origin main

# 7. Create version tag
git tag -a v1.0.1 -m "Bug fix: description"
git push origin --tags
```

---

## Environment Variables

### Required in `.env` (Backend)
```
OPENAI_API_KEY=sk-proj-...
DEBUG=false
FRONTEND_URL=https://lenoir-chatbot.vercel.app
REDIS_URL=redis://redis:6379
```

### Required in `.env.local` (Frontend)
```
NEXT_PUBLIC_API_URL=https://lenoir-chatbot-production.up.railway.app
NEXT_PUBLIC_FRONTEND_URL=https://lenoir-chatbot.vercel.app
```

### Railway Environment Variables
```
OPENAI_API_KEY=sk-proj-...
DEBUG=false
FRONTEND_URL=https://lenoir-chatbot.vercel.app
REDIS_URL=redis://internal-redis:6379 (or managed Redis)
```

### Vercel Environment Variables
```
NEXT_PUBLIC_API_URL=https://lenoir-chatbot-production.up.railway.app
```

**Never:**
- ❌ Log environment variables
- ❌ Commit .env files
- ❌ Expose API keys in frontend
- ❌ Use API keys in client-side code

---

## Version Checklist

### Before Releasing Version (v1, v2, v3, etc.)

- [ ] All tests passing (unit + integration + E2E)
- [ ] Manual testing complete (all features work)
- [ ] Code reviewed for quality
- [ ] All docs updated:
  - [ ] VERSIONS.md with version info
  - [ ] SETUP_GUIDE.md if setup changed
  - [ ] PROJECT_DETAILS.md if tech stack changed
  - [ ] IMPLEMENTATION_SUMMARY.md if code structure changed
- [ ] No secrets in code
- [ ] Docker compose works locally
- [ ] Deployed to Railway (backend) + Vercel (frontend)
- [ ] Live endpoints tested
- [ ] Health check returns correct status
- [ ] Chat works end-to-end
- [ ] Git tag created: `git tag -a vX.Y.Z -m "Version X.Y.Z description"`
- [ ] Tag pushed: `git push origin vX.Y.Z`

---

## Summary for Lenoir

✅ **Test before push** (unit + integration + E2E + manual)
✅ **Update docs** whenever you change code
✅ **Use version branches** (v1, v2, v3)
✅ **Tag releases** (v1.0.0, v2.0.0)
✅ **Discover rules** during development and document them
✅ **Keep code DRY** and reusable
✅ **Comment the "why"** not the "what"
✅ **Follow git workflow** (pull → branch → test → push)
✅ **Never push untested code**
✅ **Bring up new patterns** and discuss

Ready to start v2? 🚀
