# Changelog

All notable changes to Cross are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
Cross uses [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- `st-speed` — AI performance benchmarking with `--ai-caption`, `--ai-short`,
  `--ai-title`, `--ai-summary` options for AI-generated narrative
- `st-find` — keyword search across prompts, stories, and titles with
  multi-keyword AND/OR logic and context preview
- `st-fix --mode iterate` — iterative per-claim fixing: each claim is rewritten
  and immediately fact-checked before moving to the next
- `st-fact --ai all` — fact-check with all configured AI providers in parallel
- Timing data collected automatically during `st-cross` and `st-fact` runs
- `CONTRIBUTING.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`
- GitHub Issue Templates and PR template

### Fixed
- `st-bang` merge failure: "Warning: could not save … 'story'" when tmp files
  lacked a `story` key
- `st-analyze` crash on `KeyError: 'summary'` when no fact-checks present —
  now gives a friendly message suggesting `st-cross` first
- `st-read` numbers now rounded to one decimal place
- `ModuleNotFoundError: No module named 'pkg_resources'` in `textstat` —
  resolved by pinning `setuptools` in `requirements.txt`
- `st-fix --mode iterate` `UnboundLocalError: fc_ai_model` when all claims
  were skipped
- `st-speed` AI calls now go through `ai_handler.py` (caching, .env keys,
  error handling) instead of direct SDK calls
- `ai_gemini.py` `TypeError: 'str' object does not support item assignment`
  in `put_content`

### Changed
- `st-fix`: post-fix fact-check now scoped to changed claims only, not the
  entire document (avoids inflating the false-claim count)

### Known Issues
- `requirements.txt`: `wyoming==1.6.3` is yanked; `google-auth==2.38.0`
  conflicts with `google-genai>=1.65.0`. Fix: see `README_opensource.md`.

---

## [0.1.0] — 2025-03-01 (initial private release)

### Added
- `st-gen` — generate a story from a `.prompt` file using a selected AI
- `st-bang` — generate stories from all 5 AI providers in parallel
- `st-cross` — cross-product fact-check: every AI fact-checks every story
- `st-fact` — fact-check a specific story
- `st-merge` — synthesize the best-scoring stories into one
- `st-fix` — rewrite false/partial claims using AI
- `st-analyze` — statistical analysis and visualization of fact-check results
- `st-edit` — view and edit story text in terminal or markdown
- `st-read` — readability metrics table (Flesch-Kincaid, Gunning Fog, etc.)
- `st-ls` — list stories and fact-checks in a JSON container
- `st-cat` — cat raw story text to stdout
- `st-post` — post stories to Discourse with optional audio attachment
- `st-speak` / `st-voice` — generate MP3 audio from story text
- `st-fetch` — fetch and summarize web content into a prompt
- `st-new` — create a new prompt from the default template
- `st-rm` — remove a story from a container
- `st-heatmap` — render fact-check score heatmap
- `st-plot` — plot fact-check scores
- `st` — interactive TUI menu
- Support for 5 AI providers: xAI (Grok), Anthropic (Claude),
  OpenAI (GPT-4o), Perplexity (Sonar), Google (Gemini)
- API response caching (`api_cache/`) with `--cache` / `--no-cache` flags
- `.env`-based API key management
- Discourse multi-site posting support

