import os, asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()                                 # reads services/rag/.env
DB_URL = os.getenv("SUPABASE_DB_URL")         # Session-pooler string

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup ─────────────────────────────
    pool = await asyncpg.create_pool(DB_URL)  # Supabase pgvector-ready pool
    app.state.pool = pool
    print("🔌  DB pool ready")                 # optional log

    yield                                      # <--- requests are served here

    # ── shutdown ────────────────────────────
    await pool.close()
    print("✅  DB pool closed")

app = FastAPI(
    title="Simoni-zer RAG",
    version="0.1.0",
    lifespan=lifespan,                         # <-- new API
)

@app.get("/healthz")
async def health():
    async with app.state.pool.acquire() as conn:
        await conn.execute("SELECT 1")         # simple check
    return {"status": "ok"}
