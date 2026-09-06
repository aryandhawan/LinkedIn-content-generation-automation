def run_linkedin_pipeline(topic: str, tone: str) -> dict:
    result = generate_post(topic=topic, tone=tone)
    poster_path = generate_poster(headline=result["poster_headline"])
    return {
        "caption": result["caption"],
        "poster_path": poster_path,
    }