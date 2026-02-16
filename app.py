from fastapi import FastAPI, Request
from datetime import datetime
import json
import httpx
import os
from pathlib import Path #log

app = FastAPI()

#FORWARD_URL = os.getenv(
#    "FORWARD_URL",
#    "https://webhook.site/e11323ff-37b1-4f16-87cf-4c9c467b8bb4"  # ← сюда будет пересылка
#)
LOG_FILE = Path(os.getenv("WEBHOOK_LOG_FILE", "webhooks.log"))

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
 
     log_entry = {
        "received_at": now(),
        "event": event_type,
        "payload": payload
     }

     with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write("RECIVED AT ")
        f.write(now())
        f.write(" <----------------------")
        f.write("\n\n")
        f.write(json.dumps(log_entry, ensure_ascii=False, indent=2))
        f.write("\n\n")
        f.write("================================================")
        f.write("\n\n")

     return {"status": "ok"}


    # ====== ПЕРЕСЫЛКА ВНЕШНЕМУ API ======
   # try:
   #     async with httpx.AsyncClient(timeout=5) as client:
   #         response = await client.post(
   #             FORWARD_URL,
   #             json=parsed
   #         )

   #     print("Forwarded to:", FORWARD_URL)
   #     print("Forward status:", response.status_code)

   # except Exception as e:
   #     print("ERROR while forwarding:", str(e))
