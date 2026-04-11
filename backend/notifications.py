import urllib.request
import urllib.error
import json

import config as cfg


def send_ha_notification(title: str, message: str) -> dict:
    webhook_url = (cfg.HA_WEBHOOK_URL or "").strip()
    token = (cfg.HA_WEBHOOK_TOKEN or "").strip()

    if not webhook_url:
        return {"ok": False, "error": "URL webhook non configurée"}

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = json.dumps({"title": title, "message": message}).encode()
    req = urllib.request.Request(webhook_url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code} — {e.reason}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def notify_low_spool(spool_name: str, tray_type: str, color_name: str, remain_pct: int):
    title = "⚠️ Filament presque vide"
    message = f"{spool_name} ({tray_type}{' ' + color_name if color_name else ''}) — {remain_pct}% restant"
    return send_ha_notification(title, message)
