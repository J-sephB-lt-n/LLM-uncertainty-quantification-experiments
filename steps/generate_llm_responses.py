"""TODO."""

import asyncio
import base64
import json
import os
from pathlib import Path

import openai
from openai.types.chat import ChatCompletion
import yaml

MODEL = "azure.gpt-4.1-2025-04-14"
TEMPERATURE = 0

llm = openai.AsyncOpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
)


async def answer_question(img_path: Path, question: str) -> ChatCompletion:
    """TODO."""
    print("Starting", img_path)
    with open(img_path, "rb") as file:
        img: bytes = file.read()

    img_b64: str = base64.b64encode(img).decode("ascii")
    img_extension: str = img_path.stem

    return await llm.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{img_extension};base64,{img_b64}"
                        },
                    },
                ],
            },
        ],
        logprobs=True,
        top_logprobs=0,
    )


async def answer_questions(questions: dict) -> dict[str, ChatCompletion]:
    async with asyncio.TaskGroup() as tg:
        tasks = []
        for filename, question in questions.items():
            tasks.append(
                tg.create_task(
                    answer_question(
                        img_path=Path(filename),
                        question=question["question"],
                    )
                )
            )

    return {
        filename: task.result() for filename, task in zip(questions, tasks, strict=True)
    }


def main():
    print("clearing outputs of previous run")
    for item in Path("./output").iterdir():
        if item.is_file():
            item.unlink()

    with open("./examples/questions.yaml", "r", encoding="utf-8") as file:
        questions: dict = yaml.safe_load(file)

    responses: dict[str, ChatCompletion] = asyncio.run(
        answer_questions(questions),
    )

    with open("output/llm_responses.json", "w", encoding="utf-8") as file:
        json.dump(
            {
                filename: {
                    "question": questions[filename],
                    "llm_response": llm_response.model_dump(),
                }
                for filename, llm_response in responses.items()
            },
            file,
        )


if __name__ == "__main__":
    main()
