"""Qdrant vector store client — production ready."""

from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

import structlog


logger = structlog.get_logger(__name__)

_client: QdrantClient | None = None


def init_qdrant(host: str = "localhost", port: int = 6333, grpc_port: int = 6334) -> QdrantClient:
    """Initialize Qdrant client. Call once at startup."""
    global _client
    _client = QdrantClient(host=host, port=port, prefer_grpc=True)
    logger.info("qdrant_init", host=host, port=port)
    return _client


def get_client() -> QdrantClient:
    if _client is None:
        raise RuntimeError("Qdrant not initialized. Call init_qdrant() first.")
    return _client


def ensure_collection(name: str, vector_dim: int = 384, distance: Distance = Distance.COSINE) -> None:
    """Create collection if it doesn't exist."""
    client = get_client()
    try:
        client.get_collection(name)
        logger.info("qdrant_collection_exists", collection=name)
    except (UnexpectedResponse, Exception):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_dim, distance=distance),
        )
        logger.info("qdrant_collection_created", collection=name, dim=vector_dim)


def upsert_points(collection: str, points: list[dict[str, Any]]) -> None:
    """Upsert points into a collection."""
    client = get_client()
    client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=p["id"],
                vector=p["vector"],
                payload={k: v for k, v in p.items() if k != "id" and k != "vector"}
            )
            for p in points
        ]
    )


def search(collection: str, query_vector: list[float], limit: int = 5, score_threshold: float | None = None) -> list[dict]:
    """Search vector collection."""
    client = get_client()
    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit,
        score_threshold=score_threshold,
    )
    return [
        {"id": r.id, "score": r.score, "payload": r.payload}
        for r in results
    ]


def delete_collection(name: str) -> None:
    """Delete a collection."""
    client = get_client()
    try:
        client.delete_collection(name)
        logger.info("qdrant_collection_deleted", collection=name)
    except UnexpectedResponse:
        pass  # Already gone