"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        from multi_agent_research_lab.services.llm_client import LLMClient
        from multi_agent_research_lab.services.search_client import SearchClient

        search_client = SearchClient()
        llm = LLMClient()

        # 1. Search
        try:
            sources = search_client.search(state.request.query, max_results=state.request.max_sources)
            state.sources = sources
        except Exception as e:
            state.errors.append(f"Researcher Search Error: {str(e)}")
            state.research_notes = f"Search failed: {str(e)}"
            return state

        if not sources:
            state.research_notes = "Không tìm thấy dữ liệu liên quan trên internet."
            return state

        # 2. Compile notes (Truncate long snippets to avoid context window overflow)
        context = ""
        for i, s in enumerate(sources):
            snippet = s.snippet[:500] + "..." if len(s.snippet) > 500 else s.snippet
            context += f"Source {i + 1} ({s.url}): {s.title}\n{snippet}\n\n"

        system_prompt = "You are a researcher. Summarize the provided search results into concise research notes with citations."
        user_prompt = f"Query: {state.request.query}\n\nSources:\n{context}"

        try:
            response = llm.complete(system_prompt, user_prompt)
            state.research_notes = response.content
            state.add_trace_event(
                "researcher_run",
                {
                    "sources_count": len(sources),
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        except Exception as e:
            state.errors.append(f"Researcher LLM Error: {str(e)}")
            state.research_notes = f"LLM Generation failed: {str(e)}"

        return state
