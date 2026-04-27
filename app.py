import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta, date

from database.db import (
    init_db, seed_foods,
    get_all_users, get_user, save_user, update_user,
    search_foods, get_all_foods, get_food, add_custom_food,
    log_food, get_logs_for_date, get_logs_for_range, delete_log_entry
)
from services.nutrition import calculate_targets, get_remaining, recommend_foods, summarise_day
from services.food_api import search_open_food_facts
from services.discord import send_daily_summary

# ─── Page Config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fourm Fitness — Nutrition Tracker",
    page_icon="fourm_logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Init ────────────────────────────────────────────────────────────────────────
init_db()
seed_foods()

# ─── Session State ───────────────────────────────────────────────────────────────
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'log_date' not in st.session_state:
    st.session_state.log_date = date.today()
if 'discord_webhook' not in st.session_state:
    st.session_state.discord_webhook = ""

# ─── CSS — Clean Light Theme ──────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Reset & base ── */
  [data-testid="stAppViewContainer"] { background: #f4f6fb; }
  [data-testid="stSidebar"] {
      background: #ffffff;
      border-right: 1px solid #e2e8f0;
  }
  [data-testid="stSidebar"] * { color: #1e293b !important; }
  html, body, p, span, div, li { color: #334155; }
  h1 { color: #0f172a !important; font-size: 1.7rem !important; font-weight: 800 !important; }
  h2 { color: #1e293b !important; font-size: 1.3rem !important; font-weight: 700 !important; }
  h3 { color: #334155 !important; font-size: 1.05rem !important; font-weight: 600 !important; }

  /* ── Sidebar brand ── */
  .brand-logo { display:block; margin:0 auto 4px; max-width:120px; }
  .brand-name {
      text-align:center; font-size:1rem; font-weight:900;
      letter-spacing:.18em; text-transform:uppercase; color:#0f172a !important;
      margin:4px 0 2px;
  }
  .brand-tagline {
      text-align:center; font-size:.6rem; letter-spacing:.14em;
      text-transform:uppercase; color:#1e64ff !important; margin:0 0 10px;
  }

  /* ── Cards ── */
  .ff-card {
      background:#ffffff; border-radius:14px; padding:20px 22px;
      box-shadow:0 1px 4px rgba(0,0,0,.06), 0 4px 16px rgba(30,100,255,.04);
      border:1px solid #e8eef8; margin-bottom:12px;
  }
  .ff-card-blue {
      background:linear-gradient(135deg,#1e64ff 0%,#0a40d0 100%);
      border-radius:14px; padding:20px 22px; color:#fff;
      box-shadow:0 4px 20px rgba(30,100,255,.25); margin-bottom:12px;
  }
  .ff-card-blue p, .ff-card-blue span, .ff-card-blue div { color:#fff !important; }

  /* ── Stat tiles ── */
  .stat-tile {
      background:#ffffff; border:1px solid #e2e8f0; border-radius:12px;
      padding:16px 10px; text-align:center;
      box-shadow:0 1px 3px rgba(0,0,0,.05);
  }
  .stat-tile .val { font-size:1.7rem; font-weight:800; color:#1e64ff; line-height:1; }
  .stat-tile .lbl { font-size:.65rem; letter-spacing:.1em; text-transform:uppercase; color:#94a3b8; margin-top:4px; }
  .stat-tile .unit { font-size:.7rem; color:#64748b; }

  /* ── Macro bars ── */
  .macro-row { margin-bottom:14px; }
  .macro-row-head { display:flex; justify-content:space-between; font-size:.82rem; color:#475569; margin-bottom:4px; }
  .macro-row-head .mlabel { font-weight:600; color:#1e293b; }
  .bar-bg { background:#f1f5f9; border-radius:6px; height:10px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:6px; transition:width .4s ease; }

  /* ── Motto strip ── */
  .motto-strip {
      background:linear-gradient(90deg,#eef2ff 0%,#f0f7ff 100%);
      border-left:3px solid #1e64ff; border-radius:0 10px 10px 0;
      padding:10px 16px; margin-bottom:16px;
      font-size:.82rem; font-style:italic; color:#334155;
  }

  /* ── Badges ── */
  .badge {
      display:inline-block; padding:2px 10px; border-radius:20px;
      font-size:.7rem; font-weight:700; letter-spacing:.06em;
      text-transform:uppercase;
  }
  .badge-blue { background:#dbeafe; color:#1d4ed8; }
  .badge-green { background:#dcfce7; color:#15803d; }
  .badge-orange { background:#ffedd5; color:#c2410c; }

  /* ── Food library card ── */
  .food-card {
      background:#fff; border:1px solid #e2e8f0; border-radius:12px;
      padding:14px 16px; margin-bottom:8px;
      box-shadow:0 1px 2px rgba(0,0,0,.04);
      transition: box-shadow .2s;
  }
  .food-card:hover { box-shadow:0 4px 12px rgba(30,100,255,.1); }
  .food-card .food-name { font-size:.9rem; font-weight:700; color:#0f172a; margin-bottom:4px; }
  .food-card .food-macros { font-size:.75rem; color:#64748b; }

  /* ── Recommend card ── */
  .rec-card {
      background:#fff; border:1px solid #dbeafe; border-radius:12px;
      padding:14px 16px; margin-bottom:10px;
      box-shadow:0 2px 8px rgba(30,100,255,.07);
  }
  .rec-card .rname { font-size:.88rem; font-weight:700; color:#0f172a; }
  .rec-card .rreason { font-size:.73rem; color:#1e64ff; margin:3px 0 8px; }
  .rec-card .rmacros { font-size:.75rem; color:#64748b; }

  /* ── Section title ── */
  .section-title {
      font-size:.72rem; font-weight:700; letter-spacing:.14em;
      text-transform:uppercase; color:#94a3b8; margin-bottom:10px;
      padding-bottom:6px; border-bottom:1px solid #f1f5f9;
  }

  /* ── Footer ── */
  .ff-footer {
      text-align:center; font-size:.65rem; letter-spacing:.18em;
      text-transform:uppercase; color:#cbd5e1; padding:20px 0 4px;
  }

  /* ── Discord share button style ── */
  .discord-btn {
      display:inline-block; background:#5865F2; color:#fff !important;
      border-radius:8px; padding:8px 16px; font-size:.82rem;
      font-weight:600; letter-spacing:.04em; cursor:pointer; border:none;
  }

  /* ── Streamlit widget tweaks ── */
  [data-testid="metric-container"] {
      background:#ffffff; border:1px solid #e2e8f0;
      border-radius:10px; padding:12px 16px;
  }
  .stButton > button {
      border-radius:10px !important; font-weight:600 !important;
      letter-spacing:.04em !important; padding:0.5rem 1.2rem !important;
  }
  .stButton > button[kind="primary"] {
      background:linear-gradient(90deg,#1040cc,#1e64ff) !important;
      border:none !important; color:#fff !important;
  }
  .stButton > button[kind="primary"]:hover {
      background:linear-gradient(90deg,#1e64ff,#3b82ff) !important;
      box-shadow:0 4px 14px rgba(30,100,255,.35) !important;
  }
  [data-testid="stTextInput"] input,
  [data-testid="stNumberInput"] input,
  [data-testid="stSelectbox"] [data-baseweb="select"] {
      border-radius:8px !important;
  }

  /* ── Mobile ── */
  @media (max-width:768px) {
      h1 { font-size:1.35rem !important; }
      .stat-tile .val { font-size:1.3rem; }
      .ff-card, .rec-card, .food-card { padding:12px 14px; }
  }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────────
def macro_bar(label: str, consumed: float, target: float, color: str, unit: str = "g"):
    pct = min(consumed / target * 100, 100) if target > 0 else 0
    st.markdown(f"""
    <div class="macro-row">
      <div class="macro-row-head">
        <span class="mlabel">{label}</span>
        <span>{consumed:.1f} / {target:.1f}{unit} &nbsp;<strong>{pct:.0f}%</strong></span>
      </div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:{pct}%;background:{color};"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def calorie_gauge(consumed: float, target: float):
    upper = max(target * 1.25, consumed * 1.1, 500)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=consumed,
        delta={
            'reference': target, 'relative': False,
            'decreasing': {'color': '#16a34a'},
            'increasing': {'color': '#dc2626'}
        },
        gauge={
            'axis': {'range': [0, upper], 'tickcolor': '#94a3b8',
                     'tickfont': {'color': '#94a3b8', 'size': 10}},
            'bar': {'color': "#1e64ff"},
            'bgcolor': '#f1f5f9',
            'borderwidth': 0,
            'steps': [
                {'range': [0, target * 0.5], 'color': '#eff6ff'},
                {'range': [target * 0.5, target], 'color': '#dbeafe'},
                {'range': [target, upper], 'color': '#fee2e2'},
            ],
            'threshold': {
                'line': {'color': '#1e64ff', 'width': 3},
                'value': target
            }
        },
        title={'text': "Calories Today", 'font': {'color': '#334155', 'size': 13}},
        number={'font': {'color': '#0f172a', 'size': 36}, 'suffix': ' kcal'}
    ))
    fig.update_layout(
        height=230,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#334155'},
        margin=dict(t=40, b=0, l=20, r=20)
    )
    return fig


def stat_tile(col, label: str, value: str, unit: str = ""):
    col.markdown(f"""
    <div class="stat-tile">
      <div class="val">{value}</div>
      <div class="unit">{unit}</div>
      <div class="lbl">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("fourm_logo.png", use_column_width=True)
    st.markdown("""
    <div>
      <p class="brand-name">Fourm Fitness</p>
      <p class="brand-tagline">Strong Fourm. Strong Future.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    users = get_all_users()
    user_names = {u['id']: u['name'] for u in users}

    if users:
        selected_name = st.selectbox(
            "Active Profile",
            options=list(user_names.values()),
            index=0 if st.session_state.user_id is None or st.session_state.user_id not in user_names
                  else list(user_names.keys()).index(st.session_state.user_id)
        )
        st.session_state.user_id = [k for k, v in user_names.items() if v == selected_name][0]

    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "🍽️ Log Food", "🔍 Food Library", "💡 Recommendations",
         "📈 History", "👤 Profile", "➕ Add Food", "⚙️ Settings"],
        label_visibility="collapsed"
    )

    st.divider()

    log_date = st.date_input("Date", value=st.session_state.log_date, label_visibility="collapsed")
    st.caption(f"📅 {log_date.strftime('%a %d %b %Y')}")
    st.session_state.log_date = log_date

    if st.session_state.user_id:
        user_row = get_user(st.session_state.user_id)
        if user_row:
            targets = calculate_targets(
                user_row['weight_kg'], user_row['height_cm'], user_row['age'],
                user_row['gender'], user_row['activity_level'], user_row['goal']
            )
            logs = get_logs_for_date(st.session_state.user_id, str(log_date))
            consumed = summarise_day(logs)
            cal_pct = min(int(consumed['calories'] / targets['calories'] * 100), 100) if targets['calories'] else 0
            st.markdown(f"**{cal_pct}% of daily goal**")
            st.progress(cal_pct / 100)
            st.caption(f"{consumed['calories']:.0f} / {targets['calories']:.0f} kcal")

    st.markdown('<p class="ff-footer" style="color:#e2e8f0;">© Fourm Fitness</p>', unsafe_allow_html=True)


# ─── Guard: no profile ────────────────────────────────────────────────────────────
if not users and page not in ("👤 Profile", "⚙️ Settings"):
    st.markdown("""
    <div class="ff-card-blue">
      <h2 style="color:#fff;margin:0 0 6px">Welcome to Fourm Fitness 👋</h2>
      <p style="color:rgba(255,255,255,.85);margin:0">Set up your profile to get started with your nutrition journey.</p>
    </div>
    """, unsafe_allow_html=True)
    page = "👤 Profile"


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    if not st.session_state.user_id:
        st.info("Create a profile to see your dashboard.")
        st.stop()

    user_row = get_user(st.session_state.user_id)
    targets = calculate_targets(
        user_row['weight_kg'], user_row['height_cm'], user_row['age'],
        user_row['gender'], user_row['activity_level'], user_row['goal']
    )
    logs = get_logs_for_date(st.session_state.user_id, str(log_date))
    consumed = summarise_day(logs)
    remaining = get_remaining(targets, consumed)

    # Header
    st.markdown(f"## {user_row['name']}'s Dashboard")
    st.caption(f"{log_date.strftime('%A, %B %d, %Y')}  ·  Goal: **{user_row['goal']}**")
    st.markdown('<div class="motto-strip">"Preparation is the only variable we control."</div>',
                unsafe_allow_html=True)

    # Top stats row
    c1, c2, c3, c4 = st.columns(4)
    remaining_cal = int(remaining['calories'])
    cal_color = "#dc2626" if remaining_cal < 0 else "#1e64ff"
    stat_tile(c1, "Remaining", f'<span style="color:{cal_color}">{remaining_cal:+d}</span>', "kcal")
    stat_tile(c2, "Protein Left", f"{remaining['protein']:.0f}", "g")
    stat_tile(c3, "Carbs Left", f"{remaining['carbs']:.0f}", "g")
    stat_tile(c4, "Fat Left", f"{remaining['fat']:.0f}", "g")

    st.markdown("")

    col_left, col_right = st.columns([1, 1.5], gap="medium")

    with col_left:
        st.markdown('<div class="ff-card" style="padding:16px;">', unsafe_allow_html=True)
        st.plotly_chart(calorie_gauge(consumed['calories'], targets['calories']),
                        use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ff-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Macronutrients</div>', unsafe_allow_html=True)
        macro_bar("Protein", consumed['protein'], targets['protein'], "#1e64ff")
        macro_bar("Carbohydrates", consumed['carbs'], targets['carbs'], "#38bdf8")
        macro_bar("Fat", consumed['fat'], targets['fat'], "#818cf8")
        macro_bar("Fiber", consumed['fiber'], targets['fiber'], "#34d399")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # Discord share
        webhook = st.session_state.discord_webhook
        if webhook:
            if st.button("📣 Share to Discord", use_container_width=True):
                ok = send_daily_summary(webhook, user_row['name'], str(log_date),
                                        consumed, targets, user_row['goal'])
                if ok:
                    st.success("✅ Summary posted to Discord!")
                else:
                    st.error("❌ Failed to post. Check your webhook URL in Settings.")

        # Donut chart
        macro_vals = [consumed['protein'] * 4, consumed['carbs'] * 4, consumed['fat'] * 9]
        if sum(macro_vals) > 0:
            st.markdown('<div class="ff-card" style="padding:16px 16px 8px;">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Calorie Breakdown</div>', unsafe_allow_html=True)
            fig_donut = go.Figure(go.Pie(
                labels=['Protein', 'Carbs', 'Fat'],
                values=macro_vals,
                hole=0.6,
                marker_colors=['#1e64ff', '#38bdf8', '#818cf8'],
                textinfo='label+percent',
                textfont=dict(size=12, color='#334155'),
                hovertemplate='<b>%{label}</b><br>%{value:.0f} kcal<extra></extra>'
            ))
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font_color='#334155', showlegend=False,
                height=230, margin=dict(t=10, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ff-card" style="text-align:center;padding:32px 16px;">
              <p style="font-size:2rem;margin:0">🍽️</p>
              <p style="color:#94a3b8;margin:8px 0 0;font-size:.9rem;">No food logged yet today.<br>Head to <strong>Log Food</strong> to get started.</p>
            </div>""", unsafe_allow_html=True)

        # Meal log table
        if logs:
            st.markdown('<div class="ff-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Today\'s Log</div>', unsafe_allow_html=True)
            df = pd.DataFrame([dict(r) for r in logs])[
                ['meal_type', 'food_name', 'quantity_g', 'calories', 'protein', 'carbs', 'fat']]
            df.columns = ['Meal', 'Food', 'g', 'kcal', 'Protein', 'Carbs', 'Fat']
            df = df.sort_values('Meal')
            st.dataframe(df, use_container_width=True, hide_index=True,
                         column_config={
                             'kcal': st.column_config.NumberColumn(format="%.0f"),
                             'Protein': st.column_config.NumberColumn(format="%.1f"),
                             'Carbs': st.column_config.NumberColumn(format="%.1f"),
                             'Fat': st.column_config.NumberColumn(format="%.1f"),
                         })
            st.markdown('</div>', unsafe_allow_html=True)

    # Targets expander
    with st.expander("📐 Your Calculated Nutrition Targets"):
        t1, t2, t3, t4, t5, t6 = st.columns(6)
        for col, lbl, val, unit in zip(
            [t1, t2, t3, t4, t5, t6],
            ['BMR', 'TDEE', 'Cal Target', 'Protein', 'Carbs', 'Fat'],
            [targets['bmr'], targets['tdee'], targets['calories'],
             targets['protein'], targets['carbs'], targets['fat']],
            ['kcal', 'kcal', 'kcal', 'g', 'g', 'g']
        ):
            col.metric(lbl, f"{val:.0f} {unit}")

    st.markdown('<div class="ff-footer">Strong Fourm. Strong Future.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LOG FOOD
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🍽️ Log Food":
    st.markdown("## 🍽️ Log Food")
    if not st.session_state.user_id:
        st.info("Create a profile first.")
        st.stop()

    st.markdown('<div class="motto-strip">"Preparation is the only variable we control."</div>',
                unsafe_allow_html=True)

    query = st.text_input("🔍 Search your food database", placeholder="e.g. chicken, oats, banana…",
                          label_visibility="collapsed")
    foods = search_foods(query) if query else get_all_foods()

    col1, col2 = st.columns([2, 1])
    with col1:
        if not foods:
            st.warning("No foods found. Try the **Food Library** for live search, or **Add Food** to create a custom entry.")
        else:
            food_options = {f"{f['name']} ({f['category']})": f['id'] for f in foods}
            selected_label = st.selectbox("Select Food", list(food_options.keys()),
                                           label_visibility="collapsed")
            selected_id = food_options[selected_label]
            food = get_food(selected_id)
    with col2:
        meal_type = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"],
                                  label_visibility="collapsed")

    if foods:
        quantity = st.slider("Serving size (grams)", min_value=5, max_value=1000, value=100, step=5)

        if food:
            factor = quantity / 100
            calc = {k: round(food[f'{k}_per_100g'] * factor, 1)
                    for k in ['calories', 'protein', 'carbs', 'fat', 'fiber']}

            st.markdown('<div class="ff-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">Nutrition for {quantity}g of {food["name"]}</div>',
                        unsafe_allow_html=True)
            mc1, mc2, mc3, mc4, mc5 = st.columns(5)
            for col, lbl, val, unit in zip(
                [mc1, mc2, mc3, mc4, mc5],
                ['Calories', 'Protein', 'Carbs', 'Fat', 'Fiber'],
                [calc['calories'], calc['protein'], calc['carbs'], calc['fat'], calc['fiber']],
                ['kcal', 'g', 'g', 'g', 'g']
            ):
                col.metric(lbl, f"{val} {unit}")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(f"➕ Log {quantity}g to {meal_type}", type="primary", use_container_width=True):
                log_food(
                    st.session_state.user_id, food['id'], food['name'],
                    quantity, calc['calories'], calc['protein'],
                    calc['carbs'], calc['fat'], calc['fiber'],
                    str(log_date), meal_type
                )
                st.success(f"✅ Logged **{quantity}g of {food['name']}** to {meal_type}!")
                st.rerun()

    st.divider()

    st.markdown("### Remove a logged item")
    logs = get_logs_for_date(st.session_state.user_id, str(log_date))
    if logs:
        del_options = {
            f"[{r['meal_type']}] {r['food_name']} — {r['quantity_g']:.0f}g ({r['calories']:.0f} kcal)": r['id']
            for r in logs
        }
        del_label = st.selectbox("Select entry", list(del_options.keys()), label_visibility="collapsed")
        if st.button("🗑️ Remove", type="secondary"):
            delete_log_entry(del_options[del_label])
            st.success("Removed.")
            st.rerun()
    else:
        st.caption("Nothing logged for this date yet.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: FOOD LIBRARY (Open Food Facts)
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Food Library":
    st.markdown("## 🔍 Food Library")
    st.caption("Live search powered by Open Food Facts — 3 million+ products worldwide")
    if not st.session_state.user_id:
        st.info("Create a profile first.")
        st.stop()

    st.markdown('<div class="motto-strip">"Preparation is the only variable we control." — Know exactly what you eat.</div>',
                unsafe_allow_html=True)

    query = st.text_input("Search millions of foods", placeholder="e.g. Greek Yogurt, Brown Rice, Quest Bar…",
                           label_visibility="collapsed")

    col_q, col_m = st.columns([3, 1])
    with col_q:
        quantity = st.slider("Serving size (grams)", min_value=5, max_value=1000, value=100, step=5,
                              key="lib_quantity")
    with col_m:
        meal_type = st.selectbox("Meal", ["Breakfast", "Lunch", "Dinner", "Snack"], key="lib_meal")

    if query and len(query) >= 2:
        with st.spinner("Searching food library…"):
            results = search_open_food_facts(query)

        if not results:
            st.warning("No results found. Try a different search term or check your connection.")
        else:
            st.markdown(f"**{len(results)} results for '{query}'**")

            for idx, item in enumerate(results):
                factor = quantity / 100
                cal = round(item['calories_per_100g'] * factor, 1)
                prot = round(item['protein_per_100g'] * factor, 1)
                carbs = round(item['carbs_per_100g'] * factor, 1)
                fat = round(item['fat_per_100g'] * factor, 1)
                fiber = round(item['fiber_per_100g'] * factor, 1)

                with st.container():
                    r1, r2 = st.columns([3, 1])
                    with r1:
                        st.markdown(f"""
                        <div class="food-card">
                          <div class="food-name">{item['name']}</div>
                          <div class="food-macros">
                            🔥 <strong>{cal}</strong> kcal &nbsp;|&nbsp;
                            💪 <strong>{prot}g</strong> protein &nbsp;|&nbsp;
                            🍞 <strong>{carbs}g</strong> carbs &nbsp;|&nbsp;
                            🥑 <strong>{fat}g</strong> fat
                            &nbsp;&nbsp;<span class="badge badge-blue">per {quantity}g</span>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with r2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"Log to {meal_type}", key=f"lib_log_{idx}", use_container_width=True):
                            food_id = add_custom_food(
                                item['name'], item['calories_per_100g'],
                                item['protein_per_100g'], item['carbs_per_100g'],
                                item['fat_per_100g'], item['fiber_per_100g']
                            )
                            log_food(
                                st.session_state.user_id, food_id, item['name'],
                                quantity, cal, prot, carbs, fat, fiber,
                                str(log_date), meal_type
                            )
                            st.success(f"✅ Logged {quantity}g of {item['name']}!")
                            st.rerun()
    else:
        st.markdown("""
        <div class="ff-card" style="text-align:center;padding:40px 20px;">
          <p style="font-size:2.5rem;margin:0">🌎</p>
          <p style="color:#94a3b8;font-size:.95rem;margin:12px 0 0;">
            Type a food name above to search 3 million+ products from Open Food Facts.<br>
            Results include full macro data per 100g.
          </p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💡 Recommendations":
    st.markdown("## 💡 What to Eat Next")
    if not st.session_state.user_id:
        st.info("Create a profile first.")
        st.stop()

    user_row = get_user(st.session_state.user_id)
    targets = calculate_targets(
        user_row['weight_kg'], user_row['height_cm'], user_row['age'],
        user_row['gender'], user_row['activity_level'], user_row['goal']
    )
    logs = get_logs_for_date(st.session_state.user_id, str(log_date))
    consumed = summarise_day(logs)
    remaining = get_remaining(targets, consumed)

    st.caption(f"Based on what you've logged today — goal: **{user_row['goal']}**")
    st.markdown('<div class="motto-strip">"Preparation is the only variable we control." — Choose your next meal with intent.</div>',
                unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    for col, lbl, val, unit, good_when_pos in zip(
        [r1, r2, r3, r4],
        ['Calories', 'Protein', 'Carbs', 'Fat'],
        [remaining['calories'], remaining['protein'], remaining['carbs'], remaining['fat']],
        ['kcal', 'g', 'g', 'g'],
        [True, True, True, True]
    ):
        color = "#1e64ff" if val >= 0 else "#dc2626"
        col.markdown(f"""
        <div class="stat-tile">
          <div class="val" style="color:{color}">{val:.0f}</div>
          <div class="unit">{unit} remaining</div>
          <div class="lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    if remaining['calories'] <= 50:
        st.markdown("""
        <div class="ff-card-blue">
          <h3 style="color:#fff;margin:0 0 4px">🎯 Goal reached!</h3>
          <p style="color:rgba(255,255,255,.85);margin:0">You've hit your calorie target for today. Great work — rest and recover well.</p>
        </div>""", unsafe_allow_html=True)
    else:
        all_foods = get_all_foods()
        recs = recommend_foods(remaining, [dict(f) for f in all_foods], top_n=9)
        if not recs:
            st.info("Your remaining macros are very low — you're close to your daily targets.")
        else:
            st.markdown("### Top Food Picks")
            cats = sorted(set(r['category'] for r in recs))
            for cat in cats:
                cat_recs = [r for r in recs if r['category'] == cat]
                if not cat_recs:
                    continue
                st.markdown(f'<div class="section-title">{cat}</div>', unsafe_allow_html=True)
                cols = st.columns(min(3, len(cat_recs)))
                for col, rec in zip(cols, cat_recs):
                    with col:
                        st.markdown(f"""
                        <div class="rec-card">
                          <div class="rname">{rec['name']}</div>
                          <div class="rreason">✓ {rec['reason']}</div>
                          <div class="rmacros">
                            🔥 {rec['calories_per_100g']:.0f} kcal/100g<br>
                            💪 {rec['protein_per_100g']:.1f}g &nbsp;
                            🍞 {rec['carbs_per_100g']:.1f}g &nbsp;
                            🥑 {rec['fat_per_100g']:.1f}g
                          </div>
                        </div>""", unsafe_allow_html=True)

    st.divider()
    with st.expander("📌 Goal-Specific Advice"):
        goal = user_row['goal']
        if goal == 'Lose Weight':
            st.markdown("""
**Fat loss tips:**
- Prioritise high-protein, low-calorie foods (chicken breast, Greek yogurt, eggs, cottage cheese)
- Fill half your plate with non-starchy vegetables — they're very low calorie and high volume
- Choose complex carbs in moderation (sweet potato, oats, quinoa)
- Watch liquid calories — they add up fast without making you feel full
""")
        elif goal == 'Gain Muscle':
            st.markdown("""
**Muscle gain tips:**
- Target 1.8–2.2g protein per kg of bodyweight daily
- Time carbs around training — oats pre-workout, rice or potato post-workout
- Don't shy away from healthy fats (avocado, whole eggs, nuts)
- Eat in a controlled surplus — quality matters more than quantity
""")
        else:
            st.markdown("""
**Maintenance tips:**
- Balance macros at every meal — protein + carbs + fat + colour
- Track consistently so you catch trends early
- Hydration matters — thirst often mimics hunger
- Adjust if bodyweight shifts over 2–3 weeks
""")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 History":
    st.markdown("## 📈 Intake History")
    if not st.session_state.user_id:
        st.info("Create a profile first.")
        st.stop()

    user_row = get_user(st.session_state.user_id)
    targets = calculate_targets(
        user_row['weight_kg'], user_row['height_cm'], user_row['age'],
        user_row['gender'], user_row['activity_level'], user_row['goal']
    )

    c1, c2 = st.columns(2)
    with c1:
        start = st.date_input("From", value=date.today() - timedelta(days=13))
    with c2:
        end = st.date_input("To", value=date.today())

    rows = get_logs_for_range(st.session_state.user_id, str(start), str(end))

    if not rows:
        st.markdown("""
        <div class="ff-card" style="text-align:center;padding:40px;">
          <p style="font-size:2rem;margin:0">📅</p>
          <p style="color:#94a3b8;margin:10px 0 0;">No data for this date range yet.<br>Start logging meals to see your progress.</p>
        </div>""", unsafe_allow_html=True)
    else:
        df = pd.DataFrame([dict(r) for r in rows])
        df['log_date'] = pd.to_datetime(df['log_date'])

        # Summary stats
        st.markdown('<div class="ff-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Period Average</div>', unsafe_allow_html=True)
        s1, s2, s3, s4, s5 = st.columns(5)
        for col, lbl, val, unit in zip(
            [s1, s2, s3, s4, s5],
            ['Avg Calories', 'Avg Protein', 'Avg Carbs', 'Avg Fat', 'Days Tracked'],
            [df['total_calories'].mean(), df['total_protein'].mean(),
             df['total_carbs'].mean(), df['total_fat'].mean(), len(df)],
            ['kcal', 'g', 'g', 'g', '']
        ):
            col.metric(lbl, f"{val:.0f} {unit}".strip())
        st.markdown('</div>', unsafe_allow_html=True)

        # Calorie chart
        fig_cal = go.Figure()
        fig_cal.add_trace(go.Scatter(
            x=df['log_date'], y=df['total_calories'],
            mode='lines+markers', name='Calories',
            line=dict(color='#1e64ff', width=2.5),
            marker=dict(size=7, color='#1e64ff', line=dict(color='white', width=2)),
            fill='tozeroy', fillcolor='rgba(30,100,255,0.06)'
        ))
        fig_cal.add_hline(y=targets['calories'], line_dash='dash',
                          line_color='#38bdf8', line_width=1.5,
                          annotation_text='Target', annotation_font_color='#38bdf8')
        fig_cal.update_layout(
            title="Daily Calories vs Target",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#334155', height=280,
            xaxis=dict(gridcolor='#f1f5f9', tickcolor='#94a3b8'),
            yaxis=dict(gridcolor='#f1f5f9', tickcolor='#94a3b8'),
            margin=dict(t=40, b=0, l=0, r=0), showlegend=False
        )
        st.plotly_chart(fig_cal, use_container_width=True, config={'displayModeBar': False})

        # Macro bars
        fig_macro = go.Figure()
        for col_key, color, label in [
            ('total_protein', '#1e64ff', 'Protein'),
            ('total_carbs', '#38bdf8', 'Carbs'),
            ('total_fat', '#818cf8', 'Fat')
        ]:
            fig_macro.add_trace(go.Bar(
                x=df['log_date'], y=df[col_key],
                name=label, marker_color=color, opacity=0.85
            ))

        fig_macro.update_layout(
            title="Daily Macros",
            barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#334155', height=280,
            xaxis=dict(gridcolor='#f1f5f9'), yaxis=dict(gridcolor='#f1f5f9'),
            margin=dict(t=40, b=0, l=0, r=0),
            legend=dict(orientation='h', y=1.12, x=0, font_size=11)
        )
        st.plotly_chart(fig_macro, use_container_width=True, config={'displayModeBar': False})

        with st.expander("Raw data"):
            display_df = df.copy()
            display_df['log_date'] = display_df['log_date'].dt.strftime('%Y-%m-%d')
            display_df.columns = ['Date', 'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber']
            st.dataframe(display_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Profile":
    st.markdown("## 👤 Profile")

    tab_labels = ["Edit Profile" if users else "Create Profile"]
    if users:
        tab_labels.append("New Profile")
    tabs = st.tabs(tab_labels)

    activity_options = [
        "Sedentary (little or no exercise)",
        "Lightly Active (1-3 days/week)",
        "Moderately Active (3-5 days/week)",
        "Very Active (6-7 days/week)",
        "Extra Active (physical job or 2x training)"
    ]

    def profile_form(defaults=None):
        d = defaults or {}
        name = st.text_input("Name *", value=d.get('name', ''), placeholder="Your name")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Age", min_value=10, max_value=100, value=int(d.get('age', 25)))
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0,
                                      value=float(d.get('height_cm', 170.0)), step=0.5)
            act_idx = activity_options.index(d['activity_level']) \
                if d.get('activity_level') in activity_options else 2
            activity = st.selectbox("Activity Level", activity_options, index=act_idx)
        with c2:
            gender = st.selectbox("Gender", ["Male", "Female"],
                                   index=0 if d.get('gender', 'Male') == 'Male' else 1)
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0,
                                      value=float(d.get('weight_kg', 70.0)), step=0.5)
            goal = st.selectbox("Goal", ["Lose Weight", "Maintain Weight", "Gain Muscle"],
                index={"Lose Weight": 0, "Maintain Weight": 1, "Gain Muscle": 2}.get(
                    d.get('goal', 'Maintain Weight'), 1))
        return name, age, gender, height, weight, activity, goal

    with tabs[0]:
        if users and st.session_state.user_id:
            row = get_user(st.session_state.user_id)
            defaults = dict(row) if row else {}
        else:
            defaults = {}

        name, age, gender, height, weight, activity, goal = profile_form(defaults)

        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Please enter a name.")
            elif users and st.session_state.user_id:
                update_user(st.session_state.user_id, name, age, gender, height, weight, activity, goal)
                st.success("✅ Profile updated!")
                st.rerun()
            else:
                uid = save_user(name, age, gender, height, weight, activity, goal)
                st.session_state.user_id = uid
                st.success(f"✅ Profile created for {name}!")
                st.rerun()

        if users and st.session_state.user_id:
            row = get_user(st.session_state.user_id)
            if row:
                targets = calculate_targets(
                    row['weight_kg'], row['height_cm'], row['age'],
                    row['gender'], row['activity_level'], row['goal']
                )
                with st.expander("📊 Your Nutrition Targets"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("BMR", f"{targets['bmr']:.0f} kcal")
                    c2.metric("TDEE", f"{targets['tdee']:.0f} kcal")
                    c3.metric("Daily Target", f"{targets['calories']:.0f} kcal")
                    c4, c5, c6 = st.columns(3)
                    c4.metric("Protein", f"{targets['protein']:.0f} g")
                    c5.metric("Carbs", f"{targets['carbs']:.0f} g")
                    c6.metric("Fat", f"{targets['fat']:.0f} g")

    if len(tab_labels) > 1:
        with tabs[1]:
            name, age, gender, height, weight, activity, goal = profile_form()
            if st.button("➕ Create New Profile", type="primary", use_container_width=True):
                if not name.strip():
                    st.error("Please enter a name.")
                else:
                    uid = save_user(name, age, gender, height, weight, activity, goal)
                    st.session_state.user_id = uid
                    st.success(f"✅ New profile created for {name}!")
                    st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD FOOD
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Food":
    st.markdown("## ➕ Add Custom Food")
    st.caption("Values per 100g")

    with st.form("add_food_form", clear_on_submit=True):
        food_name = st.text_input("Food Name *", placeholder="e.g. Homemade Granola")
        c1, c2 = st.columns(2)
        with c1:
            calories = st.number_input("Calories (kcal/100g) *", min_value=0.0, max_value=900.0, step=1.0)
            carbs = st.number_input("Carbohydrates (g/100g)", min_value=0.0, max_value=100.0, step=0.1)
            fiber = st.number_input("Fiber (g/100g)", min_value=0.0, max_value=100.0, step=0.1)
        with c2:
            protein = st.number_input("Protein (g/100g)", min_value=0.0, max_value=100.0, step=0.1)
            fat = st.number_input("Fat (g/100g)", min_value=0.0, max_value=100.0, step=0.1)

        if st.form_submit_button("Add to Database", type="primary", use_container_width=True):
            if not food_name.strip():
                st.error("Food name is required.")
            elif calories <= 0:
                st.error("Calories must be greater than 0.")
            else:
                add_custom_food(food_name.strip(), calories, protein, carbs, fat, fiber)
                st.success(f"✅ **{food_name}** added!")

    st.divider()
    st.markdown("### Food Database")
    all_foods = get_all_foods()
    if all_foods:
        df = pd.DataFrame([dict(f) for f in all_foods])[
            ['name', 'category', 'calories_per_100g', 'protein_per_100g',
             'carbs_per_100g', 'fat_per_100g', 'fiber_per_100g']]
        df.columns = ['Food', 'Category', 'kcal', 'Protein(g)', 'Carbs(g)', 'Fat(g)', 'Fiber(g)']
        st.dataframe(df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    st.markdown("## ⚙️ Settings")

    st.markdown("### 🔗 Discord Integration")
    st.markdown("""
    <div class="ff-card">
      <p style="margin:0 0 8px;font-weight:600;">Share your daily nutrition summary to your Discord server</p>
      <p style="margin:0;font-size:.85rem;color:#64748b;">
        To set this up: open Discord → go to your server → right-click a channel → Edit Channel →
        Integrations → Webhooks → New Webhook → Copy Webhook URL
      </p>
    </div>
    """, unsafe_allow_html=True)

    webhook = st.text_input(
        "Discord Webhook URL",
        value=st.session_state.discord_webhook,
        placeholder="https://discord.com/api/webhooks/...",
        type="password"
    )
    col_save, col_test = st.columns(2)
    with col_save:
        if st.button("💾 Save Webhook", type="primary", use_container_width=True):
            st.session_state.discord_webhook = webhook
            st.success("✅ Webhook saved for this session!")
    with col_test:
        if st.button("🧪 Test Webhook", use_container_width=True):
            if not webhook:
                st.error("Enter a webhook URL first.")
            else:
                import requests
                try:
                    resp = requests.post(webhook, json={"content": "✅ **Fourm Fitness** — webhook connected! *Strong Fourm. Strong Future.*"}, timeout=5)
                    if resp.status_code in (200, 204):
                        st.success("✅ Test message sent to Discord!")
                    else:
                        st.error(f"Failed: HTTP {resp.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("### 📣 How Discord sharing works")
    st.markdown("""
    Once a webhook is saved:
    - Go to your **Dashboard**
    - Click **Share to Discord** — your daily nutrition summary will be posted as a formatted embed to your Discord channel
    - Your community and clients can see your progress in real time
    """)

    st.divider()
    st.markdown("### ℹ️ App Info")
    st.markdown("""
    | | |
    |---|---|
    | **App** | Fourm Fitness Nutrition Tracker |
    | **Food Database** | 40+ seeded foods + Open Food Facts (3M+ live) |
    | **Data Storage** | Local SQLite (private, on-device) |
    | **Version** | 2.0 |
    """)
