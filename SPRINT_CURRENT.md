# SPRINT_CURRENT.md — PyPI Distribution Sprint

> **For AI coding agents working in this repo.**  
> Full design rationale lives in the companion private repo `../cross-internal/distribution/TASK_INDEX.md`.  
> Update `../cross-internal/SPRINT_BACKLOG.md` when tasks are completed.

---

## Status snapshot (2026-04-03)

A1–A8, B1, B2, B3, B5, C1 all complete. Ready for PyPI publish.

| Task | Description | Status |
|------|-------------|--------|
| B3 | `CROSS_NO_CACHE=1` env var support in all AI handlers | ✅ Done — cross-ai-core 0.4.1 |
| A9 | Publish to PyPI as `cross-ai` | 🟡 In progress — Step 3 next |

---

## B3 — `CROSS_NO_CACHE=1` env var 🟡 BLOCKER

Honor `CROSS_NO_CACHE=1` set in `~/.crossenv` or `.env` without requiring per-command `--no-cache` flags.

**Where to implement:** each AI handler's `get_cached_response()` in the **`cross-ai-core`** repo (`~/github/cross-ai-core/cross_ai_core/`), not in this repo.

```python
# In get_cached_response() of every ai_*.py handler — add before reading cache:
if os.environ.get("CROSS_NO_CACHE"):
    return None
```

After implementing, bump the version in `cross-ai-core/pyproject.toml` and reinstall:
```bash
pip install -e ../cross-ai-core/
```

**Verify:**
```bash
CROSS_NO_CACHE=1 st-gen my_topic.prompt   # must call API, not return cached response
```

---

## A9 — Publish to PyPI

**Prerequisites: B3 done, working tree clean, no hardcoded secrets.**

### Pre-publish

- [x] **Step 0** — Tests: 411 passed, 57 skipped
- [x] **Step 1** — README cleanup: slug updated, `symbolic_links.bash` → `pip install -e .`, Project Structure corrected
- [x] **Step 2** — Orphan history: single-commit `Initial public release v0.1.0` force-pushed; no secrets in tree
- [x] **Step 3** — Build and verify: clean build, `twine check` PASSED on both artifacts; fixed license format + bumped cross-ai-core min to 0.4.1
- [x] **Step 4** — Test install from wheel: `INSTALL_EXIT:0`, `st-admin --help` ✓, `st-gen --help` ✓
- [x] **Step 5** — Published as `crossai-cli` (cross-ai name was squatted; crossai blocked by similarity): https://pypi.org/project/crossai-cli/0.1.0/

### Post-deploy

- [ ] Make repo public — GitHub → Settings → Danger Zone → Change visibility → Public
- [ ] Publish wiki — `bash script/push_wiki.sh`
- [ ] Verify pipx install: `pipx install crossai-cli && st-admin --setup && st --help`
- [ ] Tag the release — `git tag v0.1.0 && git push origin v0.1.0`
- [ ] Update `CHANGELOG.md` with release date and summary

---

## Commit message format

```
[dist] B3: CROSS_NO_CACHE=1 env var in all AI handlers
[dist] A9: publish cross-ai 0.1.0 to PyPI
```

---

# BACKLOG

Post-A9, in rough priority order:

- [ ] **B7** Rename `cross-ai-core` → `crossai-core` on PyPI to match the crossai.dev brand (publish new name, update dependency in `crossai-cli`)
- [ ] **B4** `st-admin --cache-info` / `--cache-clear` / `--cache-cull DAYS` — print path, file count, total size; delete all or entries older than N days
- [ ] **B6** Windows/WSL2 install docs in `docs/wiki/Onboarding.md`
- [ ] `st-admin --upgrade` — upgrade `cross-ai` from PyPI and platform tools in one command
- [ ] `--parallel` flag for `st-cross` — run fact-checks for a given model in parallel; needs per-provider rate-limit logic
- [ ] Add cooking/baking domain to Cross-Stones benchmark (prompt + 10 test cases)
- [ ] Upgrade `st-man` one-line command descriptions (currently sparse)
