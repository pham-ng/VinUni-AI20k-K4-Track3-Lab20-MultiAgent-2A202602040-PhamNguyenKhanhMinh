"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        from multi_agent_research_lab.services.llm_client import LLMClient

        llm = LLMClient()

        system_prompt = (
            "You are a technical writer. Write a clear and comprehensive final answer based on the analysis. "
            f"Target audience: {state.request.audience}. "
            "Make sure to include inline citations."
        )
        user_prompt = (
            f"Query: {state.request.query}\n\n"
            f"Analysis Notes:\n{state.analysis_notes}\n\n"
            f"Original Research Notes:\n{state.research_notes}"
        )

        try:
            response = llm.complete(system_prompt, user_prompt)
            state.final_answer = response.content
            state.add_trace_event(
                "writer_run",
                {
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        except Exception as e:
            state.errors.append(f"Writer LLM Error: {str(e)}")
            state.final_answer = f"Writing failed: {str(e)}"
        return state
