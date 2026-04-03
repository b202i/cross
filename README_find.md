# st-find — Search Stories and Prompts

`st-find` is a powerful search tool for finding keywords in your story containers (`.json`) and prompt files (`.prompt`). It supports wildcards, boolean operators, and can search specific fields or entire documents.

---

## Quick Start

```bash
# Simple keyword search (all fields)
st-find pizza -t

# Boolean AND (both required, no quotes!)
st-find +pizza +dough -t

# Boolean NOT (exclude keywords)
st-find +camping ^RV ^electric -t

# Boolean OR (either matches)
st-find bike bicycle -t

# Wildcards (quotes needed)
st-find "bike*" -t

# Search specific file
st-find +pizza +dough pizza_dough.json -t

# Recursive search
st-find "*guide*" -t -r
```

---

## Boolean Operators

Combine keywords without quotes for powerful searches:

| Operator | Meaning | Example |
|---|---|---|
| `+keyword` | REQUIRED (AND) | `+pizza +dough` - both must be present |
| `^keyword` | EXCLUDED (NOT) | `+pizza ^frozen` - pizza without frozen |
| `keyword` | OPTIONAL (OR) | `bike bicycle` - either matches |

### Boolean Examples

```bash
# Find camping stories, but exclude RV content
st-find +camping ^RV -t

# Find stories about pizza that mention both dough and recipe
st-find +pizza +dough +recipe -s

# Find bike or bicycle in titles
st-find bike bicycle -t

# Complex: report required, must mention AI
st-find +report "AI*" OpenAI ChatGPT -s

# Multiple exclusions
st-find +camping ^RV ^electric ^generator -t
```

---

## Wildcards

Wildcards expand pattern matching but **must be quoted** to prevent shell expansion:

| Wildcard | Matches | Example |
|---|---|---|
| `*` | Any sequence | `"bike*"` → bike, bicycle, bikes |
| `?` | Single char | `"AI?"` → AIs, AIR (3 chars) |

### Wildcard Examples

```bash
# All words starting with bike
st-find "bike*" -t

# Three-letter words starting with AI
st-find "AI?" -s

# Anything containing guide
st-find "*guide*" -t

# Complex patterns
st-find "camp*" -t -r

# Combine with boolean (wildcards in quotes)
st-find +pizza "*italian*" -s
st-find "+camp*" ^RV -t
```

**Important:** Wildcards require quotes. Without quotes, the shell expands `*` before passing to st-find:

```bash
st-find bike* -t     # WRONG - shell expands to filenames
st-find "bike*" -t   # CORRECT - st-find handles the wildcard
```

---

## Search Options

| Flag | Field | Description |
|---|---|---|
| `-t` `--title` | Title | Search story titles only |
| `-p` `--prompt` | Prompt | Search .prompt files and data/prompt fields |
| `-s` `--story` | Story | Search text, markdown, and spoken fields |
| `-a` `--all` | All | Search all fields (default if no flag) |
| `-r` `--recursive` | — | Search subdirectories |
| `-v` `--verbose` | — | Show search details |

### Option Examples

```bash
# Search only titles
st-find "camping" -t

# Search only story text
st-find "+report AI" -s

# Search only prompts
st-find "markdown" -p

# Search everything (default)
st-find pizza

# Recursive search in all subdirectories
st-find "*guide*" -t -r

# Verbose mode (shows pattern breakdown)
st-find +pizza +dough -t -v
```

---

## Common Use Cases

### 1. Find Stories by Topic

```bash
# All camping stories
st-find camping -t

# Camping without RV
st-find +camping ^RV -t

# Multiple related topics
st-find camping hiking backpacking -t
```

### 2. Find Technical Content

```bash
# AI-related stories
st-find "AI*" -t

# Specific AI providers
st-find OpenAI anthropic gemini -s

# Technical topics
st-find +python +programming -s
```

### 3. Content Quality Control

```bash
# Find stories that need fact-checking
st-find +report ^fact -s

# Find unfinished work
st-find "TODO" "FIXME" "draft" -s

# Stories with specific claims
st-find +claim +false -s
```

### 4. Research and Analysis

```bash
# Find all guides
st-find "*guide*" -t -r

# Educational content
st-find tutorial howto guide introduction -s

# Specific data or statistics
st-find +data +statistic +research -s
```

### 5. Finding Prompts

```bash
# Find prompts about specific topics
st-find "report" -p

# Prompts with markdown formatting
st-find "markdown" -p

# All prompts in a directory
st-find "*" template -p
```

---

## Path Detection

st-find is smart about detecting filenames:

```bash
# Search current directory
st-find +pizza +dough -t

# Search specific file (detected automatically)
st-find +pizza +dough pizza.json -t

# Search specific directory
st-find camping ../other -t

# Recursive from specific path
st-find "*guide*" health/ -t -r
```

