# AI Performance Metrics and Speed Comparison

## Overview

The Cross system provides a unique opportunity to measure and compare AI performance in real-world scenarios. With `st-bang` running parallel AI requests and `st-cross` running cross-product fact-checking, we have perfect **apples-to-apples** comparisons for AI speed and performance benchmarking.

## Key Insight: Built-in Performance Comparisons

Both `st-bang` and `st-cross` already capture **wall-clock time** for each AI operation, making them ideal for performance comparison:

- **st-bang**: Measures time for each AI to generate a story from the same prompt (parallel execution)
- **st-cross**: Measures time for each AI to fact-check stories (N×N matrix of timings)

These provide **legitimate, unbiased speed comparisons** because:
1. Same prompt/task for all AIs
2. Same environment and network conditions
3. Measured concurrently (eliminating time-of-day bias)
4. Real-world workloads (not synthetic benchmarks)

## Standard Performance Metrics in AI

### 1. Response Time (Latency)
**Unit**: seconds (s) or milliseconds (ms)

The time from request submission to complete response.

**Example**:
```
xai         05:17  (317 seconds)
anthropic   03:45  (225 seconds)
openai      04:33  (273 seconds)
gemini      02:58  (178 seconds)
```

### 2. Throughput
**Unit**: tokens per second (tok/s) or requests per second (req/s)

How much work can be completed in a given time period.

**Example**:
```
openai generated 1,072 tokens in 273s = 3.93 tok/s
gemini generated 1,287 tokens in 178s = 7.23 tok/s
```

### 3. Time to First Token (TTFT)
**Unit**: milliseconds (ms)

The delay before the AI starts generating output (streaming mode).

**Note**: Not currently captured by Cross, but relevant for real-time applications.

### 4. Wall-Clock Time
**Unit**: mm:ss or seconds

Total elapsed time for a parallel operation (from first start to last completion).

**Example from st-cross**:
```
Column total (perplexity): 01:10  (70 seconds)
Overall wall time: 06:01  (361 seconds for N×N fact-checks)
```

### 5. Cost Efficiency
**Unit**: dollars per request or cost per 1M tokens

Financial performance metric.

**Example**:
```
Task: Generate 1,500-word report
- openai:  $0.03 (1,239 tokens total × $0.0025/1K input + $0.010/1K output)
- gemini:  $0.00 (free tier)
```

## Data Capture Strategy

### Current State
Cross currently captures timing data at the **command level** but not in the JSON containers:
- `st-bang` displays elapsed time per AI during execution
- `st-cross` displays cell-by-cell timing in the N×N matrix
- Wall-clock totals are computed and displayed

### Recommended Additions

#### 1. Add Timing Fields to JSON Container

**In `data` objects** (raw AI responses):
```json
{
  "make": "xai",
  "model": "grok-2-latest",
  "prompt": "...",
  "gen_payload": {...},
  "gen_response": {...},
  "timing": {
    "start_time": 1710188400.123,     // Unix timestamp
    "end_time": 1710188717.456,       // Unix timestamp
    "elapsed_seconds": 317.333,       // Computed
    "tokens_input": 193,              // From usage
    "tokens_output": 1287,            // From usage
    "tokens_per_second": 4.07         // Computed
  },
  "md5_hash": "..."
}
```

**In `story.fact` objects** (fact-check results):
```json
{
  "make": "perplexity",
  "model": "sonar-pro",
  "report": "...",
  "timing": {
    "start_time": 1710188800.789,
    "end_time": 1710188892.345,
    "elapsed_seconds": 91.556,
    "tokens_input": 450,
    "tokens_output": 320,
    "tokens_per_second": 3.49
  },
  "counts": [14, 19, 15, 2, 0],
  "score": 1.29
}
```

#### 2. Capture from Existing Usage Data

Most AI APIs already return timing-relevant data in their responses:

