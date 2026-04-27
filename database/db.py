import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Tuple
from config.settings import settings


def get_connection():
    os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            height_cm REAL NOT NULL,
            weight_kg REAL NOT NULL,
            activity_level TEXT NOT NULL,
            goal TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories_per_100g REAL NOT NULL,
            protein_per_100g REAL NOT NULL,
            carbs_per_100g REAL NOT NULL,
            fat_per_100g REAL NOT NULL,
            fiber_per_100g REAL DEFAULT 0,
            category TEXT DEFAULT 'General'
        );

        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            quantity_g REAL NOT NULL,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            fiber REAL NOT NULL,
            log_date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (food_id) REFERENCES foods(id)
        );
    """)
    conn.commit()
    conn.close()


def seed_foods():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM foods")
    count = cur.fetchone()[0]
    if count > 0:
        conn.close()
        return

    foods = [
        # Proteins
        ("Chicken Breast (cooked)", 165, 31.0, 0.0, 3.6, 0.0, "Protein"),
        ("Salmon (cooked)", 208, 20.0, 0.0, 13.0, 0.0, "Protein"),
        ("Tuna (canned in water)", 116, 26.0, 0.0, 0.8, 0.0, "Protein"),
        ("Eggs (whole)", 155, 13.0, 1.1, 11.0, 0.0, "Protein"),
        ("Greek Yogurt (plain, 0%)", 59, 10.0, 3.6, 0.4, 0.0, "Protein"),
        ("Cottage Cheese (low fat)", 72, 12.4, 2.7, 1.0, 0.0, "Protein"),
        ("Turkey Breast (cooked)", 135, 30.0, 0.0, 1.0, 0.0, "Protein"),
        ("Beef (lean, cooked)", 215, 26.0, 0.0, 12.0, 0.0, "Protein"),
        ("Shrimp (cooked)", 99, 24.0, 0.0, 0.3, 0.0, "Protein"),
        ("Tofu (firm)", 76, 8.0, 1.9, 4.8, 0.3, "Protein"),
        ("Lentils (cooked)", 116, 9.0, 20.0, 0.4, 7.9, "Protein"),
        ("Black Beans (cooked)", 132, 8.9, 23.7, 0.5, 8.7, "Protein"),
        ("Chickpeas (cooked)", 164, 8.9, 27.4, 2.6, 7.6, "Protein"),
        ("Whey Protein Powder", 375, 80.0, 7.5, 4.0, 0.0, "Protein"),
        # Carbohydrates
        ("Brown Rice (cooked)", 112, 2.6, 23.5, 0.9, 1.8, "Carbs"),
        ("White Rice (cooked)", 130, 2.7, 28.2, 0.3, 0.4, "Carbs"),
        ("Oats (rolled, dry)", 389, 17.0, 66.0, 7.0, 10.6, "Carbs"),
        ("Sweet Potato (baked)", 90, 2.0, 20.7, 0.1, 3.3, "Carbs"),
        ("Quinoa (cooked)", 120, 4.4, 21.3, 1.9, 2.8, "Carbs"),
        ("Whole Wheat Bread", 247, 13.0, 41.0, 3.4, 6.0, "Carbs"),
        ("White Pasta (cooked)", 131, 5.0, 25.0, 1.1, 1.8, "Carbs"),
        ("Banana", 89, 1.1, 23.0, 0.3, 2.6, "Carbs"),
        ("Apple", 52, 0.3, 14.0, 0.2, 2.4, "Carbs"),
        ("Blueberries", 57, 0.7, 14.5, 0.3, 2.4, "Carbs"),
        ("Orange", 47, 0.9, 12.0, 0.1, 2.4, "Carbs"),
        ("Potato (boiled)", 87, 1.9, 20.0, 0.1, 1.8, "Carbs"),
        # Fats
        ("Avocado", 160, 2.0, 9.0, 15.0, 7.0, "Fats"),
        ("Almonds", 579, 21.0, 22.0, 50.0, 12.5, "Fats"),
        ("Walnuts", 654, 15.0, 14.0, 65.0, 6.7, "Fats"),
        ("Olive Oil", 884, 0.0, 0.0, 100.0, 0.0, "Fats"),
        ("Peanut Butter (natural)", 588, 25.0, 20.0, 50.0, 6.0, "Fats"),
        ("Chia Seeds", 486, 17.0, 42.0, 31.0, 34.4, "Fats"),
        ("Flaxseeds", 534, 18.0, 29.0, 42.0, 27.3, "Fats"),
        ("Cheddar Cheese", 402, 25.0, 1.3, 33.0, 0.0, "Fats"),
        ("Whole Milk", 61, 3.2, 4.8, 3.3, 0.0, "Fats"),
        # Vegetables
        ("Broccoli (cooked)", 35, 2.4, 7.2, 0.4, 3.3, "Vegetables"),
        ("Spinach (raw)", 23, 2.9, 3.6, 0.4, 2.2, "Vegetables"),
        ("Kale (raw)", 49, 4.3, 9.0, 0.9, 3.6, "Vegetables"),
        ("Carrots (raw)", 41, 0.9, 10.0, 0.2, 2.8, "Vegetables"),
        ("Bell Pepper (raw)", 31, 1.0, 6.0, 0.3, 2.1, "Vegetables"),
        ("Cucumber (raw)", 15, 0.7, 3.6, 0.1, 0.5, "Vegetables"),
        ("Tomato (raw)", 18, 0.9, 3.9, 0.2, 1.2, "Vegetables"),
        ("Mushrooms (raw)", 22, 3.1, 3.3, 0.3, 1.0, "Vegetables"),
        ("Zucchini (raw)", 17, 1.2, 3.1, 0.3, 1.0, "Vegetables"),
        ("Cauliflower (cooked)", 23, 1.8, 4.5, 0.5, 2.0, "Vegetables"),
    ]

    cur.executemany("""
        INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, fiber_per_100g, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, foods)
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def save_user(name, age, gender, height_cm, weight_kg, activity_level, goal) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (name, age, gender, height_cm, weight_kg, activity_level, goal)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, age, gender, height_cm, weight_kg, activity_level, goal))
    user_id = cur.lastrowid
    conn.commit()
    conn.close()
    return user_id


