# Blind LLM Vulnerability Detection on SecVulEval (Linux Kernel)

EECS4080 project, York University, Fall 2026. Supervisor: Prof. Song Wang.
Project: *Enhancing LLM Vulnerability Detection Skills via Adversarial Testing and Reinforcement Learning*.

This repository contains the baseline experiment: a blind, function-level test of how well an LLM
(Claude Opus 5.5, through Claude Code) detects real Linux kernel vulnerabilities, following the setup
of Experiment 1 in the [SecVulEval paper](https://arxiv.org/abs/2505.19828).

## Results (function level)

The test set has 241 functions from the 100 newest Linux kernel CVEs in
[SecVulEval](https://huggingface.co/datasets/arag0rn/SecVulEval): 123 vulnerable functions and 118 fixed versions.

|                    | Model says vulnerable | Model says not vulnerable |
|--------------------|-----------------------|---------------------------|
| Vulnerable (123)   | 91 (TP)               | 32 (FN)                   |
| Fixed (118)        | 34 (FP)               | 84 (TN)                   |

| Model                         | Precision | Recall | F1     |
|-------------------------------|-----------|--------|--------|
| Claude-3.7-Sonnet (paper)     | 41.86%    | 75.63% | 53.89% |
| GPT-4.1 (paper)               | 40.65%    | 73.11% | 52.25% |
| Claude Opus 5.5 (this study)  | 72.80%    | 73.98% | 73.39% |

The setups differ (model, a single call instead of the paper's multi-agent pipeline, Linux-only data),
and the model may have seen these 2024 fixes during training, so the numbers are not a direct
head-to-head comparison. For the 118 functions that have both versions, the model told the vulnerable
and the fixed version apart correctly in 57 pairs (48%).

## How it works

1. `my-project/collect_data.py` downloads SecVulEval, keeps Linux kernel functions, takes the 100 newest
   CVEs by CVE ID (CVE-2024-45025 to CVE-2024-49859) and saves the vulnerable code, the fixed code and the
   lines changed by the patch.
2. `my-project/make_samples.py` writes every vulnerable and fixed function to its own file
   (`blind-run/samples/s001.c` to `s241.c`) in a shuffled order (random seed 4080). The files contain code
   only; the answer key is `my-project/blind_key.csv`.
3. `blind-run/run_blind.sh` runs one fresh, non-interactive Claude Code session per sample, using the CLI
   script of the find-vulnerabilities skill (`blind-run/.claude/skills/find-vulnerabilities/`). The prompt
   was changed to a defensive code review that answers in JSON: `is_vulnerable`, `cwe`,
   `vulnerable_statements` (statement + reason) and `suggested_fix`.
4. `my-project/score.py` compares `is_vulnerable` with the answer key and computes precision, recall and F1.

## Repository layout

```
my-project/
  collect_data.py                          data collection
  make_samples.py                          blind samples + answer key
  score.py                                 function-level scoring
  secvuleval_linux_newest100.csv           one row per vulnerable function (code, fixed code, changed lines)
  secvuleval_linux_newest100_by_cve.csv    one row per CVE
  blind_key.csv                            answer key: sample -> label, CVE, CWE, function
  function_level_results.csv               prediction for every sample
  exploration/                             first scripts used to explore the dataset
blind-run/
  samples/                                 the 241 blind samples
  results/                                 the model's answers (.json), run logs and raw session logs
  run_blind.sh                             batch runner
  .claude/skills/find-vulnerabilities/     detection script (modified prompt, fixed model)
```

## Reproduce

Requirements: Python 3, the [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) CLI, and `jq`.

```bash
cd my-project
python3 -m pip install -r requirements.txt
python3 collect_data.py
python3 make_samples.py

cd ../blind-run
caffeinate -i bash run_blind.sh      # macOS; on Linux run: bash run_blind.sh

cd ../my-project
python3 score.py
```

`run_blind.sh` skips samples that already have a result, so it can be restarted after an interruption.

## Experiment settings

| Setting     | Value |
|-------------|-------|
| Model       | `claude-opus-5-5`, fixed with `--model`; recorded in each sample's `.stream.jsonl` |
| Tool        | Claude Code 2.1.319 (`blind-run/results/run_info.txt`) |
| Runs        | One run per sample (pass@1), 241 runs on 2026-11-19 |
| Temperature | Not configurable in Claude Code (the paper used 0.1) |
| Context     | The function only; commit messages and the dataset's `context` field are not given to the model |

## Limitations

- The model was released after these CVEs were fixed, so it may have seen the patches during training.
- One model call per function, without the paper's multi-agent pipeline or extracted context.
- 100 Linux CVEs from 2024; 52 of them are CWE-476 (NULL pointer dereference).
- A "fixed" function can still contain a different bug, so some false positives may be real issues.
- Statement-level results (whether the flagged lines and reasons are correct) are not scored automatically.

## References

- Ahmed et al., *SecVulEval: Benchmarking LLMs for Real-World C/C++ Vulnerability Detection*, 2025.
  [arXiv:2505.19828](https://arxiv.org/abs/2505.19828)
- SecVulEval dataset (MIT license): [huggingface.co/datasets/arag0rn/SecVulEval](https://huggingface.co/datasets/arag0rn/SecVulEval)
