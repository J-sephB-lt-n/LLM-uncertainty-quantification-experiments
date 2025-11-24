# LLM-uncertainty-quantification-experiments

Generate LLM answers to the proposed questions (tasks):
(WARNING: this first deletes all outputs of previous runs)

```bash
uv run python -m steps.generate_llm_responses --model_name 'gpt-4.1'
cat output/llm_responses.json | jq .
```

Assess the LLM responses (i.e. check answers for correctness against the known true answers):

```bash
uv run python -m steps.assess_llm_responses
cat output/llm_assessment.json | jq .
```