- **OpenAI**: `usage.prompt_tokens`, `usage.completion_tokens`
- **Anthropic**: `usage.input_tokens`, `usage.output_tokens`
- **xAI**: `usage.input_tokens`, `usage.output_tokens`
- **Gemini**: `usage_metadata.prompt_token_count`, `usage_metadata.candidates_token_count`

**Implementation**: Modify `st-gen.py` and `st-fact.py` to capture `time.time()` before and after API calls.

## Performance Analysis Tools

### 1. Command-Line Summary Tool: `st-speed`

Propose new command to analyze speed across containers:

```bash
st-speed report.json
```

Output:
```
Performance Summary: report.json

Story Generation (st-bang equivalent):
  AI           Time    Tokens   Tok/s   Cost
  ──────────────────────────────────────────
  gemini       02:58    1,287    7.23   $0.00
  anthropic    03:45    1,072    4.76   $0.15
  openai       04:33      982    3.59   $0.12
  xai          05:17    1,019    3.21   $0.08

Wall-clock time: 05:17 (parallel execution)

Fact-Checking Performance:
  AI           Avg Time   Median   Min    Max
  ──────────────────────────────────────────
  gemini       01:22      01:10   00:58  02:20
  perplexity   01:30      01:28   01:05  01:55
  openai       01:45      01:39   01:21  02:15
  anthropic    02:05      01:58   01:45  02:45
  xai          02:15      02:10   01:50  03:05
```

### 2. Time-Series Analysis: `st-speed --history`

Track performance over time (requires multiple runs):

```bash
st-speed --history crypto/*.json
```

Output:
```
AI Performance Over Time (N=5 reports)

openai/gpt-4o:
  Mean generation time: 04:23 ± 00:42 (σ = 42s)
  Trend: -5s per week (getting faster)
  Tokens/second: 3.8 ± 0.5

gemini/gemini-2.5-flash:
  Mean generation time: 02:45 ± 00:15 (σ = 15s)
  Trend: +2s per week (getting slower)
  Tokens/second: 7.1 ± 0.3
```

### 3. Comparative Visualization: `st-speed --plot`

Generate performance comparison graphs:

```bash
st-speed --plot report.json
```

Creates:
- **Bar chart**: Response time by AI
- **Box plot**: Distribution of fact-check times per AI
- **Time series**: Performance trend over multiple reports
- **Scatter plot**: Response time vs. output tokens
- **Efficiency plot**: Cost vs. time trade-offs

### 4. Statistical Comparison

Basic statistics to track:

| Metric | Description | Use Case |
|--------|-------------|----------|
| **Mean** | Average response time | Overall performance |
| **Median** | Middle value | Typical performance (robust to outliers) |
| **Std Dev (σ)** | Variability | Consistency/reliability |
| **Min/Max** | Range | Best/worst case |
| **Percentile (P95)** | 95% of requests faster than | SLA planning |
| **Coefficient of Variation** | σ/mean | Relative consistency |

**Example**:
```
gemini generation time:
  Mean:   178s
  Median: 175s
  σ:      12s
  CV:     6.7%  (very consistent)

xai generation time:
  Mean:   317s
  Median: 310s
  σ:      45s
  CV:     14.2% (more variable)
```

## Weekly Performance Tracking

### Automated Benchmark Suite

Run weekly benchmarks with standard prompts:

```bash
# Create benchmark prompt
cat > benchmark_week12.prompt << EOF
Write a 500-word analysis of current cryptocurrency trends,
focusing on Bitcoin and Ethereum price movements.
EOF

# Run benchmark
st-bang benchmark_week12.prompt
st-cross benchmark_week12.json

# Archive results
mkdir -p benchmarks/2026-03-11
cp benchmark_week12.json benchmarks/2026-03-11/
```

### Aggregate Analysis

```bash
# Analyze trends over multiple weeks
st-speed --history benchmarks/*/*.json --output weekly_report.md
```

Output includes:
- Week-over-week speed changes
- Consistency improvements/regressions
- Cost trends
- Reliability metrics (failure rates)

## Real-World Example from Your Data

Based on the st-cross output you shared:

