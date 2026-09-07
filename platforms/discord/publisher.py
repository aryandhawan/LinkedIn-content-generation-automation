import os

import requests
from pydantic import BaseModel
from fastapi import FastAPI
from platforms.discord.text_gen import Reply
from dotenv import load_dotenv

load_dotenv()
app=FastAPI()


def build_discord_payload(reply: dict) -> dict:
    return {
        "title": reply["title"],
        "description": reply["description"],
    }
@app.post('/publish')
def publish_discord(request: Reply):

    response=requests.post(os.getenv('DISCORD_WEBHOOK_URL'),json=build_discord_payload(request.model_dump()))
    response.raise_for_status()
    print("published")