import requests
from typing import List, Dict, Optional


OPEN_FOOD_FACTS_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def search_open_food_facts(query: str, page_size: int = 20) -> List[Dict]:
    """Search Open Food Facts for products matching the query."""
    try:
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": page_size,
            "fields": "product_name,brands,nutriments,serving_size,image_front_small_url"
        }
        resp = requests.get(OPEN_FOOD_FACTS_URL, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for product in data.get("products", []):
            name = product.get("product_name", "").strip()
            brand = product.get("brands", "").strip()
            if not name:
                continue
            n = product.get("nutriments", {})
            calories = n.get("energy-kcal_100g", n.get("energy_100g", 0))
            if calories and calories > 900:
                calories = 0
            protein = n.get("proteins_100g", 0)
            carbs = n.get("carbohydrates_100g", 0)
            fat = n.get("fat_100g", 0)
            fiber = n.get("fiber_100g", 0)

            if not calories and not protein and not carbs and not fat:
                continue

            display_name = f"{name} ({brand})" if brand else name
            results.append({
                "name": display_name,
                "calories_per_100g": float(calories or 0),
                "protein_per_100g": float(protein or 0),
                "carbs_per_100g": float(carbs or 0),
                "fat_per_100g": float(fat or 0),
                "fiber_per_100g": float(fiber or 0),
                "source": "Open Food Facts",
            })
        return results
    except Exception as e:
        return []
