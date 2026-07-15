from __future__ import annotations

from functools import lru_cache

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from config import settings
from tools import scrape_url, web_search

load_dotenv()


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    return ChatGroq(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
    )


def build_search_agent():
    return create_agent(model=get_llm(), tools=[web_search])


def build_reader_agent():
    return create_agent(model=get_llm(), tools=[scrape_url])


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Produce clear, factual, source-grounded reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Requirements:
- Keep the writing factual, concise, and professional.
- Synthesize the scraped evidence instead of repeating it verbatim.
- Call out uncertainty when the evidence is incomplete.

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Risks or Open Questions
- Conclusion
- Sources (list all URLs found in the research)""",
        ),
    ]
)

critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest, specific, and practical.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...""",
        ),
    ]
)

revision_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You revise research reports using critic feedback while staying faithful to the provided evidence.",
        ),
        (
            "human",
            """Revise the research report below.

Topic:
{topic}

Available Research:
{research}

Current Report:
{report}

Critic Feedback:
{critique}

Instructions:
- Fix the weaknesses called out by the critic.
- Do not invent claims that are not supported by the research.
- Keep the same markdown structure unless a change improves clarity.
- Return the fully revised report only.""",
        ),
    ]
)

_llm = get_llm()
writer_chain = writer_prompt | _llm | StrOutputParser()
critic_chain = critic_prompt | _llm | StrOutputParser()
revision_chain = revision_prompt | _llm | StrOutputParser()

# Backward-compatible alias for older imports.
crictic_chain = critic_chain
