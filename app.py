from fastapi import FastAPI, Request
from datetime import datetime
import httpx

app = FastAPI()

TARGET_URL = "https://webhook.site/e11323ff-37b1-4f16-87cf-4c9c467b8bb4"

def now():
    return datetime.utcnow().isoformat() + "Z"

async def send_to_api(data: dict):
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(TARGET_URL, json=data)
        response.raise_for_status()

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    outgoing_payload = None

    if event_type == "deployment":
        deployment = payload.get("deployment", {})

        outgoing_payload = {
            "source": "github",
            "event": "deployment_started",
            "deployment_id": deployment.get("id"),
            "environment": deployment.get("environment"),
            "status": "in_progress",
            "timestamp": deployment.get("created_at") or now()
        }

    elif event_type == "deployment_status":
        deployment = payload.get("deployment", {})
        status = payload.get("deployment_status", {})

        outgoing_payload = {
            "source": "github",
            "event": "deployment_finished",
            "deployment_id": deployment.get("id"),
            "environment": deployment.get("environment"),
            "status": status.get("state"),
            "timestamp": status.get("created_at") or now()
        }

    if outgoing_payload:
        try:
            await send_to_api(outgoing_payload)
            print("➡️ Sent to external API:", outgoing_payload)
        except Exception as e:
            print("❌ Failed to send webhook:", str(e))

    return {"status": "ok"}
