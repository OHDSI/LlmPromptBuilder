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
POSITIVE_CRITERIA_FIND_PHENOTYPE_ALGORITHM_RELATED_TEXT: List[str] = [

    # ─ P – Population / data source
    r"data\s+source|dataset\s+name|Optum|CPRD|MarketScan|MIMIC",
    r"care\s+(setting|site)|primary\s+care|inpatient|ambulatory",
    r"EHR|EMR|claims\s+database|administrative\s+claims",
    r"geographic\s+(catchment|region|country)",
    r"age\s+range|sex|gender|race|ethnicity|insurance",
    r"(enrollment|eligibility)\s+(window|criteria)|continuous\s+enrollment",
    r"(baseline\s+)?(wash[-\s]?out|look[-\s]?back)",

    # ─ I/T – Intervention / Target / Exposure
    r"index\s+date|cohort\s+entry|time[- ]?zero",
    r"(primary\s+)?exposure|drug|procedure|device|index\s+diagnosis",
    r"ICD[- ]?9|ICD[- ]?10|SNOMED|CPT|HCPCS|LOINC|RxNorm|ATC",
    r"≥\s*\d+\s*(codes?|occurrences?)|first|second\s+hit|incident\s+use",
    r"dose|strength|days’?\s+supply|DDD|cumulative\s+exposure",
    r"time[- ]varying\s+exposure|as[- ]treated|intent[- ]to[- ]treat",

    # ─ C – Comparator / Control
    r"active\s+comparator|reference\s+therapy|standard\s+of\s+care",
    r"(unexposed|control)\s+cohort|negative\s+control",
    r"propensity\s+score|(PS)\s*(matching|weighting|stratification)|IPTW|SMR",

    # ─ O – Outcome / Validation
    r"primary\s+endpoint|clinical\s+outcome|safety\s+event",
    r"(outcome|phenotyping)\s+algorithm|rule[- ]based\s+classifier",
    r"chart\s+review|manual\s+validation|gold\s+standard",
    r"PPV|positive\s+predictive\s+value|sensitivity|specificity|F[- ]?score",
    r"algorithm\s+accuracy|validation\s+statistics|AUROC|AUPRC",

    # ─ T – Timing / Follow-up
    r"follow[- ]up|time[- ]at[- ]risk|observation\s+window|risk\s+window",
    r"censoring|end\s+of\s+follow[- ]up|study\s+end[- ]date",
    r"grace\s+period|exposure\s+gap|latency\s+period",
    r"immortal\s+time|landmark\s+analysis",

    # ─ Extras / Reporting
    r"inclusion\s+criteria|exclusion\s+criteria",
    r"cohort\s+flow\s+diagram|attrition\s+counts|CONSORT",
    r"(RECORD[- ]PE|STaRT[- ]RWE)\s+checklist",
]

DEFAULT_POSITIVE_CRITERIA_IS_RELEVANT = POSITIVE_CRITERIA_FIND_PHENOTYPE_ALGORITHM_RELATED_TEXT

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

    header_lines = [
        "TASK — Read one paragraph as an expert informatician.",
        "",
        f"The purpose is {purpose}.",
        f"The text is from {data_origin}.",
        "",
        'Return { "is_relevant": true } **only if**:',
    ]

    first_bullet = "• at least one *Look-for* item appears in the paragraph"
    if neg:
        first_bullet += ", **and**"
    header_lines.append(first_bullet)

    if neg:
        header_lines.append(
            "• none of the *Should-NOT-contain* items appear (if any are defined)."
        )

    header_lines.extend(
        [
            "",
            'Otherwise return { "is_relevant": false }.',
            "",
            "Use lowercase booleans and nothing else.",
        ]
    )

    header = textwrap.dedent("\n".join(header_lines)) + "\n"

    sections: List[str] = [_build_criteria_section("Look-for (any of)", pos)]
    if neg:
        sections.append(_build_criteria_section("Should-NOT-contain (any of)", neg))

    parts = [header, *sections]

    if _chain is not None:  # pragma: no cover
        return _chain(parts)

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
