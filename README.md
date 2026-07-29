# Tandem AI Labs — LinkedIn Content Agent

A hybrid, agentic content pipeline that scouts real trending discussions, reasons about what's actually worth posting about, generates a branded LinkedIn post end-to-end, and publishes it — with a human approval gate before anything goes public.

Built as a working demonstration of agentic reasoning + reliable orchestration, split deliberately across code and no-code tooling based on what each does best.

---

## What it does

1. **Scouts trends** — a LangChain tool-calling agent checks both Hacker News and Reddit for current discussion, genuinely deciding what's relevant rather than just dumping raw feeds
2. **Presents judged findings** — surfaces 3-5 topics with reasoning on why each matters to an AI automation agency, citing which source each came from
3. **You pick a topic and tone** — via a simple terminal prompt (pick by number, or type your own)
4. **Generates the post** — a structured LLM call produces both a full LinkedIn caption and a short, distinct poster headline in one pass, written to sound like a genuine voice in the space — not generic AI-post filler
5. **Generates a branded poster** — a clean, templated graphic (not AI-generated imagery) with the headline rendered in crisp, correctly-spelled text every time
6. **You approve or discard** — see the real caption and the real poster before anything goes anywhere
7. **Publishes automatically** — on approval, a webhook call hands the caption + image to a Make.com scenario, which posts it to the company LinkedIn page

---

## Why this architecture

### Hybrid by design, not by accident
The reasoning core (trend discovery, relevance judgment, content generation) runs locally in Python — this is where genuine agentic decision-making happens, and where full control over the tool-calling loop matters. Publishing to LinkedIn is handed off to Make.com, which already solves the OAuth/API integration problem reliably — there's no value in re-building that from scratch. Each tool does the part it's actually good at.

### Why templated graphics, not AI-generated images
Diffusion models render text unreliably — garbled or misspelled words are a known, common failure mode, even in top-tier image models. Since every poster needs a specific, correct headline, images are composed programmatically (Pillow: real font, real positioning) instead of generated. This trades illustrative variety for guaranteed correctness and full brand consistency across every post.

### Why the agent checks both sources unconditionally, not one-then-fallback
Hacker News and Reddit surface genuinely different kinds of relevant content — mainstream tech discourse versus community-level discussion. Both are checked every run, and the agent's real discretion is exercised in judging which of the combined results are actually worth posting about, not in choosing which source to skip.

### Resilience by default
Either data source can fail (rate limits, timeouts, downtime) without crashing the run — each tool fails gracefully and returns nothing rather than raising, so the agent continues reasoning with whatever succeeded.

### Human-in-the-loop, twice
No post reaches LinkedIn without a human seeing the actual caption and the actual poster first. This isn't a limitation — for anything publishing on a company's behalf, a review gate is the correct design, not a missing feature.

### Architecture Flowchart 

![alt text](image.png)

---

## Tech stack

| Layer | Technology |
|---|---|
| Agent reasoning / tool-calling | LangChain (`langchain-classic`) + Groq (Llama 3.3 70B) |
| Structured output | Pydantic + `.with_structured_output()` |
| Trend sources | Hacker News (Algolia Search API), Reddit (public RSS) |
| Content generation | `langchain-groq` |
| Image generation | Pillow (programmatic, template-based) |
| Publishing orchestration | Make.com (webhook trigger → LinkedIn Company Post module) |
| Human-in-the-loop | Terminal-based (CLI prompts) |

---

## Project structure

```
linkedin_agent/
├── tools.py          # Hacker News + Reddit fetchers — resilient, fail gracefully
├── agent.py           # Tool-calling agent: fetches, judges relevance, structures output
├── content_gen.py     # Generates caption + poster headline in one structured call
├── image_gen.py       # Composites the branded poster graphic (Pillow)
├── publisher.py       # Sends caption + image to Make.com via webhook (multipart/form-data)
├── main.py            # Orchestrates the full flow, including both HITL gates
├── config.yaml
├── requirements.txt
└── .env               # API keys + webhook URL (gitignored)
```

---

## Setup

**1. Install dependencies:**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**2. Environment variables** — create `.env`:
```
GROQ_API_KEY=your_groq_api_key
MAKE_WEBHOOK_URL=your_make_com_webhook_url
```

**3. Make.com scenario** — build a scenario with:
- A **Custom Webhook** trigger (generates the URL used above)
- A **LinkedIn — Create a Company Image Post** module, with:
  - **Content** field mapped to the incoming caption
  - **Title / Alt Text** mapped to the incoming poster headline (not the full caption — LinkedIn/Make field limits are shorter than the full post text)
  - **File** mapped to the incoming image data
- The scenario must be **activated (turned on)**, not left in test/draft mode, or the webhook will return a 410 error after its first test call

**4. Run it:**
```bash
python main.py
```

---

## Known limitations & honest tradeoffs

- Trend sources are fixed (Hacker News + Reddit r/artificial) — not yet configurable per run
- No cross-run deduplication — the same trending topic could resurface across consecutive runs
- HITL is terminal-based; a client-facing version would need WhatsApp Business API or similar, which requires business verification and message template pre-approval through Meta — a meaningfully bigger setup step deliberately out of scope for this build
- Poster template is a single fixed style — extending to multiple selectable templates would be a natural next step

---

## Author

Built by **Aryan Dhawan** — AI/ML engineer, building independently under [Tandem AI Labs](https://tandem-ai.tech).