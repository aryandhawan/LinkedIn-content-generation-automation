import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()


class Reply(BaseModel):
    title: str
    description: str
    color: str

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

DISCORD_HUMAN_PROMPT = """Original content to reformat for Discord:

{original_content}

Reformat this for Discord following the rules above."""


prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a content formatter that adapts already-generated
content for posting to a Discord channel via webhook, using a rich embed.

You will be given the original transformed content (already written by the
core content generation step) as input. Your job is NOT to generate new
ideas or facts — only to reformat and re-tone this existing content to fit
Discord's conventions, and output it in the exact structure needed for a
Discord embed.

Discord conventions to follow:
- Tone is more casual and direct than LinkedIn — drop corporate phrasing,
  hook-lines, and hashtags entirely. Hashtags are not a Discord convention
  and should never appear.
- Keep it short. Discord embeds are read at a glance in a chat feed, not
  as long-form reading. Prefer 2-4 sentences over a full paragraph.
- Use Discord markdown where it helps: **bold** for the key point, `code`
  formatting only if genuinely relevant (e.g. a technical term), bullet
  points (using "-") only if listing 2-3 short items, never a long list.
- Never invent facts, numbers, or claims not present in the original
  content. Your job is tone and format, not new content.

Output exactly this structure, and nothing else:

TITLE: <a short, attention-grabbing title, under 100 characters>
DESCRIPTION: <the reformatted body text, following the conventions above>
COLOR: <a single hex color code without the #, chosen to match the
  content's mood — e.g. 5865F2 for neutral/informational, 57F287 for
  positive/success-toned content, FEE75C for announcements>

Do not add any text before TITLE: or after the COLOR: line. Do not wrap
the output in code blocks or add explanations of what you did.""")
,
    ("human",DISCORD_HUMAN_PROMPT)])



chain = prompt | llm.with_structured_output(Reply)


def generate_Discord_message(current_message,max_retries: int = 2) -> dict:
    """
    Generates Discord content
    Returns a dict:
    Retries on Groq's occasional tool-calling parse failures (a known
    intermittent issue with function-calling on Llama-based models) —
    the underlying generation is usually fine, it's the strict parsing
    that occasionally hiccups.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = chain.invoke({"original_content": current_message})
            return result.model_dump() # converts the model response to JSON
        except Exception as e:
            last_error = e
            if "tool_use_failed" in str(e):
                print(f"[content_gen] Tool-call parsing failed, retrying ({attempt + 1}/{max_retries})...")
                continue
            raise

    raise last_error

if __name__ == "__main__":
    print(generate_Discord_message(current_message="We just wrapped up a deep dive into how transformer attention mechanisms actually scale with sequence length — turns out the naive quadratic cost isn't the whole story once you factor in memory bandwidth. Sharing the breakdown below."))

