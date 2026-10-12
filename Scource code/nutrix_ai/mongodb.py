"""
MongoDB connection and helpers for Nutrix AI.

Uses the `motor` async driver for non-blocking I/O with FastAPI.
All collections are indexed by the Supabase user_id (UUID string).
"""

import os
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Connection singleton
# ---------------------------------------------------------------------------

_client: AsyncIOMotorClient | None = None
_db = None


def get_mongo_client() -> AsyncIOMotorClient:
    """Return the shared Motor client, creating it on first call."""
    global _client
    if _client is None:
        import certifi
        uri = os.environ.get("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI environment variable is not set")
        _client = AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
    return _client


def get_mongo_db():
    """Return the default database handle."""
    global _db
    if _db is None:
        _db = get_mongo_client()["nutrix_ai"]
    return _db


async def close_mongo():
    """Gracefully close the Motor client."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None


# ---------------------------------------------------------------------------
# Index creation (called once at startup)
# ---------------------------------------------------------------------------

async def ensure_indexes():
    """Create compound indexes for fast per-user queries."""
    db = get_mongo_db()

    # chat_messages: fast retrieval of a user's conversation history
    await db.chat_messages.create_index(
        [("user_id", 1), ("session_id", 1), ("created_at", -1)],
        name="idx_chat_user_session_time",
    )

    # ingredient_scans: fast retrieval of a user's scan history
    await db.ingredient_scans.create_index(
        [("user_id", 1), ("created_at", -1)],
        name="idx_scans_user_time",
    )

    # diet_planner_inputs: fast retrieval of a user's diet plan inputs
    await db.diet_planner_inputs.create_index(
        [("user_id", 1), ("created_at", -1)],
        name="idx_diet_user_time",
    )

    logger.info("MongoDB indexes ensured")


# ---------------------------------------------------------------------------
# Helper functions – Chat Messages
# ---------------------------------------------------------------------------

async def save_chat_message(
    user_id: str,
    role: str,
    content: str,
    session_id: str | None = None,
):
    """Insert a single chat message (user or AI)."""
    db = get_mongo_db()
    doc = {
        "user_id": user_id,
        "session_id": session_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.chat_messages.insert_one(doc)
    return str(result.inserted_id)


async def get_chat_history(
    user_id: str,
    session_id: str | None = None,
    limit: int = 50,
    skip: int = 0,
):
    """Return recent chat messages for a user, newest first."""
    db = get_mongo_db()
    query: dict = {"user_id": user_id}
    if session_id:
        query["session_id"] = session_id
    cursor = (
        db.chat_messages.find(query, {"_id": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    messages = await cursor.to_list(length=limit)
    # Return in chronological order for display
    messages.reverse()
    return messages


async def delete_chat_history(user_id: str, session_id: str | None = None):
    """Delete all chat messages for a user (optionally scoped to a session)."""
    db = get_mongo_db()
    query: dict = {"user_id": user_id}
    if session_id:
        query["session_id"] = session_id
    result = await db.chat_messages.delete_many(query)
    return result.deleted_count


# ---------------------------------------------------------------------------
# Helper functions – Ingredient Scans
# ---------------------------------------------------------------------------

async def save_ingredient_scan(
    user_id: str,
    input_type: str,
    input_reference: str,
    ai_result: dict,
):
    """Save an ingredient-scan result to MongoDB."""
    db = get_mongo_db()
    doc = {
        "user_id": user_id,
        "input_type": input_type,
        "input_reference": input_reference,
        "ai_result": ai_result,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.ingredient_scans.insert_one(doc)
    return str(result.inserted_id)


async def get_scan_history(user_id: str, limit: int = 20, skip: int = 0):
    """Return recent ingredient scans for a user, newest first."""
    db = get_mongo_db()
    cursor = (
        db.ingredient_scans.find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)


async def delete_scan_history(user_id: str):
    """Delete all ingredient scan records for a user."""
    db = get_mongo_db()
    result = await db.ingredient_scans.delete_many({"user_id": user_id})
    return result.deleted_count


# ---------------------------------------------------------------------------
# Helper functions – Diet Planner Inputs
# ---------------------------------------------------------------------------

async def save_diet_planner_input(
    user_id: str,
    age: int,
    height: float,
    weight: float,
    goal: str,
    diet_type: str,
    chroma_doc_id: str | None = None,
):
    """Save the user's diet-plan input parameters to MongoDB."""
    db = get_mongo_db()
    doc = {
        "user_id": user_id,
        "age": age,
        "height": height,
        "weight": weight,
        "goal": goal,
        "diet_type": diet_type,
        "chroma_doc_id": chroma_doc_id,  # link back to the ChromaDB entry
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.diet_planner_inputs.insert_one(doc)
    return str(result.inserted_id)


async def get_diet_planner_history(user_id: str, limit: int = 20, skip: int = 0):
    """Return the user's past diet-planner inputs, newest first."""
    db = get_mongo_db()
    cursor = (
        db.diet_planner_inputs.find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    return await cursor.to_list(length=limit)
