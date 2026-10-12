import unittest
import os
import sqlite3
import datetime
import pandas as pd
from diet_planner.models import UserProfile, FoodItem
from diet_planner.calculator import (
    calculate_bmr,
    calculate_tdee,
    compute_gain_plan,
    compute_loss_plan,
    recalibrate
)
from diet_planner.db import (
    init_databases,
    save_user_profile,
    get_user_profile,
    log_weight,
    get_weight_logs,
    log_meal,
    get_daily_logged_nutrition,
    get_nutrition_from_ifct
)
from diet_planner.planner import format_health_filters, validate_and_replace_with_ifct, generate_local_offline_meal
from diet_planner.recommender import get_meal_context, recommend_foods

class TestDietCalculator(unittest.TestCase):
    def test_bmr_and_tdee(self):
        bmr = calculate_bmr(70.0, 175.0, 30, 'male')
        expected_bmr = (10 * 70.0) + (6.25 * 175.0) - (5 * 30) + 5.0
        self.assertEqual(bmr, expected_bmr)

        tdee = calculate_tdee(bmr, 'lightly_active')
        self.assertEqual(tdee, bmr * 1.375)

    def test_compute_gain_plan(self):
        # Current weight: 60kg, target weight: 65kg in 10 weeks
        # weight to gain = 5kg -> total surplus = 38500 kcal
        # daily surplus = 38500 / 70 = 550 kcal, capped at 500 kcal.
        tdee = 2000.0
        target_cal, prot, carbs, fat, surplus = compute_gain_plan(tdee, 60.0, 65.0, 10)
        self.assertEqual(surplus, 500.0)
        self.assertEqual(target_cal, 2500.0)
        self.assertEqual(prot, 120.0) # 60 * 2 = 120g
        self.assertEqual(fat, round((2500.0 * 0.25) / 9.0, 1)) # 25% of calories

    def test_compute_loss_plan(self):
        # Current weight: 80kg, target: 70kg in 10 weeks
        # deficit needed = 10 * 7700 = 77000 kcal -> daily deficit = 1100 kcal.
        # Cap 1: 500 kcal. Cap 2: 20% of TDEE (20% of 2000 = 400 kcal).
        # Hence deficit is capped at 400 kcal.
        tdee = 2000.0
        target_cal, prot, carbs, fat, deficit = compute_loss_plan(tdee, 80.0, 70.0, 10, 'male')
        self.assertEqual(deficit, 400.0)
        self.assertEqual(target_cal, 1600.0)

    def test_recalibrate(self):
        # Test gain recalibration
        # expected gain = 300 surplus * 7 / 7700 = 0.27 kg
        # logs = [70.0, 70.1] -> actual gain = 0.1 kg (under expected * 0.5)
        # Should increase surplus by 100 kcal
        new_cal = recalibrate(1800.0, [70.0, 70.1], 300.0, is_gain=True)
        self.assertEqual(new_cal, 1800.0 + 300.0 + 100.0)

        # Test loss recalibration
        # expected loss = 400 deficit * 7 / 7700 = 0.36 kg
        # logs = [80.0, 79.9] -> actual loss = 0.1 kg (under expected * 0.5)
        # Should increase deficit (decrease target by 100 kcal)
        new_cal_loss = recalibrate(2000.0, [80.0, 79.9], 400.0, is_gain=False)
        self.assertEqual(new_cal_loss, 2000.0 - 400.0 - 100.0)


class TestDatabaseAndIntegration(unittest.TestCase):
    def setUp(self):
        if os.path.exists("nutriscan.db"):
            try:
                os.remove("nutriscan.db")
            except PermissionError:
                pass
        init_databases()

    def test_profile_db_roundtrip(self):
        profile_dict = {
            'user_id': 'test_user_99',
            'age': 25,
            'height': 170.0,
            'weight': 65.0,
            'gender': 'female',
            'activity_level': 'sedentary',
            'food_preference': 'vegan',
            'goal': 'weight_loss',
            'health_conditions': ['diabetes'],
            'allergens': ['gluten']
        }
        save_user_profile(profile_dict)
        retrieved = get_user_profile('test_user_99')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['age'], 25)
        self.assertIn('diabetes', retrieved['health_conditions'])
        self.assertIn('gluten', retrieved['allergens'])

    def test_weight_logging(self):
        log_weight('test_user_99', 65.0, '2026-07-01')
        log_weight('test_user_99', 64.5, '2026-07-08')
        logs = get_weight_logs('test_user_99')
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0][1], 65.0)

    def test_meal_logging_budget(self):
        today = datetime.date.today().isoformat()
        log_meal('test_user_99', today, 'breakfast', 'Oats', 200, 6, 35, 3)
        log_meal('test_user_99', today, 'lunch', 'Rice & Dal', 300, 10, 50, 4)
        
        logged = get_daily_logged_nutrition('test_user_99', today)
        self.assertEqual(logged['calories'], 500)

    def test_ifct_lookup(self):
        res = get_nutrition_from_ifct("Paneer Tikka")
        if res:
            name, cal, prot, carb, fat = res
            self.assertIn("Paneer Tikka", name)
            self.assertGreater(cal, 100)

    def test_recommender(self):
        # Verify cosine similarity recommendations doesn't crash
        # remaining: 1000 cal, 50 prot, 120 carbs
        rec = recommend_foods(
            user_id='test_user_99',
            daily_cal=1500,
            daily_prot=80,
            daily_carb=180,
            user_allergens=['nuts'],
            user_goal='weight_loss',
            meal_context='evening snack',
            n=3
        )
        self.assertFalse(rec.empty)
        self.assertTrue(len(rec) <= 3)
        # Should not contain nut allergens
        for name in rec['name']:
            self.assertNotIn("Almond", name)
            self.assertNotIn("Walnut", name)

if __name__ == "__main__":
    unittest.main()
