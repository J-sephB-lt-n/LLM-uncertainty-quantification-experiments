"""TODO"""

import json
import altair as alt


def main():
    """TODO"""
    with open("output/llm_assessment.json", "r", encoding="utf-8") as file:
        assessments: dict = json.load(file)

    plot_data: list[dict] = []
    for filename, data in assessments.items():
        for example in data["extracted"]:
            plot_data.append(
                {
                    "filename": filename,
                    "key": example["key"],
                    "expected": example["expected"],
                    "llm_is_correct": example["llm_is_correct"],
                    "min_logprob": example["min_logprob"],
                }
            )

    plot_data = sorted(
        plot_data,
        key=lambda x: x["min_logprob"],
        reverse=True,
    )

    with open("output/plot_data.json", "w", encoding="utf-8") as file:
        json.dump(plot_data, file)

    n_total = len(plot_data)
    n_correct = 0
    cumulative_plot_data = []
    for i, item in enumerate(plot_data):
        if item["llm_is_correct"]:
            n_correct += 1
        cumulative_plot_data.append(
            {
                "data_included_fraction": (i + 1) / n_total,
                "cumulative_accuracy": n_correct / (i + 1),
                "min_logprob": item["min_logprob"],
                "n_cumulative": i + 1,
                "n_correct": n_correct,
            }
        )

    chart = (
        alt.Chart(alt.Data(values=cumulative_plot_data))
        .mark_line(point=True)
        .encode(
            x=alt.X(
                "data_included_fraction:Q",
                title="Fraction of Data Included (ordered by confidence)",
                axis=alt.Axis(format="%"),
            ),
            y=alt.Y(
                "cumulative_accuracy:Q",
                title="Cumulative Accuracy",
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domain=[0, 1]),
            ),
            tooltip=[
                alt.Tooltip(
                    "data_included_fraction:Q",
                    title="Fraction of Data",
                    format=".2%",
                ),
                alt.Tooltip(
                    "cumulative_accuracy:Q",
                    title="Cumulative Accuracy",
                    format=".2%",
                ),
                alt.Tooltip("min_logprob:Q", title="Min Logprob Threshold"),
                alt.Tooltip("n_cumulative:Q", title="Examples Included"),
                alt.Tooltip("n_correct:Q", title="Correct Examples"),
            ],
        )
        .properties(
            title="Cumulative Accuracy vs. Confidence Threshold",
            width=800,
            height=400,
        )
        .interactive()
    )

    chart.save("output/cumulative_accuracy.html")

    histogram = (
        alt.Chart(alt.Data(values=plot_data))
        .mark_bar(opacity=0.7, binSpacing=0)
        .encode(
            x=alt.X(
                "min_logprob:Q",
                bin=alt.Bin(maxbins=100),
                title="min(logprob)",
            ),
            y=alt.Y("count():Q", stack=None, title="Count"),
            color=alt.Color("llm_is_correct:N", title="LLM is Correct"),
            tooltip=[
                alt.Tooltip("llm_is_correct:N", title="LLM is correct"),
                alt.Tooltip("count():Q", title="Number of examples"),
            ],
        )
        .properties(
            title="Distribution of min(logprob)",
            width=800,
            height=400,
        )
        .interactive()
    )
    histogram.save("output/logprob_distributions.html")


if __name__ == "__main__":
    main()
