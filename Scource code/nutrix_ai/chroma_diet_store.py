"""
ChromaDB storage for AI Diet Planner responses.

Diet plan LLM outputs are stored here (NOT in MongoDB), tagged with the
Supabase user_id so retrieval is always per-user.
"""

import json
import uuid
import logging
from datetime import datetime, timezone

import chromadb

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton ChromaDB client & collection
# ---------------------------------------------------------------------------

_chroma_client: chromadb.ClientAPI | None = None
_diet_collection = None


def _get_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(path="./chroma_data")
    return _chroma_client


def get_diet_plan_collection():
    """Return (or create) the `user_diet_plans` collection."""
    global _diet_collection
    if _diet_collection is None:
        client = _get_client()
        _diet_collection = client.get_or_create_collection(name="user-diet-plans")
    return _diet_collection


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_diet_plan_to_chroma(user_id: str, plan_json: dict) -> str:
    """
    Store a diet-plan LLM response in ChromaDB.

    The plan JSON is serialised to a string and stored as the document.
    Metadata includes the user_id for per-user filtering plus a timestamp.

    Returns the generated document ID so MongoDB can reference it.
    """
    collection = get_diet_plan_collection()
    doc_id = str(uuid.uuid4())
    plan_text = json.dumps(plan_json, ensure_ascii=False)

    collection.upsert(
        ids=[doc_id],
        documents=[plan_text],
        metadatas=[{
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }],
    )
    logger.info("Saved diet plan %s for user %s to ChromaDB", doc_id, user_id)
    return doc_id


def get_diet_plans_from_chroma(user_id: str, limit: int = 20) -> list[dict]:
    """
    Retrieve all diet plans stored for a given user from ChromaDB.

    Returns a list of dicts with keys: id, plan, created_at.
    """
    collection = get_diet_plan_collection()
    results = collection.get(
        where={"user_id": user_id},
        limit=limit,
    )

    plans = []
    if results and results.get("ids"):
        for i, doc_id in enumerate(results["ids"]):
            try:
                plan = json.loads(results["documents"][i])
            except (json.JSONDecodeError, IndexError):
                plan = results["documents"][i]

            plans.append({
                "id": doc_id,
                "plan": plan,
                "created_at": results["metadatas"][i].get("created_at", ""),
            })

    # Sort newest-first
    plans.sort(key=lambda p: p["created_at"], reverse=True)
    return plans


def delete_diet_plan_from_chroma(doc_id: str):
    """Delete a single diet plan by its ChromaDB document ID."""
    collection = get_diet_plan_collection()
    collection.delete(ids=[doc_id])
    logger.info("Deleted diet plan %s from ChromaDB", doc_id)


def delete_all_diet_plans_for_user(user_id: str) -> int:
    """Delete every diet plan belonging to a user. Returns count deleted."""
    collection = get_diet_plan_collection()
    existing = collection.get(where={"user_id": user_id})
    if existing and existing.get("ids"):
        collection.delete(ids=existing["ids"])
        count = len(existing["ids"])
        logger.info("Deleted %d diet plans for user %s from ChromaDB", count, user_id)
        return count
    return 0
