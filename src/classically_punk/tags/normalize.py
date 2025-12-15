"""
Tag normalization, slang aliasing, and language handling utilities.

Provides functions to clean tags, detect language, and generate graph edges for
slang/alias relationships and language variants.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from langdetect import detect, DetectorFactory
from unidecode import unidecode

from classically_punk.graph.schema import Edge

# langdetect determinism
DetectorFactory.seed = 42


def normalize_tag(text: str) -> str:
    """
    Normalize a tag: lowercase, strip accents, drop most punctuation, collapse spaces.
    """
    lowered = unidecode(text).lower()
    cleaned = re.sub(r"[^a-z0-9\s\-']", " ", lowered)
    collapsed = re.sub(r"\s+", " ", cleaned).strip()
    return collapsed


def detect_language(text: str) -> Optional[str]:
    """
    Detect language code (best-effort).
    """
    try:
        return detect(text)
    except Exception:
        return None


@dataclass
class TagAlias:
    alias: str
    canonical: str
    language: Optional[str] = None
    region: Optional[str] = None
    confidence: float = 1.0
    source: str = "manual"
    version: str = "v1"


def build_slang_edges(aliases: Iterable[TagAlias]) -> List[Edge]:
    """
    Build SLANG_ALIAS edges from TagAlias records.
    """
    edges: List[Edge] = []
    for ta in aliases:
        edges.append(
            Edge(
                src=f"tag::{normalize_tag(ta.alias)}",
                dst=f"tag::{normalize_tag(ta.canonical)}",
                type="SLANG_ALIAS",
                weight=ta.confidence,
                source=ta.source,
                version=ta.version,
            )
        )
    return edges


def build_language_variant_edges(
    variants: Iterable[Dict[str, str]],
    source: str = "translation",
    version: str = "v1",
) -> List[Edge]:
    """
    Build LANG_VARIANT edges between canonical and translated tags.
    variants: iterable of dicts with keys: canonical, translated, language (target lang code)
    """
    edges: List[Edge] = []
    for row in variants:
        canonical = normalize_tag(row["canonical"])
        translated = normalize_tag(row["translated"])
        lang = row.get("language")
        edges.append(
            Edge(
                src=f"tag::{canonical}",
                dst=f"tag::{translated}",
                type="LANG_VARIANT",
                weight=1.0,
                source=f"{source}:{lang}" if lang else source,
                version=version,
            )
        )
    return edges

