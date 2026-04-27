import requests
from typing import Dict


def send_daily_summary(
    webhook_url: str,
    user_name: str,
    date_str: str,
    consumed: Dict,
    targets: Dict,
    goal: str
) -> bool:
    """Post a daily nutrition summary embed to a Discord webhook."""
    try:
        cal_pct = int(consumed["calories"] / targets["calories"] * 100) if targets["calories"] else 0
        prot_pct = int(consumed["protein"] / targets["protein"] * 100) if targets["protein"] else 0
        carbs_pct = int(consumed["carbs"] / targets["carbs"] * 100) if targets["carbs"] else 0
        fat_pct = int(consumed["fat"] / targets["fat"] * 100) if targets["fat"] else 0

        def bar(pct):
            filled = min(int(pct / 10), 10)
            return "█" * filled + "░" * (10 - filled)

        color = 0x1e64ff

        embed = {
            "title": f"📊 {user_name}'s Daily Nutrition — {date_str}",
            "description": f"*Goal: {goal}*\n\n\"Preparation is the only variable we control.\"",
            "color": color,
            "fields": [
                {
                    "name": "🔥 Calories",
                    "value": f"`{bar(cal_pct)}` {consumed['calories']:.0f} / {targets['calories']:.0f} kcal ({cal_pct}%)",
                    "inline": False
                },
                {
                    "name": "💪 Protein",
                    "value": f"`{bar(prot_pct)}` {consumed['protein']:.1f} / {targets['protein']:.1f}g ({prot_pct}%)",
                    "inline": True
                },
                {
                    "name": "🍞 Carbs",
                    "value": f"`{bar(carbs_pct)}` {consumed['carbs']:.1f} / {targets['carbs']:.1f}g ({carbs_pct}%)",
                    "inline": True
                },
                {
                    "name": "🥑 Fat",
                    "value": f"`{bar(fat_pct)}` {consumed['fat']:.1f} / {targets['fat']:.1f}g ({fat_pct}%)",
                    "inline": True
                },
            ],
            "footer": {
                "text": "Fourm Fitness — Strong Fourm. Strong Future."
            }
        }

        payload = {"embeds": [embed]}
        resp = requests.post(webhook_url, json=payload, timeout=6)
        return resp.status_code in (200, 204)
    except Exception:
        return False
