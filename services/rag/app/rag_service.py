# services/rag/app/rag_service.py

import os
import asyncio
from typing import List

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from pgvector.asyncpg import register_vector
from dotenv import load_dotenv
import traceback
import json
from prompts import build_persona_prompt


load_dotenv()

DB_URL = os.getenv("SUPABASE_DB_URL")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
GEN_MODEL = "llama3"

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

async def get_relevant_documents(query: str, conn) -> List[str]:
    print(f"[INFO] Generating embedding for query: {query}")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": query}
        )
        print(f"[DEBUG] Ollama embedding response status: {resp.status_code}")
        #print(f"[DEBUG] Ollama embedding response text: {resp.text}")
        resp.raise_for_status()
        query_embedding = resp.json()["embedding"]

    print("[INFO] Fetching relevant documents from database")
    rows = await conn.fetch(
        """
        SELECT content, source
        FROM documents
        ORDER BY embedding <#> $1
        LIMIT 3
        """,
        query_embedding
    )
    return [{"content": row["content"], "source": row["source"]} for row in rows]

async def generate_answer(query: str, context: List[str]) -> str:
    print("[INFO] Constructing prompt for answer generation")
    prompt = build_persona_prompt(query, context)

    print("[PROMPT] ----------------------------")
    print(prompt)
    print("-------------------------------------")

    print("[INFO] Calling Ollama to generate answer (streaming)")
    timeout = httpx.Timeout(60.0)  # Increase timeout to 60 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_URL}/api/generate",
            json={"model": GEN_MODEL, "prompt": prompt},
        ) as resp:
            resp.raise_for_status()
            full_response = ""
            async for line in resp.aiter_lines():
                if line.strip():
                    print(f"[STREAM] {line}")
                    try:
                        full_response += json.loads(line)["response"]
                    except Exception as e:
                        print(f"[WARN] Skipping malformed line: {line}")
                        continue
            print(f"[INFO] Final response: {full_response.strip()}")
            return full_response.strip()


@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    print(f"[INFO] Received query: {request.query}")
    try:
        print("[INFO] Connecting to database pool...")
        pool = await asyncpg.create_pool(
            DB_URL,
            init=register_vector,
            statement_cache_size=0
        )
        async with pool.acquire() as conn:
            documents = await get_relevant_documents(request.query, conn)
        await pool.close()

        if not documents:
            print("[WARN] No documents found for the query.")
            raise HTTPException(status_code=404, detail="No relevant documents found.")

        answer = await generate_answer(request.query, documents)
        sources = [doc["source"] for doc in documents]
        print("[INFO] Successfully generated response.")
        return QueryResponse(answer=answer, sources=sources)

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
