from fastapi import FastAPI, Request
import json
from datetime import datetime

app = FastAPI()

def now():
    return datetime.utcnow().isoformat()

@app.post("/webhook")
async def receive_webhook(request: Request):
    # читаем JSON из тела запроса
    payload = await request.json()

    # заголовок с типом события GitHub
    event_type = request.headers.get("X-GitHub-Event")

    print("\n================ WEBHOOK RECEIVED ================\n")
    print("recived at -", now())
    print(f"Event type: {event_type}")
    print("Payload:")
    print(json.dumps(payload, indent=2))
    print("\n==================================================\n")

    return {"status": "ok"}
