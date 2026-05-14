"""Web search tools for research and competitive analysis."""

from __future__ import annotations

from typing import Any
from langchain.tools import tool
import structlog

logger = structlog.get_logger(__name__)


@tool
def web_search(query: str) -> str:
    """
    Search the web for information on a given query.

    Use this to research competitor activities, market trends, keyword data,
    audience pain points, and any other information needed for marketing strategy.

    Args:
        query: The search query (be specific and concise)

    Returns:
        A formatted summary of top search results with snippets.
    """
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        logger.info("web_search_completed", query=query[:60], length=len(results))
        return results
    except Exception as exc:
        logger.error("web_search_failed", error=str(exc))
        return f"Search failed: {exc}"


@tool
def competitor_analysis(competitor_name: str, topic: str | None = None) -> str:
    """
    Analyze a competitor's marketing presence and content.

    Args:
        competitor_name: Name of the competitor company
        topic: Optional specific topic or product line to focus on

    Returns:
        Summary of competitor's marketing positioning, content themes,
        posting frequency, and estimated audience engagement.
    """
    query = f"{competitor_name} marketing strategy content {topic or ''}"
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        logger.info("competitor_analysis_done", competitor=competitor_name)
        return f"Competitor Analysis for {competitor_name}:\n\n{results}"
    except Exception as exc:
        logger.error("competitor_analysis_failed", error=str(exc))
        return f"Analysis failed: {exc}"


@tool
def keyword_research(keyword: str) -> str:
    """
    Research keyword data including search volume, difficulty, and related terms.

    Args:
        keyword: The keyword or keyphrase to research

    Returns:
        Estimated search volume, competition level, related keywords,
        and content opportunities for SEO/SEA.
    """
    query = f"{keyword} search volume SEO keyword difficulty"
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        logger.info("keyword_research_done", keyword=keyword[:60])
        return f"Keyword Research — '{keyword}':\n\n{results}"
    except Exception as exc:
        logger.error("keyword_research_failed", error=str(exc))
        return f"Keyword research failed: {exc}"


@tool
def trending_topics(topic: str, limit: int = 5) -> str:
    """
    Find currently trending topics related to a keyword or industry.

    Args:
        topic: Industry or topic to find trends for
        limit: Maximum number of trending topics to return (default 5)

    Returns:
        List of trending topics with brief context and engagement indicators.
    """
    query = f"trending {topic} 2026"
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()
        results = search.run(query)
        logger.info("trending_topics_done", topic=topic, limit=limit)
        return f"Trending Topics — {topic}:\n\n{results[:2000]}"
    except Exception as exc:
        logger.error("trending_topics_failed", error=str(exc))
        return f"Trending topics failed: {exc}"


# --------------------------------------------------------------------------


class SearchTools:
    """Bundle all search tools for easy tool registration."""

    TOOLS = [web_search, competitor_analysis, keyword_research, trending_topics]
    TOOL_NAMES = {t.name: t for t in TOOLS}