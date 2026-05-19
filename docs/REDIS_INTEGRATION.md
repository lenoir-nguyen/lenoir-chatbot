# Redis Integration Guide

This document explains where and how Redis is used in the Lenoir Chatbot backend.

---

## 🎯 Overview

Redis is used as an **optional optimization layer** for caching user session preferences. The system gracefully falls back if Redis is unavailable.

**Current Usage:** Cache language preference per user session (24h TTL)

---

## 📁 Files Involved

### 1. `cache.py` — Redis Client Wrapper (Reusable)
**Purpose:** Provides a clean interface for Redis operations

**Key Functions:**
- `cache_get(key)` — Retrieve cached data (returns None if miss or error)
- `cache_set(key, value, ttl)` — Store data with expiration
- `cache_delete(key)` — Remove cached data
- `is_redis_available()` — Check if Redis is running

**Design:**
- All errors are caught → app doesn't crash if Redis is down
- Async-compatible but uses sync client (Redis package limitation)
- Serializes/deserializes JSON automatically

```python
# Example Usage (from chat.py):
cached_session = await cache_get(f"session:{session_id}")
if cached_session:
    language = cached_session.get("language", "en")
```

---

### 2. `routers/chat.py` — API Endpoint with Redis Integration

**Redis Usage Location:** `get_or_create_session()` function

```python
async def get_or_create_session(session_id: str = None, language: str = "en") -> tuple[str, str]:
    """
    Session Management Logic:
    1. Generate session_id if not provided (enables browser tracking)
    2. Check Redis cache for this session
    3. Use cached language if found
    4. Cache new session for 24 hours
    5. Return (session_id, resolved_language)
    """
    session_id = session_id or str(uuid.uuid4())
    
    # REDIS READ: Try to get cached preferences
    cached_session = await cache_get(f"session:{session_id}")
    
    if cached_session:
        language = cached_session.get("language", language)
    else:
        # REDIS WRITE: Store new session preferences
        await cache_set(f"session:{session_id}", {"language": language}, ttl=86400)
    
    return session_id, language
```

**Called From:** `chat_message()` endpoint
```python
@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    # REDIS USAGE: Get or create session
    session_id, language = await get_or_create_session(
        session_id=request.session_id,
        language=request.language
    )
    # Rest of logic uses resolved language...
```

**Why This Design:**
- Extracted into reusable function (avoid DRY)
- Easy to extend to multiple endpoints
- Clean separation of concerns

---

### 3. `main.py` — Health Check with Redis Status

**Redis Usage Location:** `health_check()` endpoint

```python
@app.get("/health")
async def health_check():
    # REDIS CHECK: Verify cache layer is accessible
    redis_status = "connected" if is_redis_available() else "disconnected"
    
    return {
        "status": "ok",
        "redis": redis_status
    }
```

**Purpose:** Monitoring endpoint that shows Redis connectivity

---

### 4. `docker-compose.yml` — Redis Service Configuration

**Redis Container Setup:**
```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: lenoir-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes  # Persist data to disk
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]   # Auto-health check
      interval: 10s
```

**Backend Connection:**
```yaml
  backend:
    environment:
      REDIS_URL: redis://redis:6379        # Points to Redis container
    depends_on:
      redis:
        condition: service_healthy          # Wait for Redis to be ready
```

---

## 🔄 Data Flow Example

### User's First Message
```
1. Frontend sends: {"message": "Hi", "language": "fr", "session_id": null}

2. Backend:
   - Generate session_id (e.g., "uuid-123")
   - Check Redis for session:uuid-123 → MISS (not cached yet)
   - Cache new session: {"language": "fr"} with 24h TTL
   
3. Backend uses language="fr" for response

4. Response sent back with language="fr"
```

### User's Second Message (Same Session)
```
1. Frontend sends: {"message": "How are you?", "language": null, "session_id": "uuid-123"}

2. Backend:
   - Check Redis for session:uuid-123 → HIT (cached!)
   - Retrieve language="fr" from cache (super fast)
   - Use language="fr" for response (even though not in request)
   
3. Backend uses language="fr" for response

4. Response sent back with language="fr"
```

---

