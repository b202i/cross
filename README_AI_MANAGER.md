# README_AI_MANAGER.md — AI Model Management in CrossAI

## Overview

AI is the defining moving part of CrossAI.  New models ship weekly, pricing
changes, capabilities improve, and occasionally a provider retires a model with
no warning.  This document captures the current model-management architecture,
its limitations, and the design of a proper **AI Manager** that lets the user
stay current without editing Python source files.

---

## The Problem Today

Every AI make has its active model hard-coded as a module-level constant:

```python
# ai_anthropic.py
AI_MODEL = "claude-opus-4-5"

# ai_gemini.py
AI_MODEL = "gemini-2.5-flash"

# ai_openai.py
AI_MODEL = "gpt-4o"

# ai_perplexity.py
AI_MODEL = "sonar-pro"

# ai_xai.py
AI_MODEL = "grok-4-1-fast-reasoning"
```

These constants are read at import time by `BaseAIHandler.get_model()` and flow
into every AI call through `AI_HANDLER_REGISTRY` in `ai_handler.py`.

### Consequences

| Symptom | Root cause |
|---------|------------|
| Changing a model requires editing a `.py` file | Model is a source constant |
| No runtime visibility into which model is active | No central display |
| Switching to a faster/cheaper model for bulk work requires a code change | Same |
| Discovering available models requires reading docs or source comments | No query tool |
| A retired model causes silent failures at runtime | No staleness check |
| Cross-product runs mix models if files are edited mid-session | No session lock |

---

## Current Architecture

```text
.env  (API keys only — no model config today)
    |
ai_handler.py  ->  AI_HANDLER_REGISTRY  ->  ai_<make>.py
                                                AI_MODEL (constant)
                                                get_model() -> returns constant
```

`AI_LIST` in `ai_handler.py` controls which makes are active.
`AI_MODEL` in each `ai_<make>.py` controls which model that make uses.
There is no runtime override path today.

---

## Proposed AI Manager

### Goals

1. **See** the active model for every make with one command
2. **Change** the model for one make without editing source
3. **List** available models for a make, pulled from the provider API
4. **Validate** that the configured model still exists before a run
5. **Lock** models for a session so a long cross-product run is consistent
6. **Restore** defaults easily

### Configuration file: `.ai_models`

A new plain-text config file at the project root, alongside `.env`:

```env
# .ai_models — active model overrides
# Format: <make>=<model>
# Blank lines and # comments are ignored.
# Missing entries fall back to the compiled-in default in ai_<make>.py.

anthropic=claude-opus-4-5
gemini=gemini-2.5-flash
openai=gpt-4o
perplexity=sonar-pro
xai=grok-4-1-fast-reasoning
```

Rules:

- If `.ai_models` does not exist, every make uses its compiled-in default
- An entry in `.ai_models` overrides the source constant at runtime
- `.ai_models` is committed to git so model choices travel with the project
- `.ai_models.local` (gitignored) can hold per-machine overrides

### Override lookup order (highest to lowest priority)

```text
1. --model flag on the CLI           (per-command, one-shot)
2. .ai_models.local                  (per-machine override, gitignored)
3. .ai_models                        (project default, committed)
4. AI_MODEL constant in ai_<make>.py (compiled-in fallback)
```

---

## New Module: `ai_manager.py`

Single module that owns all model-management logic.

```python
# ai_manager.py

from pathlib import Path

MODELS_FILE       = Path(".ai_models")
MODELS_FILE_LOCAL = Path(".ai_models.local")


def get_active_model(make: str, cli_override: str = None) -> str:
    """
    Return the model to use for a given make, respecting the override chain.
    Priority: CLI flag > .ai_models.local > .ai_models > compiled-in default
    """
    if cli_override:
        return cli_override
    for config in (MODELS_FILE_LOCAL, MODELS_FILE):
        model = _read_model_from_file(config, make)
        if model:
            return model
    from ai_handler import AI_HANDLER_REGISTRY
    return AI_HANDLER_REGISTRY[make].get_model()


def set_active_model(make: str, model: str, local: bool = False) -> None:
    """Write a model override to .ai_models (or .ai_models.local)."""
    target = MODELS_FILE_LOCAL if local else MODELS_FILE
    _write_model_to_file(target, make, model)


def list_active_models() -> dict:
    """Return {make: model} for all registered makes."""
    from ai_handler import AI_LIST
    return {make: get_active_model(make) for make in AI_LIST}


def reset_model(make: str, local: bool = False) -> None:
    """Remove override for a make, restoring compiled-in default."""
    target = MODELS_FILE_LOCAL if local else MODELS_FILE
    _write_model_to_file(target, make, None)


def validate_models() -> list:
    """
    Check that each configured model is still listed as available.
    Returns a list of warning strings (empty list = all OK).
    """
    warnings = []
    from ai_handler import AI_LIST
    for make in AI_LIST:
        model = get_active_model(make)
        available = _fetch_available_models(make)
        if available and model not in available:
            warnings.append(
                f"  {make}: '{model}' not in available models -- "
                f"run 'st-ai --list {make}' to see current options"
            )
    return warnings


def _read_model_from_file(path: Path, make: str):
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            k, _, v = line.partition("=")
            if k.strip() == make and v.strip():
                return v.strip()
    return None


def _write_model_to_file(path: Path, make: str, model):
    lines = path.read_text().splitlines() if path.exists() else []
    new_lines = []
    found = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"{make}=") or stripped.startswith(f"{make} ="):
            if model:
                new_lines.append(f"{make}={model}")
            found = True
        else:
            new_lines.append(line)
    if not found and model:
        new_lines.append(f"{make}={model}")
    path.write_text("\n".join(new_lines) + "\n")


def _fetch_available_models(make: str) -> list:
    """
    Best-effort: fetch available model IDs from the provider API.
    Returns [] if the provider does not support a model-list endpoint.
    """
    fetchers = {
        "anthropic":  _models_anthropic,
        "openai":     _models_openai,
        "gemini":     _models_gemini,
        "perplexity": _models_perplexity,
        "xai":        _models_xai,
    }
    fn = fetchers.get(make)
    if fn is None:
        return []
    try:
        return fn()
    except Exception:
        return []
```

