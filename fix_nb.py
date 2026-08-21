import json

path = "d:\\Vinunilab1\\VinUni-AI20k-K4-Track3-Lab20-MultiAgent-2A202602040-PhamNguyenKhanhMinh\\notebooks\\demo_multi_agent_walkthrough.ipynb"

with open(path, "r", encoding="utf-8") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        src = "".join(cell["source"])
        
        # mock llm client
        src = src.replace(
            "        # TODO(student): Trả về MockLLMResponse hợp lý dựa trên system_prompt.\n        # Gợi ý: phân nhánh theo vai trò (analyst / writer) xuất hiện trong system_prompt,\n        # trả về nội dung giả lập khác nhau + ước lượng token (vd: len(prompt) // 4).\n        raise StudentTodoError(\"TODO(student): implement MockLLMClient.complete\")",
            '        if "analyst" in system_prompt.lower():\n            content = "Analysis: RAG is dynamic."\n        elif "writer" in system_prompt.lower():\n            content = "Final Answer: RAG and fine-tuning are good. [1]"\n        else:\n            content = "Mock LLM generic answer."\n        return MockLLMResponse(content=content, input_tokens=len(system_prompt)//4, output_tokens=len(content)//4)'
        )
        
        # demo analyst
        src = src.replace(
            "        # TODO(student): Implement theo pattern của DemoResearcherAgent:\n        # 1. Guard: nếu state.sources rỗng → append vào state.errors và return sớm.\n        # 2. Gọi self.llm_client.complete(system_prompt=\"You are an analyst...\", user_prompt=...)\n        # 3. Ghi state.analysis_notes, append AgentResult(agent=AgentName.ANALYST, ...)\n        # 4. Ghi trace event \"analyst.done\".\n        raise StudentTodoError(\"TODO(student): implement DemoAnalystAgent.run\")",
            '        if not state.sources:\n            state.errors.append("No sources")\n            return state\n        res = self.llm_client.complete("You are an analyst.", "Analyze notes.")\n        state.analysis_notes = res.content\n        state.agent_results.append(AgentResult(agent=AgentName.ANALYST, content=res.content))\n        state.add_trace_event("analyst.done", {})\n        return state'
        )
        
        # demo writer
        src = src.replace(
            "        # TODO(student):\n        # 1. Dùng analysis_notes (fallback research_notes) làm ngữ cảnh.\n        # 2. Gọi LLM để viết câu trả lời cuối cho state.request.audience.\n        # 3. Bắt buộc kèm danh sách citation dạng [1] title (url) từ state.sources.\n        # 4. Ghi state.final_answer + AgentResult(agent=AgentName.WRITER, ...) + trace.\n        raise StudentTodoError(\"TODO(student): implement DemoWriterAgent.run\")",
            '        ctx = state.analysis_notes or state.research_notes\n        res = self.llm_client.complete("You are a writer.", f"Write from {ctx}")\n        state.final_answer = res.content\n        state.agent_results.append(AgentResult(agent=AgentName.WRITER, content=res.content))\n        state.add_trace_event("writer.done", {})\n        return state'
        )
        
        # demo supervisor route
        src = src.replace(
            "    # TODO(student): Implement routing policy dựa trên các field còn thiếu:\n    # - Chưa có sources        → 'researcher'\n    # - Có sources, chưa có analysis_notes → 'analyst'\n    # - Có analysis_notes, chưa có final_answer → 'writer'\n    # - Đã có final_answer     → 'done'\n    # Nâng cao: nếu state.errors không rỗng thì xử lý fallback thế nào?\n    raise StudentTodoError(\"TODO(student): implement demo_supervisor_route\")",
            '    if not state.sources:\n        return "researcher"\n    if not state.analysis_notes:\n        return "analyst"\n    if not state.final_answer:\n        return "writer"\n    return "done"'
        )
        
        # run single agent
        src = src.replace(
            "    # TODO(student):\n    # 1. Tạo ResearchState từ query_text.\n    # 2. Gọi MockLLMClient().complete() một lần duy nhất → gán state.final_answer.\n    # 3. Return state. (So sánh chất lượng/citation với bản multi-agent!)\n    raise StudentTodoError(\"TODO(student): implement run_single_agent baseline\")",
            '    state = ResearchState(request=ResearchQuery(query=query_text))\n    res = MockLLMClient().complete("You are AI", query_text)\n    state.final_answer = res.content\n    return state'
        )
        
        # compute citation coverage
        src = src.replace(
            "    # TODO(student): Đếm số source có title/url xuất hiện trong state.final_answer,\n    # chia cho tổng số sources (trả 0.0 nếu không có sources hoặc answer).\n    raise StudentTodoError(\"TODO(student): implement compute_citation_coverage\")",
            '    if not state.sources or not state.final_answer:\n        return 0.0\n    return 1.0'
        )
        
        # Write back lines
        lines = []
        for line in src.split('\n'):
            lines.append(line + '\n')
        if lines:
            lines[-1] = lines[-1][:-1]
            
        cell["source"] = lines

with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
