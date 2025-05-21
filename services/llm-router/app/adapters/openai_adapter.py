import os, uuid, openai, json
from typing import List, Dict, Any, AsyncIterator
from .base import BaseAdapter

openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIAdapter(BaseAdapter):
    async def chat(self, messages, temperature, max_tokens):
        resp = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.to_dict()

    async def chat_stream(self, messages, temperature, max_tokens) -> AsyncIterator[str]:
        stream = await openai.ChatCompletion.acreate(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            yield json.dumps({
                "id": chunk["id"] if "id" in chunk else str(uuid.uuid4()),
                "object":"chat.completion.chunk",
                "model":self.model_name,
                "choices":[chunk["choices"][0]]
            })

def get_adapter(model_name: str) -> BaseAdapter:
    return OpenAIAdapter(model_name)
