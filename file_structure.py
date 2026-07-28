"""
Run this once from your project root to scaffold the LinkedIn outreach agent project.
Usage: python setup_structure.py
"""

import os

STARTER_CONTENT = {
    ".gitignore": (
        "venv/\n"
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "*.log\n"
    ),
    ".env": "# API keys go here — never commit this file\nGROQ_API_KEY=\nMAKE_WEBHOOK_URL=\n",
    "config.yaml": (
        "# Tunable parameters\n"
        "llm:\n"
        "  model_name: \"llama-3.3-70b-versatile\"\n"
        "  temperature: 0.4\n\n"
        "sources:\n"
        "  hackernews_url: \"https://hn.algolia.com/api/v1/search?tags=front_page\"\n"
        "  reddit_rss_url: \"https://www.reddit.com/r/artificial/top/.rss?t=day\"\n"
    ),
    "README.md": "# LinkedIn Outreach Agent\n\nAgentic content-discovery + LinkedIn post generator with HITL approval.\n",
    "requirements.txt": (
        "groq\n"
        "requests\n"
        "python-dotenv\n"
        "pyyaml\n"
    ),
}

FILES = [
    "main.py",        # entry point — runs the terminal HITL loop end to end
    "agent.py",        # the agent's reasoning: tool selection, decision loop
    "tools.py",        # Hacker News + Reddit fetch functions (the agent's callable tools)
    "content_gen.py",  # post text + image generation once a topic is chosen
    "publisher.py",    # sends final approved post to the Make.com webhook
    "config.yaml",
    ".env",
    ".gitignore",
    "requirements.txt",
    "README.md",
]


def create_file(path: str):
    if os.path.exists(path):
        print(f"  skip (exists): {path}")
        return
    content = STARTER_CONTENT.get(path, "")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  created: {path}")


def main():
    print("Scaffolding LinkedIn agent project...\n")
    for fname in FILES:
        create_file(fname)
    print("\nDone.")


if __name__ == "__main__":
    main()