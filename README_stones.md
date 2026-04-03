# Cross-Stones — AI Benchmark Suite

> *How smart is it? How fast is it? Cross-Stones finds out.*

Cross-Stones is the built-in benchmark suite for [Cross](README.md).
It evaluates multiple AI models across a standard set of domains and produces a
composite score that reflects both **accuracy** (how factually correct the AI's
reports are) and **speed** (how quickly it generates and fact-checks them).

The name is borrowed from curling, where "stones" are the units of play and
scoring is determined by how close each stone lands to the target.
In Cross-Stones, each domain prompt is the target, and each AI gets one throw.

---

## Quickstart

```bash
# Run the full N×N benchmark for one domain
st-cross cross_stones/domains/healthcare_medical.json

# Score a single domain
st-stones cross_stones/domains/healthcare_medical.json

# Score all 10 domains in the standard benchmark set
st-stones cross_stones/cross-stones-10.json

# Run any missing domains, then score everything
st-stones --run cross_stones/cross-stones-10.json

# One-time: lock current timing as the speed baseline (enables absolute scoring)
st-stones --set-baseline cross_stones/cross-stones-10.json

# Visualise cross-stone scores broken down by AI — compare openai vs xai vs anthropic
st-stones --domain --ai-caption cross_stones/cross-stones-10.json
```

That's it. By the time the last command prints, you have a ranked leaderboard
showing accuracy, speed, and composite **Cross-Stone** scores for every AI
across every domain.  Run `--set-baseline` once after your first complete run —
it switches speed scoring from relative (meaningless for a single AI, not
comparable across time) to absolute (scored against a locked reference point).

---

## How It Works — The Cross-Product Methodology

Cross-Stones builds on Cross's core **cross-product** approach:

1. **Every AI generates a report** for the same domain prompt — independently,
   with no knowledge of what the others produce. With 5 AI providers and 10
   domains, that is 50 reports.

2. **Every AI fact-checks every report** — including its own. With 5 AIs and 5
   reports per domain, that is a 5×5 fact-check matrix (25 cells) per domain,
   or 250 fact-check operations across all 10 domains.

3. **Scores are aggregated** per AI model across all domains to produce the
   final `cross_stone_score`.

The cross-product design surfaces things a single-AI evaluation cannot:

| Pattern | What it reveals |
|---------|----------------|
| High self-score, low peer scores | AI is lenient with its own claims |
| High peer scores, low self-score | AI is an unusually harsh self-critic |
| Consistent row (evaluator) scores | Stable fact-checking style regardless of who wrote it |
| Consistent column (author) scores | Report quality holds up across all reviewers |
| Diagonal vs off-diagonal gap | Degree of self-serving bias across the field |

---

## The 10 Benchmark Domains

Each domain has a dedicated prompt file in this directory.
Prompts ask the AI to generate **exactly 10 specific, fact-checkable claims**
at calibrated difficulty — roughly half verifiable with basic research, half
requiring primary sources or technical documentation.

| # | Domain | Prompt File | Focus |
|---|--------|-------------|-------|
| 1 | Software Development & Programming | `software_development.prompt` | AI coding tools, productivity metrics, code quality |
| 2 | Customer Service & Support | `customer_service.prompt` | Chatbot automation, deflection rates, platform ROI |
| 3 | Marketing & Content Creation | `marketing_content.prompt` | Generative AI adoption, campaign ROI, ethics |
| 4 | Education & Learning | `education_learning.prompt` | Student/educator adoption, outcomes, policy |
| 5 | Data Analytics & Business Intelligence | `data_analytics.prompt` | BI platform AI, NL querying, governance |
| 6 | Healthcare & Medical Analysis | `healthcare_medical.prompt` | FDA-cleared devices, imaging benchmarks, CDS |
| 7 | Finance & Business Decision Making | `finance_business.prompt` | Fraud detection, trading, regulatory frameworks |
| 8 | Writing, Editing & Summarizing | `writing_editing.prompt` | Writing tool adoption, quality benchmarks, policy |
| 9 | Research, Search & Q&A | `research_qa.prompt` | MMLU/HLE benchmarks, hallucination rates, tools |
| 10 | Creative Media (Images, Video, Audio) | `creative_media.prompt` | Generative tools, copyright, deepfake regulation |

Prompts are intentionally neutral — no domain favors any particular AI
provider's training focus or architectural strengths.