### Model-list fetcher stubs — how each provider exposes its models

| Make | Live endpoint | Notes |
|------|---------------|-------|
| `anthropic` | none | curated static list from source comment |
| `openai` | `GET /v1/models` | `client.models.list()` — SDK supported |
| `gemini` | `GET /v1beta/models` | `client.models.list()` — SDK supported; see `list_gemini_models.py` |
| `perplexity` | none | curated static list from source comment |
| `xai` | `GET /v1/models` | OpenAI-compatible; `client.models.list()` |

`list_gemini_models.py` already exists in the project and demonstrates the
Gemini live-list pattern; the same approach applies to OpenAI and xAI.

---

## New CLI tool: `st-ai`

A new top-level command for model management, following the existing `st-*` style.

```text
st-ai                                    # show active model for every make
st-ai --list anthropic                   # list available models from provider API
st-ai --list all                         # list models for all makes
st-ai --set anthropic claude-sonnet-4-5  # override model for this make
st-ai --reset anthropic                  # remove override, restore default
st-ai --reset all                        # reset all overrides
st-ai --validate                         # check all configured models still exist
st-ai --local                            # apply --set/--reset to .ai_models.local
```

### Example session

```text
$ st-ai
  make        model                     source
  ──────────────────────────────────────────────────────
  xai         grok-4-1-fast-reasoning   .ai_models
  anthropic   claude-opus-4-5           .ai_models
  openai      gpt-4o                    .ai_models
  perplexity  sonar-pro                 compiled-in
  gemini      gemini-2.5-flash          compiled-in

$ st-ai --list openai
  Available OpenAI models (text generation):
    gpt-4o              <- active
    gpt-4o-mini
    o3
    o3-mini
    o4-mini
    gpt-4.5-preview

$ st-ai --set openai o3
  openai model set to: o3  (written to .ai_models)

$ st-ai --validate
  All configured models are available.
```

---

## Integration into `ai_handler.py`

A small change to `process_prompt()` and `get_ai_model()` makes the override
transparent to every caller — no `st-*` script needs to change:

```python
# ai_handler.py  (change summary)

from ai_manager import get_active_model

def process_prompt(ai_key: str, prompt: str, verbose: bool, use_cache: bool,
                   model_override: str = None):
    handler_cls = AI_HANDLER_REGISTRY.get(ai_key)
    model = get_active_model(ai_key, cli_override=model_override)
    payload = handler_cls.get_payload(prompt, model=model)
    ...

def get_ai_model(ai_key: str, cli_override: str = None) -> str:
    return get_active_model(ai_key, cli_override=cli_override)
```

Each `ai_<make>.py` payload builder will accept an optional `model=` kwarg
so the override can be passed through.  The existing `AI_MODEL` constant
becomes the default value of that kwarg — no behaviour changes if
`ai_manager` is not in use.

---

## Integration into `st.py` — Settings menu

A new top-level `x: Settings` entry appears in the Main menu alongside
Generate, View, Edit, Analyze, Post, and Utility.  Settings is the place
where the user can inspect and change any persistent configuration without
leaving the interactive shell or editing files by hand.

```text
=== Main Menu ===
...
x: Settings

=== Settings Menu ===
a: View active AI models (all makes)
m: Set AI model for current make
v: View active TTS voice
V: Set TTS voice (launch st-voice)
t: View default prompt template
T: Set default prompt template
e: View editor setting
E: Set editor ($EDITOR or vi)
s: Show all current settings

esc: Escape back to the previous menu
?: Display this menu
ASF: Next AI, Story, Fact
```

### What each Settings command does

