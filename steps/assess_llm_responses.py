"""TODO."""

import json
import re
from dataclasses import dataclass


def main():
    with open("output/llm_responses.json", "r", encoding="utf-8") as file:
        responses: dict = json.load(file)

    assessments: dict = {}
    for filename, response in responses.items():
        assessment = {}
        assessment["question"] = response["question"]["question"]
        assessment["extracted"] = []
        for expected_value in response["question"]["expected_values"]:
            key: str = list(expected_value.keys())[0]
            expected_value: str = list(expected_value.values())[0]
            llm_response_text: str = response["llm_response"]["choices"][0]["message"][
                "content"
            ]
            find_llm_value: re.Match | None = re.search(
                rf"(<{re.escape(key)}>(.*?)</{re.escape(key)}>)",
                llm_response_text,
                flags=re.DOTALL,
            )
            llm_capture: str | None = (
                find_llm_value.groups()[0] if find_llm_value else None
            )
            llm_value: str | None = (
                find_llm_value.groups()[1] if find_llm_value else None
            )

            llm_is_correct: bool
            if llm_value is None:
                llm_is_correct = False
            elif str(expected_value).strip().lower() == llm_value.strip().lower():
                llm_is_correct = True
            else:
                llm_is_correct = False

            tokens: list[ResponseToken] = []
            if find_llm_value:
                tokens: list[ResponseToken] = _find_substring_token_logprobs(
                    llm_response=response["llm_response"]["choices"][0],
                    target_substr=llm_capture,
                )

            record: dict = {
                "key": key,
                "expected": expected_value,
                "llm_capture": llm_capture,
                "llm_value": llm_value,
                "llm_is_correct": llm_is_correct,
                "tokens": tokens,
            }
            assessment["extracted"].append(record)

        assessments[filename] = assessment


@dataclass
class ResponseToken:
    text: str
    log_prob: float


def _find_substring_token_logprobs(
    llm_response: dict, target_substr: str
) -> list[ResponseToken]:
    log_probs: list[dict] = llm_response["logprobs"]["content"]

    # anchor to start of LLM response and get substring containing `target_substr` #
    for end_idx, _ in enumerate(log_probs):
        if target_substr in "".join(tok["token"] for tok in log_probs[: end_idx + 1]):
            break
    else:
        raise LookupError(
            "`target_substr` not found in LLM response (LLM response "
            + "created by recombining the tokens)."
        )

    # extend toward start of LLM response to get smallest substring containing `target_substr` #
    for start_idx in range(end_idx, -1, -1):
        if target_substr in "".join(
            tok["token"] for tok in log_probs[start_idx : end_idx + 1]
        ):
            break

    return [
        ResponseToken(text=tok["token"], log_prob=tok["logprob"])
        for tok in log_probs[start_idx : end_idx + 1]
    ]


if __name__ == "__main__":
    main()