def update_user(user_id, name, age, gender, height_cm, weight_kg, activity_level, goal):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET name=?, age=?, gender=?, height_cm=?, weight_kg=?, activity_level=?, goal=?
        WHERE id=?
    """, (name, age, gender, height_cm, weight_kg, activity_level, goal, user_id))
    conn.commit()
    conn.close()


def search_foods(query: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM foods WHERE LOWER(name) LIKE ? ORDER BY category, name", (f"%{query.lower()}%",))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_foods():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM foods ORDER BY category, name")
    rows = cur.fetchall()
    conn.close()
    return rows


def get_food(food_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM foods WHERE id = ?", (food_id,))
    row = cur.fetchone()
    conn.close()
    return row


def add_custom_food(name, calories, protein, carbs, fat, fiber=0.0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, fiber_per_100g, category)
        VALUES (?, ?, ?, ?, ?, ?, 'Custom')
    """, (name, calories, protein, carbs, fat, fiber))
    food_id = cur.lastrowid
    conn.commit()
    conn.close()
    return food_id


def log_food(user_id, food_id, food_name, quantity_g, calories, protein, carbs, fat, fiber, log_date, meal_type):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO food_logs (user_id, food_id, food_name, quantity_g, calories, protein, carbs, fat, fiber, log_date, meal_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, food_id, food_name, quantity_g, calories, protein, carbs, fat, fiber, log_date, meal_type))
    conn.commit()
    conn.close()


def get_logs_for_date(user_id: int, date: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM food_logs WHERE user_id = ? AND log_date = ? ORDER BY meal_type, id
    """, (user_id, date))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_logs_for_range(user_id: int, start_date: str, end_date: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT log_date,
               SUM(calories) as total_calories,
               SUM(protein) as total_protein,
               SUM(carbs) as total_carbs,
               SUM(fat) as total_fat,
               SUM(fiber) as total_fiber
        FROM food_logs
        WHERE user_id = ? AND log_date BETWEEN ? AND ?
        GROUP BY log_date
        ORDER BY log_date
    """, (user_id, start_date, end_date))
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_log_entry(log_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM food_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()
