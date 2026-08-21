import sys
import re

# 1. Update cli.py to import get_langchain_callbacks
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
        res = workflow.run(state, config=config)
        if callbacks:
            trace_id = callbacks[0].get_trace_id()
            if trace_id:
                res.trace.append({"trace_id": trace_id})
        return res"""

new_run_multi = """    def run_multi(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        config = {}
        from multi_agent_research_lab.observability.tracing import get_langchain_callbacks
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

# 2. Update benchmark.py notes
bench_file = 'src/multi_agent_research_lab/evaluation/benchmark.py'
with open(bench_file, 'r', encoding='utf-8') as f:
    bench_content = f.read()

old_metrics_return = """            failure_rate=failure,
            notes="; ".join(state.errors) if failure else None
        )"""

new_metrics_return = """            failure_rate=failure,
            notes="; ".join([str(e) for e in state.errors]) if failure else ""
        )"""

bench_content = bench_content.replace(old_metrics_return, new_metrics_return)
with open(bench_file, 'w', encoding='utf-8') as f:
    f.write(bench_content)
