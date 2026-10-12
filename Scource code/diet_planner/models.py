from dataclasses import dataclass, field
from typing import List

@dataclass
class UserProfile:
    age: int
    height: float  # in cm
    weight: float  # in kg
    gender: str  # 'male' or 'female'
    activity_level: str  # 'sedentary', 'lightly_active', 'moderately_active', 'very_active'
    food_preference: str  # 'vegetarian', 'non-vegetarian', 'vegan'
    goal: str  # 'weight_loss', 'maintenance', 'muscle_gain'
    health_conditions: List[str] = field(default_factory=list)  # e.g. ['diabetes', 'hypertension', 'thyroid', 'cholesterol', 'pcos']
    allergens: List[str] = field(default_factory=list)  # e.g. ['gluten', 'lactose', 'nuts', 'egg', 'fish', 'soy']
    user_id: str = "default_user"

    def __post_init__(self):
        self.gender = self.gender.strip().lower()
        self.activity_level = self.activity_level.strip().lower()
        self.food_preference = self.food_preference.strip().lower()
        self.goal = self.goal.strip().lower()
        self.health_conditions = [c.strip().lower() for c in self.health_conditions]
        self.allergens = [a.strip().lower() for a in self.allergens]
        self.user_id = self.user_id.strip()


@dataclass
class FoodItem:
    name: str
    category: str  # 'breakfast', 'lunch', 'dinner', 'snack'
    calories: float  # kcal per base serving
    protein: float  # grams per base serving
    carbs: float  # grams per base serving
    fat: float  # grams per base serving
    preference: str  # 'vegan', 'veg', 'non-veg'
    serving_unit: str  # e.g., "1 cup (150g)", "2 rotis"
    health_tags: List[str] = field(default_factory=list)  # e.g., ['diabetic_friendly', 'low_sodium', 'low_cholesterol', 'goitrogen_free']

    def is_suitable_for_preference(self, user_pref: str) -> bool:
        """
        Check if food item matches user food preference.
        - vegan: matches 'vegan'
        - vegetarian/veg: matches 'vegan', 'veg'
        - non-vegetarian: matches anything ('vegan', 'veg', 'non-veg')
        """
        if user_pref == 'vegan':
            return self.preference == 'vegan'
        elif user_pref in ('vegetarian', 'veg'):
            return self.preference in ('vegan', 'veg')
        return True  # Non-vegetarian can eat anything

    def is_suitable_for_conditions(self, conditions: List[str]) -> bool:
        """
        Check if food is appropriate for the user's health conditions.
        If user has certain conditions, they may need to avoid or restrict items
        lacking specific health tags.
        """
        for cond in conditions:
            if cond == 'diabetes':
                # Diabetic friendly means low GI, complex carbs, low added sugar
                if 'diabetic_friendly' not in self.health_tags:
                    return False
            elif cond == 'hypertension':
                # Hypertension friendly means low sodium
                if 'low_sodium' not in self.health_tags:
                    return False
            elif cond == 'cholesterol':
                # High cholesterol friendly means low saturated fats / low cholesterol
                if 'low_cholesterol' not in self.health_tags:
                    return False
            elif cond == 'thyroid':
                # Thyroid friendly means avoid or limit raw goitrogenic foods
                if 'thyroid_friendly' not in self.health_tags:
                    return False
        return True


@dataclass
class MealPlanItem:
    food_item: FoodItem
    portion: float  # Multiplier of base serving (e.g. 0.5, 1.0, 1.5, 2.0)

    @property
    def calories(self) -> float:
        return round(self.food_item.calories * self.portion, 1)

    @property
    def protein(self) -> float:
        return round(self.food_item.protein * self.portion, 1)

    @property
    def carbs(self) -> float:
        return round(self.food_item.carbs * self.portion, 1)

    @property
    def fat(self) -> float:
        return round(self.food_item.fat * self.portion, 1)


@dataclass
class MealPlanDay:
    day_name: str
    breakfast: List[MealPlanItem] = field(default_factory=list)
    lunch: List[MealPlanItem] = field(default_factory=list)
    dinner: List[MealPlanItem] = field(default_factory=list)
    snacks: List[MealPlanItem] = field(default_factory=list)

    @property
    def total_calories(self) -> float:
        return round(
            sum(item.calories for item in self.breakfast + self.lunch + self.dinner + self.snacks), 1
        )

    @property
    def total_protein(self) -> float:
        return round(
            sum(item.protein for item in self.breakfast + self.lunch + self.dinner + self.snacks), 1
        )

    @property
    def total_carbs(self) -> float:
        return round(
            sum(item.carbs for item in self.breakfast + self.lunch + self.dinner + self.snacks), 1
        )

    @property
    def total_fat(self) -> float:
        return round(
            sum(item.fat for item in self.breakfast + self.lunch + self.dinner + self.snacks), 1
        )
