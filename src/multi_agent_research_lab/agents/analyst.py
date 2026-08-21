"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        from multi_agent_research_lab.services.llm_client import LLMClient

        llm = LLMClient()

        system_prompt = (
            "You are an expert analyst. Analyze the provided research notes. "
            "Extract key claims, compare viewpoints, and synthesize findings."
        )
        user_prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}"

        try:
            response = llm.complete(system_prompt, user_prompt)
            state.analysis_notes = response.content
            state.add_trace_event(
                "analyst_run",
                {
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        except Exception as e:
            state.errors.append(f"Analyst LLM Error: {str(e)}")
            state.analysis_notes = f"Analysis failed: {str(e)}"
        return state
