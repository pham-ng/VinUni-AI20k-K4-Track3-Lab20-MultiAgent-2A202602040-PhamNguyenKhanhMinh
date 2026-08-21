"""Real unit tests for Supervisor routing policy."""

import pytest

from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routing() -> None:
    supervisor = SupervisorAgent()
    request = ResearchQuery(query="Test query")
    
    # Case 1: No research notes -> route to researcher
    state1 = ResearchState(request=request)
    state1 = supervisor.run(state1)
    assert state1.route_history[-1] == "researcher"
    
    # Case 2: Has research notes, no analysis -> route to analyst
    state2 = ResearchState(request=request, research_notes="Some notes")
    state2 = supervisor.run(state2)
    assert state2.route_history[-1] == "analyst"
    
    # Case 3: Has analysis, no final answer -> route to writer
    state3 = ResearchState(request=request, research_notes="Notes", analysis_notes="Analysis")
    state3 = supervisor.run(state3)
    assert state3.route_history[-1] == "writer"
    
    # Case 4: Has final answer -> route to done
    state4 = ResearchState(request=request, research_notes="Notes", analysis_notes="Analysis", final_answer="Answer")
    state4 = supervisor.run(state4)
    assert state4.route_history[-1] == "done"
