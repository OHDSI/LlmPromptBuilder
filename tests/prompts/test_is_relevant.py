"""tests/test_is_relevant.py
Unit tests for the *is_relevant* prompt‑builder helper.

Run with pytest:

    pytest -q
"""
from __future__ import annotations

import re
from typing import List

import pytest

from is_relevant import (
    DEFAULT_ACTIONABLE_BULLETS,
    build_is_relevant_prompt,
)

###############################################################################
# Fixtures & helpers
###############################################################################

def _strip_ws(text: str) -> str:
    """Normalize whitespace for robust substring checks."""
    return re.sub(r"\s+", " ", text).strip()


###############################################################################
# Tests
###############################################################################

def test_default_prompt_contains_mandatory_fragments() -> None:
    """The default prompt must include both JSON answers & all canonical bullets."""
    prompt = build_is_relevant_prompt(
        data_origin="routine health data (claims, EHR, registry, etc.)",
        purpose="building or validating a computable cohort/phenotype",
    )

    prompt_nows = _strip_ws(prompt)

    # Mandatory JSON answer snippets
    assert "{ \"is_relevant\": true }" in prompt_nows
    assert "{ \"is_relevant\": false }" in prompt_nows

    # Every canonical bullet should appear verbatim preceded by a bullet star.
    for bullet in DEFAULT_ACTIONABLE_BULLETS:
        assert f"* {bullet}" in prompt, f"Missing bullet: {bullet}"


def test_custom_actionable_details_override_defaults() -> None:
    """Supplying *details* replaces (does not append to) the default bullets."""
    custom_details: List[str] = [
        "signal‑noise ratio window",
        "hyper‑specific eligibility criterion",
    ]
    prompt = build_is_relevant_prompt(
        data_origin="claims data",
        purpose="validating a phenotype",
        details=custom_details,
    )

    # Custom bullets must be present …
    for bullet in custom_details:
        assert f"* {bullet}" in prompt

    # … while *none* of the canonical ones appear.
    for default in DEFAULT_ACTIONABLE_BULLETS:
        assert f"* {default}" not in prompt


def test_prompt_is_plain_string() -> None:
    """Regardless of the optional llm‑prompt‑builders dependency, output is str."""
    prompt = build_is_relevant_prompt("claims", "cohort")
    assert isinstance(prompt, str)


###############################################################################
# Optional: quick sanity check that the prompt ends with the strict guidance.
###############################################################################

def test_prompt_final_instruction() -> None:
    prompt = build_is_relevant_prompt("claims", "cohort")
    assert prompt.strip().endswith("Use lowercase booleans and nothing else."), (
        "Prompt must end with the lowercase‑boolean instruction",
    )
