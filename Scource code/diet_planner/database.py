from typing import List
from diet_planner.models import FoodItem

# Curated dataset of popular Indian food items with nutritional details.
# Portion calculations and calories are estimated for standard single-portion servings.
INDIAN_FOODS: List[FoodItem] = [
    # --- BREAKFAST ---
    FoodItem(
        name="Vegetable Poha",
        category="breakfast",
        calories=220.0,
        protein=4.0,
        carbs=38.0,
        fat=5.0,
        preference="vegan",
        serving_unit="1 plate (150g)",
        health_tags=["thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Oats Upma",
        category="breakfast",
        calories=210.0,
        protein=6.0,
        carbs=35.0,
        fat=4.0,
        preference="vegan",
        serving_unit="1 plate (150g)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Moong Dal Cheela",
        category="breakfast",
        calories=180.0,
        protein=9.0,
        carbs=26.0,
        fat=4.0,
        preference="vegan",
        serving_unit="1 piece (with green chutney)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Idli with Sambar",
        category="breakfast",
        calories=230.0,
        protein=6.0,
        carbs=44.0,
        fat=2.0,
        preference="vegan",
        serving_unit="2 pieces idli + 1 bowl sambar",
        health_tags=["thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Paneer Bhurji with Brown Bread",
        category="breakfast",
        calories=340.0,
        protein=18.0,
        carbs=28.0,
        fat=16.0,
        preference="veg",
        serving_unit="75g paneer bhurji + 2 slices bread",
        health_tags=["diabetic_friendly", "thyroid_friendly"]
    ),
    FoodItem(
        name="Sprouts Salad",
        category="breakfast",
        calories=150.0,
        protein=8.0,
        carbs=24.0,
        fat=1.0,
        preference="vegan",
        serving_unit="1 bowl (150g)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Boiled Eggs with Wheat Toast",
        category="breakfast",
        calories=250.0,
        protein=16.0,
        carbs=18.0,
        fat=10.0,
        preference="non-veg",
        serving_unit="2 large boiled eggs + 1 slice toast",
        health_tags=["diabetic_friendly", "thyroid_friendly"]
    ),
    FoodItem(
        name="Egg Omelette with Spinach & Brown Bread",
        category="breakfast",
        calories=270.0,
        protein=17.0,
        carbs=16.0,
        fat=14.0,
        preference="non-veg",
        serving_unit="2 egg omelette + 1 slice bread",
        health_tags=["diabetic_friendly", "thyroid_friendly"]
    ),
    FoodItem(
        name="Aloo Paratha with Curd",
        category="breakfast",
        calories=360.0,
        protein=8.0,
        carbs=52.0,
        fat=12.0,
        preference="veg",
        serving_unit="1 medium paratha + 1/2 cup curd",
        health_tags=["thyroid_friendly"]
    ),
    FoodItem(
        name="Daliya (Broken Wheat) Porridge",
        category="breakfast",
        calories=200.0,
        protein=7.0,
        carbs=38.0,
        fat=2.0,
        preference="veg",
        serving_unit="1 bowl (150g, cooked in skimmed milk)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),

    # --- LUNCH ---
    FoodItem(
        name="Roti with Dal Tadka & Bhindi Sabji",
        category="lunch",
        calories=420.0,
        protein=16.0,
        carbs=65.0,
        fat=10.0,
        preference="vegan",
        serving_unit="2 rotis + 1 bowl dal + 1 bowl bhindi",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Brown Rice with Rajma Masala & Salad",
        category="lunch",
        calories=450.0,
        protein=15.0,
        carbs=75.0,
        fat=8.0,
        preference="vegan",
        serving_unit="1 cup brown rice + 1 bowl rajma",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Paneer Tikka Roll (Whole Wheat)",
        category="lunch",
        calories=380.0,
        protein=16.0,
        carbs=42.0,
        fat=14.0,
        preference="veg",
        serving_unit="1 whole wheat roll",
        health_tags=["thyroid_friendly"]
    ),
    FoodItem(
        name="Chicken Curry with Roti & Salad",
        category="lunch",
        calories=480.0,
        protein=32.0,
        carbs=48.0,
        fat=14.0,
        preference="non-veg",
        serving_unit="150g chicken curry + 2 rotis",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol"]
    ),
    FoodItem(
        name="Fish Curry with Rice & Cucumber Salad",
        category="lunch",
        calories=450.0,
        protein=28.0,
        carbs=54.0,
        fat=11.0,
        preference="non-veg",
        serving_unit="120g fish curry + 1 cup rice",
        health_tags=["thyroid_friendly", "low_cholesterol"]
    ),
    FoodItem(
        name="Tofu Stir-fry with Quinoa",
        category="lunch",
        calories=380.0,
        protein=18.0,
        carbs=45.0,
        fat=12.0,
        preference="vegan",
        serving_unit="1 bowl (100g tofu + 1 cup quinoa)",
        health_tags=["diabetic_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Vegetable Pulav with Onion Raita",
        category="lunch",
        calories=350.0,
        protein=8.0,
        carbs=58.0,
        fat=9.0,
        preference="veg",
        serving_unit="1 plate pulav + 1/2 cup raita",
        health_tags=["thyroid_friendly"]
    ),
    FoodItem(
        name="Chana Masala with Jeera Rice",
        category="lunch",
        calories=440.0,
        protein=14.0,
        carbs=72.0,
        fat=9.0,
        preference="vegan",
        serving_unit="1 bowl chole + 1 cup rice",
        health_tags=["thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Egg Bhurji with Multi-grain Roti",
        category="lunch",
        calories=410.0,
        protein=20.0,
        carbs=44.0,
        fat=15.0,
        preference="non-veg",
        serving_unit="2 egg bhurji + 2 rotis",
        health_tags=["diabetic_friendly", "thyroid_friendly"]
    ),

    # --- DINNER ---
    FoodItem(
        name="Moong Dal Khichdi with Curd",
        category="dinner",
        calories=350.0,
        protein=12.0,
        carbs=54.0,
        fat=8.0,
        preference="veg",
        serving_unit="1 large bowl khichdi + 1/2 cup curd",
        health_tags=["thyroid_friendly", "low_cholesterol"]
    ),
    FoodItem(
        name="Grilled Chicken Breast with Sauteed Veggies",
        category="dinner",
        calories=380.0,
        protein=38.0,
        carbs=12.0,
        fat=10.0,
        preference="non-veg",
        serving_unit="150g grilled chicken + 1 cup stir-fry veg",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Palak Paneer with Missi Roti",
        category="dinner",
        calories=440.0,
        protein=20.0,
        carbs=45.0,
        fat=18.0,
        preference="veg",
        serving_unit="1 bowl palak paneer + 2 missi rotis",
        health_tags=["diabetic_friendly", "thyroid_friendly"]
    ),
    FoodItem(
        name="Dal Makhani with Roti & Cucumber Salad",
        category="dinner",
        calories=460.0,
        protein=16.0,
        carbs=60.0,
        fat=15.0,
        preference="veg",
        serving_unit="1 bowl dal + 2 rotis",
        health_tags=["thyroid_friendly"]
    ),
    FoodItem(
        name="Grilled Tandoori Fish with Mint Chutney & Salad",
        category="dinner",
        calories=290.0,
        protein=26.0,
        carbs=6.0,
        fat=16.0,
        preference="non-veg",
        serving_unit="150g fish fillet + green salad",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Soya Chunks Curry with Roti & Salad",
        category="dinner",
        calories=390.0,
        protein=24.0,
        carbs=50.0,
        fat=9.0,
        preference="vegan",
        serving_unit="1 bowl soya curry + 2 rotis",
        health_tags=["diabetic_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Lauki Sabji with Yellow Dal & Phulka",
        category="dinner",
        calories=320.0,
        protein=12.0,
        carbs=52.0,
        fat=6.0,
        preference="vegan",
        serving_unit="1 bowl lauki + 1 bowl dal + 2 phulka",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Mushroom Matar Masala with Roti",
        category="dinner",
        calories=360.0,
        protein=14.0,
        carbs=48.0,
        fat=10.0,
        preference="vegan",
        serving_unit="1 bowl mushroom peas + 2 rotis",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),

    # --- SNACKS ---
    FoodItem(
        name="Roasted Makhana (Foxnuts)",
        category="snack",
        calories=90.0,
        protein=2.5,
        carbs=18.0,
        fat=0.5,
        preference="vegan",
        serving_unit="1 bowl (25g)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Roasted Chana",
        category="snack",
        calories=140.0,
        protein=7.0,
        carbs=22.0,
        fat=2.0,
        preference="vegan",
        serving_unit="1/2 cup (40g)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Mixed Nuts (Almonds & Walnuts)",
        category="snack",
        calories=95.0,
        protein=3.0,
        carbs=3.0,
        fat=8.0,
        preference="vegan",
        serving_unit="1 handful (15g)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Masala Chaas (Buttermilk)",
        category="snack",
        calories=45.0,
        protein=2.0,
        carbs=3.0,
        fat=1.5,
        preference="veg",
        serving_unit="1 glass (200ml)",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Sprouted Moong Salad",
        category="snack",
        calories=80.0,
        protein=4.5,
        carbs=13.0,
        fat=0.5,
        preference="vegan",
        serving_unit="1/2 cup",
        health_tags=["diabetic_friendly", "thyroid_friendly", "low_cholesterol", "low_sodium"]
    ),
    FoodItem(
        name="Paneer Tikka Cubes",
        category="snack",
        calories=150.0,
        protein=9.0,
        carbs=4.0,
        fat=11.0,
        preference="veg",
        serving_unit="4 small pieces (75g)",
        health_tags=["diabetic_friendly", "thyroid_friendly"]
    ),
    FoodItem(
        name="Green Tea with Digestive Biscuits",
        category="snack",
        calories=90.0,
        protein=1.0,
        carbs=15.0,
        fat=3.0,
        preference="vegan",
        serving_unit="1 cup tea + 2 biscuits",
        health_tags=["thyroid_friendly"]
    )
]


def get_foods_by_category(category: str) -> List[FoodItem]:
    """Helper to fetch foods belonging to a specific category."""
    return [item for item in INDIAN_FOODS if item.category == category]
