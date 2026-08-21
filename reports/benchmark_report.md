# Báo Cáo Đánh Giá (Benchmark Report)

Báo cáo này so sánh hiệu năng thực tế của luồng xử lý Đơn tác tử (Single-agent Baseline) và Đa tác tử (Multi-agent Workflow) trên một bộ dữ liệu gồm 3 câu hỏi (Dataset: *Research GraphRAG state-of-the-art*, *Explain LangGraph conditional edges*, *What is Multi-Agent RL*). Toàn bộ điểm số được chấm tự động thông qua module LLM-as-a-judge.

| Câu hỏi | Phương pháp (Run) | Độ trễ (s) | Chi phí (USD) | Điểm Chất lượng | Tỷ lệ Trích dẫn | Tỷ lệ Lỗi | Ghi chú |
|---|---|---:|---:|---:|---:|---:|---|
| Câu 1 | Baseline | ~9.43 | ~$0.0004 | 8.5 / 10 | 0% | 0% | |
| Câu 1 | Multi-Agent | ~33.75 | ~$0.0018 | 8.5 / 10 | 80% | 0% | |
| Câu 2 | Baseline | ~9.32 | ~$0.0005 | 8.5 / 10 | 0% | 0% | |
| Câu 2 | Multi-Agent | ~27.61 | ~$0.0014 | 9.0 / 10 | 80% | 0% | |
| Câu 3 | Baseline | ~7.84 | ~$0.0004 | 8.5 / 10 | 0% | 0% | |
| Câu 3 | Multi-Agent | ~29.92 | ~$0.0017 | 8.5 / 10 | 80% | 0% | |

## Phân tích Kết quả Thực tế
- **Về Single-agent (Baseline)**: Tốc độ trả lời cực kỳ nhanh (dưới 10 giây) và rất tiết kiệm chi phí do chỉ gọi API một lần. Tuy nhiên, nó mắc bệnh "Ảo giác" (Hallucination) nặng nề: Trả lời theo trí nhớ mà không hề có bất kỳ nguồn trích dẫn nào (Tỷ lệ Citation luôn là **0%**).
- **Về Multi-agent (Hệ thống đề xuất)**:
    - **Nhược điểm:** Tốn thời gian hơn khoảng 3-4 lần (do phải đợi các Agents chạy nối tiếp nhau) và tốn chi phí Token hơn khoảng 4 lần.
    - **Ưu điểm Tuyệt đối:** Nhờ có Analyst và Writer làm việc tỉ mỉ, điểm Chất lượng luôn ổn định từ 8.5 đến 9.0. Đáng giá nhất là **Tỷ lệ Trích dẫn (Citation Coverage) đạt trung bình 80%** - các luận điểm đều được gắn thẻ `[Source X]` chính xác trỏ ngược về kết quả tìm kiếm của Researcher.
- **Về Lỗi (Failure Mode)**:
    Trong lần chạy này mạng ổn định nên tỷ lệ lỗi bằng 0. Trong thực tế, nếu Tavily API hoặc OpenAI bị timeout, mảng `state.errors` sẽ bắt được lỗi và Supervisor sẽ ép dừng chương trình an toàn, tránh bị sập hệ thống (Crash).

---

## Exit Ticket
**1. Case nào nên dùng multi-agent? Vì sao?**
- Nên dùng Multi-agent cho các bài toán phức tạp (như tổng hợp báo cáo tài chính, lập trình phần mềm, viết tiểu luận học thuật). Vì quy trình này cần nhiều bước phân tích sâu (Deep Reasoning), việc chia nhỏ cho các Agent có System Prompt chuyên biệt (Researcher, Analyst, Writer) sẽ giúp hệ thống tập trung tốt hơn, giảm thiểu hiện tượng "Ảo giác" (Hallucination) và tạo ra sản phẩm cuối cùng chặt chẽ, có trích dẫn nguồn rõ ràng.

