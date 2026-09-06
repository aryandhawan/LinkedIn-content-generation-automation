"""
Streamlit UI: pick a topic and tone, generate content for one or more
platforms, preview it, then approve to actually publish. Mirrors the
generate -> review -> publish HITL flow from the original CLI.
"""

import base64

import requests
import streamlit as st

BACKEND_URL = "http://localhost:8000"  # change if your backend runs elsewhere

st.set_page_config(page_title="Content Transformer", layout="centered")
st.title("Automated Content Transformation")

# session state holds whatever's been generated but not yet published
if "linkedin_draft" not in st.session_state:
    st.session_state.linkedin_draft = None
if "discord_draft" not in st.session_state:
    st.session_state.discord_draft = None

# ---------- input ----------

with st.expander("Trending topics", expanded=False):
    if st.button("Fetch trending topics"):
        resp = requests.get(f"{BACKEND_URL}/topics", timeout=15)
        st.session_state.topics = resp.json().get("topics", [])
    for t in st.session_state.get("topics", []):
        st.markdown(f"**[{t['source']}]** {t['title']}  \n_{t['reason']}_")

topic = st.text_input("Topic", placeholder="e.g. how transformer attention scales")
tone = st.selectbox("Tone", ["direct", "playful", "formal"])
platforms = st.multiselect("Platforms", ["linkedin", "discord"], default=["linkedin"])

if st.button("Generate", type="primary", disabled=not topic):
    if "linkedin" in platforms:
        with st.spinner("Generating LinkedIn post..."):
            resp = requests.post(
                f"{BACKEND_URL}/generate/linkedin",
                json={"topic": topic, "tone": tone},
                timeout=60,
            )
            resp.raise_for_status()
            st.session_state.linkedin_draft = resp.json()

    if "discord" in platforms:
        with st.spinner("Generating Discord post..."):
            resp = requests.post(
                f"{BACKEND_URL}/generate/discord",
                json={"topic": topic, "tone": tone},
                timeout=60,
            )
            resp.raise_for_status()
            st.session_state.discord_draft = resp.json()

st.divider()

# ---------- LinkedIn preview + approve ----------

if st.session_state.linkedin_draft:
    st.subheader("LinkedIn — preview")
    draft = st.session_state.linkedin_draft

    poster_bytes = base64.b64decode(draft["poster_base64"])
    st.image(poster_bytes, caption="Generated poster")

    edited_caption = st.text_area("Caption (editable)", value=draft["caption"], height=150)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Publish to LinkedIn", type="primary"):
            with st.spinner("Publishing..."):
                resp = requests.post(
                    f"{BACKEND_URL}/publish/linkedin",
                    json={"caption": edited_caption, "poster_base64": draft["poster_base64"]},
                    timeout=30,
                )
            if resp.ok:
                st.success("Published to LinkedIn.")
                st.session_state.linkedin_draft = None
            else:
                st.error(f"Publish failed: {resp.text}")
    with col2:
        if st.button("Discard LinkedIn draft"):
            st.session_state.linkedin_draft = None
            st.rerun()

# ---------- Discord preview + approve ----------

if st.session_state.discord_draft:
    st.subheader("Discord — preview")
    draft = st.session_state.discord_draft

    edited_title = st.text_input("Title (editable)", value=draft["title"])
    edited_description = st.text_area("Description (editable)", value=draft["description"], height=100)

    st.markdown(f"**Embed preview**\n\n> **{edited_title}**\n> \n> {edited_description}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Publish to Discord", type="primary"):
            with st.spinner("Publishing..."):
                resp = requests.post(
                    f"{BACKEND_URL}/publish/discord",
                    json={"title": edited_title, "description": edited_description},
                    timeout=30,
                )
            if resp.ok:
                st.success("Published to Discord.")
                st.session_state.discord_draft = None
            else:
                st.error(f"Publish failed: {resp.text}")
    with col2:
        if st.button("Discard Discord draft"):
            st.session_state.discord_draft = None
            st.rerun()