---

## Running a Benchmark

### Prerequisites

Cross must be installed and your `.env` API keys must be configured.
See [README_install.md](README_install.md) for the full setup guide.

```bash
source .venv/bin/activate
```

### Step 1 — Run a single domain

Each domain benchmark is a standard Cross job. Pass the `.prompt` file path
(without extension) as the JSON container name:

```bash
st-cross cross_stones/domains/healthcare_medical.json
```

Cross looks for `healthcare_medical.prompt` alongside the JSON file, generates
one report per AI (Step 1), then runs the full N×N fact-check matrix (Step 2).
The live table updates in your terminal as each cell completes.

### Step 2 — Run all 10 domains

Pass the benchmark set config with `--run`.  `st-stones` discovers which domains
are incomplete, confirms the estimated API call count, then runs each one in
sequence automatically:

```bash
st-stones --run cross_stones/cross-stones-10.json
```

To skip the confirmation prompt (useful in scripts):

```bash
st-stones --run --no-confirmation cross_stones/cross-stones-10.json
```

> **Tip:** Each domain takes roughly 5–15 minutes depending on the number of
> AI providers configured and network latency. All results are cached — if you
> re-run, previously completed cells are skipped automatically.

### Step 3 — Review results

```bash
# Summary table of fact-check scores for a single domain
st-ls --fact cross_stones/domains/healthcare_medical.json

# Full cross-AI claims comparison (which AI agreed with which)
st-ls -C cross_stones/domains/healthcare_medical.json

# Speed analysis for a single domain
st-speed cross_stones/domains/healthcare_medical.json

# Heatmap: evaluator (rows) vs author (columns)
st-heatmap --display cross_stones/domains/healthcare_medical.json
```

---

## Scoring System

### Claim-Level Scoring

Each fact-check verdict on an individual claim is worth:

| Verdict | Points |
|---------|--------|
| True | **+2** |
| Partially True | **+1** |
| Opinion | **0** *(excluded from average)* |
| Partially False | **−1** |
| False | **−2** |

Opinion statements are excluded from the average so they do not dilute the
score, but their count and ratio are still reported — a report full of
non-falsifiable opinions tells you something.

### Domain Fact Score (`domain_fact_score`)

For each domain, the fact-check score for one AI is the average of all verdict
points across the 10 claims in its report, as assessed by each fact-checking AI.
The cross-product approach means each author's score is the **average across all
N fact-checkers**, reducing individual evaluator bias.

With 10 domains and 10 claims per domain:

| | Score |
|---|---|
| Maximum possible | **+200** pts (10 domains × 10 claims × +2) |
| Neutral (all opinions) | **0** pts |
| Minimum possible | **−200** pts (10 domains × 10 claims × −2) |

### Speed Score

Speed is measured as total elapsed seconds for report generation plus
fact-checking.  Lower time is better, so the raw value is inverted so that
**higher is always better** across both dimensions.

#### Absolute mode — the default (requires a baseline)

After your first complete benchmark run, lock the timing as the speed baseline:

```bash
st-stones --set-baseline cross_stones/cross-stones-10.json
```

From then on, speed is expressed as a **ratio against that baseline**:

```
speed_ratio = baseline_total_seconds / actual_total_seconds
```

| Ratio | Meaning |
|-------|---------|
| `1.00×` | Matches the baseline-era speed |
| `2.00×` | Twice as fast as the baseline |
| `0.50×` | Half as fast (regression) |

The leaderboard shows a **vs Baseline** column instead of raw 1/s values.
This makes scores comparable across months and years, and meaningful even
for a single-AI run.

#### Relative mode — fallback when no baseline exists

Without a baseline, speed is normalised to the fastest AI *in the current run*:

```
speed_norm = speed_score / max_speed_score   (fastest AI = 100%)
```

**Limitations of relative mode:**
- The fastest AI always gets 100% regardless of absolute speed — the number
  is only meaningful relative to the other AIs in that run.
- A single-AI run always shows 100% — completely uninformative.
- You cannot compare scores across separate runs.

When relative mode is active, the leaderboard prints a yellow warning and the
**Speed%** column is shown.  Set the baseline to eliminate both.

---

## Cross-Stone Score — the "Cross-Stone" leaderboard column

The composite benchmark score that combines accuracy and speed into a single
number used to rank the leaderboard:

**Absolute mode** (baseline set — recommended):

