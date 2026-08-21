"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from pydantic import ValidationError
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


def _parse_query(query: str) -> ResearchQuery:
    try:
        return ResearchQuery(query=query)
    except ValidationError as exc:
        console.print(
            Panel.fit(
                f"Invalid query: {exc.errors()[0]['msg']}",
                title="Input Error",
                style="red",
            )
        )
        raise typer.Exit(code=1) from exc


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    import time

    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.services.search_client import SearchClient

    _init()
    request = _parse_query(query)
    state = ResearchState(request=request)

    console.print("[yellow]Running search for baseline...[/yellow]")
    search_client = SearchClient()
    sources = search_client.search(request.query, max_results=request.max_sources)

    context = "\n\n".join([f"Title: {s.title}\nContent: {s.snippet}" for s in sources])

    console.print("[yellow]Running LLM for baseline...[/yellow]")
    llm = LLMClient()
    system_prompt = (
        "You are a helpful research assistant. "
        "Answer the user's query based ONLY on the provided search results. "
        f"Target audience: {request.audience}."
    )
    user_prompt = f"Query: {request.query}\n\nSearch Results:\n{context}"

    start_time = time.time()
    response = llm.complete(system_prompt, user_prompt)
    latency = time.time() - start_time

    state.final_answer = response.content
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Answer"))

    console.print(
        f"[green]Latency: {latency:.2f}s | "
        f"Cost: ${response.cost_usd:.4f} | "
        f"Tokens: {response.input_tokens} in / {response.output_tokens} out[/green]"
    )


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=_parse_query(query))
    workflow = MultiAgentWorkflow()
    
    from multi_agent_research_lab.observability.tracing import get_langchain_callbacks
    config = {}
    callbacks = get_langchain_callbacks()
    if callbacks:
        config["callbacks"] = callbacks
        console.print("[green]Tracing enabled![/green]")

    try:
        result = workflow.run(state, config=config)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        if callbacks:
            callbacks[0].flush()
        raise typer.Exit(code=2) from exc
        
    console.print(result.model_dump_json(indent=2))

@app.command("benchmark")
def benchmark(
    dataset: Annotated[str, typer.Option("--dataset", help="Comma-separated list of queries")] = "Research GraphRAG state-of-the-art",
) -> None:
    """Run evaluation benchmark on both baseline and multi-agent systems."""
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    from multi_agent_research_lab.core.schemas import ResearchQuery
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.services.search_client import SearchClient

    _init()
    queries = [q.strip() for q in dataset.split(",") if q.strip()]
    metrics_list = []
    
    console.print(f"[cyan]Starting benchmark on {len(queries)} queries...[/cyan]")
    
    def run_baseline(q: str) -> ResearchState:
        request = ResearchQuery(query=q)
        state = ResearchState(request=request)
        search_client = SearchClient()
        sources = search_client.search(request.query, max_results=request.max_sources)
        context = "\\n\\n".join([f"Title: {s.title}\\nContent: {s.snippet}" for s in sources])
        llm = LLMClient()
        system_prompt = "You are a helpful research assistant. Answer the user's query based ONLY on the provided search results."
        user_prompt = f"Query: {request.query}\\n\\nSearch Results:\\n{context}"
        try:
            response = llm.complete(system_prompt, user_prompt)
            state.final_answer = response.content
            state.trace = [{"name": "llm", "payload": {"cost_usd": response.cost_usd}}]
        except Exception as e:
            state.errors.append(str(e))
        return state

    def run_multi(q: str) -> ResearchState:
        state = ResearchState(request=ResearchQuery(query=q))
        workflow = MultiAgentWorkflow()
        config = {}
        from multi_agent_research_lab.observability.tracing import get_langchain_callbacks
        callbacks = get_langchain_callbacks()
        if callbacks:
            config["callbacks"] = callbacks
        res = workflow.run(state, config=config)
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
        return res

    for i, q in enumerate(queries):
        console.print(f"\\n[yellow]--- Query {i+1}/{len(queries)}: {q} ---[/yellow]")
        console.print("[dim]Running baseline...[/dim]")
        _, m_baseline = run_benchmark("Baseline", q, run_baseline)
        metrics_list.append(m_baseline)
        
        console.print("[dim]Running multi-agent...[/dim]")
        _, m_multi = run_benchmark("Multi-Agent", q, run_multi)
        metrics_list.append(m_multi)
        
    console.print("\\n[green]Benchmark complete! Generating report...[/green]\\n")
    report_md = render_markdown_report(metrics_list)
    console.print(report_md)
    
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)
    console.print("[green]Saved to reports/benchmark_report.md[/green]")
    



if __name__ == "__main__":
    app()
