"""Unit tests cho phần Pipeline & Search (Task 4–6) — phụ trách: Người 2.

Bao phủ:
    * Task 4: load/chunk/embed/index — id ổn định, chunk_index liên tục, metadata.
    * Task 5: dense search — cosine distance -> similarity, dedup, ``top_k``.
    * Task 6: BM25 — contract, lọc theo token, tie, cache index.
    * Task 7/9: RRF và fallback — tự động skip nếu teammate chưa implement xong.

Không test nào gọi network/API thật: model embedding luôn được monkeypatch, còn
ChromaDB dùng thư mục tạm ``tmp_path``.
"""

import inspect
import sys
import types

import pytest

import src.task4_chunking_indexing as indexing
import src.task5_semantic_search as semantic
import src.task6_lexical_search as lexical
from src.contracts import validate_document, validate_search_results

DOCUMENT_CONTENT = "# Học phí\n\nSinh viên đóng học phí theo học kỳ.\n"


def metadata(source="tuition.md", chunk_index=0, url=None):
    return {
        "source": source,
        "title": "Học phí",
        "doc_type": "legal",
        "url": url,
        "chunk_index": chunk_index,
    }


def corpus_item(item_id, content, chunk_index=0, source="tuition.md"):
    return {
        "id": item_id,
        "content": content,
        "metadata": metadata(source, chunk_index),
    }


def search_result(item_id, score, method="dense", chunk_index=0):
    return {
        "id": item_id,
        "content": "Sinh viên đóng học phí theo học kỳ.",
        "score": score,
        "metadata": metadata(chunk_index=chunk_index),
        "retrieval_method": method,
    }


