import sys
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report

# Setup
settings = get_settings()
configure_logging(settings.log_level)

query = "Research GraphRAG state-of-the-art"
metrics_list = []

# Baseline runner wrapper
def baseline_runner(q: str):
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.services.search_client import SearchClient
    from multi_agent_research_lab.core.schemas import ResearchQuery
    from multi_agent_research_lab.core.state import ResearchState
    
    request = ResearchQuery(query=q)
    state = ResearchState(request=request)
    
    search_client = SearchClient()
    sources = search_client.search(request.query, max_results=request.max_sources)
    context = "\n\n".join([f"Title: {s.title}\nContent: {s.snippet}" for s in sources])
    
    llm = LLMClient()
    system_prompt = "You are a helpful research assistant. Answer the user's query based ONLY on the provided search results."
    user_prompt = f"Query: {request.query}\n\nSearch Results:\n{context}"
    
    response = llm.complete(system_prompt, user_prompt)
    state.final_answer = response.content
    state.trace = [{"name": "llm", "payload": {"cost_usd": response.cost_usd}}]
    return state

# Multi-agent runner wrapper
def multi_agent_runner(q: str):
    from multi_agent_research_lab.core.schemas import ResearchQuery
    from multi_agent_research_lab.core.state import ResearchState
    from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
    
    state = ResearchState(request=ResearchQuery(query=q))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)

print("Running baseline...")
_, m_baseline = run_benchmark("Baseline", query, baseline_runner)
metrics_list.append(m_baseline)

print("Running multi-agent...")
_, m_multi = run_benchmark("Multi-Agent", query, multi_agent_runner)
metrics_list.append(m_multi)

print("\n--- BENCHMARK RESULTS ---\n")
print(render_markdown_report(metrics_list))
