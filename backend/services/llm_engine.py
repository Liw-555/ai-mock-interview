"""
LLM engine: wrapper for chat completion and embedding API calls.
Supports ECNU Plus (OpenAI-compatible) and SiliconFlow BAAI/bge-m3.
"""

import os
from typing import AsyncGenerator, Dict, Any, List

import httpx
from dotenv import load_dotenv

# Load .env before reading env vars
load_dotenv()

# Chat model (ECNU Plus)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://chat.ecnu.edu.cn/open/api/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "ecnu-plus")

# Embedding model (SiliconFlow BAAI/bge-m3)
EMBEDDING_URL = os.getenv("EMBEDDING_URL", "https://api.siliconflow.cn/v1/embeddings")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "")


async def chat_completion(
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> Dict[str, Any]:
    """
    Non-streaming chat completion.
    Returns the full response dict.
    """
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()


async def chat_completion_stream(
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> AsyncGenerator[str, None]:
    """
    Streaming chat completion.
    Yields SSE data chunks.
    """
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{LLM_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    chunk = line[6:]
                    if chunk.strip() == "[DONE]":
                        break
                    yield chunk


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get text embeddings via SiliconFlow BAAI/bge-m3.
    Returns a list of embedding vectors.
    """
    if not EMBEDDING_API_KEY:
        raise RuntimeError("EMBEDDING_API_KEY not configured in .env")

    headers = {
        "Authorization": f"Bearer {EMBEDDING_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": EMBEDDING_MODEL,
        "input": texts,
        "encoding_format": "float",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            EMBEDDING_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        # OpenAI-compatible format: data[].embedding
        return [item["embedding"] for item in data.get("data", [])]
