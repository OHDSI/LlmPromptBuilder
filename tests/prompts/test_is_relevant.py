"""pytest suite for the public API of `is_relevant.py`

These tests exercise the *current* helper that lives at the project root and
exports `DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT` and `get_is_relevant`.
"""

from __future__ import annotations

import is_relevant as ir


def test_default_criteria_non_empty() -> None:
    """Default positive criteria list must exist and be non-empty."""
    assert isinstance(ir.DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT, list)
    assert ir.DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT, "Expected at least one default criterion"


def test_prompt_contains_origin_and_purpose() -> None:
    """The generated prompt should embed the data origin and purpose."""
    origin = "clinical notes"
    purpose = "detect adverse events"
    prompt = ir.get_is_relevant(data_origin=origin, purpose=purpose)

    prompt_lower = prompt.lower()
    assert origin.lower() in prompt_lower
    assert purpose.lower() in prompt_lower


def test_custom_positive_criteria_included() -> None:
    """All custom positive criteria must appear verbatim in the prompt."""
    origin = "call-centre transcripts"
    purpose = "quality assurance"
    custom = ["mentions dosage", "mentions side effects"]

    prompt = ir.get_is_relevant(origin, purpose, positive_criteria=custom)
    prompt_lower = prompt.lower()

    for criterion in custom:
        assert criterion.lower() in prompt_lower, f"Missing custom criterion: {criterion}"


def test_negative_criteria_section_present() -> None:
    """The *Should-NOT-contain* section is only present when negatives are defined."""
    origin = "EHR"
    purpose = "phenotype validation"
    negatives = ["billing error", "doctor attitude"]

    prompt_with_neg = ir.get_is_relevant(origin, purpose, negative_criteria=negatives)
    assert "should-not-contain" in prompt_with_neg.lower()
    for n in negatives:
        assert n.lower() in prompt_with_neg.lower()

    prompt_without_neg = ir.get_is_relevant(origin, purpose)
    assert "should-not-contain" not in prompt_without_neg.lower()
    assert "look-for" in prompt_without_neg.lower()
    assert ", **and**" not in prompt_without_neg
