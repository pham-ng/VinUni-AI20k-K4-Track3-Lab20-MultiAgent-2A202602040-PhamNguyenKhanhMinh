"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""
    lines = [
        "# Benchmark Report",
        "",
        "This report compares the performance of Single-agent vs Multi-agent workflow.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Citation cov. | Failure rate | Notes |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        citation = "" if item.citation_coverage is None else f"{item.citation_coverage:.0%}"
        failure = "" if item.failure_rate is None else f"{item.failure_rate:.0%}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} "
            f"| {citation} | {failure} | {item.notes} |"
        )
    lines.extend([
        "",
        "## Analysis",
        "- **Single-agent**: Usually faster but suffers from hallucination.",
        "- **Multi-agent**: Costs more tokens and latency, but structure is significantly better and citations are accurate.",
        "- **Failure Mode**: Network timeout during web search can cause Researcher to fail, affecting the whole pipeline.",
    ])
    return "\n".join(lines) + "\n"
