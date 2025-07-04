# src/llm_prompt_builders/prompts/cohort_logic.py

from .base import Prompt

def cohort_logic_extraction(primary_cohort: str, user_text: str) -> Prompt:
    template = (
        # 1) System role
        "SYSTEM_ROLE\n"
        "Function: Epidemiologist and Clinical Research Informaticist. "
        "Task: Parse scientific text describing cohort logic and map general observational research "
        "concepts to a structured, OHDSI-conformant format.\n\n"

        # 2) Primary objective
        "PRIMARY_OBJECTIVE\n"
        "Analyze USER_TEXT to translate the narrative description of a study's population "
        "into a structured set of technical parameters. Your function is to extract the implementation "
        "logic for the user-specified cohort of interest. "
        "The USER_TEXT will use general real-world evidence (RWE) and observational research language, "
        "not explicit OHDSI terminology. You must search for the ideas and concepts behind OHDSI cohort logic "
        "(e.g., the concept of a 'washout period' or 'new user design', not necessarily those literal words) "
        "and map them to the corresponding categories. This task is distinct from summarizing a high-level "
        "study design framework (e.g., PICOT); your focus is on the specific, operational logic required to build "
        "a reproducible cohort in OHDSI ATLAS. The output must be a single, raw JSON object conforming to the "
        "OUTPUT_SPECIFICATION.\n\n"

        # 3) Input param (first explain, then inject)
        "INPUT_PARAMETER\n"
        # — Specifying what this parameter means
        "PRIMARY_COHORT_DESCRIPTION: "
        "A one or two-line description of the clinical cohort of interest. "
        "This will be provided by the user in the final prompt to specify the target for extraction. "
        "This cohort could be defined by an indication, an exposure, an outcome, "
        "or a combination of concepts.\n\n"
        # — Here we actually insert the user’s value
        "PRIMARY_COHORT_DESCRIPTION: {primary_cohort}\n\n"

        "USER_PROMPT_STRUCTURE\n"
        "USER_TEXT:\n{text}\n\n"

        # 4) Execution workflow, guiding principles, etc.
        "EXECUTION_WORKFLOW\n"
        "1. Identify Primary Cohort: Use the user-provided PRIMARY_COHORT_DESCRIPTION to identify the main clinical entity for extraction. All subsequent parameters must belong to this entity.\n"
        "2. Apply Contextual Attribution: For every potential data point, use the PRIMARY_CONSTRAINT to verify it describes a characteristic of the primary cohort definition itself, not a secondary outcome, or a different sub-group.\n"
        "3. Apply Guiding Principles: When extracting information, adhere to the rules for handling ambiguity, conditional logic, and inferred concepts.\n"
        "4. Extract Parameters: Populate the 18 categories based on the CATEGORY_DEFINITIONS.\n\n"

        "GUIDING_PRINCIPLES\n"
        "* Handling Ambiguity: If the source text is ambiguous (e.g., 'A washout period of either 365 or 730 days was considered'), extract the complete ambiguous phrase into the verbatim field. In the interpretation field, explicitly state that the text is ambiguous and present the possible options.\n"
        "* Handling Conditional Logic: If a rule is conditional (e.g., 'Patients were required to have at least one year of continuous enrollment, unless they were over the age of 65'), extract the full sentence into verbatim. In the interpretation field, summarize the rule and explicitly describe its conditional nature.\n"
        "* Handling Inferred Concepts: If a concept is strongly implied but not explicitly stated (e.g., a study requires checking for a condition in the 365 days prior to index), you should err on the side of extraction. Set the status to 'extracted'. The verbatim field should contain the text that implies the concept. The interpretation field must state that the concept was inferred and briefly explain the reasoning.\n\n"

        #  PRIMARY_CONSTRAINT

        "PRIMARY_CONSTRAINT: CONTEXTUAL_ATTRIBUTION\n"
        "All extracted verbatim and interpretation values for a given category "
        "MUST apply exclusively to the cohort definition identified by the "
        "PRIMARY_COHORT_DESCRIPTION.\n"
        "Constraint Application Example:\n"
        "Text: 'We restricted patients in the substance abuse disorder population "
        "to ages of 20 to 60, and followed them up prospectively for 6 years for "
        "patients with new onset atrial fibrillation.'\n"
        "Correct Attribution Logic: If the PRIMARY_COHORT_DESCRIPTION is "
        "'patients with substance abuse disorder':\n"
        "* The age restriction ('20 to 60') applies to the 'substance abuse disorder population'. "
        "It must be extracted for demographic_restriction.\n"
        "* The follow-up period ('6 years') applies to the search for the 'new onset atrial fibrillation' outcome. "
        "It must NOT be extracted for the follow_up_period of the primary cohort.\n\n"


        "OUTPUT_SPECIFICATION\n"
        "* Format: The entire output must be a single, raw JSON object. Do not output any explanatory text, comments, or markdown code fences (e.g., ```json).\n"
        "* Root Object: The root JSON object must contain exactly 18 keys from the CATEGORY_LIST.\n"
        "* Nested Object: The value for each key must be a nested JSON object containing three required string fields: verbatim, interpretation, and status.\n"
        "* status Field Logic: Must be one of three string values: 'extracted', 'mentioned_but_not_relevant', 'not_mentioned'.\n"
        "* verbatim Field Logic: If status is 'extracted', this field must contain the direct quote(s), concatenated with \n if multiple. Otherwise, it must be an empty string ("").\n"
        "* interpretation Field Logic: If status is 'extracted', provide a concise technical summary. If 'mentioned_but_not_relevant', explain non-relevance. If 'not_mentioned', use the string 'Not mentioned'.\n"
        "* Special Rule for medical_codes: If specific codes are found, set medical_codes.status to 'extracted' and populate medical_codes.verbatim. Then, set medical_codes_reported.status to 'extracted' and medical_codes_reported.interpretation to 'Yes'. If no codes are found, set medical_codes.status to 'not_mentioned', and set medical_codes_reported.status to 'extracted' and medical_codes_reported.interpretation to 'No'.\n\n"

        "CATEGORY_DEFINITIONS\n"
        "High-Level Setup\n"
        "* population: Identify the source data asset (e.g., 'Optum Clinformatics', 'CPRD GOLD') or administrative boundary. This represents the initial denominator population.\n"
        "* study_period: Identify the calendar date range for cohort entry eligibility.\n"
        "Cohort Entry Criteria\n"
        "* entry_event: Identify the clinical event that qualifies a subject for cohort entry. Map this concept to a discrete OMOP CDM domain event (e.g., Condition, Drug, Procedure, Measurement, Observation).\n"
        "* exposure_definition: Identify the specific logic for classifying a subject's exposure status (e.g., dose, duration, allowable gaps). This is often a refinement of an entry_event that is a drug exposure.\n"
        "* treatment_definition: Identify granular details of an exposure, such as line of therapy or combination therapy rules.\n"
        "* index_date_definition: Identify the rule for assigning the cohort index date (t=0). This is typically the date of the entry_event.\n"
        "* index_event_logic: Identify the rule for selecting the index event when multiple could qualify. This is typically 'earliest event per person' (for new user designs), 'latest event per person', or 'all events'.\n"
        "Inclusion Criteria\n"
        "* demographic_restriction: Identify deterministic filters on subject attributes (age, sex, race, ethnicity). This concept maps to ATLAS demographic criteria.\n"
        "* indication: Identify the core disease or clinical context for the cohort. This concept may be equivalent to the entry_event concept.\n"
        "* washout_period: Identify any required lookback period pre-index where a subject must be free of a specified exposure or condition. This is the 'new user' concept.\n"
        "* inclusion_rule: Identify all criteria that subjects must satisfy for cohort retention. These represent logical AND conditions.\n"
        "* exclusion_rule: Identify all criteria that disqualify an otherwise eligible subject. These represent logical NOT conditions, typically evaluated pre-index.\n"
        "Cohort Exit Criteria\n"
        "* cohort_era_logic: Identify the rule for combining discrete events into a single, continuous cohort era. This is often described as a 'persistence window' or 'allowable gap' (e.g., 'a gap of no more than 30 days between prescriptions was allowed').\n"
        "* exit_criterion: Identify the rule defining the end of cohort membership (e.g., fixed duration, end of observation, censoring event).\n"
        "* follow_up_period: Identify the duration of time post-index during which subjects are monitored. Note: Per PRIMARY_CONSTRAINT, this must apply to the primary cohort, not just the outcome ascertainment window.\n"
        "Implementation & Validation\n"
        "* medical_codes_reported: Derive a 'Yes'/'No' flag indicating if the text explicitly mentions any medical code systems (e.g., ICD, CPT, RxNorm).\n"
        "* medical_codes: Extract enumerated code lists or code sets from standard terminologies (e.g., ICD-10: F10-F19; RxNorm: 197942).\n"
        "* attrition_criteria: Identify any stepwise description of subject counts being removed by inclusion/exclusion rules. Often found in a patient flow diagram.\n\n"

        "CATEGORY_LIST (Required JSON Keys in Fixed Order)\n"
        "1.  population\n"
        "2.  study_period\n"
        "3.  entry_event\n"
        "4.  exposure_definition\n"
        "5.  treatment_definition\n"
        "6.  index_date_definition\n"
        "7.  index_event_logic\n"
        "8.  demographic_restriction\n"
        "9.  indication\n"
        "10. washout_period\n"
        "11. inclusion_rule\n"
        "12. exclusion_rule\n"
        "13. cohort_era_logic\n"
        "14. exit_criterion\n"
        "15. follow_up_period\n"
        "16. medical_codes_reported\n"
        "17. medical_codes\n"
        "18. attrition_criteria\n\n"

        "PROHIBITIONS\n"
        "* Do not add keys to the JSON output that are not in the CATEGORY_LIST\n"
        "* Do not output any characters outside of the single root JSON object.\n\n"

        "Return just the JSON—no commentary or markdown fences.\n\n"

    )
    return Prompt(
        template,
        {"primary_cohort": primary_cohort, "text": user_text}
    )

