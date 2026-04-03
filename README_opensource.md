# Cross: Open Source Transition Guide

This document tracks the work needed to transition Cross from a private
development repository to a clean, welcoming public open-source project.

---

## Status Overview

| Step | Status |
|------|--------|
| Rename repo to `cross` | ✅ Done |
| MIT license in place | ✅ Done |
| `.env` / `discourse.json` gitignored | ✅ Done |
| `cross-story` separated to its own repo | ✅ Done |
| CONTRIBUTING.md | ✅ Done |
| CHANGELOG.md | ✅ Done |
| CODE_OF_CONDUCT.md | ✅ Done |
| GitHub Issue Templates | ✅ Done |
| PR template | ✅ Done |
| CI workflow (`.github/workflows/tests.yml`) | ✅ Done — 55 tests pass |
| Fix `requirements.txt` dependency conflicts | ✅ Done |
| Migrate internal working files to `cross-internal` | ⬜ TODO — run `script/migrate_internal_docs.sh` |
| Make GitHub repo public | ⬜ TODO |
| Publish to PyPI as `cross-st` | ✅ Done — `cross-st 0.1.0` |

---

## The Core Problem: 50 Internal Working Files in Root

During active development, 50 working files accumulated in the project root.
These contain valuable institutional knowledge (design decisions, bug fixes,
implementation notes) but they clutter the public repo and are confusing to
new contributors.

**Best practice: move them to a private companion repository.**

---

## The Three-Repository Model

```
cross/           ← PUBLIC  — all source code, user docs, tests
cross-story/     ← PRIVATE — your personal story/report data
cross-internal/  ← PRIVATE — development notes, design decisions, internal docs
```

This is a well-established pattern:
- Linux kernel: public code + private vendor negotiations
- Many commercial open-source projects have a private "company" repo alongside the public one
- The public repo stays clean and contributor-friendly
- Institutional knowledge is preserved and version-controlled, just not public

---

## How to Create `cross-internal`

```bash
# 1. Create the private repo on GitHub (UI or gh CLI)
gh repo create b202i/cross-internal --private --description "Cross internal development notes"

# 2. Run the migration script (copies files to cross-internal, removes from cross)
bash script/migrate_internal_docs.sh

# 3. Commit the cleanup in the public repo
cd ~/github/cross
git add -A
git commit -m "Remove internal working files (moved to cross-internal)"
git push
```

The script `script/migrate_internal_docs.sh` automates moving the 50 files.
See that script for the exact list of files that move.

---

## Files Moving to `cross-internal`

### Bug fix logs (replace with GitHub Issues + CHANGELOG.md)
- `BUG_FIX_DOTENV_LOADING.txt`
- `BUG_FIX_SUMMARY.txt`
- `BUGFIX_STORY_STRUCTURE.md`
- `BUGFIX_st_fact_all_cached.md`

### Feature planning (replace with GitHub Issues + Projects)
- `FEATURE_AI_CAPTION.md`
- `FEATURE_fact_check_current_all_ai.md`
- `PHASE1_IMPLEMENTATION.md`

### Implementation / design notes
- `AI_CAPTION_AUTH_FIX.md`, `AI_CAPTION_FIX_SUMMARY.txt`
- `AI_CAPTION_FRAMEWORK_CLARIFICATION.md`, `AI_CAPTION_FRAMEWORK_VERIFICATION.txt`
- `AI_CAPTION_IMPLEMENTATION.txt`, `AI_CAPTION_NOTE.txt`, `AI_CAPTION_READY.txt`
- `AI_HUMAN_READABLE_FIX.md`
- `AI_OPTIONS_FIX_FILTER.md`, `AI_OPTIONS_INDEX.md`
- `AI_OPTIONS_STATUS.md`, `AI_OPTIONS_SUMMARY.md`
- `AI_SHORT_COMPLETE.txt`, `AI_SHORT_FEATURE.txt`
- `AI_SHORT_QUICKSTART.txt`, `AI_SHORT_TROUBLESHOOTING.txt`
- `AI_STORY_PROMPT_IMPROVEMENT.md`
- `IMPLEMENTATION_AI_OPTIONS.md`, `IMPLEMENTATION_error_handling.md`
- `KEY_CHOICE_at_symbol.md`
- `REFACTORING_COMPLETE.md`
- `WORD_COUNT_IMPROVEMENTS.txt`

### Testing notes
- `REGRESSION_TESTS_CAPTION.txt`, `REGRESSION_TESTS_SUMMARY.txt`
- `TESTING_AI_OPTIONS.md`, `TESTING_QUICKSTART.md`
- `TESTING_ROADMAP.md`, `TESTING_SUMMARY.md`

### Speed / timing working notes
- `ST_SPEED_COMPLETE.txt`, `ST_SPEED_ENHANCEMENT.md`
- `ST_SPEED_FINAL.txt`, `ST_SPEED_STATUS.md`
- `TIMING_QUICKREF.txt`, `TIMING_RERUN_ANSWER.md`
- `TIMING_RERUN_COMPLETE.txt`, `TIMING_VERSIONING_ISSUE.md`

