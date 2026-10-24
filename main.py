import json
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

DATA_FILE = "data.json"
COLLECTION_NAME = "books"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
QDRANT_PATH = "qdrant_data"
TOP_K_MAX = 10

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

model: Optional[SentenceTransformer] = None
client: Optional[QdrantClient] = None
vector_size: Optional[int] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, client, vector_size

    logger.info("Memuat model: %s", EMBEDDING_MODEL)
    model = SentenceTransformer(EMBEDDING_MODEL)
    vector_size = len(model.encode("contoh"))
    logger.info("Dimensi vector: %d", vector_size)

    client = QdrantClient(path=QDRANT_PATH)
    logger.info("Qdrant aktif di: %s", QDRANT_PATH)

    koleksi_ada = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in koleksi_ada:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info("Collection '%s' dibuat.", COLLECTION_NAME)
    else:
        logger.info("Collection '%s' sudah ada.", COLLECTION_NAME)

    yield

    model = None
    client = None
    vector_size = None


app = FastAPI(title="Semantic Search Buku", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


class IndexResponse(BaseModel):
    status: str
    indexed: int
    collection: str


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=TOP_K_MAX)


class SearchResult(BaseModel):
    id: int
    title: Optional[str] = None
    text: str
    category: str
    score: float


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: List[SearchResult]


def muat_dokumen() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        raise HTTPException(status_code=404, detail=DATA_FILE + " tidak ditemukan")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        dokumen = json.load(f)

    if not dokumen:
        raise HTTPException(status_code=400, detail="Dataset kosong")

    for d in dokumen:
        if "text" not in d or "category" not in d:
            raise HTTPException(
                status_code=400,
                detail="Entrik tidak valid (butuh text dan category): " + str(d),
            )

    return dokumen


def pastikan_koleksi() -> None:
    if client is None or vector_size is None:
        raise HTTPException(status_code=503, detail="Aplikasi belum siap")

    koleksi_ada = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in koleksi_ada:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def hitung_point() -> int:
    if client is None:
        return 0

    try:
        info = client.get_collection(collection_name=COLLECTION_NAME)
        jumlah = getattr(info, "points_count", None)
        if jumlah is None:
            jumlah = getattr(info, "vectors_count", 0)
        return jumlah or 0
    except Exception:
        logger.exception("Gagal menghitung point")
        return 0


@app.get("/health")
def health():
    return {
        "status": "OK",
        "collection": COLLECTION_NAME,
        "model": EMBEDDING_MODEL,
    }


@app.post("/index", response_model=IndexResponse)
def indexkan():
    pastikan_koleksi()
    dokumen = muat_dokumen()

    teks = [d["text"] for d in dokumen]
    vektor = model.encode(teks, normalize_embeddings=True).tolist()

    poin = []
    for d, v in zip(dokumen, vektor):
        poin.append(
            PointStruct(
                id=int(d.get("id", dokumen.index(d) + 1)),
                vector=v,
                payload={
                    "title": d.get("title", ""),
                    "text": d["text"],
                    "category": d["category"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=poin)
    logger.info("%d dokumen diindex ke %s", len(poin), COLLECTION_NAME)

    return IndexResponse(
        status="ok",
        indexed=len(poin),
        collection=COLLECTION_NAME,
    )


@app.post("/search", response_model=SearchResponse)
def cari(req: SearchRequest):
    pastikan_koleksi()

    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query tidak boleh kosong")

    vektor_kueri = model.encode(req.query.strip(), normalize_embeddings=True).tolist()

    total = hitung_point()
    if total == 0:
        return SearchResponse(query=req.query, top_k=req.top_k, results=[])

    batas = min(req.top_k, total)

    hasil = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vektor_kueri,
        limit=batas,
        with_payload=True,
    )

    hasil_akhir = []
    for poin in hasil.points:
        payload = poin.payload or {}
        hasil_akhir.append(
            SearchResult(
                id=int(poin.id),
                title=payload.get("title"),
                text=payload.get("text", ""),
                category=payload.get("category", ""),
                score=float(poin.score),
            )
        )

    return SearchResponse(query=req.query, top_k=req.top_k, results=hasil_akhir)
