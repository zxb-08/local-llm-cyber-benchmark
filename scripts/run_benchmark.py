#!/usr/bin/env python3
"""Run the prompt set against local Ollama models and save raw outputs plus timing.

The published numbers in this repo were collected by hand in the terminal
(`ollama run <model> --verbose`). This script automates the same procedure so
you can re-run or extend it. It uses only the standard library.

Examples
    python scripts/run_benchmark.py                          # all models, 1 run per prompt
    python scripts/run_benchmark.py --runs 3 --models qwen3:8b
    python scripts/run_benchmark.py --host http://localhost:11434 --out results/raw

Per model settings mirror the manual runs (see report.md, section 2.4).
Output: <out>/<model>/<prompt-id>.run<k>.json and <out>/summary.csv
"""
import argparse
import csv
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# model tag -> extra request fields used in the published runs
MODELS = {
    "qwen3:4b-instruct": {},
    "qwen3:8b": {"think": False},  # hybrid model: /set nothink
    "huihui_ai/foundation-sec-abliterated:8b-Q4_K_M": {
        "system": "You are a helpful assistant."  # overrides the build's baked-in system prompt
    },
}
THINK_RE = re.compile(r"<think>.*?</think>", re.S)


def chat(host, model, prompt, extra, num_ctx, temperature, timeout):
    messages = []
    if "system" in extra:
        messages.append({"role": "system", "content": extra["system"]})
    messages.append({"role": "user", "content": prompt})
    body = {
        "model": model,
        "stream": False,
        "messages": messages,
        "options": {"num_ctx": num_ctx, "temperature": temperature},
    }
    if "think" in extra:
        body["think"] = extra["think"]
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    data["_wall_s"] = time.time() - t0
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--models", nargs="*", default=list(MODELS))
    ap.add_argument("--prompts", default=str(ROOT / "prompts" / "prompts.json"))
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--num-ctx", type=int, default=4096)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=300, help="seconds per request (guards against reasoning loops)")
    ap.add_argument("--out", default=str(ROOT / "results" / "raw"))
    args = ap.parse_args()

    prompts = json.loads(Path(args.prompts).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in args.models:
        extra = MODELS.get(model, {})
        mdir = out / model.replace("/", "_").replace(":", "_")
        mdir.mkdir(exist_ok=True)
        for p in prompts:
            for k in range(1, args.runs + 1):
                try:
                    d = chat(args.host, model, p["prompt"], extra, args.num_ctx, args.temperature, args.timeout)
                except Exception as e:  # timeouts, HTTP errors
                    print(f"{model} {p['id']} run{k}: FAILED ({e})")
                    rows.append([model, p["id"], k, "", "", "", "", "failed"])
                    continue
                raw = d.get("message", {}).get("content", "")
                final = THINK_RE.sub("", raw).strip()
                leak = "</think>" in raw or "<think>" in raw
                ev_n, ev_ns = d.get("eval_count", 0), d.get("eval_duration", 0)
                rate = ev_n / (ev_ns / 1e9) if ev_ns else 0.0
                total_s = d.get("total_duration", 0) / 1e9
                rec = {"model": model, "prompt_id": p["id"], "run": k, "raw_output": raw,
                       "final_answer": final, "think_leak": leak, "eval_count": ev_n,
                       "eval_rate_tok_s": round(rate, 2), "total_duration_s": round(total_s, 2),
                       "options": {"num_ctx": args.num_ctx, "temperature": args.temperature}, "extra": extra}
                (mdir / f"{p['id']}.run{k}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
                rows.append([model, p["id"], k, round(rate, 2), ev_n, round(total_s, 2), leak, "ok"])
                print(f"{model:50s} {p['id']} run{k}: {rate:5.1f} tok/s, {ev_n:5d} tok, {total_s:6.1f}s, leak={leak}")
    with open(out / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["model", "prompt", "run", "eval_rate_tok_s", "eval_count", "total_duration_s", "think_leak", "status"])
        w.writerows(rows)
    print("wrote", out / "summary.csv")


if __name__ == "__main__":
    main()
