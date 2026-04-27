from dataclasses import dataclass
from typing import Optional


@dataclass
class FoodItem:
    id: Optional[int]
    name: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float = 0.0
    category: str = 'General'


@dataclass
class FoodLog:
    id: Optional[int]
    user_id: int
    food_id: int
    food_name: str
    quantity_g: float
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    log_date: str
    meal_type: str
