from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, Optional

from agents import critic_chain, revision_chain, writer_chain
from config import settings
from models import CritiqueResult, ResearchPipelineState, ScrapedSource, SearchHit
from tools import scrape_page, search_web

ProgressCallback = Optional[Callable[[str, str], None]]

_SCORE_PATTERN = re.compile(r"Score:\s*(\d{1,2})/10", re.IGNORECASE)


def _emit(callback: ProgressCallback, step: str, message: str) -> None:
    if callback is not None:
        callback(step, message)


def _parse_bullets(raw: str, section_name: str) -> list[str]:
    lines = raw.splitlines()
    in_section = False
    bullets: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith(f"{section_name.lower()}:"):
            in_section = True
            continue
        if in_section and stripped.endswith(":") and not stripped.startswith("-"):
            break
        if in_section and stripped.startswith("-"):
            bullets.append(stripped.lstrip("- ").strip())

    return bullets


def parse_critique(raw: str) -> CritiqueResult:
    score_match = _SCORE_PATTERN.search(raw)
    verdict = None

    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("one line verdict:"):
            verdict = stripped.split(":", 1)[1].strip() or None
            break

    return CritiqueResult(
        raw=raw,
        score=int(score_match.group(1)) if score_match else None,
        strengths=_parse_bullets(raw, "Strengths"),
        improvements=_parse_bullets(raw, "Areas to Improve"),
        verdict=verdict,
    )


def _format_search_results(results: Iterable[SearchHit]) -> str:
    blocks = []
    for index, result in enumerate(results, start=1):
        blocks.append(
            "\n".join(
                [
                    f"Source {index}",
                    f"Title: {result.title}",
                    f"URL: {result.url}",
                    f"Snippet: {result.snippet}",
                ]
            )
        )
    return "\n\n".join(blocks)


def _format_scraped_sources(sources: Iterable[ScrapedSource]) -> str:
    blocks = []
    for index, source in enumerate(sources, start=1):
        title = source.title or "Untitled page"
        if source.success:
            content = source.content or "No content extracted."
        else:
            content = f"Scrape failed: {source.error or 'Unknown error'}"

        blocks.append(
            "\n".join(
                [
                    f"Document {index}",
                    f"Title: {title}",
                    f"URL: {source.url}",
                    f"Content: {content}",
                ]
            )
        )
    return "\n\n".join(blocks)


def build_research_context(search_results: list[SearchHit], scraped_sources: list[ScrapedSource]) -> str:
    return (
        "SEARCH RESULTS\n"
        f"{_format_search_results(search_results)}\n\n"
        "SCRAPED SOURCE CONTENT\n"
        f"{_format_scraped_sources(scraped_sources)}"
    )


def collect_scraped_sources(search_results: list[SearchHit]) -> list[ScrapedSource]:
    selected_results = search_results[: settings.scrape_source_limit]
    if not selected_results:
        return []

    collected: list[ScrapedSource] = []
    with ThreadPoolExecutor(max_workers=len(selected_results)) as executor:
        future_map = {
            executor.submit(scrape_page, result.url): result.url for result in selected_results
        }
        for future in as_completed(future_map):
            collected.append(future.result())

    order = {result.url: index for index, result in enumerate(selected_results)}
    collected.sort(key=lambda item: order.get(item.url, 999))
    return collected


def run_research_pipeline(topic: str, progress_callback: ProgressCallback = None) -> ResearchPipelineState:
    clean_topic = topic.strip()
    if not clean_topic:
        raise ValueError("Topic cannot be empty.")

    state = ResearchPipelineState(topic=clean_topic)

    _emit(progress_callback, "search", "Searching recent sources.")
    state.search_results = search_web(clean_topic)
    if not state.search_results:
        raise RuntimeError("No search results were returned for this topic. Try a broader query.")

    _emit(
        progress_callback,
        "reader",
        f"Scraping top {min(len(state.search_results), settings.scrape_source_limit)} sources in parallel.",
    )
    state.scraped_sources = collect_scraped_sources(state.search_results)
    state.research_context = build_research_context(state.search_results, state.scraped_sources)

    _emit(progress_callback, "writer", "Drafting the research report.")
    state.report = writer_chain.invoke(
        {
            "topic": state.topic,
            "research": state.research_context,
        }
    )

    _emit(progress_callback, "critic", "Reviewing the report quality.")
    critique_text = critic_chain.invoke({"report": state.report})
    state.critique = parse_critique(critique_text)

    while (
        state.critique.score is not None
        and state.critique.score < settings.critic_pass_score
        and state.revision_count < settings.max_revision_rounds
    ):
        state.revision_count += 1
        _emit(
            progress_callback,
            "revision",
            f"Applying revision round {state.revision_count} from critic feedback.",
        )
        state.report = revision_chain.invoke(
            {
                "topic": state.topic,
                "research": state.research_context,
                "report": state.report,
                "critique": state.critique.raw,
            }
        )

        _emit(progress_callback, "critic", "Re-scoring the revised report.")
        critique_text = critic_chain.invoke({"report": state.report})
        state.critique = parse_critique(critique_text)

    _emit(progress_callback, "done", "Pipeline completed.")
    return state
