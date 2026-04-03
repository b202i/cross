# AI Options Framework - Quick Start

**Standardized AI content generation across Cross tools**

---

## What is This?

A consistent framework for generating AI-written content (titles, captions, summaries, stories) across all Cross tools.

---

## For Users

### Five Content Types

```bash
st-speed --ai-title report.json        # Max 10 words
st-speed --ai-short report.json        # Max 80 words
st-speed --ai-caption report.json      # 100-160 words
st-speed --ai-summary report.json      # 120-200 words
st-speed --ai-story report.json        # 800-1200 words → JSON
```

### Choose Your AI

```bash
st-speed --ai-caption --ai gemini report.json
st-speed --ai-caption --ai anthropic report.json
st-speed --ai-caption --ai openai report.json
```

### Read More
- **[README_AI_OPTIONS.md](README_AI_OPTIONS.md)** — Complete user guide with examples

---

## For Developers

### Implementing in a New Tool

**4 core functions to add:**
1. `build_ai_prompt(data, content_type)` — Create prompts
2. `validate_ai_content(content, content_type)` — Validate output
3. `generate_ai_content(...)` — Call AI
4. `save_story_to_container(...)` — Save stories to JSON

**Argument parser:**
```python
ai_group = parser.add_argument_group('AI Content Generation')
ai_group.add_argument('--ai-title', action='store_true', 
                    help='Generate short title (max 10 words) → stdout')
ai_group.add_argument('--ai-short', action='store_true',
                    help='Generate short caption (max 80 words) → stdout')
ai_group.add_argument('--ai-caption', action='store_true',
                    help='Generate detailed caption (100-160 words) → stdout')
ai_group.add_argument('--ai-summary', action='store_true',
                    help='Generate concise summary (120-200 words) → stdout')
ai_group.add_argument('--ai-story', action='store_true',
                    help='Generate comprehensive story (800-1200 words) → new story in JSON')
```

### Read More
- **[IMPLEMENTATION_AI_OPTIONS.md](IMPLEMENTATION_AI_OPTIONS.md)** — Step-by-step implementation guide

---

## For Testers

### Run Tests

```bash
./test_ai_options.sh
```

### Manual Tests

```bash
# Test each content type
st-speed --ai-title report.json
st-speed --ai-short report.json
st-speed --ai-caption report.json
st-speed --ai-summary report.json
st-speed --ai-story report.json

# Test error handling
st-speed --ai-title --ai-short report.json  # Should error

# Test AI selection
st-speed --ai-caption --ai gemini report.json
```

### Read More
- **[TESTING_AI_OPTIONS.md](TESTING_AI_OPTIONS.md)** — Complete test suite

---

## Word Count Requirements

**DO NOT CHANGE** — These are standardized across all tools:

| Content Type | Min Words | Max Words | Output |
|--------------|-----------|-----------|--------|
| `--ai-title` | 1 | 10 | stdout |
| `--ai-short` | 1 | 80 | stdout |
| `--ai-caption` | 100 | 160 | stdout |
| `--ai-summary` | 120 | 200 | stdout |
| `--ai-story` | 800 | 1200 | JSON file |

---

## Current Status

### ✅ Implemented
- `st-speed` — Performance analysis

### 🔄 Planned
- `st-analyze` — Cross-product analysis
- `st-fact` — Fact-check summaries
- `st-merge` — Merge analysis
- `st-gen` — Story metadata

---

## Key Principles

1. **Consistency** — Same options, same behavior, all tools
2. **Validation** — Strict word count enforcement
3. **Data-Driven** — Content must include numbers/metrics
4. **AI-Agnostic** — Works with any AI provider
5. **Cached** — Reuse results for speed
6. **Error-Tolerant** — Warnings, not crashes

---

## Files in This Framework

| File | Purpose |
|------|---------|
| `README_AI_OPTIONS.md` | User guide with examples |
| `IMPLEMENTATION_AI_OPTIONS.md` | Developer implementation guide |
| `TESTING_AI_OPTIONS.md` | Comprehensive test suite |
| `test_ai_options.sh` | Automated regression tests |
| `st-speed.py` | Reference implementation |

---

## Quick Examples

### Example 1: Blog Post Title

```bash
$ st-speed --ai-title muscle_amino_acids.json
OpenAI Outperforms All AIs by 2-8x
```

### Example 2: Documentation Caption

```bash
$ st-speed --ai-caption muscle_amino_acids.json
OpenAI leads fact-checking at 34s average (median 35s, range 3-64s), 
followed by Perplexity at 49s, while Gemini (87s), xAI (109s), and 
Anthropic (263s) trail behind. Consistency is the key differentiator: 
OpenAI and Perplexity maintain low variance (StdDev ~25-28s), delivering 
reliable sub-minute performance. In contrast, Anthropic's 228s StdDev 
and xAI's 107s variance create unpredictable latency spikes, with xAI's 
254s outlier pushing its maximum beyond 4 minutes despite an 88s median. 
For production reliability, default to OpenAI or Perplexity.
```

### Example 3: Comprehensive Analysis

```bash
$ st-speed --ai-story --ai anthropic muscle_amino_acids.json
  Generating story with anthropic...
  ✓ Story saved as story 3 (1043 words)
  File updated: muscle_amino_acids.json

$ st-read -s 3 muscle_amino_acids.json
[... 1043 word comprehensive analysis ...]
```

---

## Architecture

```
┌─────────────────────────────────────────────┐
│ User runs: st-speed --ai-caption report.json│
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  st-speed.py   │ Argument parsing
         │                │ Validates: only one option
         └────────┬───────┘
                  │
                  ▼
    ┌─────────────────────────┐
    │ build_ai_prompt()       │ Creates prompt for "caption"
    │ • Adds data table       │ with 100-160 word requirement
    │ • Adds requirements     │
    └─────────┬───────────────┘
              │
              ▼
  ┌───────────────────────────┐
  │ generate_ai_content()     │ Calls AI
  │ • process_prompt()        │ (uses ai_handler.py)
  │ • get_content()           │
  └─────────┬─────────────────┘
            │
            ▼
┌───────────────────────────┐
│ validate_ai_content()     │ Checks word count (100-160)
│ • Word count check        │ Checks for numbers
│ • Data presence check     │
└─────────┬─────────────────┘
          │
          ▼
  ┌───────────────┐
  │ Output to     │ Print to stdout
  │ stdout        │
  └───────────────┘
```

---

## Getting Help

1. **User questions:** See [README_AI_OPTIONS.md](README_AI_OPTIONS.md)
2. **Implementation:** See [IMPLEMENTATION_AI_OPTIONS.md](IMPLEMENTATION_AI_OPTIONS.md)
3. **Testing:** See [TESTING_AI_OPTIONS.md](TESTING_AI_OPTIONS.md)
4. **Reference code:** See [st-speed.py](st-speed.py)

---

## Contributing

When adding AI options to a tool:

1. Copy functions from `st-speed.py` (or use implementation guide)
2. Update argument parser with all five options
3. Customize `build_ai_prompt()` for your data
4. Keep validation and word counts identical
5. Add tests to `test_ai_options.sh`
6. Update this document's "Current Status" section

---

*This is an AI-oriented project. We need to be good at this.*

---

*Last Updated: March 19, 2026*

