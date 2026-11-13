from report import CaseResult, render_markdown


def test_summary_line_counts_passes_correctly():
    results = [
        CaseResult(id="a", category="retrieval", description="x", passed=True),
        CaseResult(id="b", category="retrieval", description="y", passed=False),
    ]
    markdown = render_markdown(results, judge_model="gpt-4.1")
    assert "1/2 cases passed" in markdown
    assert "gpt-4.1" in markdown


def test_failing_case_is_marked_in_the_table():
    results = [CaseResult(id="bad-case", category="adversarial", description="x", passed=False)]
    markdown = render_markdown(results, judge_model="gpt-4.1")
    assert "bad-case" in markdown
    assert "FAIL" in markdown


def test_sub_checks_are_listed_in_the_details_section():
    results = [
        CaseResult(
            id="c",
            category="hallucination_live",
            description="checks several things",
            passed=False,
            checks={"is_invented": True, "respects_restriction": False},
            notes="violated vegetarian restriction",
        )
    ]
    markdown = render_markdown(results, judge_model="gpt-4.1")
    assert "is_invented" in markdown
    assert "respects_restriction" in markdown
    assert "violated vegetarian restriction" in markdown
