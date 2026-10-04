"""Minimal Mistral REST client (replaces langchain-mistralai; no heavy dependencies)."""
import requests
from . import settings

SMALL = "mistral-small-latest"
MEDIUM = "mistral-medium-latest"
EMBED = "mistral-embed"


class MistralError(RuntimeError):
    pass


def _headers(key):
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def chat(messages, model=SMALL, temperature=0.3, heavy=False, timeout=60):
    key = settings.MISTRAL_MEDIUM_KEY if heavy else settings.MISTRAL_API_KEY
    if not key:
        raise MistralError("Missing MISTRAL_API_KEY")
    try:
        r = requests.post(f"{settings.MISTRAL_BASE}/chat/completions", headers=_headers(key), timeout=timeout,
                          json={"model": model, "messages": messages, "temperature": temperature})
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        raise MistralError(f"Mistral request failed: {e.__class__.__name__}") from e
    except (KeyError, IndexError, ValueError) as e:
        raise MistralError("Unexpected Mistral response") from e


def embed(texts, timeout=60):
    key = settings.MISTRAL_API_KEY
    if not key:
        raise MistralError("Missing MISTRAL_API_KEY")
    try:
        r = requests.post(f"{settings.MISTRAL_BASE}/embeddings", headers=_headers(key), timeout=timeout,
                          json={"model": EMBED, "input": texts})
        r.raise_for_status()
        return [d["embedding"] for d in r.json()["data"]]
    except requests.RequestException as e:
        raise MistralError(f"Embedding request failed: {e.__class__.__name__}") from e
    except (KeyError, ValueError) as e:
        raise MistralError("Unexpected embedding response") from e