class FakeCollection:
    """ChromaDB collection giả cho dense search."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def query(self, **kwargs):
        self.calls.append(kwargs)
        return self.response


class FakeEmbeddingModel:
    """Model giả để test không phải tải model thật."""

    def __init__(self, vector=(0.1, 0.2)):
        self.vector = list(vector)
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append((list(texts), kwargs))
        return [list(self.vector) for _ in texts]


def chroma_space(collection):
    """Đọc ``hnsw.space`` của collection (dict ở chromadb 1.x)."""
    configuration = collection.configuration
    if isinstance(configuration, dict):
        return configuration["hnsw"]["space"]
    return configuration.hnsw.space


def is_stub(module, name):
    """True nếu hàm của teammate vẫn còn ``raise NotImplementedError``."""
    return "NotImplementedError" in inspect.getsource(getattr(module, name))


# --------------------------------------------------------------------------- #
# Task 4 — load / chunk / embed / index
# --------------------------------------------------------------------------- #


def test_load_documents_extracts_title_url_and_doc_type(tmp_path, monkeypatch):
    legal = tmp_path / "legal"
    news = tmp_path / "news"
    legal.mkdir()
    news.mkdir()
    (legal / "policy-tuition.md").write_text(
        "# Chính sách học phí\n\nSinh viên đóng học phí theo học kỳ.", encoding="utf-8"
    )
    (news / "article_01.md").write_text(
        "# Thông báo học phí\n\n**Source:** https://example.com/hoc-phi\n\nNội dung.",
        encoding="utf-8",
    )
    (legal / "empty.md").write_text("   \n\n", encoding="utf-8")
    (legal / "no-heading.md").write_text("Quy định không có heading.", encoding="utf-8")
    (legal / ".hidden.md").write_text("File ẩn không được đọc.", encoding="utf-8")

    monkeypatch.setattr(indexing, "STANDARDIZED_DIR", tmp_path)
    documents = {item["id"]: item for item in indexing.load_documents()}

    assert set(documents) == {
        "legal/policy-tuition.md",
        "legal/no-heading.md",
        "news/article_01.md",
    }
    # Không có H1 -> fallback về tên file đã chuẩn hóa.
    assert documents["legal/no-heading.md"]["metadata"]["title"] == "No Heading"
    legal_document = documents["legal/policy-tuition.md"]
    assert legal_document["metadata"]["title"] == "Chính sách học phí"
    assert legal_document["metadata"]["doc_type"] == "legal"
    assert legal_document["metadata"]["url"] is None
    assert legal_document["metadata"]["source"] == "policy-tuition.md"

    news_document = documents["news/article_01.md"]
    assert news_document["metadata"]["url"] == "https://example.com/hoc-phi"
    assert news_document["metadata"]["doc_type"] == "news"
    validate_document(news_document)


def test_load_documents_returns_empty_when_directory_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(indexing, "STANDARDIZED_DIR", tmp_path / "missing")
    assert indexing.load_documents() == []


def test_chunk_documents_keeps_ids_stable_and_chunk_index_contiguous():
    document = {
        "id": "legal/tuition.md",
        "content": DOCUMENT_CONTENT * 40,
        "metadata": {
            "source": "tuition.md",
            "title": "Học phí",
            "doc_type": "legal",
            "url": None,
        },
    }

    chunks = indexing.chunk_documents([document])
    chunks_again = indexing.chunk_documents([document])

    assert chunks
    assert [chunk["id"] for chunk in chunks] == [chunk["id"] for chunk in chunks_again]
    assert [chunk["id"] for chunk in chunks] == [
        f"legal/tuition.md::chunk-{index}" for index in range(len(chunks))
    ]
    for index, chunk in enumerate(chunks):
        validate_document(chunk, require_chunk=True)
        assert chunk["metadata"]["chunk_index"] == index
        assert chunk["metadata"]["source"] == "tuition.md"
        assert chunk["content"] == chunk["content"].strip()


def test_chunk_documents_respects_size_and_overlap():
    content = "Sinh viên đóng học phí theo học kỳ. " * 60
    document = {
        "id": "legal/tuition.md",
        "content": content,
        "metadata": {
            "source": "tuition.md",
            "title": "Học phí",
            "doc_type": "legal",
            "url": None,
        },
    }

    chunks = indexing.chunk_documents([document])

    assert len(chunks) > 1
    limit = int(indexing.CHUNK_SIZE * 1.1)
    assert all(len(chunk["content"]) <= limit for chunk in chunks)
    # Overlap làm tổng độ dài các chunk lớn hơn văn bản gốc.
    assert sum(len(chunk["content"]) for chunk in chunks) > len(content)


def test_chunk_documents_skips_whitespace_only_document():
    document = {
        "id": "legal/blank.md",
        "content": "   \n\n\t",
        "metadata": {
            "source": "blank.md",
            "title": "Blank",
            "doc_type": "legal",
            "url": None,
        },
    }
    assert indexing.chunk_documents([document]) == []


def test_embed_texts_uses_one_model_and_normalizes(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "sentence_transformers")
    model = FakeEmbeddingModel()
    monkeypatch.setattr(indexing, "get_embedding_model", lambda: model)

    vectors = indexing.embed_texts(["học phí", "học bổng"])

    assert vectors == [[0.1, 0.2], [0.1, 0.2]]
    assert model.calls[0][1]["normalize_embeddings"] is True
    assert indexing.embed_texts([]) == []


def test_embed_texts_rejects_unsupported_provider(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    with pytest.raises(ValueError, match="EMBEDDING_PROVIDER"):
        indexing.embed_texts(["học phí"])


def test_embed_chunks_attaches_embedding_to_every_chunk(monkeypatch):
    monkeypatch.setattr(
        indexing, "embed_texts", lambda texts: [[0.5, 0.5] for _ in texts]
    )
    chunks = [corpus_item("chunk-0", "học phí"), corpus_item("chunk-1", "học bổng")]

    embedded = indexing.embed_chunks(chunks)

    assert [chunk["embedding"] for chunk in embedded] == [[0.5, 0.5], [0.5, 0.5]]
    assert indexing.embed_chunks([]) == []


def test_get_collection_uses_cosine_space(tmp_path, monkeypatch):
    monkeypatch.setattr(indexing, "CHROMA_DIR", tmp_path / "chroma_db")
    assert chroma_space(indexing.get_collection()) == "cosine"


def test_index_to_vectorstore_is_idempotent_and_restores_url_none(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(indexing, "CHROMA_DIR", tmp_path / "chroma_db")
    chunks = [
        {**corpus_item("chunk-0", "học phí", 0), "embedding": [1.0, 0.0]},
        {**corpus_item("chunk-1", "học bổng", 1, source="news.md"), "embedding": [0.0, 1.0]},
    ]
    chunks[1]["metadata"]["url"] = "https://example.com/hoc-bong"

    indexing.index_to_vectorstore(chunks)
    indexing.index_to_vectorstore(chunks)  # chạy lại không được tạo dữ liệu trùng

    collection = indexing.get_collection()
    payload = collection.get(include=["documents", "metadatas"])
    assert collection.count() == len(chunks)
    assert sorted(payload["ids"]) == ["chunk-0", "chunk-1"]

    metadatas = {item_id: meta for item_id, meta in zip(payload["ids"], payload["metadatas"])}
    # ChromaDB bỏ key None nên url=None phải được ghi là "" và đọc lại thành None.
    normalized = indexing.normalize_chroma_metadata(metadatas["chunk-0"])
    assert normalized["url"] is None
    assert normalized["chunk_index"] == 0
    assert metadatas["chunk-0"]["source"] == "tuition.md"
    assert metadatas["chunk-1"]["url"] == "https://example.com/hoc-bong"
    indexing.index_to_vectorstore([])  # no-op, không được raise


# --------------------------------------------------------------------------- #
# Task 5 — dense search
# --------------------------------------------------------------------------- #


def dense_response(ids=("chunk-0", "chunk-1"), distances=(0.1, 0.4)):
    return {
        "ids": [list(ids)],
        "documents": [[f"nội dung {item_id}" for item_id in ids]],
        "metadatas": [[metadata(chunk_index=index) for index, _ in enumerate(ids)]],
        "distances": [list(distances)],
    }


def test_semantic_search_converts_distance_to_score_and_sorts(monkeypatch):
    collection = FakeCollection(dense_response())
    monkeypatch.setattr(semantic, "embed_texts", lambda texts: [[0.1, 0.2]])
    monkeypatch.setattr(semantic, "get_collection", lambda: collection)

    output = semantic.semantic_search("học phí", top_k=2)

    validate_search_results(output, top_k=2, expected_method="dense")
    assert [item["id"] for item in output] == ["chunk-0", "chunk-1"]
    assert output[0]["score"] == pytest.approx(0.9)
    assert output[1]["score"] == pytest.approx(0.6)
    assert collection.calls[0]["query_embeddings"] == [[0.1, 0.2]]
    assert collection.calls[0]["n_results"] == 2


def test_semantic_search_drops_duplicate_ids_and_respects_top_k(monkeypatch):
    response = {
        "ids": [["chunk-0", "chunk-0", "chunk-1"]],
        "documents": [["a", "a", "b"]],
        "metadatas": [[metadata(0), metadata(0), metadata(1)]],
        "distances": [[0.1, 0.1, 0.2]],
    }
    monkeypatch.setattr(semantic, "embed_texts", lambda texts: [[0.1, 0.2]])
    monkeypatch.setattr(semantic, "get_collection", lambda: FakeCollection(response))

    output = semantic.semantic_search("học phí", top_k=1)

    assert [item["id"] for item in output] == ["chunk-0"]
    validate_search_results(output, top_k=1, expected_method="dense")


def test_semantic_search_returns_empty_without_calling_model(monkeypatch):
    def fail(texts):
        raise AssertionError("embed_texts không được gọi cho query rỗng")

    monkeypatch.setattr(semantic, "embed_texts", fail)
    assert semantic.semantic_search("", top_k=3) == []
    assert semantic.semantic_search("   ", top_k=3) == []
    assert semantic.semantic_search("học phí", top_k=0) == []


def test_semantic_search_restores_url_none_from_missing_metadata(monkeypatch):
    response = dense_response(ids=("chunk-0",), distances=(0.2,))
    # ChromaDB bỏ hẳn key khi giá trị metadata là None.
    del response["metadatas"][0][0]["url"]
    monkeypatch.setattr(semantic, "embed_texts", lambda texts: [[0.1, 0.2]])
    monkeypatch.setattr(semantic, "get_collection", lambda: FakeCollection(response))

    output = semantic.semantic_search("học phí", top_k=1)

    assert output[0]["metadata"]["url"] is None
    validate_search_results(output, top_k=1, expected_method="dense")


# --------------------------------------------------------------------------- #
# Task 6 — BM25 lexical search
# --------------------------------------------------------------------------- #


def bm25_corpus(*contents):
    return [
        corpus_item(f"chunk-{index}", content, index)
        for index, content in enumerate(contents)
    ]


def test_tokenize_lowercases_and_keeps_vietnamese():
    assert lexical.tokenize("Học phí 2026: HK1") == ["học", "phí", "2026", "hk1"]


def test_lexical_search_returns_contract_even_when_idf_is_zero(monkeypatch):
    # Corpus nhỏ làm IDF = 0 -> không được lọc theo ``score > 0``.
    corpus = bm25_corpus("tuition fee payment policy", "library opening hours")
    monkeypatch.setattr(lexical, "CORPUS", corpus)

    output = lexical.lexical_search("tuition fee", top_k=2)

    validate_search_results(output, top_k=2, expected_method="bm25")
    assert [item["id"] for item in output] == ["chunk-0"]
    assert output[0]["content"] == "tuition fee payment policy"
    assert output[0]["metadata"]["chunk_index"] == 0


def test_lexical_search_filters_chunks_without_query_tokens(monkeypatch):
    corpus = bm25_corpus("học phí học kỳ", "học bổng sinh viên", "thư viện mở cửa")
    monkeypatch.setattr(lexical, "CORPUS", corpus)

    output = lexical.lexical_search("thư viện", top_k=3)

    assert [item["id"] for item in output] == ["chunk-2"]
    validate_search_results(output, top_k=3, expected_method="bm25")


def test_lexical_search_respects_top_k_and_orders_by_score(monkeypatch):
    corpus = bm25_corpus(
        "học phí học phí học phí", "học phí học bổng", "học phí", "thư viện"
    )
    monkeypatch.setattr(lexical, "CORPUS", corpus)

    output = lexical.lexical_search("học phí", top_k=2)

    assert len(output) == 2
    scores = [item["score"] for item in output]
    assert scores == sorted(scores, reverse=True)
    validate_search_results(output, top_k=2, expected_method="bm25")


def test_lexical_search_returns_empty_for_blank_query_or_empty_corpus(monkeypatch):
    monkeypatch.setattr(lexical, "CORPUS", [])
    monkeypatch.setattr(lexical, "load_corpus", lambda: [])
    assert lexical.lexical_search("học phí", top_k=3) == []

    monkeypatch.setattr(lexical, "CORPUS", bm25_corpus("học phí"))
    assert lexical.lexical_search("   ", top_k=3) == []
    assert lexical.lexical_search("học phí", top_k=0) == []
    # Query không có token nào (chỉ dấu câu) cũng phải trả rỗng.
    assert lexical.lexical_search("!!!", top_k=3) == []


def test_bm25_index_is_cached_until_corpus_changes():
    first = bm25_corpus("học phí", "học bổng")
    second = bm25_corpus("thư viện")

    index_one, tokens_one = lexical.get_bm25_index(first)
    index_two, tokens_two = lexical.get_bm25_index(first)

    assert index_one is index_two
    assert tokens_one is tokens_two
    assert tokens_one[0] == {"học", "phí"}

    index_three, _ = lexical.get_bm25_index(second)
    assert index_three is not index_one


def test_load_corpus_prefers_vectorstore_then_standardized(monkeypatch):
    stored = [corpus_item("chunk-0", "học phí")]
    standardized = [corpus_item("chunk-1", "học bổng", 1)]
    monkeypatch.setattr(lexical, "_corpus_from_standardized", lambda: standardized)

    # Có index trong ChromaDB -> dùng luôn, không chunk lại.
    monkeypatch.setattr(lexical, "_corpus_from_vectorstore", lambda: stored)
    assert lexical.load_corpus() == stored

    # ChromaDB rỗng -> fallback sang data/standardized.
    monkeypatch.setattr(lexical, "_corpus_from_vectorstore", lambda: [])
    assert lexical.load_corpus() == standardized

    # ChromaDB lỗi -> cũng không được crash.
    def unavailable():
        raise RuntimeError("chroma offline")

    monkeypatch.setattr(lexical, "_corpus_from_vectorstore", unavailable)
    assert lexical.load_corpus() == standardized


# --------------------------------------------------------------------------- #
# Nhánh biên và tích hợp (ChromaDB thật, không gọi network)
# --------------------------------------------------------------------------- #


def test_get_embedding_model_loads_and_caches_one_instance(monkeypatch):
    created = []

    class FakeSentenceTransformer:
        def __init__(self, model_name):
            created.append(model_name)

    fake_module = types.ModuleType("sentence_transformers")
    fake_module.SentenceTransformer = FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    monkeypatch.setattr(indexing, "_embedding_model", None)

    first = indexing.get_embedding_model()
    second = indexing.get_embedding_model()

    assert first is second
    assert created == [indexing.EMBEDDING_MODEL]


def test_semantic_search_returns_empty_when_embedding_is_empty(monkeypatch):
    monkeypatch.setattr(semantic, "embed_texts", lambda texts: [])
    monkeypatch.setattr(
        semantic, "get_collection", lambda: pytest.fail("không được query ChromaDB")
    )
    assert semantic.semantic_search("học phí", top_k=3) == []


def test_load_corpus_reads_indexed_chunks_from_chroma(tmp_path, monkeypatch):
    monkeypatch.setattr(indexing, "CHROMA_DIR", tmp_path / "chroma_db")
    chunks = [
        {**corpus_item("chunk-0", "học phí", 0), "embedding": [1.0, 0.0]},
        {**corpus_item("chunk-1", "học bổng", 1), "embedding": [0.0, 1.0]},
    ]
    indexing.index_to_vectorstore(chunks)

    corpus = lexical.load_corpus()

    assert sorted(item["id"] for item in corpus) == ["chunk-0", "chunk-1"]
    assert all(item["metadata"]["url"] is None for item in corpus)
    assert corpus[0]["metadata"]["source"] == "tuition.md"


def test_load_corpus_falls_back_to_standardized_files(tmp_path, monkeypatch):
    legal = tmp_path / "legal"
    legal.mkdir()
    (legal / "hoc-phi.md").write_text(
        "# Học phí\n\nSinh viên đóng học phí theo học kỳ.", encoding="utf-8"
    )
    monkeypatch.setattr(indexing, "STANDARDIZED_DIR", tmp_path)
    # CHROMA_DIR rỗng -> BM25 phải chunk lại từ data/standardized.
    monkeypatch.setattr(indexing, "CHROMA_DIR", tmp_path / "chroma_db")

    corpus = lexical.load_corpus()

    assert [item["id"] for item in corpus] == ["legal/hoc-phi.md::chunk-0"]
    assert corpus[0]["metadata"]["doc_type"] == "legal"


def test_run_pipeline_prints_hint_without_documents(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(indexing, "STANDARDIZED_DIR", tmp_path / "missing")
    indexing.run_pipeline()
    assert "No documents found" in capsys.readouterr().out


def test_run_pipeline_indexes_chunks_and_warns_on_dimension_mismatch(
    tmp_path, monkeypatch, capsys
):
    legal = tmp_path / "standardized" / "legal"
    legal.mkdir(parents=True)
    (legal / "hoc-phi.md").write_text(
        "# Học phí\n\n" + "Sinh viên đóng học phí theo học kỳ. " * 40, encoding="utf-8"
    )
    monkeypatch.setattr(indexing, "STANDARDIZED_DIR", tmp_path / "standardized")
    monkeypatch.setattr(indexing, "CHROMA_DIR", tmp_path / "chroma_db")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "sentence_transformers")
    monkeypatch.setattr(indexing, "get_embedding_model", lambda: FakeEmbeddingModel())

    indexing.run_pipeline()

    output = capsys.readouterr().out
    assert "Indexed" in output
    # Vector 2 chiều của fake model khác EMBEDDING_DIM -> phải cảnh báo re-index.
    assert "Warning: embedding dimension" in output
    assert indexing.get_collection().count() == len(
        indexing.chunk_documents(indexing.load_documents())
    )


# --------------------------------------------------------------------------- #
# Task 7/9 — RRF và fallback: chỉ chạy khi teammate đã implement xong
# --------------------------------------------------------------------------- #


def test_rerank_rrf_uses_rank_based_score_and_deduplicates():
    import src.task7_reranking as reranking

    if is_stub(reranking, "rerank_rrf"):
        pytest.skip("Task 7 (RRF) chưa implement — bàn giao cho Người 1")

    dense = [search_result("chunk-0", 0.9), search_result("chunk-1", 0.8)]
    bm25 = [
        search_result("chunk-1", 7.0, "bm25"),
        search_result("chunk-2", 5.0, "bm25"),
    ]

    fused = reranking.rerank_rrf([dense, bm25], top_k=3, k=60)

    validate_search_results(fused, top_k=3, expected_method="hybrid")
    assert [item["id"] for item in fused] == ["chunk-1", "chunk-0", "chunk-2"]
    assert fused[0]["score"] == pytest.approx(1 / 61 + 1 / 62)


def test_retrieve_keeps_hybrid_when_dense_score_meets_threshold(monkeypatch):
    import src.task9_retrieval_pipeline as pipeline

    if is_stub(pipeline, "retrieve"):
        pytest.skip("Task 9 (retrieve/fallback) chưa implement — bàn giao cho Người 1")

    dense = [search_result("chunk-0", 0.5, "dense")]
    fused = [search_result("chunk-0", 0.03, "hybrid")]
    calls = {"fallback": 0}

    monkeypatch.setattr(pipeline, "semantic_search", lambda query, top_k: dense)
    monkeypatch.setattr(pipeline, "lexical_search", lambda query, top_k: [])
    monkeypatch.setattr(pipeline, "rerank_rrf", lambda lists, top_k: fused)

    def fallback(query, top_k):
        calls["fallback"] += 1
        return []

    monkeypatch.setattr(pipeline, "pageindex_search", fallback)

    output = pipeline.retrieve("học phí", top_k=2, score_threshold=0.5)

    # Score bằng đúng threshold thì chưa được coi là "dưới threshold".
    assert calls["fallback"] == 0
    assert output == fused
    validate_search_results(output, top_k=2, expected_method="hybrid")
