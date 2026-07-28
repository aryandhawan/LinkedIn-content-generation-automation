"""
Generates LinkedIn post content: a full caption AND a short poster headline,
from the same call so both stay thematically consistent.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()


class PostContent(BaseModel):
    caption: str = Field(description="The full LinkedIn post caption text, ready to publish")
    poster_headline: str = Field(description="A short, punchy headline under 10 words, for use on a visual poster — distinct wording from the caption's opening, but same core message")


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    api_key=os.getenv("GROQ_API_KEY")
)

structured_llm = llm.with_structured_output(PostContent)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a LinkedIn content writer for an AI automation agency.
Write engaging, professional LinkedIn posts that establish the founder as a credible,
insightful voice in AI/automation — never generic corporate filler.
 
Rules for the caption:
- Open with a hook, not a generic statement
- Keep it scannable: short paragraphs, occasional line breaks
- End with either a question, a call to action, or a forward-looking statement
- Do not use excessive emojis or hashtag spam — 3-5 relevant hashtags at the end is enough
- Aim for roughly 800-1200 characters — enough room for a real hook, 2-3 short paragraphs,
  and a closing question, without rambling. (LinkedIn's actual limit is ~3000 characters;
  this target is a stylistic choice for readability, not a platform constraint.)
 
Rules for the poster_headline:
- Target length: roughly 8-14 words. This should naturally wrap to exactly 2 lines
  on a square poster — not fit on 1 line, and not spill onto 3.
- Must be a complete, substantive thought on its own — someone should understand
  the core idea from this headline alone, without needing the caption.
- Reword the core message rather than copying the caption's opening line verbatim.
- BAD example (too short, looks sparse on a large poster): "Simpler AI Starts Here"
- GOOD example, for illustration only — do NOT reuse this, generate your own based on
  the actual topic given (right length, wraps to 2 full lines): The Real Reason Most
  Chatbots Fail Has Nothing To Do With The AI Model"""),
    ("human", "Topic: {topic}\n\nDesired tone: {tone}\n\nGenerate the post.")
])

chain = prompt | structured_llm


def generate_post(topic: str, tone: str, max_retries: int = 2) -> dict:
    """
    Generates LinkedIn post content for the given topic and tone.
    Returns a dict: {"caption": str, "poster_headline": str}

    Retries on Groq's occasional tool-calling parse failures (a known
    intermittent issue with function-calling on Llama-based models) —
    the underlying generation is usually fine, it's the strict parsing
    that occasionally hiccups.
    """
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = chain.invoke({"topic": topic, "tone": tone})
            return result.model_dump()
        except Exception as e:
            last_error = e
            if "tool_use_failed" in str(e):
                print(f"[content_gen] Tool-call parsing failed, retrying ({attempt + 1}/{max_retries})...")
                continue
            raise  

    raise last_error
