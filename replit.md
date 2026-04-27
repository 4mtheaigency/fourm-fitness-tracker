# CalorieFit Pro

A calorie and macro tracking app built with Streamlit + Python + SQLite.

## Overview
Reconciled from three build artifacts (design → build → integration):
- **Design (ChatGPT):** User profiles, food logging, macro tracking, food recommendations, reporting
- **Build (Claude):** Python/Streamlit, SQLite, Plotly, settings/models/services architecture
- **Integration (Gemini):** Google Cloud plan adapted to Replit-native SQLite instead

## Architecture

```
app.py                  # Main Streamlit application (all pages)
config/settings.py      # App settings, macro ratios, activity multipliers
models/user.py          # UserProfile dataclass + BMR/TDEE calculation
models/food.py          # FoodItem + FoodLog dataclasses
database/db.py          # SQLite operations (init, seed, CRUD for users/foods/logs)
services/nutrition.py   # Nutrition calculations + food recommendation engine
data/                   # SQLite database stored here (auto-created)
requirements.txt        # Python dependencies
```

## Features
- **User Profiles** — multiple profiles with BMR/TDEE calculation (Mifflin-St Jeor)
- **Dashboard** — calorie gauge, macro progress bars, macro donut chart, daily log table
- **Log Food** — search 40+ seeded foods across 5 categories, log by meal, delete entries
- **Recommendations** — smart scoring algorithm matches remaining macros to best foods
- **History** — 14-day line + bar charts vs targets, period averages
- **Add Food** — custom food database entries per 100g

## Running
```
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
```

## Dependencies
- streamlit 1.32.0, pandas 2.1.0, numpy 1.25.0, plotly 5.15.0
- python-dotenv 1.0.0, requests 2.31.0
- sqlite3 (stdlib), datetime, json, logging (all stdlib)

## Notes
- No external API keys required — uses a seeded local food database (40+ foods)
- USDA API key optional (env var `USDA_API_KEY`) for future food search extension
- Database auto-initialises and seeds on first run
