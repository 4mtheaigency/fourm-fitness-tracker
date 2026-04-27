from typing import List, Dict, Tuple
from config.settings import settings


def calculate_targets(weight_kg: float, height_cm: float, age: int, gender: str,
                       activity_level: str, goal: str) -> Dict[str, float]:
    if gender.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    multiplier = settings.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    tdee = bmr * multiplier
    adjustment = settings.GOAL_ADJUSTMENTS.get(goal, 0)
    cal_target = max(1200, tdee + adjustment)

    protein_g = (cal_target * settings.DEFAULT_MACRO_RATIOS['protein']) / 4
    carbs_g = (cal_target * settings.DEFAULT_MACRO_RATIOS['carbs']) / 4
    fat_g = (cal_target * settings.DEFAULT_MACRO_RATIOS['fat']) / 9

    if goal == 'Gain Muscle':
        protein_g = max(protein_g, weight_kg * 2.0)
    elif goal == 'Lose Weight':
        protein_g = max(protein_g, weight_kg * 1.8)

    return {
        'calories': round(cal_target, 0),
        'protein': round(protein_g, 1),
        'carbs': round(carbs_g, 1),
        'fat': round(fat_g, 1),
        'fiber': 25.0,
        'bmr': round(bmr, 0),
        'tdee': round(tdee, 0)
    }


def get_remaining(targets: Dict, consumed: Dict) -> Dict[str, float]:
    return {
        key: round(targets.get(key, 0) - consumed.get(key, 0), 1)
        for key in ['calories', 'protein', 'carbs', 'fat', 'fiber']
    }


def recommend_foods(remaining: Dict[str, float], all_foods: list, top_n: int = 8) -> List[Dict]:
    """Score foods based on how well a 100g serving fills the remaining macros."""
    recommendations = []

    rem_cal = max(remaining.get('calories', 0), 0)
    rem_prot = max(remaining.get('protein', 0), 0)
    rem_carbs = max(remaining.get('carbs', 0), 0)
    rem_fat = max(remaining.get('fat', 0), 0)

    if rem_cal <= 0:
        return []

    for food in all_foods:
        cal = food['calories_per_100g']
        prot = food['protein_per_100g']
        carbs = food['carbs_per_100g']
        fat = food['fat_per_100g']

        score = 0.0

        if rem_prot > 5 and prot > 0:
            score += min(prot / rem_prot, 1.0) * 40
        if rem_carbs > 5 and carbs > 0:
            score += min(carbs / rem_carbs, 1.0) * 30
        if rem_fat > 2 and fat > 0:
            score += min(fat / rem_fat, 1.0) * 20

        if cal <= rem_cal:
            score += 10
        else:
            score -= 15

        if score > 0:
            recommendations.append({
                'id': food['id'],
                'name': food['name'],
                'category': food['category'],
                'calories_per_100g': cal,
                'protein_per_100g': prot,
                'carbs_per_100g': carbs,
                'fat_per_100g': fat,
                'fiber_per_100g': food['fiber_per_100g'],
                'score': round(score, 2),
                'reason': _build_reason(prot, carbs, fat, rem_prot, rem_carbs, rem_fat)
            })

    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations[:top_n]


def _build_reason(prot, carbs, fat, rem_prot, rem_carbs, rem_fat) -> str:
    parts = []
    if rem_prot > 5 and prot >= 10:
        parts.append("high protein")
    if rem_carbs > 10 and carbs >= 15:
        parts.append("good carbs")
    if rem_fat > 3 and fat >= 5:
        parts.append("healthy fats")
    if not parts:
        parts.append("balanced option")
    return ", ".join(parts).capitalize()


def summarise_day(logs: list) -> Dict[str, float]:
    total = {'calories': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'fiber': 0.0}
    for log in logs:
        total['calories'] += log['calories']
        total['protein'] += log['protein']
        total['carbs'] += log['carbs']
        total['fat'] += log['fat']
        total['fiber'] += log['fiber']
    return {k: round(v, 1) for k, v in total.items()}
