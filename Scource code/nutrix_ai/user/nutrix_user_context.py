import json
import logging
from nutrix_ai.database import SessionLocal, HealthProfile, DietPlan, SavedItem

logger = logging.getLogger(__name__)

class NutrixUserContext:
    """
    Retrieves user-specific health, diet, and scanned label context from the SQLite database.
    """
    def __init__(self):
        self.health_lens = None
        self.fitness_lens = None

    def set_health_lens_context(self, food_data):
        self.health_lens = food_data
        
    def set_fitness_lens_context(self, fitness_data):
        self.fitness_lens = fitness_data

    def get_context(self, user_id_str: str, intent_tags: list):
        """
        Returns a structured dictionary with the user's real database context.
        """
        try:
            if user_id_str.startswith("user_"):
                user_id = int(user_id_str.replace("user_", ""))
            else:
                user_id = int(user_id_str)
        except ValueError:
            logger.error(f"Invalid user_id format: {user_id_str}")
            return None
            
        context_data = {}
        db = SessionLocal()
        
        try:
            # 1. Fetch Health Profile
            if 'PERSONALIZED' in intent_tags or 'NUTRITION' in intent_tags:
                profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
                if profile:
                    context_data['nutrition'] = {
                        "goal": profile.goal,
                        "diet_type": profile.diet_type,
                        "age": profile.age,
                        "weight_kg": profile.weight,
                        "height_cm": profile.height
                    }
                    
            # 2. Fetch Latest Diet Plan
            latest_plan = db.query(DietPlan).filter(DietPlan.user_id == user_id).order_by(DietPlan.created_at.desc()).first()
            if latest_plan:
                try:
                    plan_data = json.loads(latest_plan.plan_json)
                    context_data['active_diet_plan'] = plan_data
                except Exception as e:
                    logger.error(f"Failed to parse diet plan: {e}")
                    
            # 3. Fetch Recent Scanned Labels (SavedItems)
            recent_scans = db.query(SavedItem).filter(SavedItem.user_id == user_id, SavedItem.item_type == "scanned_label").order_by(SavedItem.created_at.desc()).limit(2).all()
            if recent_scans:
                context_data['recent_scans'] = []
                for scan in recent_scans:
                    try:
                        scan_data = json.loads(scan.item_data)
                        context_data['recent_scans'].append({
                            "timestamp": str(scan.created_at),
                            "data": scan_data
                        })
                    except Exception as e:
                        logger.error(f"Failed to parse scanned label: {e}")

            if 'FITNESS' in intent_tags:
                if self.fitness_lens:
                    context_data['fitness'] = {"recent_workout": self.fitness_lens}
                    
            if self.health_lens:
                context_data['health_lens'] = self.health_lens
                
        finally:
            db.close()
            
        if not context_data:
            return None
            
        return context_data
