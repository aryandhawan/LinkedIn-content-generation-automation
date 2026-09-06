import base64
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.agent import get_trending_topics
from core.content_gen import generate_post
from core.image_gen import generate_poster
from platforms.linkedin.publisher import publish_to_linkedin
from platforms.discord.text_gen import generate_Discord_message
from platforms.discord.publisher import build_discord_payload
import requests
import os

app = FastAPI()

DISCORD_MAKE_URL = os.getenv("DISCORD_MAKE_URL", "")


# ---------- request/response models ----------

class GenerateRequest(BaseModel):
    topic: str
    tone: str = "direct"


class LinkedInGenerateResponse(BaseModel):
    caption: str
    poster_base64: str  # PNG bytes, base64-encoded — decode client-side


class DiscordGenerateResponse(BaseModel):
    title: str
    description: str


class LinkedInPublishRequest(BaseModel):
    caption: str
    poster_base64: str


class DiscordPublishRequest(BaseModel):
    title: str
    description: str


# ---------- trending topics (for the UI's topic picker) ----------

@app.get("/topics")
def topics():
    return {"topics": get_trending_topics()}


# ---------- LinkedIn: generate, then publish ----------

@app.post("/generate/linkedin", response_model=LinkedInGenerateResponse)
def generate_linkedin(request: GenerateRequest):
    result = generate_post(topic=request.topic, tone=request.tone)
    poster_path = generate_poster(headline=result["poster_headline"])

    poster_bytes = Path(poster_path).read_bytes()
    poster_b64 = base64.b64encode(poster_bytes).decode("utf-8")

    return LinkedInGenerateResponse(caption=result["caption"], poster_base64=poster_b64)


@app.post("/publish/linkedin")
def publish_linkedin(request: LinkedInPublishRequest):
    # publish_to_linkedin expects a file path, so write the (possibly
    # user-edited) approved poster back to a temp file before publishing
    poster_bytes = base64.b64decode(request.poster_base64)
    temp_path = Path("temp_poster_to_publish.png")
    temp_path.write_bytes(poster_bytes)

    success = publish_to_linkedin(request.caption, str(temp_path))
    if not success:
        raise HTTPException(status_code=500, detail="LinkedIn publish failed")
    return {"status": "published"}


# ---------- Discord: generate, then publish ----------

@app.post("/generate/discord", response_model=DiscordGenerateResponse)
def generate_discord(request: GenerateRequest):
    reply = generate_Discord_message(request.topic)
    return DiscordGenerateResponse(title=reply["title"], description=reply["description"])


@app.post("/publish/discord")
def publish_discord_route(request: DiscordPublishRequest):
    if not DISCORD_MAKE_URL:
        raise HTTPException(status_code=500, detail="DISCORD_MAKE_URL not configured")

    payload = build_discord_payload(request.model_dump())
    response = requests.post(DISCORD_MAKE_URL, json=payload, timeout=10)
    response.raise_for_status()
    return {"status": "published"}


# ---------- original interactive CLI, unchanged, still usable directly ----------

def main():
    print("=" * 60)
    print("Checking today's trends (Hacker News + Reddit)...\n")

    topics_list = get_trending_topics()

    if not topics_list:
        print("No topics returned — check the agent's raw output above.")
        return

    for i, t in enumerate(topics_list, 1):
        print(f"{i}. [{t['source']}] {t['title']}")
        print(f"   {t['reason']}\n")
    print("=" * 60)

    choice = input(
        "\nEnter a number to pick a topic above, or type your own topic: "
    ).strip()

    if choice.isdigit() and 1 <= int(choice) <= len(topics_list):
        topic = topics_list[int(choice) - 1]["title"]
    else:
        topic = choice

    tone = input("What tone should the post have? (e.g. direct, playful, formal) ").strip()

    print("\nGenerating post...\n")
    result = generate_post(topic=topic, tone=tone)
    post_text = result["caption"]
    headline = result["poster_headline"]

    print("\nGenerating poster image...\n")
    poster_path = generate_poster(headline=headline)

    print("=" * 60)
    print(post_text)
    print("=" * 60)
    print(f"\nPoster saved to: {poster_path}")

    from PIL import Image
    Image.open(poster_path).show()

    confirm = input("\nPost this to LinkedIn? (y/n) ").strip().lower()

    if confirm == "y":
        success = publish_to_linkedin(post_text, poster_path)
        if success:
            print("\nPublished to LinkedIn.")
        else:
            print("\nSomething went wrong — check the error above. Post was not confirmed published.")
    else:
        print("\nDiscarded. Nothing was published.")


if __name__ == "__main__":
    main()