**What's detected as a path:**
- Ends in `.json` or `.prompt`
- Contains `/` (path separator)
- Exists as a file or directory

---

## Output Format

Results are displayed in a clean table:

```
File                           Story  Field    Context
---------------------------  -------  -------  ------------------------
pizza_dough.json                   1  title    Mastering the Crust: An Investigative...
pizza_dough.json                   2  title    From Thin to Thick: The Complete Guide...
pizza_dough.json                   3  text     ...the foundation: the dough. Whether...

Found 3 match(es)
```

| Column | Description |
|---|---|
| File | Filename where match was found |
| Story | Story number within .json file (empty for .prompt files) |
| Field | Field where match was found (title, text, prompt, etc.) |
| Context | Text surrounding the match (truncated) |

---

## Tips and Tricks

### Combining Operators

```bash
# Required + Optional
st-find +camping boondocking dispersed -t

# Required + Excluded + Optional
st-find +camping ^RV ^hotel boondocking -t

# Multiple required terms
st-find +pizza +dough +recipe +homemade -s
```

### Case Insensitive

All searches are case-insensitive by default:

```bash
st-find pizza -t      # matches: pizza, Pizza, PIZZA
st-find AI -s         # matches: ai, AI, Ai
```

### Regex-Like Patterns

While not full regex, wildcards provide powerful pattern matching:

```bash
# Words starting with camp
st-find "camp*" -t

# Words ending with ing
st-find "*ing" -s

# Exact length words
st-find "AI?" -s      # 3 chars starting with AI
```

### Search Multiple Directories

```bash
# Current directory
st-find camping -t

# Another directory
st-find camping ../other -t

# Recursive from root
st-find "guide*" . -t -r
```

### Debugging Searches

Use verbose mode to see what's happening:

```bash
st-find +pizza ^frozen -t -v

# Output shows:
# Searching for pattern: +pizza ^frozen
#   Required (+): 1 pattern(s)
#   Optional: 1 pattern(s)
#   Excluded (^): 1 pattern(s)
# Search in: title=True, prompt=False, story=False
# Path: ., recursive: False
```

---

## Limitations

1. **Wildcards need quotes** (shell limitation):
   ```bash
   st-find bike* -t      # WRONG
   st-find "bike*" -t    # CORRECT
   ```

2. **No full regex** (by design):
   - Use `*` and `?` for patterns
   - Use boolean operators for logic
   - Keep searches simple and fast

3. **One match per story** (to avoid spam):
   - Shows first match in each story
   - Multiple matches in same story are grouped

---

## Integration with Other Commands

### Find then Edit

```bash
# Find a story
st-find +pizza +dough -t

# Edit it
st-edit pizza_dough.json -s 1
```

### Find then Analyze

```bash
# Find stories needing review
st-find +draft -t

# Run fact-check
st-fact camping.json -s 1
```

### Find then Post

```bash
# Find finished work
st-find +ready +publish -t

# Post it
st-post camping.json -s 1
```

---

## Examples by Scenario

### Content Creator

```bash
# What have I written about camping?
st-find camping -t -r

# Which stories need images?
st-find +story ^image -s

# Find all tutorials
st-find "tutorial*" -t -r
```

### Researcher

```bash
# Find AI-related content
st-find "AI*" OpenAI GPT -s -r

# Find claims about specific topics
st-find +claim +statistic +2024 -s

# Cross-reference topics
st-find +study +research +university -s
```

### Quality Assurance

```bash
# Find unverified claims
st-find +claim ^verified -s

# Find stories without fact-checks
st-find +story ^fact -s

# Find potential issues
st-find error warning todo fixme -s
```

### Organizing Content

```bash
# All camping-related files
st-find camping -t -r

# Technical documentation
st-find +documentation +API -s

# By date or timeframe
st-find +2025 +March -s
```

---

## Command Reference

```bash
st-find [options] pattern [pattern...] [path]

Patterns:
  +keyword    Required (AND logic)
  ^keyword    Excluded (NOT logic)
  keyword     Optional (OR logic)
  "wild*"     Wildcard (quoted)

Options:
  -t --title      Search titles
  -p --prompt     Search prompts
  -s --story      Search story text
  -a --all        Search all fields (default)
  -r --recursive  Search subdirectories
  -v --verbose    Show search details

Examples:
  st-find pizza -t
  st-find +camping ^RV -t
  st-find "bike*" -s -r
  st-find +report AI OpenAI file.json -s
```

---

## See Also

- [README_ui.md](README_ui.md) — Interactive menu system
- [README.md](README.md) — Project overview
- [README_devel.md](README_devel.md) — Development guide

For more examples, run: `st-find --help`

