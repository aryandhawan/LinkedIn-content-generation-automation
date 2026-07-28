import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from pydantic import BaseModel, Field

from tools import fetch_hackernews, fetch_reddit

load_dotenv()

class Topic(BaseModel):
    title: str = Field(description="The topic or post title")
    reason: str = Field(description="Why it's relevant to an AI automation agency")
    source: str = Field(description="Either 'Hacker News' or 'Reddit'")
    url: str = Field(description="The original url")
 
 
class TopicList(BaseModel):
    topics: list[Topic]

@tool
def hackernews_tool() -> list[dict]:
    """Fetches current front-page posts from Hacker News. Good for mainstream tech,
    startup, and developer-focused discussion. Returns title, url, points, and source
    for each post"""

    return fetch_hackernews()

@tool
def reddit_tool() -> list[dict]:
    """Fetches current posts from a specified Reddit subreddit. Good for niche communities
    and specific interest groups. Returns title, url, points, and source for each post"""

    return fetch_reddit()

tools=[hackernews_tool, reddit_tool]

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,  # since this is for trend scouting, we want more factual and less creative output
    api_key=os.getenv("GROQ_API_KEY")
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a trend-scouting assistant for an AI automation agency founder.
 
Your job: check BOTH Hacker News and Reddit for today's trending content. Both sources
matter equally — mainstream tech news and community discussion often surface different,
equally valuable angles.
 
If one source returns no results or appears unavailable, do not treat this as a failure —
simply proceed using whatever the other source returned, and continue normally. Only
mention a source being unavailable if BOTH sources come back empty.
 
Once you have results from whichever source(s) succeeded, identify the 3-5 topics most
relevant and useful for someone running an AI/automation agency to post about on LinkedIn.
For each, explain why it's relevant and cite which source it came from, including the
original url."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent=create_tool_calling_agent(llm,tools=tools,prompt=prompt)

agent_executor=AgentExecutor(agent=agent,tools=tools,verbose=True)

structuring_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
).with_structured_output(TopicList)

def get_trending_topics() -> list[dict]:
    """
    Runs the agent: checks both sources, judges relevance, then structures
    the result into a reliable list of dicts (title, reason, source, url).
    """
    result = agent_executor.invoke({
        "input": "Check today's trends on both Hacker News and Reddit, and tell me which topics are worth posting about for an AI automation agency."
    })
 
    raw_output = result["output"]
 
    structured = structuring_llm.invoke(
        f"Convert the following into the required schema:\n\n{raw_output}"
    )
 
    return [t.model_dump() for t in structured.topics]

if __name__ == "__main__":
    topics = get_trending_topics()
    for i, t in enumerate(topics, 1):
        print(f"{i}. [{t['source']}] {t['title']}")
        print(f"   {t['reason']}\n")