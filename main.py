import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

from message import *

# Environments 불러오기
load_dotenv()
GITLAB_WEBHOOK_SECRET = os.getenv("GITLAB_WEBHOOK_SECRET")

app = FastAPI()


@app.post("/gitlab-link")
async def gitlab_link(request: Request):
    token = request.headers.get("X-Gitlab-Token")
    if token != GITLAB_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()
    event = payload.get("object_kind")

    if event == "push":
        await handle_pushes(payload)
    elif event == "merge_request":
        await handle_merge_request(payload)

    return {"status": "ok"}
