"""is_relevant.py
A tiny helper utility built on the `llm_prompt_builders` toolkit that
constructs a reusable prompt asking an LLM to decide whether a paragraph
contains *actionable* information for building or validating a computable
cohort/phenotype.

The LLM must answer **only** with a JSON object of the form:

    { "is_relevant": true }

or

    { "is_relevant": false }

Booleans must stay lowercase, as required by the downstream evaluator.
"""
from __future__ import annotations

import textwrap
from typing import List, Sequence

try:
    # If present, use the prompt‑composition DSL for cleaner joins.
    from llm_prompt_builders.accelerators.chain import chain as _chain  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – keeps the script self‑contained
    _chain = None

###############################################################################
# Default *positive* criteria – actionable details
###############################################################################
DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT: List[str] = [
    "data source or care setting",
    "demographic filter (age, sex, insurance, etc.)",
    "entry/index event (diagnosis/procedure/drug/lab code, ≥ n codes, look‑back, first/second hit, etc.)",
    "extra inclusion / exclusion rule",
    "wash‑out or continuous‑enrollment window",
    "exit/censor rule",
    "outcome‑finding algorithm",
    "explicit medical codes (ICD, SNOMED, CPT, RxNorm, ATC, LOINC …)",
    "follow‑up / time‑at‑risk spec",
    "comparator or exposure logic",
    "validation stats (PPV, sensitivity)",
    "attrition counts",
]

###############################################################################
# Helper for bullet sections
###############################################################################

def _build_criteria_section(label: str, items: Sequence[str]) -> str:
    bullets = "\n".join(f"* {b}" for b in items)
    return f"{label}\n\n{bullets}\n"

###############################################################################
# Public API
###############################################################################

def get_is_relevant(
    data_origin: str,
    purpose: str,
    positive_criteria: Sequence[str] | None = None,
    negative_criteria: Sequence[str] | None = None,
) -> str:
    """Compose and return the final prompt string.

    Parameters
    ----------
    data_origin
        Where the paragraph comes from – e.g. "routine health data (claims, EHR, registry)".
    purpose
        Why we care – e.g. "building or validating a computable cohort/phenotype".
    positive_criteria
        Items that *make* the text relevant.  If *None*, a comprehensive default
        list of actionable‑detail bullets is used.
    negative_criteria
        Items that *invalidate* relevance.  If *None* or empty, this section is
        omitted and only the *positive* test applies.
    """
    pos = list(positive_criteria or DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT)
    neg = list(negative_criteria or [])

    header = textwrap.dedent(
        f"""\
        TASK — Read one paragraph as an expert informatician.\n\n        The purpose is {purpose}.\n        The text is from {data_origin}.\n\n        Return {{ \"is_relevant\": true }} **only if**:\n          • at least one *Look‑for* item appears in the paragraph, **and**\n          • none of the *Should‑NOT‑contain* items appear (if any are defined).\n\n        Otherwise return {{ \"is_relevant\": false }}.\n\n        Return false as well if the paragraph is only background, discussion, or a purely prospective randomized trial with no secondary‑data algorithm.\n\n        Use lowercase booleans and nothing else.\n"""
    )

    sections: List[str] = [_build_criteria_section("Look‑for (any of)", pos)]
    if neg:
        sections.append(_build_criteria_section("Should‑NOT‑contain (any of)", neg))

    parts = [header, *sections]

    if _chain is not None:  # pragma: no cover
        return _chain(*parts)

    return "\n".join(parts).strip()


# ---------------------------------------------------------------------------
# Re‑exports
# ---------------------------------------------------------------------------
__all__ = [
    "DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT",
    "get_is_relevant",
]

from llm_prompt_builders.prompts.is_relevant import (  # type: ignore
    get_is_relevant as _impl_build,
    DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT as _DEFAULT,
)