| Key | Action | Persisted to |
|-----|--------|-------------|
| `a` | Print `make → model` table for all makes | — (read-only) |
| `m` | Prompt for new model name for the current make | `.ai_models` |
| `v` | Print current TTS voice from `.env` | — (read-only) |
| `V` | Launch `st-voice` for interactive voice testing and selection | `.env` via st-voice |
| `t` | Print current `DEFAULT_TEMPLATE` from `.env` | — (read-only) |
| `T` | Prompt for template name, write to `.env` | `.env` |
| `e` | Print current editor (`EDITOR` env var or `vi`) | — (read-only) |
| `E` | Prompt for editor name, write to `.env` and `$EDITOR` | `.env` |
| `s` | Print a full summary table of all settings | — (read-only) |

### Example `s` (show all) output

```text
  Setting                 Value
  ──────────────────────  ────────────────────────────────────
  AI xai                  grok-4-1-fast-reasoning
  AI anthropic            claude-opus-4-5
  AI openai               gpt-4o
  AI perplexity           sonar-pro
  AI gemini               gemini-2.5-flash
  TTS voice               en_US-lessac-medium
  Default template        default
  Editor                  vi
```

### Settings state and persistence

Settings are read from two sources at startup:

- **`.env`** — TTS voice, editor, default template (read via `python-dotenv`)
- **`.ai_models`** — one `make=model` line per AI make (read by `settings_get_ai_model()`)

Changes made in the Settings menu are written back immediately:
- AI model changes → `.ai_models` in the project root
- All other changes → `.env` via `python-dotenv set_key()`

The running process environment is also updated so the change takes effect
immediately without restarting `st`.

---

## Integration into `st-bang` / `st-cross` — session lock

For multi-AI parallel runs, all jobs must use the same model snapshot.
A `--lock-models` flag snapshots `.ai_models` into `.ai_models.lock` at
run start and reads exclusively from that file for the duration.

```text
st-bang --lock-models my_topic.json    # lock models for this bang run
st-cross --lock-models my_topic.json   # lock for cross-product
```

The lock file is deleted on clean exit and retained on Ctrl-C so the user
can inspect which models were active when the run was interrupted.

---

## `.gitignore` additions

```gitignore
.ai_models.local    # per-machine overrides — do not commit
.ai_models.lock     # session lock file — do not commit
```

`.ai_models` itself **is** committed — it is the project's canonical model
selection and should travel with the repo between machines.

---

## Files to Create or Change

| File | Action | Notes |
|------|--------|-------|
| `.ai_models` | **New file** | Project-default model overrides, committed to git |
| `ai_manager.py` | **New file** | Core override logic, model-list fetchers, validation |
| `st-ai.py` | **New file** | `st-ai` CLI command |
| `ai_handler.py` | Update | `process_prompt()` and `get_ai_model()` consult `ai_manager` |
| `ai_anthropic.py` | Minor | `get_payload()` accepts optional `model=` kwarg |
| `ai_gemini.py` | Minor | Same |
| `ai_openai.py` | Minor | Same |
| `ai_perplexity.py` | Minor | Same |
| `ai_xai.py` | Minor | Same |
| `st.py` | Update | Add `x: Settings` top-level menu; settings helper functions |
| `st-bang.py` | Update | Add `--lock-models` flag |
| `st-cross.py` | Update | Add `--lock-models` flag |
| `.gitignore` | Update | Add `.ai_models.local` and `.ai_models.lock` |
| `README_FAQ.md` | Update | Add "How do I change the AI model?" FAQ answer |

---

## What Does NOT Change

- `AI_MODEL` constants in each `ai_<make>.py` remain as compiled-in fallbacks
- `AI_HANDLER_REGISTRY` and `AI_LIST` in `ai_handler.py` are unchanged
- The `--ai` flag on all `st-*` commands (selects the make) is unchanged
- All `.json` container metadata records the actual make **and model** used,
  regardless of how the override was applied — the record is always accurate
- The `api_cache/` hash includes the model name, so a model change correctly
  bypasses cached responses generated by the previous model

---

## Open Questions

1. **`--model` CLI flag on every command** — Should every `st-*` command
   accept `--model` for a one-shot per-command override?  Or is
   `.ai_models` plus `st-ai --set` sufficient for most workflows?
2. **Static lists for Anthropic and Perplexity** — Neither provider exposes
   a live model-list endpoint.  The `--list` output will be a curated static
   list from the source comment.  Acceptable, or should a docs-page fetch
   be added?
3. **Model capability metadata** — Should `st-ai --list` show context window
   size, cost tier, and multimodal support alongside the model name?
   Useful for choosing between models but adds maintenance burden.
4. **Auto-suggest on 404** — Should CrossAI detect a "model not found" error
   and automatically suggest the nearest available model via `st-ai --list`?
5. **Provider deprecation headers** — Some providers return a deprecation
   warning header before retiring a model.  Should `ai_manager` surface
   these warnings to the user at call time?