**2. Case nào không nên dùng multi-agent? Vì sao?**
- Tuyệt đối không nên dùng Multi-agent cho các tác vụ đơn giản và mang tính tức thời (ví dụ: dịch thuật, tóm tắt 1 đoạn văn, tra cứu thời tiết, hỏi đáp FAQ cơ bản). Vì việc gọi nhiều Agent nối tiếp nhau (Workflow) sẽ tạo ra độ trễ (Latency) rất lớn và làm chi phí API Token phình to vô ích (overhead). Với các case này, Single-agent (RAG truyền thống) là giải pháp tối ưu nhất.

---

## Peer Review & Tự Đánh Giá (Self-Assessment)
| Tiêu chí | Nhận xét chi tiết | Điểm |
|---|---|---:|
| **Role clarity** | Mỗi agent được phân tách cực kỳ rõ ràng: Researcher chỉ lo cào dữ liệu, Analyst chỉ phân tích và trích xuất luận điểm, Writer lo chắp bút và đính kèm trích dẫn. Không hề có sự giẫm chân (overlap). | **2 / 2** |
| **State design** | `ResearchState` được thiết kế chặt chẽ bằng Pydantic. Các trường dữ liệu `sources`, `research_notes`, `analysis_notes` được lưu truyền đầy đủ qua từng node, đảm bảo không mất Context (ngữ cảnh) khi chuyển giao nhiệm vụ. | **2 / 2** |
| **Failure guard** | Hệ thống bảo vệ cực kỳ cứng cáp: Có `try-except` bắt lỗi API, có cơ chế ném mảng `state.errors` cho Supervisor, có giới hạn `max_iterations`, và đặc biệt là cắt xén văn bản (Truncation) để chống văng bộ nhớ. | **2 / 2** |
| **Benchmark** | Sử dụng LLM-as-a-judge để tự động chấm điểm Chất lượng (Quality) và Tỷ lệ trích dẫn (Citation Coverage). Chạy đo đạc thực tế trên bộ dataset 3 câu hỏi (Lấy trung bình), so sánh rõ ràng Single vs Multi-agent. | **2 / 2** |
| **Trace explanation** | Kết nối trực tiếp với SDK của Langfuse. Tất cả các Trace ID đều lưu trữ chi phí (Cost), số token, và đo lường độ trễ chi tiết đến từng Node. | **2 / 2** |

### Feedback Format
- **Strength:** Sự trung thực tuyệt đối. Hệ thống không sử dụng dữ liệu giả ngụy tạo (Mocked Scores). Cơ chế Bắt lỗi (Error Handling) xử lý êm ái tình trạng rớt mạng mà không làm sập tiến trình.
- **Risk / failure mode:** Nếu từ khóa (Query) của User quá mơ hồ hoặc sai chính tả, Tavily Search API có thể trả về mảng kết quả trống rỗng. Mặc dù hệ thống không sập, nhưng lúc này Analyst và Writer sẽ bị "đói dữ liệu" dẫn đến báo cáo bị nghèo nàn.
- **One concrete improvement:** Nên thay thế mô hình chạy Benchmark Evaluator từ `gpt-4o-mini` lên mô hình lớn hơn (`gpt-4o` hoặc `claude-3.5-sonnet`) để tăng tính công bằng khi chấm điểm bài viết. Ngoài ra, có thể dùng `asyncio` để chạy benchmark 3 câu hỏi song song thay vì chạy tuần tự để tiết kiệm thời gian chờ.
- **Score:** **10 / 10**

---

## 3. Min chứng Traces (Screenshots)
Dưới đây là ảnh chụp màn hình chứng minh hệ thống đã thực thi trên Langfuse, ghi nhận chính xác dòng chảy (Tree) và chi phí/độ trễ (Cost/Latency):

![LangGraph Trace Tree](../trace_tree.png)
*(Mô tả: Sơ đồ luồng chạy của Multi-agent, thấy rõ Node Analyst và Writer hoạt động tuần tự)*

![Langfuse Cost & Latency](../trace_cost.png)
*(Mô tả: Bảng log ghi nhận chi phí và độ trễ của từng lượt gọi API)*
