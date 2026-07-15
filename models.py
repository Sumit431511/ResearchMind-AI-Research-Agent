from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchHit(BaseModel):
    title: str
    url: str
    snippet: str = ""


class ScrapedSource(BaseModel):
    url: str
    title: Optional[str] = None
    content: str = ""
    success: bool = True
    error: Optional[str] = None


class CritiqueResult(BaseModel):
    raw: str
    score: Optional[int] = None
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    verdict: Optional[str] = None


class ResearchPipelineState(BaseModel):
    topic: str
    search_results: List[SearchHit] = Field(default_factory=list)
    scraped_sources: List[ScrapedSource] = Field(default_factory=list)
    research_context: str = ""
    report: str = ""
    critique: Optional[CritiqueResult] = None
    revision_count: int = 0
