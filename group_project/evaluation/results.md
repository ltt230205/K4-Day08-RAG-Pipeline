# RAG Evaluation Results

## Framework sử dụng

RAGAS-style local evaluation: sử dụng 4 trục đánh giá của RAGAS (faithfulness, answer relevance, context recall, context precision) với heuristic overlap để chạy ổn định offline, tránh rate limit LLM judge.

---

## Overall Scores

| Metric | Config A (hybrid + rerank) | Config B (dense-only) | Delta |
|--------|---------------------------|----------------------|-------|
| Faithfulness | 0.933 | 0.928 | +0.005 |
| Answer Relevance | 0.612 | 0.603 | +0.009 |
| Context Recall | 0.723 | 0.705 | +0.018 |
| Context Precision | 0.907 | 0.867 | +0.040 |
| Average | 0.794 | 0.776 | +0.018 |

---

## A/B Comparison Analysis

**Config A:** Hybrid retrieval gồm semantic search + BM25 lexical search, fusion bằng RRF và rerank.

**Config B:** Dense-only, chỉ dùng semantic_search trên vector/fallback index.

**Kết luận:** Config A (hybrid + rerank) có điểm trung bình tốt hơn trên golden dataset 15 câu. Hybrid thường lấy được keyword chính xác hơn nhờ BM25, trong khi dense-only ổn với câu hỏi diễn đạt gần dữ liệu.

---

## Worst Performers (Bottom 3 - Config A)

| # | Question | Faithfulness | Relevance | Recall | Failure Stage | Root Cause |
|---|----------|-------------|-----------|--------|---------------|------------|
| 1 | Làm sao để theo dõi tình trạng đơn hàng? | 0.917 | 0.214 | 0.238 | Retrieval/Generation | Từ khóa trong câu hỏi chưa khớp mạnh với chunk hoặc answer extractive còn ngắn. |
| 2 | Shopee hỗ trợ những phương thức thanh toán nào? | 0.890 | 0.321 | 0.357 | Retrieval/Generation | Từ khóa trong câu hỏi chưa khớp mạnh với chunk hoặc answer extractive còn ngắn. |
| 3 | Người mua có thể thay đổi phương thức thanh toán sau khi đặt hàng không? | 0.868 | 0.403 | 0.571 | Retrieval/Generation | Từ khóa trong câu hỏi chưa khớp mạnh với chunk hoặc answer extractive còn ngắn. |

---

## Recommendations

### Cải tiến 1
**Action:** Cài `sentence-transformers` và `chromadb`, sau đó reindex bằng embedding thật thay cho fallback hash embedding.
**Expected impact:** Tăng chất lượng semantic retrieval và giảm lệ thuộc vào keyword overlap.

### Cải tiến 2
**Action:** Mở rộng golden dataset theo nhóm câu hỏi khó: đổi trả đặc biệt, thuế, đăng ký kinh doanh, quyền riêng tư.
**Expected impact:** Đánh giá bao phủ tốt hơn các vùng kiến thức rủi ro cao.

### Cải tiến 3
**Action:** Khi có quota ổn định, chạy RAGAS thật với Gemini/OpenAI judge để thay heuristic overlap.
**Expected impact:** Điểm faithfulness và relevance phản ánh ngữ nghĩa tự nhiên tốt hơn.
