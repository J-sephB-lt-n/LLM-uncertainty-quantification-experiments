"""TODO."""

import asyncio
import base64
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
    )


async def answer_questions(questions: list[dict]) -> dict[str, ChatCompletion]:
    async with asyncio.TaskGroup() as tg:
        tasks = []
        for question in questions:
            tasks.append(
                tg.create_task(
                    answer_question(
                        img_path=Path(question["file"]),
                        question=question["question"],
                    )
                )
            )

    return {
        question["file"]: task.result()
        for question, task in zip(questions, tasks, strict=True)
    }


def main():
    with open("./examples/questions.yaml", "r", encoding="utf-8") as file:
        questions: list = yaml.safe_load(file)

    responses: dict[str, ChatCompletion] = asyncio.run(
        answer_questions(questions),
    )

    for file, response in responses.items():
        print("--", file, "--")
        print(response.choices[0].message.content)
        print("=" * 50)


if __name__ == "__main__":
    main()