```
cross_stone_score = w1 × (fact_score / max_fact_score)
                  + w2 × speed_ratio
```

**Relative mode** (no baseline — fallback):

```
cross_stone_score = w1 × (fact_score / max_fact_score)
                  + w2 × (speed_score / max_speed_score)
```

Default weights: **w1 = 0.7** (accuracy), **w2 = 0.3** (speed).

Because `speed_ratio` can exceed 1.0 in absolute mode (AI is faster than the
baseline era), the composite score can also exceed 1.0.  That is intentional —
a score above 1.0 expresses genuine multi-year improvement over the benchmark
era, something relative mode can never show.

### Output columns at a glance

| Column | What it means |
|--------|---------------|
| `Fact Score` | Raw sum of (avg peer rating × n_claims) across all domains |
| `/±200` | The ±200 ceiling/floor for 10 domains × 10 claims × ±2 |
| `Fact%` | `Fact Score / max_fact_score` as a percentage |
| `vs Baseline` | Speed ratio in absolute mode — 1.00× = baseline speed |
| `Speed (1/s)` | Raw `1 / elapsed_seconds` in relative mode |
| `Speed%` | Relative speed normalised to fastest AI (relative mode only) |
| **Cross-Stone** | **The composite `cross_stone_score` — the final ranking column** |
| `Domains` | Number of domains that contributed to this AI's score |

Weights can be adjusted — if you care only about accuracy, set `--no-speed`
(equivalent to w1 = 1.0, w2 = 0.0).  For a latency-sensitive pipeline,
try `--w1 0.5 --w2 0.5`.

The ideal AI lands in the **top-right corner** of a fact-score vs speed plot:
high accuracy *and* low latency.

### Leaderboard Plot

```bash
st-plot --plot evaluator_v_target --display cross_stones/domains/healthcare_medical.json
```

For a full cross-stones leaderboard across all 10 domains, aggregate the
`domain_fact_score` values with `st-speed --history`:

```bash
st-speed --history cross_stones/domains/*.json
```

---

## Historical Tracking & Year-over-Year Comparison

