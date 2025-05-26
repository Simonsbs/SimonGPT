import os, httpx, uuid, json, logging
from typing import List, Dict, Any, AsyncIterator
from .base import BaseAdapter

# Configure logging to output to console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

class OllamaAdapter(BaseAdapter):
    async def chat(self, messages: List[Dict[str, str]], temperature: float | None, max_tokens: int | None) -> Any:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        logger.info(f"[OllamaAdapter] chat payload: {payload}")
        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            logger.info(f"[OllamaAdapter] chat response status: {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"[OllamaAdapter] chat response data: {data}")

        return {
            "id": data.get("id", str(uuid.uuid4())),
            "object": "chat.completion",
            "model": self.model_name,
            "choices": [data["message"]],
        }

    async def chat_stream(
        self, messages: List[Dict[str, str]], temperature: float | None, max_tokens: int | None
    ) -> AsyncIterator[str]:
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        logger.info(f"[OllamaAdapter] chat_stream payload: {payload}")
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST", f"{OLLAMA_URL}/api/chat", json=payload
            ) as resp:
                logger.info(f"[OllamaAdapter] chat_stream response status: {resp.status_code}")
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    logger.info(f"[OllamaAdapter] chat_stream chunk: {chunk}")
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
