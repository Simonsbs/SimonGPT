# ingest.py
import warnings
# Suppress the unstructured‐client “coroutine never awaited” warning
warnings.filterwarnings(
    "ignore",
    "coroutine 'AsyncClient.aclose' was never awaited",
    category=RuntimeWarning,
)

import os
import sys
import asyncio
import asyncpg
import tiktoken
import httpx
from httpx import Timeout
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector, Vector
from langchain_unstructured import UnstructuredLoader

# Load environment variables
load_dotenv()

DB_URL      = os.getenv("VECTOR_DB_URL")
ROUTER_URL  = os.getenv("ROUTER_URL", "http://localhost:8080")
API_KEY     = os.getenv("ROUTER_API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL")

# Tokenizer for splitting text
enc = tiktoken.get_encoding("cl100k_base")

def load_file(path: str) -> str:
    """Load and concatenate text from the given file path."""
    docs = UnstructuredLoader(path).load()
    return "\n\n".join(d.page_content for d in docs)

def split_text(text: str, max_tokens: int = 256):
    """Yield chunks of text keeping under max_tokens."""
    words, chunk, length = text.split(), [], 0
    for w in words:
        t = len(enc.encode(w + " "))
        if length + t > max_tokens:
            yield " ".join(chunk)
            chunk, length = [], 0
        chunk.append(w)
        length += t
    if chunk:
        yield " ".join(chunk)

async def embed(text: str) -> list[float]:
    """Call LLM router's embeddings endpoint; handle multiple response formats."""
    payload = {"model": EMBED_MODEL, "input": [text]}
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    timeout = Timeout(connect=10.0, read=60.0, write=60.0, pool=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{ROUTER_URL}/v1/embeddings", json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"[ERROR] Embedding API returned {resp.status_code}: {resp.text}")
            resp.raise_for_status()
        data = resp.json()
        # New router format: {'model': 'bge-m3', 'embeddings': [[...]], ...}
        if "embeddings" in data and isinstance(data["embeddings"], list):
            first_embed = data["embeddings"][0]
            if isinstance(first_embed, list):
                return first_embed
        # Old router format: {'data': [{'embedding': [...]}, ...]}
        if "data" in data and isinstance(data["data"], list):
            first = data["data"][0]
            if isinstance(first, dict) and "embedding" in first:
                return first["embedding"]
        # Direct fallback: {'embedding': [...]}
        if "embedding" in data and isinstance(data["embedding"], list):
            return data["embedding"]
        raise ValueError(f"Unexpected embedding response format: {data}")

async def main(path: str):
    # Initialize DB and ensure table exists
    async def init(conn):
        await register_vector(conn)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS public.documents (
                id SERIAL PRIMARY KEY,
                source TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding VECTOR(1536)
            );
        """)

    pool = await asyncpg.create_pool(
        DB_URL,
        init=init,
        statement_cache_size=0,
    )

    text = load_file(path)
    async with pool.acquire() as conn:
        for chunk in split_text(text):
            try:
                vec_list = await embed(chunk)
            except Exception as e:
                print(f"[FATAL] Embedding failed for chunk '{chunk[:30]}...': {e}")
                sys.exit(1)
            vec = Vector(vec_list)
            await conn.execute(
                "INSERT INTO public.documents (source, content, embedding) VALUES ($1, $2, $3)",
                path, chunk, vec
            )
            print(f"✅ stored chunk '{chunk[:40]}…'")

    await pool.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest.py <path-to-file>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))