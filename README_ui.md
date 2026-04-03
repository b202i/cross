# The User Interface

Yakyak Social is a command-line toolkit. The `st` command provides an interactive menu
that builds and fires the underlying `st-*` commands. You can also run any `st-*` command
directly in the terminal — the menu is a convenience, not a requirement.

Start with: `st story_file.json` (or `.prompt` to generate on first run).

---

## Main Menu

```
g: Generate
v: View
e: Edit
a: Analyze
p: Post
u: Utility

esc: back  ?: show menu  ASF: next Ai / Story / Fact

st ai:xai s:1 f:1 Main>
```

---

## Submenus

**Main>Generate**
```
g: Generate and prep a story from a prompt
e: Edit a prompt file
s: Spell check a prompt file
b: Parallel generate all AI stories (Bang!)
B: Parallel generate all AI and merge
m: Merge stories 1-5 into a master story
```

**Main>View**
```
v: View story with browser
s: List stories
l: List stories and fact-checks
a: List all contents of .json file
f: List fact-checks
F: Edit a fact-check
```

**Main>Edit**
```
T: Edit title
m: Edit markdown
M: Edit markdown with browser view
v: View story with browser
s: Edit spoken
t: Edit text
f: Edit fact-check
x: Fix a story using fact-check feedback
```

**Main>Analyze**
```
f: Fact-check current story, current AI
F: Fact-check all stories, current AI
@: Fact-check current story, all AI
c: Cross-product fact-check — all stories × all AI
C: Generate Cross-Product report
v: View fact-check
r: Show reading metrics
R: Show reading metrics with legend
```

**Main>Post**
```
n: Rotate next social media site
p: Post story
a: Post story with mp3 audio
f: Post fact-check
l: Preview list of all mp3 audio
L: Post list of all mp3 audio
v: Preview post
```

**Main>Utility**
```
p: View all Cross-Product plots
P: Save all Cross-Product plots
r: Remove story (and fact-checks)
R: Remove fact-check
v: Speak story aloud with current voice
V: Render current voice to mp3 file
```

---

## Conventions

| Pattern | Meaning |
|---|---|
| lowercase | Read-only, generate, or single-item action |
| UPPERCASE | Mutating, bulk, or export action |
| `f` / `F` | Single / all — e.g. fact-check one story vs. all stories |
| `c` / `C` | Run / report — e.g. run cross-product vs. generate its report |
| `p` / `P` | View / save — e.g. view plots vs. save plots to file |
| `r` / `R` | Context-dependent: Analyze → reading metrics / metrics with legend; Utility → remove story / remove fact-check |
| `esc` | Return to previous menu |
| `?` | Display current menu |
| `A S F` | Cycle to next AI / Story / Fact-check |

---

## Workflow

The main menu is ordered top-to-bottom for a typical session:

```
Generate → View → Edit → Analyze → Post
```

1. **Generate** — create stories from a prompt using one or all AIs
2. **View** — browse and list stories and fact-checks
3. **Edit** — refine titles, text, or fix a story using fact-check feedback
4. **Analyze** — fact-check stories, run cross-product, generate reports and reading metrics
5. **Post** — publish to a Discourse site with optional audio
6. **Utility** — less-frequent tasks: plots, remove items, speak or render audio
