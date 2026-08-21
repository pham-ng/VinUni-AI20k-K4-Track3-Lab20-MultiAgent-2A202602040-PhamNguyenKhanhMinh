"""Search client abstraction for ResearcherAgent."""

import os

import requests

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def __init__(self):
        from multi_agent_research_lab.core.config import get_settings
        settings = get_settings()
        self.api_key = settings.tavily_api_key
        self.url = "https://api.tavily.com/search"

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        if not self.api_key:
            # Optionally raise an error or mock return
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": False,
        }

        response = requests.post(self.url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()

        documents = []
        for result in data.get("results", []):
            documents.append(
                SourceDocument(
                    title=result.get("title", ""),
                    url=result.get("url", ""),
                    snippet=result.get("content", ""),
                )
            )
        return documents
