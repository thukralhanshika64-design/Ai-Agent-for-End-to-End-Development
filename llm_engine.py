"""
LLM Engine — Wrapper around Ollama for all agent interactions.
Provides a single entry point for calling the local LLM with
retry logic, error handling, and optional streaming.
"""

import time
import asyncio
from langchain_groq import ChatGroq
from rich.console import Console
from config import MODEL_NAME, GROQ_API_KEY, MODEL_TEMPERATURE, MAX_RETRIES

console = Console()

# Initialize guard and a client cache so we can reuse ChatGroq instances
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file or as an environment variable.")

_CLIENTS = {}

def get_client(model_name: str | None = None):
    """Return a cached ChatGroq client for the requested model."""
    key = model_name or MODEL_NAME
    if key in _CLIENTS:
        return _CLIENTS[key]
    client = ChatGroq(model_name=key, api_key=GROQ_API_KEY, temperature=MODEL_TEMPERATURE)
    _CLIENTS[key] = client
    return client


async def astream_llm(prompt: str):
    """
    Async stream the response from the local Ollama model.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = get_client(model_name)
            async for chunk in client.astream(prompt):
                yield chunk.content
            return
        except Exception as e:
            last_error = e
            console.print(
                f"  [dim red]! Async Stream attempt {attempt}/{MAX_RETRIES} failed: {e}[/dim red]"
            )
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                console.print(f"  [dim]  Retrying in {wait}s...[/dim]")
                await asyncio.sleep(wait)

    raise RuntimeError(
        f"LLM async stream failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    )


def run_llm(prompt: str, model_name: str | None = None) -> str:
    """
    Send a prompt to the local Ollama model and return the response.

    Includes retry logic for transient failures (e.g., model still loading).

    Args:
        prompt: The full prompt string to send to the LLM.

    Returns:
        The model's text response.

    Raises:
        RuntimeError: If all retry attempts are exhausted.
    """
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = get_client(model_name)
            response = client.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            last_error = e
            console.print(
                f"  [dim red]! Attempt {attempt}/{MAX_RETRIES} failed: {e}[/dim red]"
            )
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt  # Exponential backoff
                console.print(f"  [dim]  Retrying in {wait}s...[/dim]")
                time.sleep(wait)

    raise RuntimeError(
        f"LLM call failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    )


def stream_llm(prompt: str, model_name: str | None = None):
    """
    Stream the response from the local Ollama model.
    Yields chunks of text as they are generated.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = get_client(model_name)
            for chunk in client.stream(prompt):
                yield chunk.content
            return
        except Exception as e:
            last_error = e
            console.print(
                f"  [dim red]! Stream attempt {attempt}/{MAX_RETRIES} failed: {e}[/dim red]"
            )
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt  # Exponential backoff
                console.print(f"  [dim]  Retrying in {wait}s...[/dim]")
                time.sleep(wait)

    raise RuntimeError(
        f"LLM stream failed after {MAX_RETRIES} attempts. Last error: {last_error}"
    )
