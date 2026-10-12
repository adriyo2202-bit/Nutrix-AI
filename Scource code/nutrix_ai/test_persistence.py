"""
Quick smoke test for MongoDB and ChromaDB persistence.
Run: python -m Source_Code.nutrix_ai.test_persistence
"""

import asyncio
import os
import sys

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env manually
from pathlib import Path
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


async def test_mongodb():
    from nutrix_ai.mongodb import (
        ensure_indexes, close_mongo, get_mongo_db,
        save_chat_message, get_chat_history, delete_chat_history,
        save_ingredient_scan, get_scan_history,
        save_diet_planner_input, get_diet_planner_history,
    )

    print("=" * 60)
    print("TESTING MongoDB CONNECTION")
    print("=" * 60)

    # 1. Test connection
    db = get_mongo_db()
    info = await db.command("ping")
    print(f"✅ MongoDB ping: {info}")

    # 2. Ensure indexes
    await ensure_indexes()
    print("✅ Indexes created")

    test_uid = "test-user-00000000-0000-0000-0000-000000000000"

    # 3. Save a chat message
    msg_id = await save_chat_message(test_uid, "user", "Hello from test!")
    print(f"✅ Saved chat message: {msg_id}")

    ai_msg_id = await save_chat_message(test_uid, "assistant", "Hi! I'm Nutrix AI.")
    print(f"✅ Saved AI response: {ai_msg_id}")

    # 4. Retrieve chat history
    history = await get_chat_history(test_uid, limit=10)
    print(f"✅ Chat history ({len(history)} messages):")
    for msg in history:
        print(f"   [{msg['role']}] {msg['content'][:50]}")

    # 5. Save ingredient scan
    scan_id = await save_ingredient_scan(
        user_id=test_uid,
        input_type="image",
        input_reference="test_label.jpg",
        ai_result={"overall_safety_score": 75, "ingredients": []}
    )
    print(f"✅ Saved ingredient scan: {scan_id}")

    # 6. Retrieve scan history
    scans = await get_scan_history(test_uid)
    print(f"✅ Scan history ({len(scans)} scans)")

    # 7. Save diet planner input
    diet_id = await save_diet_planner_input(
        user_id=test_uid,
        age=25, height=175.0, weight=70.0,
        goal="muscle gain", diet_type="high-protein",
        chroma_doc_id="test-chroma-id"
    )
    print(f"✅ Saved diet planner input: {diet_id}")

    # 8. Retrieve diet planner history
    diets = await get_diet_planner_history(test_uid)
    print(f"✅ Diet planner history ({len(diets)} entries)")

    # 9. Cleanup test data
    deleted = await delete_chat_history(test_uid)
    print(f"✅ Cleaned up: deleted {deleted} chat messages")
    from nutrix_ai.mongodb import delete_scan_history
    deleted_scans = await delete_scan_history(test_uid)
    print(f"✅ Cleaned up: deleted {deleted_scans} scans")
    db_handle = get_mongo_db()
    await db_handle.diet_planner_inputs.delete_many({"user_id": test_uid})
    print("✅ Cleaned up: deleted diet planner inputs")

    await close_mongo()
    print("\n✅ MongoDB tests PASSED")


def test_chromadb():
    from nutrix_ai.chroma_diet_store import (
        save_diet_plan_to_chroma,
        get_diet_plans_from_chroma,
        delete_all_diet_plans_for_user,
    )

    print("\n" + "=" * 60)
    print("TESTING ChromaDB (Diet Plans)")
    print("=" * 60)

    test_uid = "test-user-00000000-0000-0000-0000-000000000000"

    # Save a test diet plan
    plan = {
        "bmi_verdict": "Normal BMI at 22.9",
        "daily_roadmap": {
            "breakfast": "Oats with banana",
            "lunch": "Dal, rice, sabzi",
            "dinner": "Grilled paneer with roti",
            "snack": "Mixed nuts"
        },
        "mandatory_fuel": ["Dal", "Paneer", "Eggs"],
        "strictly_forbidden": ["Soda", "Alcohol"],
    }

    doc_id = save_diet_plan_to_chroma(test_uid, plan)
    print(f"✅ Saved diet plan to ChromaDB: {doc_id}")

    # Retrieve
    plans = get_diet_plans_from_chroma(test_uid)
    print(f"✅ Retrieved {len(plans)} diet plan(s) from ChromaDB")

    # Cleanup
    deleted = delete_all_diet_plans_for_user(test_uid)
    print(f"✅ Cleaned up: deleted {deleted} diet plan(s) from ChromaDB")

    print("\n✅ ChromaDB tests PASSED")


if __name__ == "__main__":
    test_chromadb()
    asyncio.run(test_mongodb())
    print("\n🎉 ALL PERSISTENCE TESTS PASSED!")
