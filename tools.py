from __future__ import annotations

import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import settings
from models import ScrapedSource, SearchHit

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
_session = requests.Session()
_session.headers.update({"User-Agent": settings.user_agent})


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _format_search_hits(results: list[SearchHit]) -> str:
    blocks = []
    for result in results:
        blocks.append(
            "\n".join(
                [
                    f"Title: {result.title}",
                    f"URL: {result.url}",
                    f"Snippet: {result.snippet}",
                ]
            )
        )
    return "\n-----\n".join(blocks)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type((requests.RequestException, RuntimeError)),
)
def search_web(query: str, max_results: int | None = None) -> list[SearchHit]:
    """Return structured search hits from Tavily."""
    clean_query = query.strip()
    if not clean_query:
        return []

    response = tavily.search(
        query=clean_query,
        max_results=max_results or settings.search_results_limit,
    )
    results: list[SearchHit] = []

    for item in response.get("results", []):
        url = item.get("url")
        if not url:
            continue

        results.append(
            SearchHit(
                title=_clean_text(item.get("title", "Untitled result")),
                url=url,
                snippet=_clean_text(item.get("content", ""))[
                    : settings.search_snippet_char_limit
                ],
            )
        )

    return results


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type(requests.RequestException),
)
def _download_page(url: str) -> requests.Response:
    response = _session.get(url, timeout=settings.scrape_timeout_seconds)
    response.raise_for_status()
    return response


def scrape_page(url: str) -> ScrapedSource:
    """Fetch and clean a page into a structured source object."""
    try:
        response = _download_page(url)
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
            tag.decompose()

        title = ""
        if soup.title and soup.title.string:
            title = _clean_text(soup.title.string)

        content = _clean_text(soup.get_text(separator=" ", strip=True))
        return ScrapedSource(
            url=url,
            title=title or "",
            content=content[: settings.scrape_char_limit],
            success=True,
        )
    except Exception as exc:
        return ScrapedSource(
            url=url,
            success=False,
            error=str(exc) or "An unknown error occurred",
        )


@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic."""
    return _format_search_hits(search_web(query))


@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    result = scrape_page(url)
    if not result.success:
        return f"Could not scrape URL: {result.error or 'An unknown error occurred'}"

    title = result.title or "Untitled page"
    return f"Title: {title}\nURL: {result.url}\nContent: {result.content}"
