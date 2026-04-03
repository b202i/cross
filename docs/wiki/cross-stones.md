# Cross-Stones Benchmark

Cross-Stones measures AI accuracy and speed across a fixed set of research domains. Run the same benchmark today, in six months, and in two years — the scores are directly comparable because the prompts, claim count, and scoring formula never change.

The name comes from curling: each AI gets one throw at the same target. The cross-product design means every AI also evaluates every other AI's throw.

---

## Quick start

```bash
# Run the full benchmark for one domain (generates + fact-checks all AIs)
st-cross cross_stones/domains/healthcare_medical.json

# Score all 10 domains in the standard set
st-stones cross_stones/cross-stones-10.json

# Run any missing domains, then score
st-stones --run cross_stones/cross-stones-10.json

# After your first complete run — lock timing as the speed baseline (do once)
st-stones --set-baseline cross_stones/cross-stones-10.json

# Save this run as a named snapshot
st-stones --record-snapshot --snapshot-label "2026-Q1" cross_stones/cross-stones-10.json

# View score history over time
st-stones --history cross_stones/cross-stones-10.json
```

---

## How it works

1. **Every AI generates a report** for the same domain prompt — 5 AIs × 10 domains = 50 reports.
2. **Every AI fact-checks every report** — 5×5 per domain = 250 fact-check operations across the full set.
3. **Scores are aggregated** per AI across domains into the final `cross_stone_score`.

The cross-product design reveals things a single-evaluator test cannot:

| Pattern | What it reveals |
|---------|----------------|
| High self-score, low peer scores | AI is lenient with its own claims |
| Consistent row scores | Stable fact-checking style regardless of author |
| Diagonal vs off-diagonal gap | Degree of self-serving bias |

---

## The 10 standard domains

| # | Domain | File |
|---|--------|------|
| 1 | Software Development & Programming | `software_development.prompt` |
| 2 | Customer Service & Support | `customer_service.prompt` |
| 3 | Marketing & Content Creation | `marketing_content.prompt` |
| 4 | Education & Learning | `education_learning.prompt` |
| 5 | Data Analytics & Business Intelligence | `data_analytics.prompt` |
| 6 | Healthcare & Medical Analysis | `healthcare_medical.prompt` |
| 7 | Finance & Business Decision Making | `finance_business.prompt` |
| 8 | Writing, Editing & Summarizing | `writing_editing.prompt` |
| 9 | Research, Search & Q&A | `research_qa.prompt` |
| 10 | Creative Media (Images, Video, Audio) | `creative_media.prompt` |

Each prompt asks the AI for **exactly 10 specific, fact-checkable claims** at calibrated difficulty — roughly half verifiable with basic research, half requiring primary sources. Prompts are intentionally neutral across provider strengths.

---

## Scoring

### Claim-level verdicts

| Verdict | Points |
|---------|--------|
| True | **+2** |
| Partially True | **+1** |
| Opinion | **0** *(excluded from average)* |
| Partially False | **−1** |
| False | **−2** |

### Fact score

Each author's domain score is averaged across all N fact-checkers, reducing individual evaluator bias. Summed across all 10 domains:

| | Score |
|---|---|
| Maximum | **+200** (10 domains × 10 claims × +2) |
| Minimum | **−200** |

### Composite Cross-Stone score

```
cross_stone_score = 0.7 × (fact_score / 200) + 0.3 × speed_ratio
```

Speed is `baseline_seconds / actual_seconds` — faster is higher. Once you set a baseline, scores above 1.0 mean the AI is meaningfully faster and more accurate than the baseline era.

Without a baseline, relative mode is used (fastest AI in the current run = 100%). Relative mode is not comparable across time — set the baseline after your first complete run.

**Adjust weights** with `--no-speed` (accuracy only) or `--w1`/`--w2` for custom splits.

---

## Reading the leaderboard

```
st-stones cross_stones/cross-stones-10.json
```

Key columns:

| Column | Meaning |
|--------|---------|
| `Fact Score` | Raw sum across all domains (out of ±200) |
| `Fact%` | Fact score as a percentage of 200 |
| `vs Baseline` | Speed ratio — 1.00× = baseline speed, 2.00× = twice as fast |
| **Cross-Stone** | **The final ranking — composite accuracy + speed** |

For a visual breakdown:

```bash
st-heatmap --display cross_stones/domains/healthcare_medical.json   # N×N score grid
st-stones --domain --ai-caption cross_stones/cross-stones-10.json   # per-domain breakdown
```

---

## Historical tracking

Set the baseline once after your first complete run:

```bash
st-stones --set-baseline cross_stones/cross-stones-10.json
```

Then after each significant run (monthly, quarterly, annually):

```bash
st-stones --record-snapshot --snapshot-label "2026-Q1" cross_stones/cross-stones-10.json
st-stones --history cross_stones/cross-stones-10.json
```

The history tables show composite score, speed ratio, and accuracy per AI per snapshot — letting you see whether a provider has improved, regressed, or stayed flat over months and years.

---

## Creating a custom domain

```bash
st-domain                          # interactive wizard
st-domain --name supply_chain      # pre-fill the slug
```

`st-domain` walks you through naming the domain, describing the topic, and smoke-testing it against one AI to confirm you get 10 fact-checkable claims back. Domains are saved to `cross_stones/domains/` by default.

To add a custom domain to the standard benchmark set, register it in `cross-stones-10.json` or create a new named set config file.

**Related:** [st-stones](st-stones.md) · [st-cross](st-cross.md) · [st-domain](st-domain.md) · [st-heatmap](st-heatmap.md) · [AI Providers](ai-providers.md)

