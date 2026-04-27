from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class UserProfile:
    id: Optional[int]
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    activity_level: str
    goal: str
    created_at: Optional[str] = None

    def calculate_bmr(self) -> float:
        if self.gender.lower() == 'male':
            return 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age + 5
        else:
            return 10 * self.weight_kg + 6.25 * self.height_cm - 5 * self.age - 161

    def calculate_tdee(self, multiplier: float) -> float:
        return self.calculate_bmr() * multiplier

    def calculate_calories_target(self, tdee: float, adjustment: int) -> float:
        return max(1200, tdee + adjustment)
