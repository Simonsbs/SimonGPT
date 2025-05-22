# services/rag/ingest.py
import os, asyncio, asyncpg, textwrap, json, tiktoken, httpx
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector, Vector      
from langchain_unstructured import UnstructuredLoader


load_dotenv()

DB_URL      = os.getenv("SUPABASE_DB_URL")
OLLAMA_URL  = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = "nomic-embed-text"

enc = tiktoken.get_encoding("cl100k_base")       # OpenAI tokenizer ≈ Llama


def load_file(path: str) -> str:
    loader = UnstructuredLoader(path)
    docs = loader.load()
    return "\n\n".join([doc.page_content for doc in docs])


def split_text(text: str, max_tokens=256):
    words  = text.split()
    chunk  = []
    length = 0
    for w in words:
        t = len(enc.encode(w + " "))
        if length + t > max_tokens:
            yield " ".join(chunk)
            chunk, length = [], 0
        chunk.append(w)
        length += t
    if chunk:
        yield " ".join(chunk)

async def embed(text: str):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": MODEL_NAME, "prompt": text}
        )
        resp.raise_for_status()
        return resp.json()["embedding"]          # list[float] len 1536

async def main(path: str):
    async def init(conn):
        # register *once* per new physical connection
        await register_vector(conn, schema="extensions")

    pool = await asyncpg.create_pool(
        DB_URL,
        init=init,                   # ← use the wrapper, not register_vector again
        statement_cache_size=0       # ← avoids all prepared-stmt clashes with the pooler
    )
    
    with open(path, "r", encoding="utf8") as f:
        raw = load_file(path)

    async with pool.acquire() as conn:
        for chunk in split_text(raw):
            vec = Vector(await embed(chunk))
            await conn.execute(
                "insert into documents (source, content, embedding) values ($1,$2,$3)",
                path, chunk, vec
            )
            print("✅ stored chunk", chunk[:40], "…")

    await pool.close()

if __name__ == "__main__":
    import sys
    asyncio.run(main(sys.argv[1]))
