from fastapi import FastAPI, Request
from datetime import datetime
import json
import httpx
import os

app = FastAPI()

FORWARD_URL = os.getenv(
    "FORWARD_URL",
    "https://webhook.site/e11323ff-37b1-4f16-87cf-4c9c467b8bb4"  # ← сюда будет пересылка
)

def now():
    return datetime.utcnow().isoformat()

def parse_github_payload(payload: dict) -> dict:
    head_commit = payload.get("head_commit", {}) or {}

    return {
        "timestamp": now(),
        "repository": payload.get("repository", {}).get("full_name"),
        "event": payload.get("event"),
        "message": head_commit.get("message"),
        "committer": head_commit.get("committer", {}),
        "modified": head_commit.get("modified", []),
    }

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()

    event_type = request.headers.get("X-GitHub-Event")

    parsed = parse_github_payload(payload)
    parsed["event"] = event_type

    # ====== ВЫВОД НА ХОСТ ======
    print("\n=========== WEBHOOK ==========")
    print("Received at:", parsed["timestamp"])
    print("Event:", parsed["event"])
    print("Repository:", parsed["repository"])
    print("Message:", parsed["message"])
    print("Committer:", parsed["committer"])
    print("Modified files:", parsed["modified"])
    print("================================\n")

    # ====== ПЕРЕСЫЛКА ВНЕШНЕМУ API ======
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                FORWARD_URL,
                json=parsed
            )

        print("Forwarded to:", FORWARD_URL)
        print("Forward status:", response.status_code)

    except Exception as e:
        print("ERROR while forwarding:", str(e))

    return {"status": "ok"}
