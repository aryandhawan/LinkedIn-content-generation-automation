import os
import requests
from dotenv import load_dotenv
 
load_dotenv()
 
MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

def publish_to_linkedin(caption: str, poster_path: str) -> bool:
    """
    Sends the caption text and poster image to Make.com via webhook.
    Returns True if the webhook accepted the request, False otherwise.
    """
    if not MAKE_WEBHOOK_URL:
        print("[publisher] MAKE_WEBHOOK_URL is not set in .env — cannot publish.")
        return False

    try:
        if poster_path:
            with open(poster_path, 'rb') as poster_file:
                files = {'poster': poster_file}
                data = {'caption': caption}
                response = requests.post(MAKE_WEBHOOK_URL, data=data, files=files)
                response.raise_for_status()

            print(f"[publisher] Successfully sent caption and poster to Make.com. Status code: {response.status_code}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"[publisher] Failed to send data to Make.com: {e}")
        return False