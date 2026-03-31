"""
Skill normalizer and inference engine.
Loads from taxonomy.json and performs:
  - Canonical name mapping (alias resolution)
  - Related skill inference
  - Ambiguous skill flagging
"""
import json
import os
import re
from typing import List, Dict, Tuple, Optional

TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "skill_taxonomy", "taxonomy.json")


def _load_taxonomy() -> dict:
    try:
        with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


_TAXONOMY_CACHE: Optional[dict] = None


def get_taxonomy() -> dict:
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is None:
        _TAXONOMY_CACHE = _load_taxonomy()
    return _TAXONOMY_CACHE


def _build_alias_map(taxonomy: dict) -> Dict[str, str]:
    """Build a flat alias → canonical_name map."""
    alias_map = {}
    for canonical, meta in taxonomy.items():
        alias_map[canonical.lower()] = canonical
        for alias in meta.get("aliases", []):
            alias_map[alias.lower()] = canonical
    return alias_map


def _normalize_token(token: str) -> str:
    return token.lower().strip()


def normalize_skills(
    raw_skills: List[str],
    taxonomy: Optional[dict] = None,
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Returns:
        normalized_skills: skills that were mapped to a canonical name
        explicit_skills: skills that appear literally in taxonomy
        inferred_skills: skills inferred from presence of other skills
        ambiguous_skills: skills that could not be resolved
    """
    if taxonomy is None:
        taxonomy = get_taxonomy()

    alias_map = _build_alias_map(taxonomy)

    normalized = []
    ambiguous = []
    canonical_found = set()

    for raw in raw_skills:
        token = _normalize_token(raw)
        if token in alias_map:
            canonical = alias_map[token]
            if canonical not in canonical_found:
                normalized.append(canonical)
                canonical_found.add(canonical)
        else:
            # Partial match: check if token is a substring of any canonical
            partial_match = None
            for alias, canonical in alias_map.items():
                if token in alias or alias in token:
                    partial_match = canonical
                    break
            if partial_match and partial_match not in canonical_found:
                normalized.append(partial_match)
                canonical_found.add(partial_match)
            else:
                ambiguous.append(raw)

    # Inference: for each canonical found, check what we can infer
    inferred = []
    inferred_set = set()
    for canonical in list(canonical_found):
        meta = taxonomy.get(canonical, {})
        for infer_skill in meta.get("infer_if_present", []):
            if infer_skill not in canonical_found and infer_skill not in inferred_set:
                inferred.append(infer_skill)
                inferred_set.add(infer_skill)

    return normalized, list(canonical_found), inferred, ambiguous


def get_related_skills(canonical: str, taxonomy: Optional[dict] = None) -> List[str]:
    if taxonomy is None:
        taxonomy = get_taxonomy()
    meta = taxonomy.get(canonical, {})
    return meta.get("related_skills", [])


def resolve_ambiguous_skill(raw: str, taxonomy: Optional[dict] = None) -> Optional[str]:
    """Try harder to resolve an ambiguous skill (fuzzy match)."""
    if taxonomy is None:
        taxonomy = get_taxonomy()
    alias_map = _build_alias_map(taxonomy)
    token = _normalize_token(raw)
    # Try removing punctuation
    cleaned = re.sub(r"[^a-z0-9 ]", "", token)
    if cleaned in alias_map:
        return alias_map[cleaned]
    return None
