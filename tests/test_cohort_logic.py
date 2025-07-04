# tests/test_cohort_logic.py
import json
import re

import pytest
from llm_prompt_builders.prompts import cohort_logic_extraction

def test_cohort_logic_template_renders():
    # 1) Call your prompt function
    primary = "patients with new onset atrial fibrillation"
    body    = "In our retrospective analysis, we included adults aged 50–80 with..."
    prompt_obj = cohort_logic_extraction(primary_cohort=primary, user_text=body)

    # 2) It should have a render() method returning a string
    text = prompt_obj.render()
    assert isinstance(text, str)

    # 3) Check that key sections appear in the output
    assert "SYSTEM_ROLE" in text
    assert "PRIMARY_OBJECTIVE" in text
    assert re.search(r"PRIMARY_COHORT_DESCRIPTION:.*" + re.escape(primary), text)
    assert "USER_TEXT:" in text
    assert body in text

    # 4) (Optionally) verify you have the JSON instruction kicker
    assert "Return just the JSON" in text

if __name__ == "__main__":
    pytest.main()
