"""Qdrant vector store setup and utilities for marketing content embeddings."""

from __future__ import annotations

from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from qdrant_client.http.exceptions import ResponseHandlingException

from ..config import QdrantSettings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Collection schemas
# ---------------------------------------------------------------------------

# Marketing content is chunked into pages of ~512 tokens.
# We use OpenAI's text-embedding-3-small (1536 dim) by default.

MARKETING_CONTENT_SCHEMA = {
    "vectors": {
        "size": 1536,
        "distance": "Cosine",
    },
    "params": {
        "optimize_index": True,
    },
    "payload_schema": {
        "content_id": {
            "type": "keyword",
        },
        "artifact_type": {
            "type": "keyword",
        },
        "stage_name": {
            "type": "keyword",
        },
        "campaign_id": {
            "type": "keyword",
        },
        "chunk_index": {
            "type": "integer",
        },
        "text": {
            "type": "text",
        },
        "metadata": {
            "type": "text",  # JSON stored as string
        },
    },
}


def create_client(settings: QdrantSettings | None = None) -> QdrantClient:
    """Create a Qdrant client from settings."""
    if settings is None:
        settings = QdrantSettings()
    return QdrantClient(host=settings.host, port=settings.port, timeout=10)


def ensure_collection(client: QdrantClient, settings: QdrantSettings | None = None) -> None:
    """
    Create the marketing content collection if it doesn't exist.

    Safe to call multiple times — will no-op if collection already exists.
    """
    if settings is None:
        settings = QdrantSettings()

    try:
        collections = client.get_collections().collections
        names = [c.name for c in collections]
    except ResponseHandlingException as exc:
        logger.warning("qdrant_unreachable", error=str(exc))
        raise

    if settings.collection_name in names:
        logger.debug("qdrant_collection_exists", collection=settings.collection_name)
        return

    vector_params = qdrant_models.VectorParams(
        size=settings.vector_size,
        distance=qdrant_models.Distance.COSINE,
    )

    client.create_collection(
        collection_name=settings.collection_name,
        vectors_config=vector_params,
    )

    # Add payload schema fields
    for field_name, field_schema in MARKETING_CONTENT_SCHEMA["payload_schema"].items():
        client.set_payload(
            collection_name=settings.collection_name,
            payload={field_name: {"type": field_schema["type"]}},
        )

    logger.info("qdrant_collection_created", collection=settings.collection_name, vector_size=settings.vector_size)


def upsert_content(
    client: QdrantClient,
    collection_name: str,
    content_id: str,
    artifact_type: str,
    stage_name: str,
    campaign_id: str,
    chunks: list[dict[str, Any]],
) -> int:
    """
    Upsert embedded content chunks into Qdrant.

    Args:
        content_id:      Unique ID for the content piece (e.g., "cv-001")
        artifact_type:  Type of artifact (market_brief, copy_variants, etc.)
        stage_name:     Pipeline stage that produced this content
        campaign_id:    Campaign this belongs to
        chunks:         List of {"text": str, "embedding": list[float], "metadata": dict}

    Returns:
        Number of chunks upserted.
    """
    from uuid import uuid4

    points = []
    for i, chunk in enumerate(chunks):
        point_id = str(uuid4())
        points.append(
            qdrant_models.PointStruct(
                id=point_id,
                vector=chunk["embedding"],
                payload={
                    "content_id": content_id,
                    "artifact_type": artifact_type,
                    "stage_name": stage_name,
                    "campaign_id": campaign_id,
                    "chunk_index": i,
                    "text": chunk["text"],
                    "metadata": chunk.get("metadata", {}),
                },
            )
        )

    client.upsert(collection_name=collection_name, points=points)
    logger.debug("qdrant_content_upserted", content_id=content_id, chunks=len(chunks))
    return len(points)


def search_content(
    client: QdrantClient,
    collection_name: str,
    query_embedding: list[float],
    content_id_filter: str | None = None,
    artifact_type_filter: str | None = None,
    campaign_id_filter: str | None = None,
    limit: int = 5,
    score_threshold: float = 0.7,
) -> list[dict[str, Any]]:
    """
    Search for similar content in the vector store.

    Returns a list of results with score >= score_threshold.
    """
    from qdrant_client.models import FieldCondition, Filter, MatchKeyword, Range

    must_conditions = []
    if content_id_filter:
        must_conditions.append(FieldCondition(key="content_id", match=MatchKeyword(value=content_id_filter)))
    if artifact_type_filter:
        must_conditions.append(FieldCondition(key="artifact_type", match=MatchKeyword(value=artifact_type_filter)))
    if campaign_id_filter:
        must_conditions.append(FieldCondition(key="campaign_id", match=MatchKeyword(value=campaign_id_filter)))

    search_filter = Filter(must=must_conditions) if must_conditions else None

    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        query_filter=search_filter,
        limit=limit,
        score_threshold=score_threshold,
    )

    return [
        {
            "id": r.id,
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


def delete_content_by_content_id(client: QdrantClient, collection_name: str, content_id: str) -> int:
    """Delete all chunks for a given content_id. Returns number deleted."""
    from qdrant_client.models import FieldCondition, Filter, MatchKeyword

    results = client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[FieldCondition(key="content_id", match=MatchKeyword(value=content_id))]
        ),
    )
    logger.debug("qdrant_content_deleted", content_id=content_id)
    return 0  # Qdrant delete doesn't return count in this API version