"""Extracción de factores de sentimiento desde documentos financieros.

Estrategia en dos capas:

- **Determinista (siempre disponible):** léxico financiero ponderado + detección de
  negaciones. Reproducible y sin dependencia de red, ideal para tests y entrevistas.
- **Gancho LLM (opcional):** si se inyecta un `LLMExtractor`, se usa para extraer
  factores estructurados (sentimiento, temas, guía). Así el sistema demuestra
  integración con IA generativa sin acoplarse a un proveedor.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from app.core.logging import logger


# Léxico financiero simple y ponderado (-3..+3)
POSITIVE_TERMS: dict[str, int] = {
    "growth": 2, "beat": 3, "record": 2, "profit": 2, "upgrade": 3, "outperform": 3,
    "increase": 1, "strong": 2, "expansion": 2, "surge": 2, "bullish": 3, "guidance raised": 3,
    "margin expansion": 2, "free cash flow": 2, "buyback": 2, "dividend": 1, "accelerate": 2,
    "demand": 1, "momentum": 1, "recovery": 1, "optimistic": 2,
}

NEGATIVE_TERMS: dict[str, int] = {
    "loss": -2, "miss": -3, "downgrade": -3, "underperform": -3, "decline": -2,
    "decrease": -1, "weak": -2, "contraction": -2, "plunge": -2, "bearish": -3,
    "guidance cut": -3, "margin compression": -2, "bankruptcy": -3, "lawsuit": -2,
    "investigation": -2, "default": -3, "layoff": -2, "slowdown": -2, "pressure": -1,
    "risk": -1, "concern": -1, "volatility": -1, "inflation": -1,
}

NEGATION_WORDS = {"no", "not", "not", "never", "n't", "without", "fail", "failed", "unable"}


class LLMExtractor(Protocol):
    """Interfaz opcional que puede implementar un proveedor de LLM."""

    def extract_factors(self, text: str) -> dict:  # pragma: no cover - contrato
        ...


@dataclass
class SentimentResult:
    """Resultado del análisis de sentimiento de un documento."""

    score: float
    positive_hits: list[str] = field(default_factory=list)
    negative_hits: list[str] = field(default_factory=list)
    n_positive: int = 0
    n_negative: int = 0
    llm_used: bool = False
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "score": round(self.score, 4),
            "positive_hits": self.positive_hits[:10],
            "negative_hits": self.negative_hits[:10],
            "n_positive": self.n_positive,
            "n_negative": self.n_negative,
            "llm_used": self.llm_used,
            "extra": self.extra,
        }


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z'\-]+", text.lower())


def _is_negated(tokens: list[str], idx: int, window: int = 3) -> bool:
    """Detecta si un término está negado por las palabras previas dentro de la ventana."""
    start = max(0, idx - window)
    for tok in tokens[start:idx]:
        if tok in NEGATION_WORDS or tok.endswith("n't"):
            return True
    return False


def extract_sentiment(text: str, llm: LLMExtractor | None = None) -> SentimentResult:
    """Extrae sentimiento de un documento. Usa LLM si se provee, si no, léxico determinista."""
    if llm is not None:
        try:
            factors = llm.extract_factors(text)
            score = float(factors.get("sentiment", factors.get("score", 0.0)))
            logger.info("Sentimiento extraído con LLM (score≈%.3f)", score)
            return SentimentResult(score=score, llm_used=True, extra=factors)
        except Exception as exc:  # pragma: no cover - fallback defensivo
            logger.warning("Fallo el extractor LLM, usando fallback determinista: %s", exc)

    tokens = _tokenize(text)
    pos_hits: list[str] = []
    neg_hits: list[str] = []
    total = 0.0

    # Normalización por longitud (por ~1000 tokens)
    scale = max(1.0, len(tokens) / 1000.0)
    for i, tok in enumerate(tokens):
        if tok in POSITIVE_TERMS:
            weight = POSITIVE_TERMS[tok]
            if _is_negated(tokens, i):
                weight = -weight
                neg_hits.append(tok)
            else:
                pos_hits.append(tok)
            total += weight
        elif tok in NEGATIVE_TERMS:
            weight = NEGATIVE_TERMS[tok]
            if _is_negated(tokens, i):
                weight = -weight
                pos_hits.append(tok)
            else:
                neg_hits.append(tok)
            total += weight

    raw = total / scale
    # Comprimir a [-1, 1] mediante tanh suave
    import math

    score = math.tanh(raw / 10.0)
    logger.info("Sentimiento determinista: score=%.3f (+%d / -%d)", score, len(pos_hits), len(neg_hits))
    return SentimentResult(
        score=score,
        positive_hits=pos_hits,
        negative_hits=neg_hits,
        n_positive=len(pos_hits),
        n_negative=len(neg_hits),
    )


def aggregate_document_sentiment(docs: list[dict], llm: LLMExtractor | None = None) -> dict:
    """Agrega sentimiento de múltiples documentos a un factor macro único."""
    if not docs:
        return {"macro_sentiment": 0.0, "per_document": [], "n_docs": 0}

    results = []
    for doc in docs:
        res = extract_sentiment(doc.get("content", ""), llm=llm)
        results.append({"name": doc.get("name", "doc"), **res.as_dict()})

    scores = [r["score"] for r in results]
    macro = sum(scores) / len(scores)
    logger.info("Sentimiento macro agregado: %.4f sobre %d documentos", macro, len(results))
    return {"macro_sentiment": round(macro, 4), "per_document": results, "n_docs": len(docs)}