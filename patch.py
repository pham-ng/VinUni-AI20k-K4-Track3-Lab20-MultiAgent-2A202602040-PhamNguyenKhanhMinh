import sys
import re

file_path = 'src/multi_agent_research_lab/evaluation/benchmark.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_metrics = r'        metrics = BenchmarkMetrics\(\s*run_name=run_name,\s*latency_seconds=latency,\s*estimated_cost_usd=cost,\s*quality_score=9.0, # Mocked quality score\s*citation_coverage=0.9, # Mocked citation coverage\s*failure_rate=0.0\s*\)'

new_metrics = '''        # LLM-as-a-judge Evaluation
        quality_score = 0.0
        citation_coverage = 0.0
        
        if state.final_answer:
            from multi_agent_research_lab.services.llm_client import LLMClient
            import re as regex
            eval_llm = LLMClient()
            
            sys_q = "You are a strict academic grader. Rate the following answer's quality from 0.0 to 10.0 based on depth, accuracy, and structure. Reply with ONLY a float number."
            usr_q = f"Query: {query}\\nAnswer: {state.final_answer}"
            try:
                q_res = eval_llm.complete(sys_q, usr_q)
                match = regex.search(r"\\d+(\\.\\d+)?", q_res.content)
                quality_score = float(match.group()) if match else 5.0
                cost += q_res.cost_usd or 0.0
            except Exception:
                quality_score = 0.0
                
            sys_c = "You are a strict academic grader. Estimate the citation coverage (0.0 to 1.0) of the following answer. 1.0 means every claim has an inline citation. Reply with ONLY a float number."
            usr_c = f"Answer: {state.final_answer}"
            try:
                c_res = eval_llm.complete(sys_c, usr_c)
                match = regex.search(r"\\d+(\\.\\d+)?", c_res.content)
                citation_coverage = float(match.group()) if match else 0.0
                cost += c_res.cost_usd or 0.0
            except Exception:
                citation_coverage = 0.0
                
        metrics = BenchmarkMetrics(
            run_name=run_name, 
            latency_seconds=latency,
            estimated_cost_usd=cost,
            quality_score=quality_score,
            citation_coverage=citation_coverage,
            failure_rate=0.0
        )'''

content = re.sub(old_metrics, lambda m: new_metrics, content)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
