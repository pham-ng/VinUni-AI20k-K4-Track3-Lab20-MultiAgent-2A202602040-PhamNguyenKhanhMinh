import sys
import re

# 1. Update cli.py run_multi
cli_file = 'src/multi_agent_research_lab/cli.py'
with open(cli_file, 'r', encoding='utf-8') as f:
    cli_content = f.read()

old_run_multi = """    def run_multi(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        config = {}
        callbacks = get_langchain_callbacks()
        if callbacks:
            config["callbacks"] = callbacks
        return workflow.run(state, config=config)"""

new_run_multi = """    def run_multi(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        config = {}
        callbacks = get_langchain_callbacks()
        if callbacks:
            config["callbacks"] = callbacks
        res = workflow.run(state, config=config)
        if callbacks:
            trace_id = callbacks[0].get_trace_id()
            if trace_id:
                res.trace.append({"trace_id": trace_id})
        return res"""

cli_content = cli_content.replace(old_run_multi, new_run_multi)
with open(cli_file, 'w', encoding='utf-8') as f:
    f.write(cli_content)

# 2. Update benchmark.py to push scores
bench_file = 'src/multi_agent_research_lab/evaluation/benchmark.py'
with open(bench_file, 'r', encoding='utf-8') as f:
    bench_content = f.read()

old_metrics_return = """        failure = 1.0 if len(state.errors) > 0 else 0.0
        metrics = BenchmarkMetrics(
            run_name=run_name, 
            latency_seconds=latency,
            estimated_cost_usd=cost,
            quality_score=quality_score,
            citation_coverage=citation_coverage,
            failure_rate=failure,
            notes="; ".join(state.errors) if failure else None
        )"""

new_metrics_return = """        failure = 1.0 if len(state.errors) > 0 else 0.0
        metrics = BenchmarkMetrics(
            run_name=run_name, 
            latency_seconds=latency,
            estimated_cost_usd=cost,
            quality_score=quality_score,
            citation_coverage=citation_coverage,
            failure_rate=failure,
            notes="; ".join(state.errors) if failure else None
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
                pass"""

bench_content = bench_content.replace(old_metrics_return, new_metrics_return)
with open(bench_file, 'w', encoding='utf-8') as f:
    f.write(bench_content)
