# dashboard/core/api.py
import requests
from .config import API_BASE

def api_post(path: str, payload=None, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.post(f"{API_BASE}{path}", json=payload or {}, headers=headers, timeout=90)
    if r.status_code >= 400:
        raise RuntimeError(f"{path} → {r.status_code}: {r.text}")
    return r.json()
