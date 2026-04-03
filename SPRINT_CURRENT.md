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
| A9 | Publish to PyPI as `cross-ai` | 🔲 Next |

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

## A9 — Publish to PyPI 🔲

**Prerequisites: B3 done, working tree clean, no hardcoded secrets.**

### Step 0 — Tests

```bash
pytest                        # all tests must pass
pytest --tb=short -q          # compact output
```

Fix any failures before proceeding. Do not publish a broken package.

### Step 1 — README cleanup

Before going public, audit the repo root for accuracy:
- `README.md` developer setup section still references `bash script/symbolic_links.bash` — update to `pip install -e .`
- Verify quick-start commands work end-to-end from a fresh clone

### Step 2 — Orphan the git history

The private development history contains a committed `.env` file (removed in commit `5613b4a`) and commits that touched `API_KEY` strings. **Do not make the repo public with this history.**

```bash
cd ~/github/cross

# 1. Verify the working tree is clean
git status

# 2. Audit for any hardcoded secrets
grep -r "API_KEY\s*=\s*[a-zA-Z0-9]" --include="*.py" --include="*.toml" --include="*.md" .

# 3. Create an orphan branch — no history
git checkout --orphan clean-main
git add -A
git commit -m "Initial public release v0.1.0"

# 4. Replace main and force-push (wipes all history on GitHub)
git branch -D main
git branch -m main
git push --force origin main
```

Safe because: the repo is currently **private**; `.env`, `api_cache/`, `tmp/` are all gitignored.

### Step 3 — Build and verify

```bash
pip install build twine
python -m build
twine check dist/*
```

Confirm `dist/` contains both `.tar.gz` and `.whl`. Confirm `twine check` passes with no warnings.

### Step 4 — Test install from wheel (optional but recommended)

```bash
python3.11 -m venv /tmp/cross-test-venv
source /tmp/cross-test-venv/bin/activate
pip install dist/cross_ai-0.1.0-py3-none-any.whl
st-admin --help
st-gen --help
deactivate
rm -rf /tmp/cross-test-venv
```

### Step 5 — Publish to PyPI

```bash
twine upload dist/*
```

Package name on PyPI: **`cross-ai`**. Confirm at `https://pypi.org/project/cross-ai/`.

---

## Post-deploy checklist

After `twine upload` succeeds, do these in order:

1. **Make repo public** — GitHub → Settings → Danger Zone → Change visibility → Public
2. **Publish wiki** — `bash script/push_wiki.sh` (pushes `docs/wiki/` to the GitHub Wiki)
3. **Verify pipx install works** from a clean environment:
   ```bash
   pipx install cross-ai
   st-admin --setup
   st --help
   ```
4. **Tag the release** — `git tag v0.1.0 && git push origin v0.1.0`
5. **Update CHANGELOG.md** with release date and summary

---

## Commit message format

```
[dist] B3: CROSS_NO_CACHE=1 env var in all AI handlers
[dist] A9: publish cross-ai 0.1.0 to PyPI
```

---

# BACKLOG

Post-A9, in rough priority order:

- [ ] **B4** `st-admin --cache-info` / `--cache-clear` / `--cache-cull DAYS` — print path, file count, total size; delete all or entries older than N days
- [ ] **B6** Windows/WSL2 install docs in `docs/wiki/Onboarding.md`
- [ ] `st-admin --upgrade` — upgrade `cross-ai` from PyPI and platform tools in one command
- [ ] `--parallel` flag for `st-cross` — run fact-checks for a given model in parallel; needs per-provider rate-limit logic
- [ ] Add cooking/baking domain to Cross-Stones benchmark (prompt + 10 test cases)
- [ ] Upgrade `st-man` one-line command descriptions (currently sparse)