### Historical / branding decisions
- `README_app_name.md`
- `README_namechange.md`
- `README_rebrand_cross.md`
- `README_yakyak.md`

---

## Files Staying in the Public Repo

These are user-facing or needed for contributors:

| File | Why public |
|------|-----------|
| `README.md` | Project landing page |
| `README_install.md` | New user install guide |
| `README_FAQ.md` | Troubleshooting |
| `README_AI_OPTIONS.md` | User feature docs |
| `README_AI_MANAGER.md` | User feature docs |
| `README_CACHE_CONTROL.md` | User feature docs |
| `README_cross_product.md` | User feature docs |
| `README_error_handling.md` | User feature docs |
| `README_error_examples.md` | User feature docs |
| `README_fetch.md` | User feature docs |
| `README_find.md` | User feature docs |
| `README_merge.md` | User feature docs |
| `README_post.md` | User feature docs |
| `README_speed_comparison.md` | User feature docs |
| `README_story_separation.md` | Architecture docs |
| `README_testing.md` | Contributor guide |
| `README_ui.md` | User feature docs |
| `README_license.md` | Legal |
| `README_devel.md` | Developer setup (→ fold into CONTRIBUTING.md eventually) |
| `AI_PROMPT_BEST_PRACTICES.md` | User tips |
| `AI_OPTIONS_QUICKSTART.md` | User quickstart |
| `AI_OPTIONS_COMMANDS.sh` | Reference |
| `COMMERCIAL_LICENSE.md` | Public commercial use policy |
| `CONTRIBUTING.md` | Contributor onboarding |
| `CHANGELOG.md` | Release history |
| `CODE_OF_CONDUCT.md` | Community standards |

---

## Standard Open Source Infrastructure

These are the files that every serious open source project has.
They make the project welcoming to contributors and discoverable on GitHub.

### CONTRIBUTING.md
Guidelines for contributors: dev setup, coding style, submitting PRs.
Currently covered partially by `README_devel.md` — fold that content in over time.

### CHANGELOG.md
One place to track what changed in each release.
Replaces the scattered `BUG_FIX_*.txt` and `*_COMPLETE.txt` files.
Follow [Keep a Changelog](https://keepachangelog.com) format.

### CODE_OF_CONDUCT.md
Standard Contributor Covenant. Required by GitHub for a green "community"
health score. Signals a welcoming project to potential contributors.

### .github/ISSUE_TEMPLATE/
Bug report and feature request templates.
These replace the `BUGFIX_*.md` and `FEATURE_*.md` working files —
GitHub Issues become the canonical tracker going forward.

### .github/pull_request_template.md
Checklist shown when a PR is opened.

### .github/workflows/tests.yml
Activate the existing `test.yml.template` as a real CI workflow.
Every PR runs `pytest` automatically — required for any credible open source project.

---

## Requirements Cleanup (fix before going public)

Current conflicts in `requirements.txt`:

**1. `wyoming==1.6.3`** — this version was yanked from PyPI.
Change to the next available version:
```
wyoming==1.7.0
```
Or remove if the Wyoming/Home Assistant voice pipeline integration is not
actively maintained.

**2. `google-auth==2.38.0`** — hard pin conflicts with `google-genai>=1.65.0`
which requires `google-auth>=2.47.0`. Remove the pin:
```
google-auth>=2.47.0
```

Run after fixing:
```bash
pip install -r requirements.txt
pip check   # verify no remaining conflicts
```

---

## Going Public on GitHub

When the repo is clean and ready:

1. GitHub → Settings → Danger Zone → **Change repository visibility → Public**
2. Add a repository **description**:  
   `"AI-powered cross-product fact-checking and story generation"`
3. Add **topics**: `ai`, `fact-checking`, `llm`, `discourse`, `cli`, `python`,
   `openai`, `anthropic`, `gemini`, `xai`, `perplexity`
4. Enable **Issues** and **Discussions** in Settings → Features
5. Pin the repo to your GitHub profile

---

## PyPI Publication

Cross is published on PyPI as `cross-st`:

1. Install with `pipx install cross-st` (recommended) or `pip install cross-st`
2. TTS variant: `pipx install "cross-st[tts]"`
3. First-time setup: `st-admin --setup`
4. GitHub Actions handles automated PyPI publishing on tagged releases

> **Note:** The PyPI package names `cross` and `cross-ai` were already taken.
> An inadvertent publish as `crossai-cli` was yanked. The canonical name is `cross-st`.

---

## Summary: Order of Operations

```
1. Fix requirements.txt conflicts            (10 min)
2. Create cross-internal repo on GitHub      (5 min)
3. bash script/migrate_internal_docs.sh      (5 min)
4. Activate .github/workflows/tests.yml      (15 min)
5. Review README.md — landing page for strangers?
6. GitHub → Settings → Change visibility → Public
7. Announce
```

---

## Related Docs

- [README_install.md](README_install.md) — Installation guide
- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [CHANGELOG.md](CHANGELOG.md) — Release history
- [README_license.md](README_license.md) — License details
- [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) — Commercial use policy
