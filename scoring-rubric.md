# Scoring rubric

## Headline score (0-5) per prompt and model

The final answer is compared with [`ground-truth.md`](ground-truth.md). Where a model prints reasoning text
(`<think>...</think>`), the **whole output is read, but the final answer carries the weight**; reasoning only
matters if it changes the final answer or wastes time. The leak is recorded separately in
[`results/leak-ledger.csv`](results/leak-ledger.csv).

| Score | Meaning |
|---|---|
| 5 | Correct and complete, follows every instruction, nothing invented |
| 4 | Correct with minor gaps or one small error |
| 3 | Mostly right but a meaningful error, omission or constraint miss |
| 2 | Several errors, or the key point is missing/hedged |
| 1 | Mostly wrong or unusable, though partly on topic |
| 0 | Wrong, fabricated as fact, or no answer |

## Sub-scores (recorded where noted in `results/scores.csv`)

| Column | What it checks |
|---|---|
| correctness | Facts, IDs, arithmetic and syntax match the ground truth |
| completeness | Covers the key points the ground truth lists |
| instruction_following | Length, format, "show steps", "list the evidence" |
| hallucination | 5 = nothing invented; 0 = invented details stated as fact |

Sub-scores were not recorded for every general prompt, so some cells are blank.

## Other rules

- **Speed** is the `eval rate` printed by `ollama run --verbose` (generation tokens per second). The prompt-eval rate is
  ignored because prompt caching distorts it.
- **Reasoning leak**: `</think>` text visible in the output counts as a leak. It is not penalised in the headline score
  unless it changes the answer, but its token and time cost stays in the speed numbers.
- A run that never finishes (P3, Foundation-Sec) scores 0 and has no speed record.
- Scores are **single-rater and non-blind** (see Limitations in the report).