### Step 2 Cross-Product Performance

**Fact-checker speed** (checking xai's story):
```
xai        → 06:01  (361 seconds)
anthropic  → 05:30  (330 seconds)
openai     → 01:21  (81 seconds)   ⭐ Fastest
perplexity → 01:10  (70 seconds)   ⭐ Fastest
gemini     → 02:20  (140 seconds)
```

**Analysis**:
- perplexity and openai are **5× faster** than xai for fact-checking
- This is a perfect apples-to-apples comparison: same task, same content
- Cost considerations: faster ≠ cheaper (need to factor in API pricing)

**Wall-clock time**: 06:01 total (because operations run in parallel by column)

## Implementation Roadmap

### Phase 1: Data Capture (Week 1)
- [ ] Modify `st-gen.py` to capture timing data
- [ ] Modify `st-fact.py` to capture timing data
- [ ] Update JSON schema with `timing` objects
- [ ] Backfill timing from existing `usage` data where possible

### Phase 2: Basic Analysis (Week 2)
- [ ] Create `st-speed` command for basic summaries
- [ ] Support `--ai <ai>` to filter by AI
- [ ] Support `--history` for multi-file analysis
- [ ] Output CSV for external analysis

### Phase 3: Visualization (Week 3)
- [ ] Integrate matplotlib/seaborn for graphs
- [ ] Generate bar charts (response time)
- [ ] Generate box plots (variability)
- [ ] Generate time-series plots (trends)
- [ ] Add `--ai-caption` flag for AI-generated insights (see FEATURE_AI_CAPTION.md)
  - Highlights obvious and non-obvious patterns
  - Provides actionable recommendations
  - Similar to st-analyze's AI-generated analysis

### Phase 4: Advanced Metrics (Week 4)
- [ ] Cost-efficiency analysis (time × price)
- [ ] Quality-speed trade-offs (score vs. time)
- [ ] Predictive modeling (expected time for N tokens)
- [ ] Weekly automated benchmarking
- [ ] **Consider:** Integrate speed metrics into st-analyze reports
  - Add `--include-speed` flag to st-analyze
  - Include speed tables and AI-generated caption
  - Provides complete quality + performance analysis in one report
  - **Note:** Must not "muddy the waters" - keep opt-in and clearly separated

## Best Practices

### 1. Consistent Test Conditions
- Use the same prompts for benchmarking
- Run tests at similar times of day (API performance varies)
- Use the same model versions (track when models update)
- Disable caching for fair comparisons (`--no-cache`)

### 2. Multiple Samples
- Run each test at least 3-5 times
- Use median for central tendency (robust to outliers)
- Track standard deviation for consistency
- Remove extreme outliers (>3σ from mean)

### 3. Document Context
Include in reports:
- Date/time of test
- Model versions
- Network conditions
- Prompt complexity (token count)
- Any API issues encountered

### 4. Actionable Insights
Focus on:
- **Which AI for which task?** (speed vs. quality trade-offs)
- **Cost optimization**: Fastest vs. cheapest vs. best quality
- **Reliability**: Which AIs are most consistent?
- **Trends**: Are AIs getting faster/slower over time?

## Example Use Cases

### Use Case 1: Choosing the Right AI
```
Task: Generate breaking news story (time-sensitive)
Requirement: < 3 minutes response time

Analysis (from benchmarks):
✓ gemini:  02:45 avg (meets requirement)
✓ openai:  04:23 avg (too slow)
✓ perplexity: 02:10 avg (meets requirement, fastest)

Decision: Use perplexity for breaking news
```

### Use Case 2: Cost Optimization
```
Task: Fact-check 100 stories per day

Option A: openai (fast but expensive)
  Time: 1.5 min/story × 100 = 150 min/day
  Cost: $0.05/story × 100 = $5.00/day

Option B: gemini (slower but free)
  Time: 2.0 min/story × 100 = 200 min/day
  Cost: $0.00/day

Decision: Use gemini (50 extra minutes worth $0 cost)
```

### Use Case 3: Quality vs. Speed
```
Task: In-depth investigative report

AI Rankings:
1. anthropic: Highest quality score (1.38), slower (05:30)
2. openai:    Good quality (1.29), medium speed (04:33)
3. gemini:    Good quality (1.25), fastest (02:58)

Decision: Use anthropic for quality, despite speed penalty
```

## Integration with Existing Tools

### st-analyze Integration
Extend `st-analyze.py` to include performance metrics:
- Add "Performance" section to analysis reports
- Include speed rankings in heatmaps
- Correlate speed with fact-check scores

### st-post Integration
Include performance data in published reports:
```markdown
---
Report generated by gemini (02:45, 7.2 tok/s)
Fact-checked by perplexity (01:10)
Quality score: 1.29 ⭐⭐⭐⭐
---
```

## Glossary of Terms

| Term | Definition | Typical Range |
|------|------------|---------------|
| **Latency** | Time from request to response | 1s - 600s |
| **Throughput** | Tokens generated per second | 2 - 50 tok/s |
| **TTFT** | Time to first token (streaming) | 200ms - 2s |
| **Wall-clock** | Total elapsed time (parallel ops) | Varies |
| **Token** | ~4 characters of text | N/A |
| **Request** | One API call | N/A |
| **Session** | Full workflow (gen + fact-check) | 5min - 30min |

## Common Speed Ranges (Rough Guidelines)

Based on industry standards and Cross system observations:

| AI Provider | Story Gen (1500 words) | Fact-Check (2000 words) |
|-------------|------------------------|-------------------------|
| **OpenAI** | 3-5 min | 1-2 min |
| **Anthropic** | 4-6 min | 2-3 min |
| **Google** | 2-4 min | 1-2 min |
| **xAI** | 5-7 min | 2-4 min |
| **Perplexity** | 3-5 min | 1-2 min |

*Note: Actual times vary based on prompt complexity, model load, and network conditions.*

## Future Enhancements

### 1. Real-Time Performance Dashboard
Web interface showing:
- Live speed rankings
- 24-hour trends
- API status indicators
- Cost burn rate

### 2. Predictive Timing
Based on historical data:
```bash
st-speed --predict "1500 word report on crypto"
```
Output:
```
Estimated completion times:
  gemini:      02:50 ± 00:15 (90% confidence)
  openai:      04:20 ± 00:30
  anthropic:   05:30 ± 00:45
```

### 3. Automated Model Selection
```bash
st-gen --optimize speed crypto_report.prompt
st-gen --optimize cost crypto_report.prompt
st-gen --optimize quality crypto_report.prompt
```

### 4. Performance Alerts
```bash
# Set up monitoring
st-speed --monitor --alert-threshold 300s

# Receive notification if any AI exceeds 5 minutes
```

## Contributing Performance Data

To build a community database of AI performance:

1. **Run benchmarks** with standard prompts
2. **Export timing data**: `st-speed --export benchmark.csv`
3. **Share anonymized data** (optional, respect privacy)
4. **Aggregate across users** for broader insights

## Summary

The Cross system's `st-bang` and `st-cross` commands provide **perfect platforms for AI speed comparison**:

✅ **Apples-to-apples**: Same task, same conditions  
✅ **Real-world**: Actual workloads, not synthetic benchmarks  
✅ **Comprehensive**: Both generation and fact-checking  
✅ **Actionable**: Clear data for decision-making  

**Next steps**:
1. Implement timing data capture in JSON containers
2. Create `st-speed` analysis tool
3. Build visualization capabilities
4. Establish weekly benchmarking routine

With systematic performance tracking, Cross users can make data-driven decisions about which AI to use for which tasks, optimizing for speed, cost, or quality as needed.

---

**Related Documentation**:
- `README_devel.md` — Development details
- `README_cross_product.md` — st-cross explanation
- `st-analyze.py` — Quality analysis
- `mmd_data_analysis.py` — Statistical analysis examples

