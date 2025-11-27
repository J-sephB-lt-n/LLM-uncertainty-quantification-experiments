# LLM-uncertainty-quantification-experiments

This repo is a little experiment I did. I was interested to see if I would observe any useful correlation between a simple token-logprobs-based metric and model accurac when using a Large Language Model (LLM) on a structured data extraction task.

What I've done is:

1. Hand-curated some key/value data from image extraction tasks (with known ground truth correct answers). You can see these tasks in [./examples/questions.yaml](./examples/questions.yaml)
2. Give the tasks to a Large Language Model (LLM).
3. Check which tasks the LLM got right.
4. For each task-requested key/value pair appearing in the LLM responses, extract the logprobs of those tokens (i.e. the tokens only in that key/value pair part).
5. Make some plots assessing whether simple metrics such as `min(token-logprobs)` or `var(token-logprobs)` (i.e. aggregate measures of _model confidence_) are correlated with ground truth answer correctness.

The answer is yes, there definitely is useful correlation - you can look at the plots in [./output/\*.html](./output) to confirm this for yourself.

Not a lot of thought has been put into code quality in this repo since this was just an experiment, although I did write all of the code myself (apart from `evaluate_uncertainty.py`, which was written mostly by Gemini-2.5-pro).

## Run the Experiment

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

Export some plots visualising the correlation between LLM token logprobs and answer correctness:

```bash
uv run python -m steps.evaluate_uncertainty
ls -1 output/*.html
```

Look at the top 5 most confident wrong answers: TODO

Look at the top 5 least confident correct answers: TODO
