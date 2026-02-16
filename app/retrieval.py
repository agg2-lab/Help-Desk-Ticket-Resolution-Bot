import math
from typing import List

from openai import OpenAI
from pymongo import MongoClient
from pymongo.collection import Collection

from .config import settings


def _get_collection() -> Collection | None:
    if not settings.mongo_uri:
        return None
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    return db[settings.mongo_kb_collection]


def _embed_text(text: str) -> List[float] | None:
    if not settings.openai_api_key:
        return None
    client = OpenAI(api_key=settings.openai_api_key)
    embedding = client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )
    return embedding.data[0].embedding


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def ingest_kb_documents(documents: list[dict]) -> int:
    collection = _get_collection()
    if collection is None:
        return 0

    payload = []
    for doc in documents:
        text = doc.get("text", "").strip()
        if not text:
            continue

        payload.append(
            {
                "title": doc.get("title", "Untitled"),
                "text": text,
                "source": doc.get("source", "manual"),
                "embedding": _embed_text(text),
            }
        )

    if not payload:
        return 0

    inserted = collection.insert_many(payload)
    return len(inserted.inserted_ids)


def retrieve_context(query_text: str, limit: int = 3) -> list[dict]:
    collection = _get_collection()
    if collection is None:
        return []

    docs = list(collection.find({}, {"title": 1, "text": 1, "source": 1, "embedding": 1}).limit(500))
    if not docs:
        return []

    query_embedding = _embed_text(query_text)

    if query_embedding is None:
        # Fallback lexical retrieval when embeddings are unavailable.
        query_terms = set(query_text.lower().split())
        scored = []
        for d in docs:
            tokens = set(d.get("text", "").lower().split())
            overlap = len(query_terms.intersection(tokens))
            scored.append((overlap, d))
        top = [item[1] for item in sorted(scored, key=lambda x: x[0], reverse=True)[:limit]]
        return [
            {"title": t.get("title", "Untitled"), "source": t.get("source", "manual"), "text": t.get("text", "")}
            for t in top
            if t.get("text")
        ]

    scored_docs = []
    for d in docs:
        emb = d.get("embedding")
        if isinstance(emb, list):
            score = _cosine_similarity(query_embedding, emb)
            scored_docs.append((score, d))

    scored_docs.sort(key=lambda x: x[0], reverse=True)
    top_docs = [item[1] for item in scored_docs[:limit]]
    return [
        {"title": t.get("title", "Untitled"), "source": t.get("source", "manual"), "text": t.get("text", "")}
        for t in top_docs
        if t.get("text")
    ]
