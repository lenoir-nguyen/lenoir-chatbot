"""
Chat router for handling conversation endpoints.

This module implements the chat API with support for:
- Multi-language conversations (auto-responds in user's language)
- Conversation history management
- Session tracking with Redis caching for user preferences
- OpenAI GPT-4o integration for intelligent responses

Redis Usage:
- Caches user language preference per session (24h TTL)
- Enables faster retrieval of user preferences on subsequent messages
- Gracefully falls back if Redis is unavailable
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from config import get_settings
from cache import cache_get, cache_set
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ============================================================================
# Data Models
# ============================================================================

class Message(BaseModel):
    """Represents a single message in conversation history."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request payload for /chat/message endpoint."""
    message: str
    language: str = "en"
    history: list[Message] = []
    session_id: str = None


class ChatResponse(BaseModel):
    """Response payload from /chat/message endpoint."""
    content: str
    language: str


# ============================================================================
# Redis Session Management (Reusable Helper)
# ============================================================================

async def get_or_create_session(session_id: str = None, language: str = "en") -> tuple[str, str]:
    """
    Manage user session with Redis caching for preferences.

    This function implements the session management logic:
    1. Generate or use provided session_id (UUID if not provided)
    2. Check Redis for cached session data
    3. Use cached language if available, otherwise use request language
    4. Cache new session for future requests (24h TTL)

    This is extracted as a reusable function to avoid DRY when handling
    sessions in multiple endpoints (currently just /message, but extensible
    for future endpoints like /feedback, /preferences, etc.).

    Args:
        session_id (str, optional): Unique session identifier. If None, generates UUID.
        language (str): Requested language code (e.g., "en", "fr", "vi")

    Returns:
        tuple[str, str]: (session_id, resolved_language)
            - session_id: The session identifier (generated or provided)
            - resolved_language: Language to use (from cache or request)

    Example:
        >>> session_id, language = await get_or_create_session(session_id="user123", language="fr")
        >>> # Next time with same session_id, language will be "fr" from cache
    """
    # Generate session ID if not provided (allows browser sessions to be tracked)
    session_id = session_id or str(uuid.uuid4())

    # Try to retrieve cached session preferences from Redis
    cache_key = f"session:{session_id}"
    cached_session = await cache_get(cache_key)

    # If we found a cached session, use the cached language preference
    if cached_session:
        language = cached_session.get("language", language)
    else:
        # New session: store language preference for 24 hours
        # Next request with same session_id will retrieve this cached preference
        await cache_set(cache_key, {"language": language}, ttl=86400)

    return session_id, language


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Handle chat message requests and return GPT-4o responses.

    Workflow:
    1. Manage user session (with Redis caching)
    2. Build message history with system prompt
    3. Call OpenAI GPT-4o API
    4. Return response in user's preferred language

    Args:
        request (ChatRequest): Contains message, language, history, session_id

    Returns:
        ChatResponse: Contains response content and language used

    Raises:
        HTTPException: 500 status code if API call fails
    """
    try:
        # REDIS USAGE: Get or create session and resolve language preference
        # This checks Redis cache for the user's language setting
        session_id, language = await get_or_create_session(
            session_id=request.session_id,
            language=request.language
        )

        # Build system prompt that instructs GPT-4o to respond in user's language
        system_prompt = f"""You are a friendly and helpful AI assistant.
Always respond in {language}."""

        # Construct message array: [system_prompt, conversation_history, user_message]
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history to provide context for the AI
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message as the latest turn
        messages.append({"role": "user", "content": request.message})

        # Call OpenAI GPT-4o API with conversation context
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,  # Balanced creativity (0=deterministic, 1=random)
            max_tokens=500    # Limit response length
        )

        # Extract response text from API result
        content = response.choices[0].message.content

        # Return response in the same language (from cache or request)
        return ChatResponse(content=content, language=language)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