Cross-Stones is designed to track AI progress over time, not just rank providers
within a single run.  Two mechanisms enable this: a **locked speed baseline** and
a **snapshot history**.  See [Speed Score](#speed-score) for how the baseline
affects scoring.

### Setting the Baseline (once)

After completing a full benchmark run for the first time:

```bash
st-stones --set-baseline cross_stones/cross-stones-10.json
```

This records the average timing across all AI providers as the locked speed
baseline.  Run this **once**.  Future runs scoring faster will have
`speed_ratio > 1.0` and `cross_stone_score` may exceed 1.0, showing genuine
year-over-year improvement.

> **Important:** Do not change `speed_baseline` manually after it is set.
> If you want a new baseline (e.g. for a different benchmark set), create a new
> named set config (e.g. `cross-stones-10-2030.json`).

### Recording Snapshots

After each significant run (monthly, quarterly, annually):

```bash
st-stones --record-snapshot cross_stones/cross-stones-10.json
st-stones --record-snapshot --snapshot-label "Q1 2027" cross_stones/cross-stones-10.json
```

Each snapshot is appended to the `snapshots` array in `cross-stones-10.json`
with the date, label, per-AI scores, speed ratios, and accuracy.

### Viewing the Historical Tables

```bash
st-stones --history cross_stones/cross-stones-10.json
```

This prints three tables:
1. **Composite score over time** — `cross_stone_score` per AI per snapshot
2. **Speed ratio over time** — how much faster each AI is vs the baseline year
3. **Accuracy over time** — `fact_norm` (0–1) per AI per snapshot

Example output from 2028, looking back at 2026:

```
Cross-Stones Snapshot History  [cross-stones-10]
Speed baseline : 15.0s gen + 45.0s fc = 60.0s total  (recorded 2026-03-27)

Composite cross_stone_score over time:

| Date       | Label           | anthropic | openai | xai    | 🏆 Top AI |
|------------|-----------------|-----------|--------|--------|-----------|
| 2026-03-27 | Initial run     |    0.7834 | 1.0100 | 0.9412 | openai    |
| 2027-01-15 | Q1 2027         |    1.0255 | 1.3601 | 1.2332 | openai    |
| 2028-06-01 | Mid 2028        |    1.4112 | 1.7890 | 1.6544 | openai    |

Speed ratio vs 2026-03-27 baseline  (1.00× = at baseline, 2.00× = twice as fast):

| Date       | Label           | anthropic | openai | xai   | 🚀 Fastest vs 2026 |
|------------|-----------------|-----------|--------|-------|--------------------|
| 2026-03-27 | Initial run     |    0.86×  |  1.50× | 1.15× | openai             |
| 2027-01-15 | Q1 2027         |    1.55×  |  2.61× | 2.07× | openai             |
| 2028-06-01 | Mid 2028        |    3.20×  |  5.10× | 4.30× | openai             |
```

### Recommended Annual Workflow

```bash
# 1. Run (or re-run) the full benchmark
st-stones --run cross_stones/cross-stones-10.json

# 2. On first ever run: lock the baseline (do this ONCE)
st-stones --set-baseline cross_stones/cross-stones-10.json

# 3. Save this year's scores as a named snapshot
st-stones --record-snapshot --snapshot-label "2026-Q1" cross_stones/cross-stones-10.json

# 4. View the full history
st-stones --history cross_stones/cross-stones-10.json
```

---

## Interpreting Your Results

### Reading the Heatmap

`st-heatmap` renders an N×N grid where:
- **Rows** = the AI doing the fact-checking (evaluator)
- **Columns** = the AI that wrote the report (author)
- **Cell colour** = average fact-check score (darker = higher veracity)
- **Diagonal cells** = an AI fact-checking its own report

A well-calibrated AI should score its own report similarly to how peers score
it. A large positive gap on the diagonal suggests self-serving bias.

### Reading the Score Table

`st-ls --fact` produces a compact table showing, for each story/fact-check pair:

```
S    F  Make        True  Mostly  Opinion  Mostly  False  Score
                          True            False
1    2  openai        26       9        9       0      0   1.74
```

- **S** = story (report author index)
- **F** = fact-check AI index
- **Score** = weighted average on the −2 to +2 scale

Scores above **1.5** indicate strong factual accuracy.
Scores below **1.0** warrant scrutiny of the domain prompt or AI output.

### What Makes a Good Score?

In practice, well-grounded factual reports on established topics tend to score
in the **1.4–1.9** range. Scores above 1.9 are rare but achievable on domains
with highly verifiable, objective claims. Scores below 1.0 often indicate the
AI drifted into opinion, speculation, or confidently stated claims that
peer fact-checkers could not verify.

In absolute mode (baseline set), scores **above 1.0** mean the AI surpasses the
theoretical ceiling of the baseline year — a sign of genuine multi-year progress.

---

## Extending the Benchmark

### Adding a New Domain

1. Write a new `.prompt` file in this directory following the format of the
   existing prompts: 10 specific, fact-checkable claims at calibrated difficulty.
2. Add it to the domain table in this README.
3. Run `st-cross cross_stones/domains/your_new_domain.json`.

### Increasing Claims Per Domain

Edit the prompt file to request more claims (e.g., 20 instead of 10).
The scoring formulas scale automatically; update `max_fact_score` in your
calculations accordingly (e.g., 10 domains × 20 claims × 2 = 400 max).

### Adjusting the Weights

Pass custom weights to your scoring script or adjust the constants in
`st-plot` if you have built a custom aggregation layer.

---

## File Reference

| File | Purpose |
|------|---------|
| `*.prompt` | Domain benchmark prompts (one per domain) |
| `*.json` | Cross result containers generated by `st-cross` |

| Command | Purpose |
|---------|---------|
| `st-cross <domain>.json` | Run the full N×N benchmark for one domain |
| `st-ls --fact <domain>.json` | Display fact-check score table |
| `st-ls -C <domain>.json` | Display cross-AI claims comparison |
| `st-speed <domain>.json` | Analyse generation and fact-check timing |
| `st-speed --history cross_stones/domains/*.json` | Aggregate timing across all domains |
| `st-heatmap --display <domain>.json` | Render the N×N score heatmap |
| `st-plot --plot all --display <domain>.json` | Render all statistical plots |
| `st-stones --set-baseline cross_stones/cross-stones-10.json` | Lock current timing as speed baseline (run once) |
| `st-stones --record-snapshot cross_stones/cross-stones-10.json` | Save today's scores as a snapshot |
| `st-stones --history cross_stones/cross-stones-10.json` | Display year-over-year snapshot history |


