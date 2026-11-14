from unittest.mock import MagicMock

from judge import JudgeVerdict, judge_hallucination, parse_judge_response


def test_parse_judge_response_reads_fields():
    raw = '{"violates_restriction": true, "unsafe_or_nonsensical": false, "reasoning": "contains chicken"}'
    verdict = parse_judge_response(raw)
    assert verdict.violates_restriction is True
    assert verdict.unsafe_or_nonsensical is False
    assert verdict.reasoning == "contains chicken"


def test_parse_judge_response_strips_markdown_fences():
    raw = '```json\n{"violates_restriction": false, "unsafe_or_nonsensical": true, "reasoning": "bad"}\n```'
    verdict = parse_judge_response(raw)
    assert verdict.unsafe_or_nonsensical is True


def test_verdict_is_hallucination_true_if_either_flag_set():
    assert JudgeVerdict(True, False, "x").is_hallucination is True
    assert JudgeVerdict(False, True, "x").is_hallucination is True
    assert JudgeVerdict(False, False, "x").is_hallucination is False


def test_judge_hallucination_calls_openai_and_parses_result():
    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value.choices = [
        MagicMock(
            message=MagicMock(
                content='{"violates_restriction": false, "unsafe_or_nonsensical": false, "reasoning": "fine"}'
            )
        )
    ]

    verdict = judge_hallucination(
        name="Salad",
        ingredients=["lettuce"],
        instructions="mix",
        restrictions="vegan",
        client=fake_client,
    )

    assert verdict.is_hallucination is False
    fake_client.chat.completions.create.assert_called_once()
    _, kwargs = fake_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4.1"
    assert kwargs["response_format"] == {"type": "json_object"}
