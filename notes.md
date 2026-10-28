# Lab notes

A chronological log of how the benchmark was run, what went wrong and how each problem was handled.
Everything happened on **25 October 2026**. Screenshot links point into [`screenshots/`](screenshots/).

## Timeline

1. **Reset.** Removed the previous local models (`ollama rm`) so the benchmark started from nothing
   ([00](screenshots/setup/00-reset-old-models.png)). Checked the Ollama version, driver and GPU
   ([01](screenshots/setup/01-ollama-version-and-gpu.png), [02](screenshots/setup/02-nvidia-smi-baseline.png)).
2. **Speed settings.** Set `OLLAMA_FLASH_ATTENTION=1` and `OLLAMA_KEEP_ALIVE=30m` with `setx`, then restarted Ollama.
3. **Pulled the models** ([03](screenshots/setup/03-pulling-models.png), [04](screenshots/setup/04-ollama-list-models.png)).
4. **Qwen3 4B.** First attempt, see *Challenge 2* below. Replaced by `qwen3:4b-instruct`.
5. **GPU fit check** with `ollama ps` for every model, including three tuning attempts on Qwen3 8B
   ([gpu-offload/](screenshots/gpu-offload/)).
6. **Manual runs**: one model per terminal session, all ten prompts, `/clear` between prompts. Order: 4B Instruct,
   Qwen3 8B, Foundation-Sec 8B. Each answer was captured with its `--verbose` stats block
   ([evidence/](screenshots/evidence/)).
7. **Ground-truth check** of the fake CVE against the CVE List ([screenshot](screenshots/evidence/c3-fake-cve/cve-list-search-no-result.png)).
8. **Scoring** against [`ground-truth.md`](ground-truth.md) using [`scoring-rubric.md`](scoring-rubric.md).

## Challenges and how they were handled

### 1. Settings typed into the chat were sent to the model as a prompt
Pasting `/set parameter ...` lines (with leading spaces) into `ollama run` made Ollama treat them as ordinary text,
so the model "explained" the settings instead of applying them. Seen with Qwen3 4B
([a](screenshots/challenges/03-set-lines-sent-as-prompt-qwen3-4b-a.png),
[b](screenshots/challenges/04-set-lines-sent-as-prompt-qwen3-4b-b.png)) and with the cyber model
([screenshot](screenshots/challenges/05-set-lines-sent-as-prompt-cyber-8b.png)).
**Fix:** type each `/set` line by hand starting at the `/`, press Enter, and wait for the `Set parameter ...` confirmation.

### 2. `qwen3:4b` is a Thinking build; `/set nothink` did not help
`/show info` reported a 262,144-token context and the `thinking` capability
([screenshot](screenshots/challenges/06-show-info-qwen3-4b-thinking-build.png)). The model printed its reasoning
and a `</think>` tag on every answer even after `--think=false` and `/set nothink`
([first try](screenshots/challenges/02-thinking-build-leak-qwen3-4b-first-try.png),
[full output](screenshots/challenges/01-thinking-build-leak-qwen3-4b-full.png)), inflating tokens and time
(475 tokens for an ~85-word answer).
**Fix:** pulled `qwen3:4b-instruct`, which answers directly. The Thinking build is kept out of the results.

### 3. Qwen3 8B does not fit fully on a 6 GB GPU
Default settings loaded 6.0 GB with 30% of the model on the CPU. Flash attention plus a q8 KV cache brought it to 5.7 GB
(27% CPU), and cutting the context to 2048 to 5.5 GB (25% CPU). Further tuning would not have closed the gap, so the
8B was benchmarked as it is, with the same `num_ctx 4096` as the other models
([default](screenshots/gpu-offload/02-ps-qwen3-8b-default-30-70.png),
[tuned](screenshots/gpu-offload/03-ps-qwen3-8b-tuned-27-73.png),
[ctx 2048](screenshots/gpu-offload/04-ps-qwen3-8b-ctx2048-25-75.png)).

### 4. The cyber model ships with a system prompt and prints its reasoning
`/show info` shows a built-in system prompt asking for `<think>` sections
([screenshot](screenshots/setup/07-show-info-cyber-8b.png)). The model has no thinking capability flag, so Ollama
cannot separate the reasoning and prints it inline. Two things were tried:
- Overriding the system prompt with `You are a helpful assistant.` for the whole benchmark (reasoning still appeared on 9 of 9 finished prompts).
- A stricter prompt, `Answer directly. Never write <think> tags or show your reasoning.`, on C1 only: the reasoning stayed and stray
  `</think>` and `</assistant>` tags appeared
  ([screenshot](screenshots/challenges/07-cyber-8b-system-prompt-experiment-c1.png)).
Because the behaviour appears to come from the weights, the whole output was read and the **final answer** was scored,
with the leak recorded in [`results/leak-ledger.csv`](results/leak-ledger.csv).

### 5. P3 on the cyber model never finished
The model kept re-drafting the same SPL line ("Wait, but that gives...") and never closed its reasoning; the run was
stopped with `Ctrl+C` after several screens of repetition
([start](screenshots/evidence/p3-splunk-spl/cyber-8b-1.png), [repeating](screenshots/evidence/p3-splunk-spl/cyber-8b-3.png)).
No stats block is printed when a run is interrupted, so P3 has no speed record and scores 0.

### 6. The first source for "this CVE does not exist" was not good enough
A Google AI summary said the ID is a placeholder. That is a secondary, AI-generated source, so it was **not** used.
The CVE List search was used instead ([screenshot](screenshots/evidence/c3-fake-cve/cve-list-search-no-result.png)).

## Small things worth remembering

- `ollama run` timing: use the `eval rate`; the `prompt eval rate` is distorted by prompt caching.
- Multi-line prompts need `"""` wrapping in the terminal.
- Windows Terminal shows the Windows username in the prompt; it is blurred in every screenshot here.
- Qwen3 printed raw LaTeX (`$$ \frac{...} $$`) for the maths prompt, which is unreadable in a terminal.
