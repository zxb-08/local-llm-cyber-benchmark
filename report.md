# Local LLMs for Cybersecurity on Consumer Hardware: A Benchmark on an RTX 4050 (6 GB)

**Author:** Syed Zabiullah Rehan Mehdi ([@zxb-08](https://github.com/zxb-08)) · **Date of testing:** 25 October 2026

## Abstract

Running a language model locally avoids cloud token limits and keeps logs on the machine, but a 6 GB laptop GPU limits what is practical. This report compares three local models served by Ollama on an RTX 4050 Laptop GPU (6 GB): **Qwen3 4B Instruct**, **Qwen3 8B**, and a community build of the security-tuned **Foundation-Sec 8B**. Each model answered ten prompts (three general, four cyber knowledge, three SOC-style practical tasks) once, in a fresh context, with `num_ctx` 4096 and temperature 0.2. Answers were scored 0-5 against a pre-written ground truth, and speed was read from Ollama's `eval rate`. Qwen3 8B scored highest (3.3/5) but ran partly on the CPU at 17.0 tok/s. Qwen3 4B Instruct scored 2.8/5 at 56.8 tok/s, fully on the GPU. The security-tuned build scored 1.2/5: it mapped MITRE ATT&CK techniques best but fabricated a CVSS score for a non-existent CVE, invented log details and printed its reasoning on every finished prompt. No model produced a working Splunk query. Results come from single runs scored by one non-blind rater and should be read as a careful first pass.

## 1. Introduction

### 1.1 Problem
Cloud assistants have token and rate limits and require sending data off the machine. For security work (reading logs, explaining events, drafting detections) a local model is attractive, but the hardware here is a laptop with 6 GB of VRAM. It is not obvious which local model is both fast enough to use interactively and good enough to trust, or whether a security-tuned model is worth the trouble.

### 1.2 Goal and questions
Find a local model that responds quickly with decent output quality for cybersecurity questions and log reading, and document the evidence. Questions:

1. **Fit and speed:** which models fit in 6 GB of VRAM, and how fast are they?
2. **Quality:** how do general models compare on general, cyber knowledge and practical tasks?
3. **Specialisation:** does a security-tuned model beat a general model of the same size on security tasks?
4. **Reliability:** do the models invent facts when they should say they do not know?

### 1.3 Scope
Three models, ten prompts, one machine, one run per prompt. The study is deliberately small and hands-on; it is a practical comparison, not a validated benchmark.

## 2. Methodology

### 2.1 Approach
Every model received the same ten prompts under the same sampling settings. Outputs were captured as screenshots (with Ollama's timing block), scored against a written ground truth, and aggregated into tables and charts. The terminal was used rather than a GUI so that the commands are reproducible and no UI variables affect timing.

### 2.2 Environment

| Item | Value |
|---|---|
| Laptop | ASUS Vivobook (V16), Windows 11, 16 GB RAM |
| GPU | NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB VRAM (about 290-390 MiB in use when idle) |
| Driver / CUDA | 610.74 / 13.3 (`nvidia-smi`) |
| Runtime | Ollama 0.40.11 (llama.cpp runner) |
| Env vars | `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_KEEP_ALIVE=30m`, `OLLAMA_KV_CACHE_TYPE=q8_0` (the last added after the first 8B test) |

Details: [`results/environment.txt`](results/environment.txt); evidence: [GPU baseline](screenshots/setup/02-nvidia-smi-baseline.png), [version check](screenshots/setup/01-ollama-version-and-gpu.png).

### 2.3 Models

| Model | Tag | Size on disk | Notes |
|---|---|---|---|
| Qwen3 4B Instruct | `qwen3:4b-instruct` | 2.5 GB | 4.0B, Q4_K_M, non-thinking instruct build |
| Qwen3 8B | `qwen3:8b` | 5.2 GB | 8.2B, Q4_K_M, hybrid model; run with `/set nothink` |
| Foundation-Sec 8B | `huihui_ai/foundation-sec-abliterated:8b-Q4_K_M` | 4.9 GB | 8.0B Llama architecture, Q4_K_M; **community "abliterated" variant** of Cisco's Foundation-Sec-8B, a security-tuned *base* model. Ships with a system prompt asking for `<think>` sections |

`qwen3:4b` (2.5 GB) was pulled first but is a Thinking build, so it was dropped from the benchmark (see [notes](notes.md#2-qwen34b-is-a-thinking-build-set-nothink-did-not-help)). Setup captures: [4B Instruct](screenshots/setup/05-show-info-qwen3-4b-instruct.png), [8B](screenshots/setup/06-show-info-qwen3-8b.png), [Foundation-Sec](screenshots/setup/07-show-info-cyber-8b.png).

### 2.4 Runtime settings

| Setting | Qwen3 4B Instruct | Qwen3 8B | Foundation-Sec 8B |
|---|---|---|---|
| `num_ctx` | 4096 | 4096 | 4096 |
| `temperature` | 0.2 | 0.2 | 0.2 |
| Thinking | none (instruct build) | off (`/set nothink`) | not supported; reasoning printed inline |
| System prompt | model default | model default | `You are a helpful assistant.` (overrides the built-in prompt) |
| Context between prompts | `/clear` | `/clear` | `/clear` |

Session parameters override the model defaults shown by `/show info` (for example the 4B Instruct default temperature of 0.7 and the 8B's 0.6).

### 2.5 Prompts
Ten prompts in three groups ([`prompts/prompts.md`](prompts/prompts.md)). Multi-line prompts were sent wrapped in `"""`.

| Group | IDs | Purpose |
|---|---|---|
| General | G1-G3 | Check basic quality and instruction following without security content |
| Cyber knowledge | C1-C4 | Windows events, ATT&CK, a **non-existent CVE** (hallucination test), phishing triage |
| Practical | P1-P3 | Read logs and write a detection as an analyst would |

### 2.6 Metrics and scoring
- **Speed:** `eval rate` (generation tokens/s), `eval count` (tokens) and `total duration` from `ollama run --verbose`. Prompt-eval rate is ignored because prompt caching distorts it.
- **Fit:** loaded size and CPU/GPU split from `ollama ps`.
- **Quality:** a 0-5 headline score per prompt against [`ground-truth.md`](ground-truth.md), using [`scoring-rubric.md`](scoring-rubric.md). Sub-scores (correctness, completeness, instruction following, hallucination) were recorded for most cyber and practical prompts.
- **Reasoning leak:** `</think>` text visible in the output. The **whole output is read but the final answer carries the weight**; the leak is logged separately.

### 2.7 Procedure
1. Reset: remove old models, check GPU and versions.
2. Set the speed environment variables and restart Ollama.
3. Pull the models and confirm tags with `ollama list`.
4. For each model, in order 4B Instruct, Qwen3 8B, Foundation-Sec 8B: start `ollama run <tag> --verbose`, type the `/set` lines by hand, check `/show info` and `ollama ps`, then send G1-P3 with `/clear` between prompts and screenshot each answer with its stats block.
5. Check the fake CVE in the CVE List search.
6. Score, aggregate (`results/*.csv`) and draw charts (`scripts/make_charts.py`).

### 2.8 Deviations from the original plan
- The plan included three runs per prompt and a script. Time went into the manual runs, so there is **one run per prompt**; [`scripts/run_benchmark.py`](scripts/run_benchmark.py) was written afterwards and tested only against a mock server.
- The first 4B model was a Thinking build and was replaced by the Instruct build.
- Two ground-truth items were refined after seeing outputs: T1078 was accepted as an extra valid technique for C2, and a reference SPL query was added for P3.
- The cyber model's built-in system prompt was overridden for fairness; a stricter override was tried on C1 only.
- The cyber model's P3 run never finished and was stopped by hand.

## 3. Results

### 3.1 GPU fit

![GPU offload](charts/05-gpu-offload.png)

| Model | Setting | Loaded | GPU / CPU | Evidence |
|---|---|---|---|---|
| Qwen3 4B Instruct | default | 2.9 GB | 100% / 0% | [ps](screenshots/gpu-offload/01-ps-qwen3-4b-instruct-100pct-gpu.png) |
| Qwen3 8B | default, ctx 4096 | 6.0 GB | 70% / 30% | [ps](screenshots/gpu-offload/02-ps-qwen3-8b-default-30-70.png) |
| Qwen3 8B | flash attention + q8 KV cache, ctx 4096 | 5.7 GB | 73% / 27% | [ps](screenshots/gpu-offload/03-ps-qwen3-8b-tuned-27-73.png) |
| Qwen3 8B | same, ctx 2048 | 5.5 GB | 75% / 25% | [ps](screenshots/gpu-offload/04-ps-qwen3-8b-ctx2048-25-75.png) |
| Foundation-Sec 8B | default, ctx 4096 | 5.4 GB | 78% / 22% | [ps](screenshots/gpu-offload/05-ps-cyber-8b-22-78.png) |

Only the 4B model fits. Tuning moved the 8B only slightly (the 2048-context re-run of G1 gave 18.56 tok/s against 16.24 before tuning, see [capture](screenshots/challenges/08-qwen3-8b-g1-ctx2048-speed.png)), so the 8B was benchmarked at the same 4096 context as the others.

### 3.2 Speed

![Generation speed](charts/01-speed.png)

Mean generation speed over the prompts that finished: **56.8 tok/s** (4B Instruct), **17.0 tok/s** (Qwen3 8B), **20.4 tok/s** (Foundation-Sec, 9 prompts). The 4B is 3.3× faster than Qwen3 8B and 2.8× faster than Foundation-Sec. Each model's speed was steady across prompts (4B: 55.1-58.1, 8B: 15.9-17.9, cyber: 18.8-21.3 tok/s).

Time to a finished answer depends on both speed and verbosity:

![Time to a complete answer](charts/06-response-time.png)

Total time over the prompts: 4B Instruct 124 s, Qwen3 8B 340 s, Foundation-Sec 185 s (9 prompts). Per-prompt values:

| Prompt | Qwen3 4B Instruct | Qwen3 8B | Foundation-Sec 8B |
|---|---|---|---|
| G1 | 56.2 tok/s · 93 tok · 2.0 s | 16.2 tok/s · 89 tok · 6.2 s | 18.8 tok/s · 550 tok · 29.9 s |
| G2 | 58.1 tok/s · 300 tok · 5.6 s | 17.4 tok/s · 279 tok · 16.7 s | 21.3 tok/s · 257 tok · 12.4 s |
| G3 | 57.0 tok/s · 53 tok · 1.3 s | 17.9 tok/s · 60 tok · 3.8 s | 21.1 tok/s · 342 tok · 16.6 s |
| C1 | 55.1 tok/s · 1837 tok · 33.7 s | 16.6 tok/s · 1322 tok · 80.3 s | 20.9 tok/s · 613 tok · 29.8 s |
| C2 | 57.4 tok/s · 544 tok · 10.0 s | 17.4 tok/s · 312 tok · 18.3 s | 21.0 tok/s · 457 tok · 22.1 s |
| C3 | 57.8 tok/s · 403 tok · 7.4 s | 17.2 tok/s · 635 tok · 37.2 s | 21.1 tok/s · 364 tok · 17.9 s |
| C4 | 57.4 tok/s · 733 tok · 13.2 s | 16.9 tok/s · 789 tok · 47.2 s | 19.5 tok/s · 547 tok · 28.5 s |
| P1 | 56.1 tok/s · 1217 tok · 22.1 s | 15.8 tok/s · 1211 tok · 77.0 s | 20.9 tok/s · 290 tok · 14.4 s |
| P2 | 55.4 tok/s · 553 tok · 10.4 s | 17.1 tok/s · 444 tok · 26.7 s | 19.0 tok/s · 239 tok · 13.1 s |
| P3 | 57.4 tok/s · 1044 tok · 18.6 s | 17.5 tok/s · 463 tok · 27.0 s | did not finish |

*Foundation-Sec times include its printed reasoning. G1 for Qwen3 8B was measured before the flash-attention and KV-cache variables were active and while other models were downloading in the background; the later prompts ran on an idle machine.*

### 3.3 Quality overall

![Score by prompt](charts/02-score-heatmap.png)

| Prompt | Qwen3 4B Instruct | Qwen3 8B | Foundation-Sec 8B |
|---|---|---|---|
| G1 | 3 | 4 | 2 |
| G2 | 1 | 5 | 0 |
| G3 | 4 | 3 | 1 |
| C1 | 2 | 3 | 1 |
| C2 | 1 | 3 | 4 |
| C3 | 4 | 2 | 0 |
| C4 | 4 | 4 | 3 |
| P1 | 3 | 3 | 0 |
| P2 | 4 | 4 | 1 |
| P3 | 2 | 2 | 0 |
| **Average** | **2.8** | **3.3** | **1.2** |

![Average score by category](charts/03-category-scores.png)

| Category | Qwen3 4B Instruct | Qwen3 8B | Foundation-Sec 8B |
|---|---|---|---|
| General (G1-G3) | 2.7 | **4.0** | 1.0 |
| Cyber knowledge (C1-C4) | 2.8 | **3.0** | 2.0 |
| Practical (P1-P3) | **3.0** | **3.0** | 0.3 |

![Quality vs speed](charts/04-quality-vs-speed.png)

### 3.4 Prompt by prompt

#### G1 · Explain a fridge
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 3 | About 75 words, kid-level tone, but skips the compressor and says the liquid "gets hot" and turns into gas, which reverses the cause | [shot](screenshots/evidence/g1-explain/qwen3-4b-instruct.png) |
| Qwen3 8B | 4 | Correct cycle (coolant absorbs heat, compression, heat released outside) within the limit; run 1 has no analogy. A second run at ctx 2048 used a "mini freezer" analogy and the brand name "freon" | [shot](screenshots/evidence/g1-explain/qwen3-8b.png) |
| Foundation-Sec | 2 | About 130 words (limit 100), a numbered parts list, "an engine with belts and pulleys" in the compressor | [shot](screenshots/evidence/g1-explain/cyber-8b.png) |

#### G2 · Train arrival time (correct: 11:45 AM)
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 1 | Method right (2.5 h = 2 h 30 min) but adds 30 minutes to 11:15 and answers **12:45 PM**; prints raw LaTeX | [shot](screenshots/evidence/g2-arithmetic/qwen3-4b-instruct-2.png) |
| Qwen3 8B | 5 | Correct, clear steps, **11:45 AM** | [shot](screenshots/evidence/g2-arithmetic/qwen3-8b-1.png) |
| Foundation-Sec | 0 | Computes 9.15 + 2.5 = 11.65 (decimal time), then answers **~12:00 PM** with no steps in the final answer | [shot](screenshots/evidence/g2-arithmetic/cyber-8b.png) |

#### G3 · 3-sentence email (max 70 words)
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 4 | Exactly 3 sentences, about 33 words; invents names ("Professor Smith", "Alex Johnson") | [shot](screenshots/evidence/g3-constraints/qwen3-4b-instruct.png) |
| Qwen3 8B | 3 | 4 sentences (one too many), about 43 words, adds a subject line | [shot](screenshots/evidence/g3-constraints/qwen3-8b.png) |
| Foundation-Sec | 1 | 7 sentences and about 87 words; "our team/our project" wording; "Your name" placeholder | [shot](screenshots/evidence/g3-constraints/cyber-8b.png) |

#### C1 · Windows Event ID 4625
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 2 | Strong structure and the right investigation ideas (source IP, correlate with 4624, lockout policy), but the logon-type table is wrong (it lists 5 as RDP; RDP is 10) and it calls 4648 an account lockout (that is 4740). 1,837 tokens | [table error](screenshots/evidence/c1-event-4625/qwen3-4b-instruct-2.png) |
| Qwen3 8B | 3 | Logon type 3 = network is right; type 10 is called "Interactive" (it is RemoteInteractive) and 4626 is called a lockout; the sample event pairs a "logon type not granted" reason with a bad-password status code. The PowerShell example was not run and looks invalid. 80 s | [errors](screenshots/evidence/c1-event-4625/qwen3-8b-3.png), [sample log](screenshots/evidence/c1-event-4625/qwen3-8b-2.png) |
| Foundation-Sec | 1 | Never says 4625 is a **failed** logon; treats a burst as a benign loop or scheduled task; calls 4689 "service start" (it is process termination). Re-run with a stricter system prompt scored 0 | [shot](screenshots/evidence/c1-event-4625/cyber-8b.png), [re-run](screenshots/challenges/07-cyber-8b-system-prompt-experiment-c1.png) |

#### C2 · MITRE ATT&CK mapping (expected T1021.001 + T1003.001; T1078 accepted)
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 1 | Answers T1078, T1087, T1548 with wrong names ("Credential Dumping", "Exploitation of RDP", "Credential Access") | [shot](screenshots/evidence/c2-attack-mapping/qwen3-4b-instruct-1.png) |
| Qwen3 8B | 3 | Right families but wrong IDs: T1003.002 (SAM, not LSASS) and "T1021.02" (malformed); T1078 correct; labels T1021 "Execution" | [shot](screenshots/evidence/c2-attack-mapping/qwen3-8b.png) |
| Foundation-Sec | 4 | **T1078, T1021, T1003**: correct IDs and names, parent techniques only, sensible order | [shot](screenshots/evidence/c2-attack-mapping/cyber-8b.png) |

#### C3 · Non-existent CVE
`CVE-2023-98765` returned no results in the CVE List ([search](screenshots/evidence/c3-fake-cve/cve-list-search-no-result.png)).

| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 4 | Says it is not in the official database and invents no details; slightly overconfident ("does not appear in any official list") | [shot](screenshots/evidence/c3-fake-cve/qwen3-4b-instruct.png) |
| Qwen3 8B | 2 | Says it knows no such CVE, then writes a "hypothetical" CVE with a CVSS 9.8 vector, fake product and patch version | [shot](screenshots/evidence/c3-fake-cve/qwen3-8b-1.png) |
| Foundation-Sec | 0 | States "the CVSS score for this CVE is 9.8" as fact | [shot](screenshots/evidence/c3-fake-cve/cyber-8b.png) |

#### C4 · Phishing email
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 4 | Correct verdict, 4 of 5 signs (the password request only in passing); misquotes the Reply-To as `helpdesk884-1@gmail.com`; claims the domain "does not exist" | [shot](screenshots/evidence/c4-phishing/qwen3-4b-instruct-1.png) |
| Qwen3 8B | 4 | All five signs, Reply-To quoted correctly; padded to 10 points including weak ones (grammar, personalisation) | [shot](screenshots/evidence/c4-phishing/qwen3-8b-1.png) |
| Foundation-Sec | 3 | Right verdict, all five signs in a few words each; reads the Reply-To address as the recipient; asserts the link goes to a ".com" site | [shot](screenshots/evidence/c4-phishing/cyber-8b.png) |

#### P1 · Windows log triage (password spray, then success)
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 3 | Right story and blocks the IP, but counts six failures (there are five), calls it brute force/credential stuffing, and only says to "verify if accounts were compromised" | [shot](screenshots/evidence/p1-windows-log/qwen3-4b-instruct-1.png) |
| Qwen3 8B | 3 | Counts five failures correctly and flags the `svc_backup` success, but calls logon type 3 "Interactive", never blocks the IP and hedges on compromise | [shot](screenshots/evidence/p1-windows-log/qwen3-8b-1.png) |
| Foundation-Sec | 0 | Reads it as an automated process "every minute" (events are 2 s apart), misses the failures and the success, gives no actions | [shot](screenshots/evidence/p1-windows-log/cyber-8b.png) |

#### P2 · Linux log triage (brute force, root login, new user)
| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 4 | Correct incident and IP; hedges that the new user may be "legitimate administrative action"; no IP block or session kill | [shot](screenshots/evidence/p2-linux-log/qwen3-4b-instruct-1.png) |
| Qwen3 8B | 4 | Correct incident; calls the new user likely attacker persistence; changes root password and disables root SSH; no IP block | [shot](screenshots/evidence/p2-linux-log/qwen3-8b.png) |
| Foundation-Sec | 1 | Invents `useradd -c 'Support Dept.' support` and "last password change was yesterday"; no brute-force call, no persistence call, no next steps | [shot](screenshots/evidence/p2-linux-log/cyber-8b.png) |

#### P3 · Splunk SPL query
Reference: `index=wineventlog EventCode=4625 earliest=-10m | stats count by Source_Network_Address | where count > 5` (not run in a live Splunk). Syntax was checked by reading, with Splunk's [`streamstats` documentation](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Streamstats) for `window` (events) versus `time_window` (time).

| Model | Score | Observation | Evidence |
|---|---|---|---|
| 4B Instruct | 2 | Invents a `parse` command, quotes `"EventID"` as a string, uses `streamstats window=10m` (`window` takes an event count), splits `source` as if it held the IP; but gives valid alert-setup steps (trigger on results, last 10 minutes) | [first](screenshots/evidence/p3-splunk-spl/qwen3-4b-instruct-1.png), [final](screenshots/evidence/p3-splunk-spl/qwen3-4b-instruct-3.png) |
| Qwen3 8B | 2 | Starts from `inputlookup` (a CSV lookup, not events), uses `timechart ... by` then filters a field that does not exist, invents an `alert` command; only the last example has a valid base search (`EventCode=4625`) | [shot](screenshots/evidence/p3-splunk-spl/qwen3-8b-1.png), [valid base](screenshots/evidence/p3-splunk-spl/qwen3-8b-2.png) |
| Foundation-Sec | 0 | Reasoning loop: repeats the same re-draft paragraph, never closes its reasoning, no query; stopped with Ctrl+C | [start](screenshots/evidence/p3-splunk-spl/cyber-8b-1.png), [repeating](screenshots/evidence/p3-splunk-spl/cyber-8b-3.png) |

### 3.5 Reasoning leak ledger (Foundation-Sec)
The model printed `<think>` reasoning followed by `</think>` and the answer on every prompt that finished, even with the built-in system prompt overridden.

| Prompt | Reasoning text in output | Tokens | Time |
|---|---|---|---|
| G1 | yes | 550 | 29.9 s |
| G2 | yes | 257 | 12.4 s |
| G3 | yes | 342 | 16.6 s |
| C1 | yes | 613 | 29.8 s |
| C2 | yes | 457 | 22.1 s |
| C3 | yes | 364 | 17.9 s |
| C4 | yes | 547 | 28.5 s |
| P1 | yes | 290 | 14.4 s |
| P2 | yes | 239 | 13.1 s |
| P3 | loop |  |  |

Qwen3 4B Instruct and Qwen3 8B (with `nothink`) printed no reasoning text.

### 3.6 Side experiments
- **Thinking build:** `qwen3:4b` ignored `--think=false` and `/set nothink` and printed its reasoning every time ([full output](screenshots/challenges/01-thinking-build-leak-qwen3-4b-full.png), [info](screenshots/challenges/06-show-info-qwen3-4b-thinking-build.png)).
- **Stricter system prompt (C1, Foundation-Sec):** `Answer directly. Never write <think> tags or show your reasoning.` did not remove the reasoning and added stray `</think>` and `</assistant>` tags; the answer scored 0 ([capture](screenshots/challenges/07-cyber-8b-system-prompt-experiment-c1.png)). One run only, so this shows the prompt did not help, not that it made things worse.
- **8B context reduction:** halving the context saved about 0.2 GB and did not achieve a full GPU load.

## 4. Discussion

**Fit decides speed.** The 4B model is fully on the GPU and generates at about 57 tok/s. Both 8B models spill 22-30% to the CPU and run at 16-21 tok/s. That is a threefold speed gap for a roughly twofold size gap, because the slow part of the model sets the pace. On this laptop the practical limit is a model of about 5 GB including its cache.

**Bigger helped, modestly.** Qwen3 8B led by 0.5 points overall (3.3 vs 2.8), mainly on general reasoning (G2 arithmetic) and a bit on cyber knowledge. On the three practical tasks the two tied. With one run per prompt, a 0.5-point gap is suggestive, not conclusive. The 4B also did better on strict formatting (G3).

**The security-tuned build did not help, except on ATT&CK IDs.** It had the best ATT&CK mapping and, on a good day, a terse phishing analysis, but it scored lowest on everything else. Plausible contributors, none of them tested here: the model is a security-tuned *base* model rather than an instruct model; the community build was modified ("abliterated") and ships a prompt forcing `<think>` sections; and the 4-bit quantisation. The result applies to this build, not to Cisco's official model or to security-tuned models in general.

**Where models fail is predictable.** Errors were mostly confident, specific, plausible details: logon-type numbers, event IDs, ATT&CK sub-technique IDs, SPL command names. Prose structure was usually fine. These are exactly the details an analyst would copy into a ticket or a query, so they need checking against primary sources.

**Hallucination pattern.** On the fake CVE only the 4B Instruct declined to elaborate. The larger or specialised models filled the gap (Qwen3 8B labelled its invention "hypothetical"; Foundation-Sec did not). A disclaimer does not make a fabricated CVSS vector safe to paste into a report.

**Practical recommendation for this laptop.** Use Qwen3 4B Instruct as the everyday model for quick questions and for summarising or explaining logs, and keep Qwen3 8B for tasks that need more careful reasoning when waiting 1-1.5 minutes is acceptable. Treat all output as a draft: verify IDs, syntax and counts.

## 5. Limitations

1. **One run per prompt** at temperature 0.2. Repeat runs vary (Qwen3 8B's two G1 runs differed), so small score or speed differences are not significant.
2. **Single, non-blind rater.** Scores were assigned by one rater, an AI assistant, reading the screenshots against the ground truth with model names visible. A blind, multi-rater re-score was planned and not done.
3. **Small prompt set.** Ten English prompts; three practical tasks. Coverage of security tasks is thin.
4. **Ground truth refined after seeing outputs** in two places (T1078 accepted for C2; reference SPL added for P3). Facts were not all verified against primary sources in this repo; see the references and re-check before reuse. The reference SPL was not run in Splunk, and P3 syntax judgements are by reading.
5. **Different reasoning behaviour across models** (no thinking, thinking off, leaked reasoning) means the comparison is of "as it runs under Ollama" behaviour, not of identical conditions. The cyber model's times include its reasoning tokens.
6. **One community build** stands in for "the security model"; results do not transfer to Cisco's official release or other quantisations.
7. **Measurement conditions.** Qwen3 8B's first G1 run was measured before the speed settings were active and while downloads were running; later runs were not. Speed in the offload chart compares single runs on different prompts.
8. **P3 on Foundation-Sec has no speed record** because the run was interrupted.
9. **One machine and one Ollama version.** Results depend on the GPU, driver and Ollama build.
10. **Screenshot edits.** The Windows username in the prompt is blurred and a few pixels of clipped text at image edges were trimmed. Nothing else was altered.

## 6. Future work

- Repeat each prompt 3-5 times (use `scripts/run_benchmark.py`) and report mean and spread.
- Blind, multi-rater scoring, with answers shuffled and model names removed.
- Test an official instruct build of Foundation-Sec and other security-tuned models, and a different quantisation of the 8B that fits fully in 6 GB.
- Add retrieval: give the model the relevant Microsoft or ATT&CK page and see whether the factual errors disappear.
- Add longer log-reading tasks that stress the context window, and run the Splunk and Sigma outputs against a real instance.
- Add a GUI (Open WebUI or LM Studio) for daily use, and compare runtimes on the same model.

## 7. Conclusion

- A 6 GB laptop GPU runs a 4B model fast and fully on the GPU; 8B models run, but partly on the CPU and about three times slower.
- On this prompt set Qwen3 8B was the most accurate (3.3/5), Qwen3 4B Instruct the best trade-off (2.8/5 at 56.8 tok/s), and the security-tuned community build the weakest (1.2/5).
- All models made confident technical errors, and none could write a working Splunk query, so local models here are drafting aids, not sources of truth.
- Hallucination checks (a fake CVE) and reading the whole output, not just the answer, exposed problems that a speed test would never show.

## References

1. Ollama. https://ollama.com and API reference https://github.com/ollama/ollama/blob/main/docs/api.md
2. llama.cpp. https://github.com/ggml-org/llama.cpp
3. Qwen3 models on Ollama. https://ollama.com/library/qwen3
4. Cisco Foundation AI, *Foundation-Sec-8B*: https://huggingface.co/fdtn-ai/Foundation-Sec-8B ; announcement https://blogs.cisco.com/security/foundation-sec-cisco-foundation-ai-first-open-source-security-model ; paper https://arxiv.org/abs/2504.21039
5. Community build used here: https://ollama.com/huihui_ai/foundation-sec-abliterated
6. Microsoft Learn, *4625(F): An account failed to log on*. https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625
7. Microsoft Learn, *4624(S): An account was successfully logged on* (logon types). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4624
8. MITRE ATT&CK: [T1003.001 LSASS Memory](https://attack.mitre.org/techniques/T1003/001/), [T1021.001 Remote Desktop Protocol](https://attack.mitre.org/techniques/T1021/001/), [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/), [T1003.002 Security Account Manager](https://attack.mitre.org/techniques/T1003/002/)
9. Splunk, `streamstats` command reference. https://docs.splunk.com/Documentation/Splunk/latest/SearchReference/Streamstats
10. CVE List search. https://www.cve.org/ ; National Vulnerability Database https://nvd.nist.gov/

## Appendix A: scores and verdicts

| Prompt | Model | Score | Verdict |
|---|---|---|---|
| G1 | Qwen3 4B Instruct | 3 | Under the limit and kid-friendly but skips the compressor and gets the evaporation cause backwards |
| G1 | Qwen3 8B | 4 | Correct mechanism within the limit; no kid-level analogy in run 1 |
| G1 | Foundation-Sec 8B | 2 | ~130 words (limit 100); parts list rather than a kid-level explanation; belts-and-pulleys error |
| G2 | Qwen3 4B Instruct | 1 | Right method; final answer 12:45 PM is wrong (correct 11:45 AM) |
| G2 | Qwen3 8B | 5 | Correct: 11:45 AM with clear steps |
| G2 | Foundation-Sec 8B | 0 | Decimal-time error; final answer ~12:00 PM; no steps in the final answer |
| G3 | Qwen3 4B Instruct | 4 | Exactly 3 sentences and ~33 words; invented names |
| G3 | Qwen3 8B | 3 | 4 sentences instead of 3; under the word limit; added a subject line |
| G3 | Foundation-Sec 8B | 1 | 7 sentences and ~87 words against 3 and 70 |
| C1 | Qwen3 4B Instruct | 2 | Good structure; wrong logon types and wrong event for lockout (4648) |
| C1 | Qwen3 8B | 3 | Logon type 3 right; type 10 and 4626 wrong; inconsistent sample log |
| C1 | Foundation-Sec 8B | 1 | Never says 4625 is a failed logon; treats a burst as a benign loop |
| C2 | Qwen3 4B Instruct | 1 | Wrong IDs (T1078/T1087/T1548) and wrong technique names |
| C2 | Qwen3 8B | 3 | Right families; wrong sub-technique IDs (T1003.002 and T1021.02) |
| C2 | Foundation-Sec 8B | 4 | Correct parent technique IDs and names (T1078 T1021 T1003) |
| C3 | Qwen3 4B Instruct | 4 | Declined to invent details for the unpublished CVE |
| C3 | Qwen3 8B | 2 | Said unknown then wrote a labelled-hypothetical CVE with CVSS 9.8 |
| C3 | Foundation-Sec 8B | 0 | Stated CVSS 9.8 as fact for an unpublished CVE |
| C4 | Qwen3 4B Instruct | 4 | 4 of 5 signs; misquoted the Reply-To address |
| C4 | Qwen3 8B | 4 | All 5 signs; padded with weak points |
| C4 | Foundation-Sec 8B | 3 | Right verdict; terse; read Reply-To as the recipient |
| P1 | Qwen3 4B Instruct | 3 | Right story; miscounted failures (6 vs 5); called it brute force not spray; blocks the IP |
| P1 | Qwen3 8B | 3 | Counted 5 failures correctly; logon type 3 mislabelled; no IP block; hedged on compromise |
| P1 | Foundation-Sec 8B | 0 | Read a spray plus a successful logon as an automated loop; no actions |
| P2 | Qwen3 4B Instruct | 4 | Correct incident; hedged on persistence; no IP block or session kill |
| P2 | Qwen3 8B | 4 | Called the new user persistence; no IP block |
| P2 | Foundation-Sec 8B | 1 | Invented a useradd command and a password change yesterday; no next steps |
| P3 | Qwen3 4B Instruct | 2 | Invented parse command; streamstats window misuse; valid alert setup steps |
| P3 | Qwen3 8B | 2 | Last example has a valid base search; aggregation broken; invented alert command |
| P3 | Foundation-Sec 8B | 0 | Reasoning loop; no query produced |

## Appendix B: data files

| File | Contents |
|---|---|
| [`results/scores.csv`](results/scores.csv) | Headline score, sub-scores and verdict per prompt and model |
| [`results/speed.csv`](results/speed.csv) | `eval rate`, tokens and total duration per prompt and model |
| [`results/offload.csv`](results/offload.csv) | `ollama ps` loaded size and CPU/GPU split |
| [`results/leak-ledger.csv`](results/leak-ledger.csv) | Reasoning-leak record for the Foundation-Sec build |
| [`results/environment.txt`](results/environment.txt) | Hardware, versions, variables, tags and commands |
