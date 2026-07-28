"""
Entry point — runs the full flow end to end:
agent finds trending topics -> HITL topic/tone selection -> generate post -> HITL approval -> publish
"""

from agent import get_trending_topics
from content_gen import generate_post
from image_gen import generate_poster
from PIL import Image
from publisher import publish_to_linkedin


def main():
    print("=" * 60)
    print("Checking today's trends (Hacker News + Reddit)...\n")

    topics = get_trending_topics()

    if not topics:
        print("No topics returned — check the agent's raw output above.")
        return

    for i, t in enumerate(topics, 1):
        print(f"{i}. [{t['source']}] {t['title']}")
        print(f"   {t['reason']}\n")
    print("=" * 60)

    # --- HITL: pick a topic by number, or type your own ---
    choice = input(
        "\nEnter a number to pick a topic above, or type your own topic: "
    ).strip()

    if choice.isdigit() and 1 <= int(choice) <= len(topics):
        topic = topics[int(choice) - 1]["title"]
    else:
        topic = choice  # user typed their own topic directly

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

    # Open the poster so you can see it alongside the caption before approving
    Image.open(poster_path).show()

    # --- HITL: final approval ---
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