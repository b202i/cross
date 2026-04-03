# st-merge — Design Notes & Roadmap

## Current state (v1)

`st-merge` takes N stories from a `.json` container and asks one AI to synthesize
them into a single master story. It is a straightforward "give everything to the AI
and let it figure it out" approach. It works, but it is blind to fact-check quality —
it treats a False claim from one AI the same as a True claim from another.

---

## The core insight: merge should be quality-aware

The cross-product gives us up to 25 fact-check reports. Each segment in each story
has been assessed by up to 5 AI. We know, for every sentence, which AI got it right
and which got it wrong. A quality-blind merge wastes that information entirely.

**The ideal merged story:**
- For each topic/claim, takes the version that the most AI fact-checkers rated True
- Discards or replaces versions rated False or Partially_false
- Stitches the selected passages into coherent prose

This is exactly what `st-fix --mode synthesize` begins to do — but at the story
level, not the claim level. `st-merge` should eventually operate at the claim level.

---

## The single-voice principle

The highest-scoring story earned its score for two reasons: it wrote accurately
**and** it expressed ideas clearly. Asking a different AI to rewrite it introduces
a voice conflict — the correction source imposes its style on the best author's work.

**The solution:** the AI that wrote the best story performs the rewrite.

- It already knows the topic, structure, and narrative arc
- It knows its own voice — sentence rhythm, hedging style, paragraph length
- It is told: *"This is your story. Here are the corrections. Rewrite it in your voice."*
- Corrections from other AI are provided as **facts to express**, not prose to copy

The result is a single consistent voice from first word to last, with accuracy
lifted by the cross-product fact-check data.

**In `st-merge` quality mode:** `args.ai` is automatically overridden to match
the `make` field of the base story after base-story selection. `--ai` only
applies in simple mode or when there is no fact-check data.

---

## Two merge modes — both are valid

### Mode 1: `simple` (no fact-check required)
The current behavior. Give all N stories to an AI and ask it to synthesize.

**When to use:** No fact-check data exists yet. Fast, zero extra cost, good for
a first pass or when the topic is low-stakes.

**Limitation:** The AI synthesizer may confidently merge False claims from multiple
stories, compounding errors rather than eliminating them.

### Mode 2: `quality` (uses fact-check data)
Uses structured claims/segments data to guide the merge. For each segment in the
target story, the AI is shown the verdicts from all checkers and the alternative
versions from other stories, and is asked to select or synthesize the best-supported
version.

**When to use:** After `st-cross` has run. Produces the highest-quality output.

**Limitation:** Requires fact-check data. Takes longer. More tokens.

