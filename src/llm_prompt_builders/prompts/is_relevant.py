"""is_relevant.py
A tiny helper utility built on top of the `llm_prompt_builders` toolkit that
constructs a reusable prompt asking an LLM to decide whether a paragraph
contains *actionable* information for building or validating a computable
cohort/phenotype.

The generated prompt instructs the model to answer **only** with a JSON object
of the form:

    { "is_relevant": true }

or

    { "is_relevant": false }

Booleans must stay lowercase, as required by the downstream evaluator.
"""
from __future__ import annotations

import textwrap
from typing import List, Sequence

try:
    # `llm_prompt_builders` offers a tiny functional DSL for composing prompt
    # fragments.  If it is available we will use its `chain` accelerator for a
    # cleaner construction; otherwise we gracefully fall back to plain string
    # concatenation so that the module still works without the extra
    # dependency.
    from llm_prompt_builders.accelerators.chain import chain as _chain  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – makes the script self‑contained
    _chain = None

###############################################################################
# Canonical *actionable detail* bullets
###############################################################################
DEFAULT_ACTIONABLE_BULLETS: List[str] = [
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


def build_actionable_details_section(details: Sequence[str] | None = None) -> str:
    """Return the *Actionable details* subsection of the prompt.

    Parameters
    ----------
    details
        A custom list of bullet strings.  When *None*, the canonical
        :pydata:`DEFAULT_ACTIONABLE_BULLETS` is used.
    """
    bullets = details or DEFAULT_ACTIONABLE_BULLETS
    bullet_lines = "\n".join(f"* {b}" for b in bullets)
    return f"Actionable details = any of\n\n{bullet_lines}\n"


def build_is_relevant_prompt(
    data_origin: str,
    purpose: str,
    details: Sequence[str] | None = None,
) -> str:
    """Compose the final prompt string.

    The helper can be used *stand‑alone* or combined with the higher‑level
    pieces that ship with *llm_prompt_builders*.

    Parameters
    ----------
    data_origin
        Where the paragraph comes from – e.g. "routine health data (claims, EHR,
        registry)".  This string is interpolated verbatim in the instructions.
    purpose
        A concise description of why we care – e.g. "building or validating a
        computable cohort/phenotype".
    details
        Optional custom bullet list replacing the defaults.

    Returns
    -------
    str
        A fully‑formed prompt ready to be sent to the LLM.
    """
    header = textwrap.dedent(
        f"""\
        TASK — Read the text as an expert informatician. Think through the meaning of the content step by step. \n
        The purpose if {purpose}. \n
        The text is from {data_origin}.\n
        Return {{ \"is_relevant\": true }} if the paragraph gives actionable details. Otherwise return {{ \"is_relevant\": false }}. Use lowercase booleans and nothing else.\n\n"""
    )

    actionable = build_actionable_details_section(details)

    footer = textwrap.dedent(
        """\
        \n\n"""
    )

    parts = [header, actionable, footer]

    # Prefer the composable DSL when available.
    if _chain is not None:  # pragma: no cover
        return _chain(parts)

    # Fallback: naïve join with a single blank line as separator.
    return "\n".join(parts).strip()


# ---------------------------------------------------------------------------
# Public re‑exports
# ---------------------------------------------------------------------------
__all__ = [
    "DEFAULT_ACTIONABLE_BULLETS",
    "build_actionable_details_section",
    "build_is_relevant_prompt",
]
