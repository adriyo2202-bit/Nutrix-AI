from typing import Tuple, Dict, List
from diet_planner.models import UserProfile

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Calculates BMR using the Mifflin-St Jeor equation:
    Men: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    Women: (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    """
    if gender.lower() == 'male':
        return (10.0 * weight) + (6.25 * height) - (5.0 * age) + 5.0
    else:
        return (10.0 * weight) + (6.25 * height) - (5.0 * age) - 161.0


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    TDEE = BMR * activity multiplier:
    Sedentary -> 1.2
    Lightly active -> 1.375
    Moderately active -> 1.55
    Very active -> 1.725
    """
    multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderately_active': 1.55,
        'very_active': 1.725
    }
    return bmr * multipliers.get(activity_level.lower(), 1.2)


def calculate_caloric_target(tdee: float, profile: UserProfile) -> float:
    """
    Determine caloric target based on target goal.
    - weight_loss: TDEE - 500 (safe limit: min 1200 for female, min 1500 for male)
    - muscle_gain: TDEE + 300
    - maintenance: TDEE
    """
    goal = profile.goal.lower()
    gender = profile.gender.lower()

    if goal == 'weight_loss':
        target = tdee - 500.0
        min_limit = 1200.0 if gender == 'female' else 1500.0
        if target < min_limit:
            target = min_limit
        return round(target, 1)
    elif goal == 'muscle_gain':
        return round(tdee + 300.0, 1)
    else:
        return round(tdee, 1)


def calculate_macro_targets(calories: float, profile: UserProfile) -> Tuple[float, float, float, Tuple[float, float, float]]:
    """
    Computes baseline macronutrient splits (in grams and percentage ratios):
    Returns:
        (carbs_g, protein_g, fat_g, (c_ratio, p_ratio, f_ratio))
    """
    has_diabetes = 'diabetes' in profile.health_conditions
    has_cholesterol = 'cholesterol' in profile.health_conditions

    # Default splits
    c_ratio, p_ratio, f_ratio = 0.50, 0.20, 0.30

    if has_cholesterol:
        if has_diabetes:
            c_ratio, p_ratio, f_ratio = 0.40, 0.35, 0.25
        elif profile.goal == 'muscle_gain':
            c_ratio, p_ratio, f_ratio = 0.45, 0.30, 0.25
        else:
            c_ratio, p_ratio, f_ratio = 0.55, 0.20, 0.25
    elif has_diabetes:
        if profile.goal == 'muscle_gain':
            c_ratio, p_ratio, f_ratio = 0.35, 0.30, 0.35
        else:
            c_ratio, p_ratio, f_ratio = 0.40, 0.25, 0.35
    elif profile.goal == 'muscle_gain':
        c_ratio, p_ratio, f_ratio = 0.45, 0.30, 0.25
    elif profile.goal == 'weight_loss':
        c_ratio, p_ratio, f_ratio = 0.45, 0.25, 0.30

    # Calculate grams
    carbs_g = (calories * c_ratio) / 4.0
    protein_g = (calories * p_ratio) / 4.0
    fat_g = (calories * f_ratio) / 9.0

    return round(carbs_g, 1), round(protein_g, 1), round(fat_g, 1), (c_ratio, p_ratio, f_ratio)


