import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
PORTAL_ENV = Path(__file__).resolve().parents[2] / "Fourm-Trainer-Portal" / ".env"
if PORTAL_ENV.exists():
    load_dotenv(PORTAL_ENV, override=False)

class Settings:
    USDA_API_KEY = os.getenv('USDA_API_KEY', '')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/calorie_tracker.db')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SUPABASE_URL = os.getenv('SUPABASE_URL') or os.getenv('VITE_SUPABASE_URL', '')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY') or os.getenv('VITE_SUPABASE_ANON_KEY', '')

    DEFAULT_MACRO_RATIOS = {
        'protein': 0.25,
        'carbs': 0.45,
        'fat': 0.30
    }

    ACTIVITY_MULTIPLIERS = {
        'Sedentary (little or no exercise)': 1.2,
        'Lightly Active (1-3 days/week)': 1.375,
        'Moderately Active (3-5 days/week)': 1.55,
        'Very Active (6-7 days/week)': 1.725,
        'Extra Active (physical job or 2x training)': 1.9
    }

    GOAL_ADJUSTMENTS = {
        'Lose Weight': -500,
        'Maintain Weight': 0,
        'Gain Muscle': 300
    }

settings = Settings()
