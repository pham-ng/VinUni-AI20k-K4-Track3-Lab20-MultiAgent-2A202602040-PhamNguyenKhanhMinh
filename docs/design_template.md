# Design Template: Hệ Thống AI Nghiên Cứu Đa Tác Tử (Multi-Agent Research Lab)

## Problem

**Bài toán:** Hệ thống cần xử lý tự động quy trình nghiên cứu chuyên sâu (Deep Research) dựa trên một truy vấn bất kỳ từ người dùng. Quá trình bao gồm: tìm kiếm dữ liệu thực tế trên Internet, phân tích các tài liệu thu thập được để rút ra luận điểm chính, và viết một bản báo cáo học thuật hoàn chỉnh có đính kèm trích dẫn nguồn.

## Why multi-agent?

**Lý do chọn Multi-Agent:**
- **Giảm Hallucination:** Single-agent (chỉ dùng LLM 1 lần) thường xuyên bịa ra thông tin nếu không có dữ kiện thực tế hoặc phải xử lý một câu hỏi quá phức tạp.
- **Phân chia vai trò (Separation of Concerns):** Giống như một phòng lab thực tế, việc tách quy trình thành các bước riêng biệt (Tìm kiếm -> Phân tích -> Viết) giúp mỗi Agent chỉ cần tập trung vào một system prompt cụ thể, tăng độ chính xác và dễ dàng debug khi có lỗi.
- **Dễ mở rộng:** Có thể thay đổi mô hình LLM rẻ hơn cho tác vụ đơn giản (như Supervisor) và mô hình mạnh hơn (như Analyst) cho tác vụ phức tạp.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối luồng chạy, quyết định Agent nào làm bước tiếp theo | ResearchState hiện tại | Tên node tiếp theo (researcher, analyst, writer, done) | Vòng lặp vô hạn nếu không có max_iteration. |
| Researcher | Tìm kiếm thông tin trên Internet thông qua Tavily API | query (Từ người dùng) | sources (danh sách bài báo), research_notes (tóm tắt thô) | Network Timeout, API giới hạn rate limit. |
| Analyst | Phân tích tài liệu thô, rút ra luận điểm và sự thật cốt lõi | research_notes, sources | analysis_notes (luận điểm chính đã lọc) | Trả về phân tích sai nếu research_notes bị rỗng. |
| Writer | Soạn thảo báo cáo Markdown cuối cùng, chèn citation | analysis_notes, audience | final_answer (Báo cáo hoàn chỉnh) | Bỏ sót trích dẫn (Citation) hoặc format sai. |

## Shared state

**Các trường (Fields) trong ResearchState:**
- request: Lưu thông tin đầu vào (query, max_sources, audience) để các agent biết cần tìm gì và viết cho ai.
- sources: Danh sách URL/Tiêu đề để làm nguồn trích dẫn sau này.
- research_notes: Ghi chú thô để Analyst có dữ liệu làm việc.
- analysis_notes: Bản nháp phân tích chuyên sâu để Writer có nội dung đáng tin cậy.
- final_answer: Sản phẩm cuối cùng trả về cho User.
- errors: Mảng lưu lỗi để Supervisor xử lý fallback.
- iteration & route_history: Để Supervisor không bị lặp vô hạn và dễ theo dõi trace.

## Routing policy

**Luồng đồ thị (Graph Workflow):**
1. **Bắt đầu (Entry Point):** Supervisor kiểm tra state.
2. Nếu sources rỗng -> Supervisor gọi Researcher.
3. Nếu đã có sources nhưng chưa có analysis_notes -> Supervisor gọi Analyst.
4. Nếu đã có analysis_notes nhưng chưa có final_answer -> Supervisor gọi Writer.
5. Khi đã có final_answer hoặc vượt quá max_iterations -> Supervisor báo done.

## Guardrails

- **Max iterations:** Giới hạn vòng lặp ở mức 6 để tránh việc tốn token vô hạn khi hệ thống kẹt ở 1 bước.
- **Timeout:** Cài đặt timeout ở HTTP client (requests) khi cào dữ liệu qua Tavily để không bị treo.
- **Retry:** Tự động retry khi LLM API trả về lỗi 5xx.
- **Fallback:** Nếu Researcher lỗi không tìm được, trả về mảng sources rỗng và ném lỗi vào state.errors để thoát an toàn.
- **Validation:** Bắt buộc Writer phải đính kèm trích dẫn (vd: [1]) bằng system prompt cứng.

## Benchmark plan

- **Query thử nghiệm:** *"Research GraphRAG state-of-the-art"*.
- **Metrics đo lường:** 
  1. Latency: Thời gian phản hồi (giây).
  2. Cost: Tiền LLM API USD.
  3. Citation Coverage: Tỷ lệ trích dẫn.
  4. Quality: Chấm điểm định tính.
- **Expected Outcome:** Multi-agent sẽ chậm hơn và tốn tiền hơn Single-agent từ 2-3 lần, nhưng Quality phải cao hơn và Citation Coverage phải đạt 100%.
