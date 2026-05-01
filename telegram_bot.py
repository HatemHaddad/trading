import os
import sys
import time
import subprocess
from datetime import datetime

import requests


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}" if TELEGRAM_TOKEN else None
POLL_TIMEOUT_SECONDS = 50
REPORT_TIMEOUT_SECONDS = int(os.getenv("REPORT_TIMEOUT_SECONDS", "300"))


def log(message: str) -> None:
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def require_config() -> None:
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not TELEGRAM_CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")


def telegram_request(method: str, payload: dict | None = None, timeout: int = 30) -> dict:
    if API_BASE is None:
        raise RuntimeError("Telegram API base URL is not configured")
    url = f"{API_BASE}/{method}"
    response = requests.post(url, json=payload or {}, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API returned not ok for {method}: {data}")
    return data


def send_message(text: str) -> None:
    try:
        telegram_request(
            "sendMessage",
            {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )
    except Exception as exc:
        log(f"Failed to send Telegram message: {exc}")


def is_authorized_chat(message: dict) -> bool:
    chat = message.get("chat") or {}
    incoming_chat_id = str(chat.get("id", ""))
    return incoming_chat_id == str(TELEGRAM_CHAT_ID)


def command_from_message(message: dict) -> str:
    text = (message.get("text") or "").strip()
    if not text.startswith("/"):
        return ""
    first = text.split()[0].lower()
    # Telegram group commands may arrive as /report@BotName.
    return first.split("@", 1)[0]


def sanitize_output(value: str) -> str:
    cleaned = value or ""
    for secret in [TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]:
        if secret:
            cleaned = cleaned.replace(str(secret), "[redacted]")
    if len(cleaned) > 3500:
        cleaned = cleaned[-3500:]
    return cleaned


def run_report() -> int:
    log("/report received; starting run_and_save.py")
    send_message("Report requested. Generating a fresh portfolio report now...")
    try:
        completed = subprocess.run(
            [sys.executable, "run_and_save.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            text=True,
            capture_output=True,
            timeout=REPORT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        log("run_and_save.py timed out")
        send_message("Report generation timed out before completion. Please check the bot container logs.")
        return 124
    except Exception as exc:
        log(f"run_and_save.py failed to start: {exc}")
        send_message("Report generation failed to start. Please check the bot container logs.")
        return 1

    output = sanitize_output((completed.stdout or "") + "\n" + (completed.stderr or ""))
    if completed.returncode == 0:
        log("run_and_save.py completed successfully")
    else:
        log(f"run_and_save.py exited with code {completed.returncode}: {output}")
        send_message(
            "Report generation failed. Exit code: "
            f"{completed.returncode}. Recent log output:\n{output}"
        )
    return completed.returncode


def get_latest_update_offset() -> int | None:
    try:
        data = telegram_request("getUpdates", {"timeout": 1, "allowed_updates": ["message"]}, timeout=5)
        updates = data.get("result", [])
        if updates:
            return max(int(update["update_id"]) for update in updates) + 1
    except Exception as exc:
        log(f"Could not initialize Telegram update offset: {exc}")
    return None


def handle_update(update: dict) -> None:
    message = update.get("message") or update.get("edited_message") or {}
    if not message:
        return
    if not is_authorized_chat(message):
        chat = message.get("chat") or {}
        log(f"Ignoring message from unauthorized chat id {chat.get('id')}")
        return

    command = command_from_message(message)
    if command == "/report":
        run_report()
    elif command in {"/start", "/help"}:
        send_message("Available command: /report - generate and send a fresh portfolio report.")


def main() -> None:
    require_config()
    offset = get_latest_update_offset()
    log("Telegram report bot started and listening for /report")
    while True:
        try:
            payload = {"timeout": POLL_TIMEOUT_SECONDS, "allowed_updates": ["message"], "offset": offset}
            data = telegram_request("getUpdates", payload, timeout=POLL_TIMEOUT_SECONDS + 10)
            for update in data.get("result", []):
                offset = int(update["update_id"]) + 1
                handle_update(update)
        except requests.RequestException as exc:
            log(f"Telegram polling request failed: {exc}")
            time.sleep(10)
        except Exception as exc:
            log(f"Unexpected bot error: {exc}")
            time.sleep(10)


if __name__ == "__main__":
    main()
