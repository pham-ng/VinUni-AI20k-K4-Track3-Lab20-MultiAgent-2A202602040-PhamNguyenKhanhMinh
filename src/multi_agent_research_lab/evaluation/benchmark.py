"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object."""

    started = perf_counter()
    try:
        state = runner(query)
        latency = perf_counter() - started
        
        # Calculate cost from trace
        cost = 0.0
        for event in state.trace:
            payload = event.get("payload", {})
            cost += payload.get("cost_usd") or 0.0
            
        # LLM-as-a-judge Evaluation
        quality_score = 0.0
        citation_coverage = 0.0
        
        if state.final_answer:
            from multi_agent_research_lab.services.llm_client import LLMClient
            import re as regex
            eval_llm = LLMClient()
            
            sys_q = "You are a strict academic grader. Rate the following answer's quality from 0.0 to 10.0 based on depth, accuracy, and structure. Reply with ONLY a float number."
            usr_q = f"Query: {query}\nAnswer: {state.final_answer}"
            try:
                q_res = eval_llm.complete(sys_q, usr_q)
                match = regex.search(r"\d+(\.\d+)?", q_res.content)
                quality_score = float(match.group()) if match else 5.0
                cost += q_res.cost_usd or 0.0
            except Exception:
                quality_score = 0.0
                
            sys_c = "You are a strict academic grader. Estimate the citation coverage (0.0 to 1.0) of the following answer. 1.0 means every claim has an inline citation. Reply with ONLY a float number."
            usr_c = f"Answer: {state.final_answer}"
            try:
                c_res = eval_llm.complete(sys_c, usr_c)
                match = regex.search(r"\d+(\.\d+)?", c_res.content)
                citation_coverage = float(match.group()) if match else 0.0
                cost += c_res.cost_usd or 0.0
            except Exception:
                citation_coverage = 0.0
                
        failure = 1.0 if len(state.errors) > 0 else 0.0
        metrics = BenchmarkMetrics(
            run_name=run_name, 
            latency_seconds=latency,
            estimated_cost_usd=cost,
            quality_score=quality_score,
            citation_coverage=citation_coverage,
            failure_rate=failure,
            notes="; ".join([str(e) for e in state.errors]) if failure else ""
        )
        
        # Push scores to Langfuse if available
        trace_id = None
        for t in state.trace:
            if "trace_id" in t:
                trace_id = t["trace_id"]
                break
                
        if trace_id:
            try:
                from multi_agent_research_lab.observability.tracing import get_langfuse_client
                client = get_langfuse_client()
                if client:
                    client.score(trace_id=trace_id, name="quality", value=quality_score)
                    client.score(trace_id=trace_id, name="citation_coverage", value=citation_coverage)
                    client.flush()
            except Exception:
                pass
    except Exception as e:
        latency = perf_counter() - started
        metrics = BenchmarkMetrics(
            run_name=run_name,
            latency_seconds=latency,
            failure_rate=1.0,
            notes=str(e)
        )
        from multi_agent_research_lab.core.schemas import ResearchQuery
        state = ResearchState(request=ResearchQuery(query=query)) # Empty fallback
        
    return state, metrics
