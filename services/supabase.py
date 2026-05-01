import requests

from config.settings import settings


def insert_wearable_data(payload):
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return False, "Supabase credentials are not configured."

    url = settings.SUPABASE_URL.rstrip("/") + "/rest/v1/wearable_data"
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code in (200, 201, 204):
        return True, ""

    return False, f"Supabase insert failed: HTTP {response.status_code} {response.text[:180]}"
