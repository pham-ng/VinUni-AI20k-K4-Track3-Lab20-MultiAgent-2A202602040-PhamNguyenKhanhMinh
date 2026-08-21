import sys

cli_file = 'src/multi_agent_research_lab/cli.py'
with open(cli_file, 'r', encoding='utf-8') as f:
    cli_content = f.read()

old_run_multi = """        res = workflow.run(state, config=config)
        if callbacks:
            trace_id = callbacks[0].get_trace_id()
            if trace_id:
                res.trace.append({"trace_id": trace_id})
        return res"""

new_run_multi = """        res = workflow.run(state, config=config)
        if callbacks:
            try:
                # Try multiple ways to get trace_id depending on langfuse version
                trace_id = getattr(callbacks[0], "trace_id", None)
                if not trace_id and hasattr(callbacks[0], "trace"):
                    trace_id = getattr(callbacks[0].trace, "id", None)
                if trace_id:
                    res.trace.append({"trace_id": trace_id})
            except Exception:
                pass
        return res"""

cli_content = cli_content.replace(old_run_multi, new_run_multi)
with open(cli_file, 'w', encoding='utf-8') as f:
    f.write(cli_content)
