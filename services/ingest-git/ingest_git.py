# ingest_git.py
import time
import os
import sys
import stat
import shutil
import asyncio
import asyncpg
import tempfile
import tiktoken
import httpx
from dotenv import load_dotenv
from pgvector.asyncpg import register_vector, Vector
from git import Repo

load_dotenv()

DB_URL      = os.getenv("VECTOR_DB_URL")
ROUTER_URL  = os.getenv("ROUTER_URL")
API_KEY     = os.getenv("ROUTER_API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL")

ALLOWED_EXT = {".py", ".md", ".txt", ".js", ".ts", ".java", ".go", ".rs"}
enc = tiktoken.get_encoding("cl100k_base")


def split_text(text: str, max_tokens: int = 256):
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
    payload = {"model": EMBED_MODEL, "input": [text]}
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{ROUTER_URL}/v1/embeddings", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data.get("embedding") or data.get("embeddings", [[None]])[0] or data.get("data", [{}])[0].get("embedding")


def on_rm_error(func, path, exc_info):
    """Handle read-only or locked files during rmtree (especially Git pack files on Windows)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


async def main(repo_url: str):
    tmp_dir = tempfile.mkdtemp()
    print(f"[INFO] Cloning {repo_url} to {tmp_dir}")
    repo = Repo.clone_from(repo_url, tmp_dir)
    commit_hash = repo.head.commit.hexsha

    pool = await asyncpg.create_pool(DB_URL, init=register_vector)

    async with pool.acquire() as conn:
        print(f"[INFO] Deleting previous records for repo: {repo_url}")
        await conn.execute("DELETE FROM public.git_documents WHERE repo = $1", repo_url)

        for root, _, files in os.walk(tmp_dir):
            for fname in files:
                path = os.path.join(root, fname)
                if not os.path.splitext(fname)[1].lower() in ALLOWED_EXT:
                    continue
                rel_path = os.path.relpath(path, tmp_dir)
                print(f"[DEBUG] Processing: full='{path}' rel='{rel_path}'")
                with open(path, encoding="utf-8", errors="ignore") as f:
                    content = f.read().replace("\x00", "")
                chunks = list(split_text(content))
                total_chunks = len(chunks)
                for i, chunk in enumerate(chunks, 1):
                    try:
                        vec_list = await embed(chunk)
                    except Exception as e:
                        print(f"[ERROR] Failed embedding chunk from {rel_path}: {e}")
                        continue
                    vec = Vector(vec_list)
                    dir_path = os.path.dirname(rel_path)
                    file_name = os.path.basename(rel_path)
                    await conn.execute("""
                        INSERT INTO public.git_documents (repo, file_path, dir_path, file_name, commit_hash, content, embedding)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, repo_url, rel_path, dir_path, file_name, commit_hash, chunk, vec)
                    print(f"✅ stored chunk from {rel_path} [{i}/{total_chunks}] ({(i/total_chunks)*100:.1f}%)")

    
    try:
        if hasattr(repo, 'close'):
            repo.close()
        shutil.rmtree(tmp_dir, onerror=on_rm_error)
    except Exception as e:
        print(f"[WARN] Could not fully delete {tmp_dir}: {e}")
        time.sleep(1)
        try:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception as inner:
            print(f"[WARN] Cleanup failed permanently: {inner}")

    
    
    await pool.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_git.py <git-repo-url>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1]))