**Auto-selection rule (so the user doesn't have to decide):**
- If `claims` data exists on the stories → use `quality-v2` mode (verdict-annotated, segment-level)
- If only scores exist (older fact-checks) → use `quality-v1` mode (score-weighted)
- If no fact-check data at all → fall back to `simple` mode with a note to the user

---

## User control philosophy

> "Generally users do not want to make decisions and just want the software to
> do the right thing."

This is the right instinct. The design should be:

```
st-merge file.json               # smart default: quality if data exists, simple otherwise
st-merge --simple file.json      # force simple merge (ignore fact-check data)
st-merge --quality file.json     # force quality merge (fail if no fact-check data)
st-merge --ai anthropic file.json  # choose the synthesizer AI
st-merge --stories 1 2 3 file.json # merge a subset of stories
```

That is five flags total. Most users will only ever type `st-merge file.json`.

---

## How quality merge works — step by step

### Step 1 — Collect segments for each story
Each story either has `story["segments"]` already (if `st-fact` was run with the
new structured format) or segments are built on-the-fly from `story["text"]` using
`build_segments()` from `mmd_util.py`. This is already implemented.

### Step 2 — Collect verdicts per segment
For each segment, look at `story["fact"][n]["claims"]` for all fact entries on that
story. If multiple fact-checks exist, aggregate: a segment is "True" if a majority
of checkers rated it True or Opinion.

Verdict priority for selection:
```
True        → include, high confidence
Opinion     → include, medium confidence (opinion claims are not wrong)
Partially_true → include with caution, flag for rewrite
Partially_false → exclude from direct use, provide as context only
False       → exclude, provide correct version from other stories if available
```

### Step 3 — Cross-story lookup for weak segments
For each segment rated Partially_false or False in story N:
1. Find segments in stories 1–5 that cover the same claim
   (currently: prompt-based; future: embedding-based)
2. Score each candidate by its True-count across all checkers
3. Provide the top candidate(s) to the synthesizer as "preferred source"

### Step 4 — Synthesis prompt
Provide the synthesizer AI with:
- The target story (highest-scoring story by average fact-check score)
- A structured list of segments with verdicts and alternatives
- Instruction: "Keep True/Opinion segments. Replace False/Partially_false
  segments using the preferred source versions provided. Stitch into
  coherent prose."

### Step 5 — Post-merge fact-check (optional, recommended)
Run `st-fact` on the merged story automatically and show a before/after score
comparison. This closes the loop and confirms quality actually improved.

---

## Choosing the target story (base story)

The synthesizer needs a structural backbone — one story that provides the
narrative flow, section order, and voice. The others contribute corrected facts.

**Auto-selection rule:**
- Use the story with the highest average fact-check score across all checkers
- If no fact-check data, use story 1 (or the first story in `--stories`)
- Allow `--base N` to override

---

## Data structure requirements

`st-merge` quality mode works best with structured claims. It degrades gracefully
without them (falls back to simple mode). The structured claims work described in
`st-fix.py` design notes is a prerequisite for full quality-merge capability.

Current status of structured claims:
- `story["segments"]` — implemented in `mmd_util.py` (`build_segments()`)
- `story["fact"][n]["claims"]` — partially implemented; `st-fact` populates
  when the new structured format is used

For now, `st-merge` quality mode can operate at the **paragraph level** using
the existing `fact["report"]` string (parsed with the existing regex), while
the segment/claims migration is completed. This is not ideal but functional.

---

## Merge credit tag

The merge credit string uses the `cross:` prefix:
```
cross:st-merge:xai:grok-4-latest,anthropic:claude-opus-4-5,...
```

This records which AI contributed source material and which AI
performed the synthesis.

For quality mode, the mode is included in the tag:
```
cross:st-merge:quality:anthropic:claude-opus-4-5 ← synthesizer
  sources: xai:grok-4-latest,anthropic:claude-opus-4-5,...
```

---

## Implementation plan

### Phase 1 — Clean up current simple mode ✓ 2026-03-05
- [x] Add header documentation following project style
- [x] Rename `yakyak:` → `cross:` in merge credit (T-01)
- [x] Add `--simple` / `--quality` flags (quality falls back to simple gracefully)
- [x] Auto-select base story by highest avg fact-check score when data exists
- [x] Print which mode is being used and why
- [x] Add progress output during AI call

### Phase 2 — Quality mode, paragraph/segment level ✓ 2026-03-05
- [x] `collect_verdicts()` — aggregate all fact-check verdicts per seg_id
- [x] `find_best_alternative()` — prompt-based cross-story lookup for weak segments
- [x] `get_quality_prompt_v2()` — verdict-annotated prompt with PREFERRED REPLACEMENT
- [x] Auto-detect claims data; fall back to score-only (v1) if claims are absent
- [x] `--post-check` / `--no-post-check` flags
- [x] Post-merge fact-check with before/after score comparison table
- [x] Merge credit tag records quality-v2 vs quality-v1 vs simple

### Phase 3 — Quality mode, claim/segment level (after structured claims are complete)
- [ ] Use `story["segments"]` and `fact["claims"]` directly (no parsing)
- [ ] Cross-story segment alignment via prompt or embedding
- [ ] Aggregate verdicts across all 5×5 fact-check entries
- [ ] Select best-supported version per claim, assemble, coherence pass

---

## Relationship to st-fix

`st-fix --mode synthesize` and `st-merge --quality` overlap in intent but differ
in scope:

| | `st-fix --mode synthesize` | `st-merge --quality` |
|---|---|---|
| Input | All stories in container | Selected stories (default: all) |
| Unit of work | Story level | Segment/claim level (Phase 3) |
| Output | Fixed version of one story | New synthesized master story |
| Post-check | Optional | Recommended, auto |
| Primary goal | Improve a specific story | Best possible single story |

They can coexist. `st-fix synthesize` is the current best tool. `st-merge quality`
will eventually be better because it operates at finer granularity.

---

## Summary

| Question | Answer |
|---|---|
| Do we use fact-check data in st-merge? | Yes — quality mode; auto-detected |
| What if no fact-check data? | Falls back to simple mode automatically |
| How much user control? | Minimal — one command works; flags available for power users |
| What is the right default? | Auto-select mode, auto-select base story, auto post-check |
| What needs to be built first? | Phase 1 cleanup; Phase 2 quality at paragraph level |
| What is the long-term goal? | Claim-level assembly (Phase 3) for near-perfect scores |

