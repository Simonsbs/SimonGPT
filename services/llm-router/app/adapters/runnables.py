# app/adapters/runnables.py
import asyncio
from langchain_core.runnables import RunnableLambda
from .ollama_adapter import get_adapter as get_ollama
from .openai_adapter import get_adapter as get_openai

# Wrap the Ollama adapter in a Runnable
ollama_chain = RunnableLambda(
    lambda inputs: asyncio.run(
        get_ollama(inputs["model"]).chat(
            inputs["messages"], inputs["temperature"], inputs["max_tokens"]
        )
    )
)

# Wrap the OpenAI adapter likewise (will work once i set OPENAI_API_KEY)
openai_chain = RunnableLambda(
    lambda inputs: asyncio.run(
        get_openai(inputs["model"]).chat(
            inputs["messages"], inputs["temperature"], inputs["max_tokens"]
        )
    )
)

def _route(inputs: dict):
    # Parse provider prefix (default=ollama)
    model_id = inputs.get("model", "")
    provider = model_id.split(":", 1)[0] if ":" in model_id else "ollama"
    return ollama_chain if provider == "ollama" else openai_chain

router_chain = RunnableLambda(_route)
