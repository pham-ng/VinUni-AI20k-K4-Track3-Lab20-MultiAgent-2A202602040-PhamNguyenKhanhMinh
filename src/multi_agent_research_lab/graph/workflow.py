"""LangGraph workflow skeleton."""

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.graph = self._build()

    def _build(self) -> object:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)

        workflow.add_node("supervisor", self.supervisor.run)
        workflow.add_node("researcher", self.researcher.run)
        workflow.add_node("analyst", self.analyst.run)
        workflow.add_node("writer", self.writer.run)

        workflow.set_entry_point("supervisor")

        def route(state: ResearchState) -> str:
            if not state.route_history:
                return END
            r = state.route_history[-1]
            if r == "done":
                return END
            return r

        workflow.add_conditional_edges(
            "supervisor",
            route,
            {"researcher": "researcher", "analyst": "analyst", "writer": "writer", END: END},
        )

        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")

        return workflow.compile()

    def run(self, state: ResearchState, config: dict | None = None) -> ResearchState:
        """Execute the graph and return final state."""
        result = self.graph.invoke(state, config=config)
        return result if isinstance(result, ResearchState) else ResearchState(**result)
