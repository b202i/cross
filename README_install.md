# Installing Cross on a New Machine

Complete step-by-step for a fresh clone on macOS.

---

## 1. System prerequisites

```bash
brew install python@3.11 ffmpeg aspell grip
```

| Package | Used by |
|---|---|
| `python@3.11` | runtime |
| `ffmpeg` | TTS audio conversion (MP3) |
| `aspell` | spell-check in `st-edit` |
| `grip` | local Markdown preview in `st-edit` |

---

## 2. Authenticate with GitHub

Both repositories (`cross` and `cross-story`) are private.
**GitHub authentication must be working before you clone.**

The easiest way on macOS:

1. Install [GitHub Desktop](https://desktop.github.com)
2. Sign in: **GitHub Desktop → Settings → Accounts → Sign in with GitHub.com**
3. Once signed in, the macOS keychain stores your credentials and the
   `git` command-line tool picks them up automatically.

Alternatively, create a **Personal Access Token** (PAT):
- GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
- Scopes needed: `repo` (full)
- When `git` prompts for a password, paste the token

---

## 3. Clone the repositories

`cross` (code) and `cross-story` (story data) are two independent private repos.
Clone them separately into the same parent directory:

```bash
git clone https://github.com/b202i/cross.git
git clone https://github.com/b202i/cross-story.git
```

Then create a symlink so Cross can find the story data at `cross/story/`:

```bash
ln -s ~/github/cross-story ~/github/cross/story
```

> **Note:** Both repos are private and require `b202i` GitHub credentials.
> `story/` is in `.gitignore` — the symlink is never committed to `cross`.

---

## 4. Create and activate the virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Your prompt will change to `(.venv)`.  
All subsequent steps assume the venv is active.

---

## 5. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 6. Install the CLI commands

Cross's `st` and `st-*` commands are `.py` files symlinked into the venv's
`bin/` so they are on `PATH` whenever the venv is active.

**Run this after step 4** — pip clears unregistered scripts from `bin/` during
install, so running the script before pip will silently lose all the links.

```bash
bash script/symbolic_links.bash
```

Expected output ends with `Verified: 22 symlink(s)`.
If the count is wrong, re-run — the script is safe to re-run.

---

## 7. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
XAI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
PERPLEXITY_API_KEY=...
GEMINI_API_KEY=...
```

Keys are obtained from each provider's developer console:

| Provider | Console URL |
|---|---|
| xAI (Grok) | https://console.x.ai |
| Anthropic (Claude) | https://console.anthropic.com |
| OpenAI (GPT) | https://platform.openai.com/api-keys |
| Perplexity | https://perplexity.ai/settings/api |
| Google Gemini | https://aistudio.google.com/app/apikey |

---

## 8. Configure Discourse (optional)

Only needed if you post to a Discourse forum.

Create `discourse.json` in the project root:

```json
{
  "sites": [
    {
      "slug": "MySite",
      "url": "https://yourforum.example.com",
      "username": "your_discourse_username",
      "api_key": "your_api_key",
      "category_id": 1
    }
  ]
}
```

Then generate the `DISCOURSE=` line in `.env`:

```bash
python3 discourse.py
```

Verify the connection:

```bash
st-post --site MySite --check
```

---

## 9. Verify the install

```bash
st --help
```

You should see the Cross interactive menu help.  
If `st` is not found, make sure the venv is active (`source .venv/bin/activate`)
and re-run `bash script/symbolic_links.bash`.

---

## Everyday use

The venv must be active for `st` to be on `PATH`:

```bash
cd cross
source .venv/bin/activate
st my_topic.json
```

---

## Updating an existing install

```bash
cd ~/github/cross
git pull                             # pull latest code
pip install -r requirements.txt      # pick up any new/updated packages
bash script/symbolic_links.bash      # re-link in case new st-* commands were added

cd ~/github/cross-story
git pull                             # pull latest story data independently
```

---

## Upgrading packages

### Always use the terminal — not PyCharm's UI

PyCharm's **Python Packages** panel (and the `↑` upgrade button in
**Settings → Project → Python Interpreter**) installs the **latest available**
version of each package, ignoring the pins in `requirements.txt`.
This will break reproducibility and can introduce incompatible versions.

**The correct workflow is always:**

```bash
source .venv/bin/activate            # make sure the venv is active
pip install -r requirements.txt      # install / sync to the pinned versions
```

### To upgrade a specific package

1. Check the new version: `pip index versions <package>`
2. Update the pin in `requirements.txt` (e.g. `anthropic==0.84.0` → `anthropic==0.85.0`)
3. Install: `pip install -r requirements.txt`
4. Test, then commit the updated `requirements.txt`

### To check what is out of date

```bash
pip list --outdated
```

### PyCharm interpreter setup

When PyCharm asks you to configure an interpreter for this project:

1. Choose **Select existing** (not "Generate new")
2. Point it at: `~/github/cross/.venv/bin/python`
3. **Do not** let PyCharm create a new venv — it will default to the system
   Python (3.14) and the audio packages will fail to install

If PyCharm shows a red error "Already contains Python with version 3.9",
the `.venv` needs to be recreated with Python 3.11:

```bash
python3.11 -m venv --clear .venv
source .venv/bin/activate
pip install -r requirements.txt
bash script/symbolic_links.bash
```

Then point PyCharm at `.venv/bin/python` again.

---

## Notes

- `.env` and `discourse.json` are in `.gitignore` — **never committed**.
  Copy them manually to each machine or use a password manager.
- `cross-story` is a separate private repo cloned independently alongside `cross`.
  If you don't have access, create an empty directory: `mkdir ~/github/cross/story`.
- **Future:** when Cross is published to PyPI as `cross-ai`, steps 4 and 5
  collapse to `pip install cross-ai` and the symlink script will not be needed.
  See ticket T-04 in `README_rebrand_cross.md`.