def compute_gain_plan(tdee: float, current_weight: float, target_weight: float, weeks: int) -> Tuple[float, float, float, float, float]:
    """
    Computes a safe calorie surplus and macro targets for weight gain.
    - 1 kg of muscle ≈ 7700 kcal surplus needed
    - Safety cap: surplus should not exceed 500 kcal/day
    - Macro split for muscle gain (ICMR guidelines):
      Protein: 2g per kg bodyweight
      Fat: 25% of target daily calories
      Carbs: remaining calories / 4
    Returns:
        (daily_target, protein_g, carbs_g, fat_g, daily_surplus)
    """
    weight_to_gain = target_weight - current_weight
    total_surplus_needed = weight_to_gain * 7700.0
    daily_surplus = total_surplus_needed / (weeks * 7.0)
    
    # Safety cap: surplus should not exceed 500 kcal/day
    daily_surplus = min(daily_surplus, 500.0)
    
    daily_target = tdee + daily_surplus
    
    # Macro split for muscle gain (ICMR guidelines)
    protein_g = current_weight * 2.0       # 2g per kg bodyweight
    fat_g = (daily_target * 0.25) / 9.0   # 25% from fat
    carbs_g = (daily_target - (protein_g * 4.0) - (fat_g * 9.0)) / 4.0  # remaining from carbs
    
    return round(daily_target, 1), round(protein_g, 1), round(carbs_g, 1), round(fat_g, 1), round(daily_surplus, 1)


def compute_loss_plan(tdee: float, current_weight: float, target_weight: float, weeks: int, gender: str) -> Tuple[float, float, float, float, float]:
    """
    Computes a safe calorie deficit and macro targets for weight loss.
    - Safety cap 1: never exceed 500 kcal deficit per day
    - Safety cap 2: never exceed 20% of TDEE
    - Safety cap 3: absolute minimums (1200 kcal for female, 1500 kcal for male)
    Returns:
        (daily_target, protein_g, carbs_g, fat_g, daily_deficit)
    """
    weight_to_lose = current_weight - target_weight
    total_deficit_needed = weight_to_lose * 7700.0
    daily_deficit = total_deficit_needed / (weeks * 7.0)
    
    # Safety cap 1: never exceed 500 kcal deficit per day
    daily_deficit = min(daily_deficit, 500.0)
    
    # Safety cap 2: never exceed 20% of TDEE
    daily_deficit = min(daily_deficit, tdee * 0.20)
    
    daily_target = tdee - daily_deficit
    
    # Safety cap 3: absolute minimums
    min_calories = 1200.0 if gender.lower() == "female" else 1500.0
    daily_target = max(daily_target, min_calories)
    
    # Recalculate effective deficit after safety caps
    effective_deficit = tdee - daily_target
    
    # Default macro split for weight loss (45% carbs, 25% protein, 30% fat)
    protein_g = (daily_target * 0.25) / 4.0
    fat_g = (daily_target * 0.30) / 9.0
    carbs_g = (daily_target * 0.45) / 4.0
    
    return round(daily_target, 1), round(protein_g, 1), round(carbs_g, 1), round(fat_g, 1), round(effective_deficit, 1)


def recalibrate(tdee: float, logged_weights: List[float], daily_offset: float, is_gain: bool = True) -> float:
    """
    Recalibrate target calorie intake based on actual progress.
    logged_weights should contain a list of weight logs in chronological order.
    Returns:
        recalibrated daily calorie target
    """
    if len(logged_weights) < 2:
        return tdee + (daily_offset if is_gain else -daily_offset)
        
    actual_change = logged_weights[-1] - logged_weights[-2]
    expected_change = daily_offset * 7.0 / 7700.0
    
    if is_gain:
        if actual_change < expected_change * 0.5:
            # gaining too slowly → increase surplus by 100 kcal
            return tdee + daily_offset + 100.0
        elif actual_change > expected_change * 1.5:
            # gaining too fast (likely fat) → reduce surplus by 100 kcal
            return tdee + daily_offset - 100.0
        return tdee + daily_offset
    else:
        # weight loss actual change is negative, so let's check actual loss
        actual_loss = -actual_change
        expected_loss = expected_change
        if actual_loss < expected_loss * 0.5:
            # losing too slowly -> increase deficit (decrease daily calories by 100)
            return tdee - daily_offset - 100.0
        elif actual_loss > expected_loss * 1.5:
            # losing too fast -> decrease deficit (increase daily calories by 100)
            return tdee - daily_offset + 100.0
        return tdee - daily_offset