## 💾 Redis Data Structure

**What Gets Stored:**
```
Key:   "session:{session_id}"
Value: {
  "language": "en" | "fr" | "vi"
}
TTL:   86400 seconds (24 hours)
```

**Example Actual Data:**
```
Key:   "session:550e8400-e29b-41d4-a716-446655440000"
Value: {"language": "fr"}
TTL:   86400
```

**View with Redis CLI:**
```bash
redis-cli
> KEYS session:*
1) "session:550e8400-e29b-41d4-a716-446655440000"
2) "session:abc-123"

> GET session:550e8400-e29b-41d4-a716-446655440000
"{\"language\": \"fr\"}"
```

---

## 🧪 Testing Redis Integration

### 1. Verify Redis is Running
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok", "redis": "connected"}
```

### 2. Test Session Caching
```bash
# First request (cache miss)
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "language": "fr",
    "session_id": "test-user-123",
    "history": []
  }'

# Second request (cache hit) - language comes from cache, not request
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How are you?",
    "language": "en",           # Different language in request
    "session_id": "test-user-123",
    "history": []
  }'
# Response will use "fr" from cache, not "en" from request!
```

### 3. View Redis Data
```bash
# Connect to Redis
redis-cli

# See all session keys
KEYS session:*

# Get specific session
GET session:test-user-123

# Manually delete a session (for testing)
DEL session:test-user-123

# Check total keys stored
DBSIZE
```

---

## 🚀 How to Extend (v5+)

### Add More Cached Fields
```python
# In get_or_create_session(), cache more preferences:
session_data = {
    "language": language,
    "theme": "dark",              # NEW
    "notifications_enabled": True  # NEW
}
await cache_set(cache_key, session_data, ttl=86400)
```

### Cache Search Results
```python
# In future RAG endpoint, cache embeddings:
cache_key = f"embedding:{query}"
embedding = await cache_get(cache_key)

if not embedding:
    embedding = compute_embedding(query)
    await cache_set(cache_key, {"embedding": embedding}, ttl=3600)
```

### Cache Facts Retrieved from Database
```python
# In future v5 RAG:
cache_key = f"facts:{user_id}"
facts = await cache_get(cache_key)

if not facts:
    facts = await db.query_facts(user_id)
    await cache_set(cache_key, facts, ttl=600)
```

---

## ❌ When Redis Fails (Graceful Degradation)

If Redis is **down or unreachable:**

1. **`cache_get()`** returns `None` → Language falls back to request value
2. **`cache_set()`** silently fails → No error, caching just disabled
3. **`is_redis_available()`** returns `False` → Health check shows "disconnected"
4. **App still works** → No session caching, but chat still functions

**Example Fallback:**
```python
# If Redis is down:
cached_session = await cache_get(f"session:{session_id}")
# Returns None (connection error caught)

if cached_session:
    language = cached_session.get("language", language)  # Not executed
else:
    # Uses request language as fallback
    await cache_set(...)  # Fails silently
```

---

## 📊 Performance Impact

| Operation | Time | Impact |
|-----------|------|--------|
| Cache miss (no Redis) | ~100ms | PostgreSQL fallback (future) |
| Cache hit (Redis) | ~1ms | 100x faster |
| OpenAI API call | 500-2000ms | Bottleneck (not cache) |
| **Total response** | 500-2000ms | Cache doesn't change end-to-end much |

**Current Status:** Cache saves ~1ms per request (negligible improvement for v1)
**Future Status:** Cache becomes valuable when v5 adds PostgreSQL queries

---

## 🎓 What You Learned

✅ Basic Redis concepts (key-value store, TTL, persistence)
✅ How to integrate Redis in FastAPI
✅ Graceful error handling (app works even if cache fails)
✅ Session management pattern (reusable for future endpoints)
✅ Docker Compose for multi-service orchestration
✅ Health check endpoints that monitor dependencies

---

## 🔗 Next Steps

- **v2:** Add voice features (Whisper STT + TTS)
- **v4:** Add PostgreSQL + conversation persistence
- **v5:** Enhance cache with facts/embeddings from RAG
- **v6:** Implement cache invalidation strategies

Happy learning! 🚀
