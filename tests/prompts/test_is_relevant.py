"""Updated pytest suite for llm_prompt_builders.prompts.is_relevant

These tests exercise the public contract of `build_is_relevant_prompt` as well
as the exported defaults.  They no longer rely on the legacy top‑level
`is_relevant` module that was removed during the package re‑org.
"""

from __future__ import annotations

import pytest

from llm_prompt_builders.prompts import is_relevant as ir


def test_default_positive_criteria_non_empty() -> None:
    """The default list of positive criteria should be a non‑empty list."""
    assert isinstance(ir.DEFAULT_POSITIVE_CRITERIA, list)
    assert ir.DEFAULT_POSITIVE_CRITERIA, "Expected DEFAULT_POSITIVE_CRITERIA to be non‑empty"


def test_prompt_contains_origin_and_purpose() -> None:
    """Generated prompt must reflect the requested data origin and purpose."""
    origin = "clinical notes"
    purpose = "detect adverse events"

    prompt = ir.build_is_relevant_prompt(data_origin=origin, purpose=purpose)

    # Case‑insensitive check to avoid surprises with capitalisation.
    prompt_lower = prompt.lower()
    assert origin.lower() in prompt_lower
    assert purpose.lower() in prompt_lower


def test_prompt_includes_custom_criteria() -> None:
    """Custom positive criteria should appear verbatim in the prompt."""
    origin = "call‑centre transcripts"
    purpose = "quality assurance"
    criteria = [
        "mentions dosage",
        "mentions side effects",
    ]

    prompt = ir.build_is_relevant_prompt(
        data_origin=origin,
        purpose=purpose,
        positive_criteria=criteria,
    )

    prompt_lower = prompt.lower()
    for criterion in criteria:
        assert criterion.lower() in prompt_lower, f"Criterion '{criterion}' missing from prompt"
