from dataclasses import dataclass, field


@dataclass
class CaseResult:
    id: str
    category: str
    description: str
    passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    notes: str = ""


def render_markdown(results: list[CaseResult], judge_model: str) -> str:
    total = len(results)
    passed = sum(1 for r in results if r.passed)

    lines = [
        "# Agent Evaluation Report",
        "",
        f"**{passed}/{total} cases passed.** Judge model: `{judge_model}`.",
        "",
        "| Case | Category | Result | Notes |",
        "|---|---|---|---|",
    ]
    for r in results:
        status = "pass" if r.passed else "FAIL"
        lines.append(f"| `{r.id}` | {r.category} | {status} | {r.notes} |")

    lines.append("")
    lines.append("## Details")
    for r in results:
        lines.append("")
        lines.append(f"### `{r.id}` — {'pass' if r.passed else 'FAIL'}")
        lines.append(f"_{r.description}_")
        lines.append("")
        for check_name, check_passed in r.checks.items():
            mark = "ok" if check_passed else "FAIL"
            lines.append(f"- [{mark}] {check_name}")
        if r.notes:
            lines.append("")
            lines.append(f"> {r.notes}")

    return "\n".join(lines) + "\n"
