import os, httpx, uuid, json
from typing import List, Dict, Any, AsyncIterator
from .base import BaseAdapter

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

class OllamaAdapter(BaseAdapter):
    async def chat(self, messages, temperature, max_tokens):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return {
            "id": data.get("id", str(uuid.uuid4())),
            "object": "chat.completion",
            "model": self.model_name,
            "choices": [data["message"]],
        }

    async def chat_stream(
        self, messages, temperature, max_tokens
    ) -> AsyncIterator[str]:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST", f"{OLLAMA_URL}/api/chat", json=payload
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    yield json.dumps(
                        {
                            "id": chunk.get("id", str(uuid.uuid4())),
                            "object": "chat.completion.chunk",
                            "model": self.model_name,
                            "choices": [
                                {
                                    "delta": chunk["message"],
                                    "index": 0,
                                    "finish_reason": None,
                                }
                            ],
                        }
                    )

def get_adapter(model_name: str) -> BaseAdapter:
    return OllamaAdapter(model_name)
