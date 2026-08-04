# Bài Tập Nhóm — E-commerce Support RAG Chatbot

## Mục Tiêu

Sau khi hoàn thành bài cá nhân, nhóm ngồi lại để xây dựng **1 trong 2 sản phẩm**:

---

## Yêu cầu 1: Sản phẩm nhóm RAG Chatbot

Xây dựng chatbot trả lời câu hỏi về chính sách thương mại điện tử và hỗ trợ khách hàng liên quan.

**Yêu cầu:**
- Giao diện chat (Streamlit / Gradio / Chainlit)
- Trả lời có citation (dựa trên Task 10)
- Hỗ trợ follow-up questions (conversation memory)
- Hiển thị source documents đã dùng

**Stack gợi ý:**
```
Chainlit/Streamlit → Retrieval (Task 9) → Generation (Task 10) → Display
```

---

## Yêu cầu 2: RAG Evaluation Pipeline

Sử dụng **1 trong 3 framework** sau để evaluate pipeline RAG của nhóm:

### Framework lựa chọn

| Framework | Cài đặt | Đặc điểm |
|-----------|---------|-----------|
| [DeepEval](https://github.com/confident-ai/deepeval) | `pip install deepeval` | Nhiều metric built-in, dễ integrate với pytest |
| [RAGAS](https://github.com/explodinggradients/ragas) | `pip install ragas` | Chuẩn industry cho RAG eval, 3 trục chính |
| [TruLens](https://github.com/truera/trulens) | `pip install trulens` | Dashboard UI, feedback functions mạnh |

### Yêu cầu Evaluation

1. **Tạo Golden Dataset** — tối thiểu 15 cặp Q&A (question, expected_answer, expected_context)
2. **Chạy evaluation** trên toàn bộ golden dataset với các metrics sau:
   - **Faithfulness** — câu trả lời có bám đúng context không?
   - **Answer Relevance** — câu trả lời có đúng câu hỏi không?
   - **Context Recall** — retriever có lấy đủ evidence không?
   - **Context Precision** — trong context lấy về, bao nhiêu % thực sự hữu ích?
3. **So sánh A/B** — chạy eval trên ít nhất 2 config khác nhau (ví dụ: có reranking vs không reranking, hoặc hybrid vs dense-only)
4. **Báo cáo** — bảng điểm + phân tích worst performers + đề xuất cải tiến

Xem code mẫu (DeepEval/RAGAS/TruLens) chi tiết trong `README.md` gốc mục "Yêu cầu 2".

### Deliverable Evaluation

- [ ] File `group_project/evaluation/golden_dataset.json` — 15+ cặp Q&A
- [ ] File `group_project/evaluation/eval_pipeline.py` — script chạy evaluation
- [ ] File `group_project/evaluation/results.md` — bảng điểm + phân tích
- [ ] So sánh A/B ít nhất 2 configs

---

## Yêu Cầu Chung

1. **Tích hợp pipeline** từ bài cá nhân của các thành viên
2. **Demo hoạt động được** trong buổi trình bày (chạy local hoặc deploy)
3. **Evaluation pipeline** chạy được và có báo cáo kết quả
4. **Code push lên repository** chung của nhóm
5. **README** mô tả kiến trúc và phân công (điền bên dưới)

---

## Kiến Trúc Hệ Thống

```
User question
    |
    v
Streamlit Chat UI (app.py)
    |
    v
Task 10: generate_with_citation()
    |
    v
Task 9: Retrieval Pipeline
    |-- Task 5: Semantic Search
    |-- Task 6: BM25 Lexical Search
    |-- Task 7: RRF Reranking
    `-- Task 8: PageIndex/Gemini fallback
    |
    v
Context formatting + document reordering
    |
    v
Gemini LLM answer with citations
    |
    v
Answer + source chunks displayed in UI
```

---

## Phân Công Công Việc

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|-----------|------|----------|------------|
| Lê Trí Tùng | 2A202601458 | Task 9: Retrieval Pipeline; Task 10: Generation có Citation; điều phối tích hợp | Done |
| Vũ Xuân Anh | 2A202602010 | Task 1: Thu thập tài liệu; Task 2: Crawl bài viết | Done |
| Nguyễn Quốc Bảo | 2A202601726 | Task 3: Convert Markdown; Task 4: Chunking & Indexing | Done |
| Đỗ Thị Thanh Loan | 2A202601654 | Task 5: Semantic Search; Task 6: Lexical Search BM25 | Done |
| Nguyễn Thuỳ Trang | 2A202601294 | Task 7: Reranking; Task 8: PageIndex Fallback | Done |

---

## Hướng Dẫn Chạy

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy app
streamlit run app.py

# Chạy evaluation nhóm
python -m group_project.evaluation.eval_pipeline

# Chạy test cá nhân Task 1-10
python -m pytest tests/test_individual.py -v
```

---

## Demo Live & Nộp Bài

### Demo flow 5-8 phút

1. Giới thiệu kiến trúc: data landing -> markdown -> chunk/index -> hybrid retrieval -> generation có citation.
2. Mở chatbot bằng `streamlit run app.py`.
3. Demo 3 câu hỏi:
   - Shopee hỗ trợ những phương thức thanh toán nào?
   - Hồ sơ đăng ký hộ kinh doanh cá thể cần những giấy tờ nào?
   - Doanh thu bán hàng online bao nhiêu thì phải nộp thuế?
4. Mở expander nguồn tham khảo để chỉ ra citation và source chunks.
5. Chạy hoặc mở `group_project/evaluation/results.md` để trình bày A/B evaluation.

### Checklist nộp bài

- [x] Task 1-10 pass automated tests.
- [x] Chatbot UI tích hợp `generate_with_citation()`.
- [x] Golden dataset có 15 câu hỏi.
- [x] Evaluation pipeline chạy được.
- [x] Báo cáo `group_project/evaluation/results.md` có bảng điểm A/B, worst performers và recommendations.
- [x] README có kiến trúc, phân công, hướng dẫn chạy và demo flow.

---

## Bonus Đã Implement

| Bonus | Điểm | Minh chứng |
|-------|------|------------|
| Giải thích cơ chế lexical search/BM25 | +5 | `src/task6_lexical_search.py` có BM25 fallback tự implement, giải thích TF/IDF, k1, b và length normalization. |
| Query Expansion / HyDE-lite | +5 | `src/task9_retrieval_pipeline.py` có `expand_query()` và `generate_hypothetical_document()` trước khi hybrid retrieval. |
| Conversation memory | +3 | `app.py` có toggle memory, truyền lịch sử chat vào `generate_with_citation(..., chat_history=...)`. |
| UI/UX hiển thị source, score, retrieval source | +3 | Streamlit expander hiển thị từng source chunk, type, score và nguồn retrieval `hybrid/pageindex/dense`. |
| Deploy-ready Streamlit app | tối đa +4 nếu deploy thật | Repo có `app.py`, `requirements.txt`, README front matter Hugging Face Spaces; chỉ cần push lên Space/Render để lấy URL public. |

Điểm kỳ vọng sau bonus nếu demo mượt: khoảng 95-98/100, tùy việc có URL deploy online thật hay không.

---

## Lưu ý

Hãy giữ lại repo này nếu như bạn học track 3 giai đoạn 2, chúng ta sẽ phát triển tiếp dự án lên knowledge graph để khắc phục các câu hỏi hóc búa khi có các câu hỏi khó.
