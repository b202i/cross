# Installing Cross

---

## Quick Install (pipx — recommended for most users)

`pipx` installs Cross into an isolated environment and puts all `st-*` commands on
your PATH — no virtualenv to manage, no `source .venv/bin/activate` needed ever.

### 1. Install pipx and set up your PATH

```bash
# macOS
brew install pipx
pipx ensurepath

# Linux — Debian / Ubuntu
sudo apt install pipx
pipx ensurepath

# Linux — Fedora / RHEL
sudo dnf install pipx
pipx ensurepath
```

Then **restart your terminal** (or open a new one) so the updated PATH takes effect.

### 2. Install Cross

```bash
pipx install cross-st
```

### 3. Set up API keys

```bash
st-admin --setup
```

The wizard prompts for each provider key and saves them to `~/.crossenv`.
At minimum you need one. [Google Gemini](https://aistudio.google.com/app/apikey)
is free — no credit card required.

### 4. Write your first report

```bash
st-new my_topic.prompt            # create a prompt from the template, opens in editor
st-bang my_topic.prompt           # generate with all AI providers, then review
```

That's it. All research and fact-checking commands are now available.

---

## Adding TTS / audio (optional)

TTS turns reports into spoken MP3 audio via a local Piper TTS server.
The commands `st-speak`, `st-voice`, and `st-prep --mp3` require it.

> **Installing the Python packages is only half the story.**
> TTS also requires a running Wyoming Piper server and an ONNX voice model file.
> The Python packages install instantly; the Piper server is the real setup step.

### 1. Install system prerequisites

```bash
# macOS
brew install ffmpeg

# Linux — Debian / Ubuntu
sudo apt install libsndfile1 ffmpeg

# Linux — Fedora / RHEL
sudo dnf install libsndfile ffmpeg

# Linux — Arch
sudo pacman -S libsndfile ffmpeg
```

`ffmpeg` handles MP3 encoding. On Linux, `libsndfile1` is required by `soundfile`
(macOS bundles it inside the wheel).

### 2. Install Cross with TTS packages

```bash
# Fresh install
pipx install "cross-st[tts]"

# Add TTS to an existing install (no reinstall needed)
pipx inject cross-st cmudict pyphen soundfile websockets wyoming yakyak
```

### 3. Set up the Piper TTS server

See **[README-TTS-audio.md](README-TTS-audio.md)** for the full walkthrough:
Docker setup, native install, downloading voice models, and configuring
`TTS_HOST` / `TTS_PORT` / `TTS_VOICE` in `~/.crossenv`.

The short form with Docker:

```bash
docker run -d \
  --name wyoming-piper \
  -p 10200:10200 \
  -v ~/piper-voices:/data \
  rhasspy/wyoming-piper \
  --voice en_US-lessac-medium
```

Or natively with pipx (no Docker required):

```bash
pipx install wyoming-piper
wyoming-piper --voice en_US-lessac-medium --uri tcp://0.0.0.0:10200
```

### 4. Configure your voice

```bash
st-admin --set-tts-voice en_US-lessac-medium
```

Good starting voices: `en_US-lessac-medium`, `en_US-ryan-high`, `en_US-libritts-high`

### 5. Test

```bash
st-speak my_topic.json     # renders story 1 → my_topic.mp3
```

---

## Developer / Contributor Install

For contributors working on the Cross codebase. Requires two repos: `cross`
(code) and `cross-story` (story data).

### 1. Authenticate with GitHub

Both repos are private. Install [GitHub Desktop](https://desktop.github.com) and
sign in, or create a Personal Access Token (PAT) with `repo` scope.

### 2. Install prerequisites

```bash
# macOS
brew install python@3.11 aspell grip

# Linux — Debian / Ubuntu
sudo apt install python3.11 python3.11-venv aspell
pip install grip

# Linux — Fedora / RHEL
sudo dnf install python3.11 aspell
pip install grip
```

| Package | Used by |
|---|---|
| `python@3.11` | runtime (3.10–3.13 all work; 3.11 is the pinned dev baseline) |
| `aspell` | spell-check in `st-edit` |
| `grip` | local Markdown preview in `st-edit` |

> **ffmpeg** is only needed for TTS/audio. Install it when you set up Piper
> (see the Adding TTS section above).

### 3. Clone both repos

```bash
git clone https://github.com/b202i/cross.git
git clone https://github.com/b202i/cross-story.git
ln -s ~/github/cross-story ~/github/cross/story
cd cross
```

`story/` is in `.gitignore` — the symlink is never committed.

### 4. Create the virtual environment and install

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 5. Configure API keys

```bash
cp .env.example .env
# open .env and fill in at least one API key
```

`.env` is in `.gitignore` — never committed. Copy it manually between machines
or use a password manager.

### 6. Configure Discourse (optional)

Only needed for posting to a Discourse forum. Create `discourse.json`:

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

Generate the `DISCOURSE=` env line and verify:

```bash
python3 discourse.py
st-post --site MySite --check
```

### 7. Verify the install

```bash
st --help
```

### Everyday developer workflow

```bash
cd ~/github/cross
source .venv/bin/activate
st my_topic.json
```

### Updating

```bash
cd ~/github/cross
git pull
pip install -r requirements.txt    # pick up any new/updated packages

cd ~/github/cross-story
git pull
```

### Upgrading packages

Always use the terminal — not PyCharm's package UI. PyCharm installs the latest
available version, ignoring pins in `requirements.txt`.

```bash
source .venv/bin/activate
pip install -r requirements.txt    # sync to pinned versions
```

To upgrade a specific package:
1. `pip index versions <package>` — check available versions
2. Update the pin in `requirements.txt`
3. `pip install -r requirements.txt`
4. Test, then commit the updated `requirements.txt`

### PyCharm interpreter setup

1. **Select existing** interpreter — point at `~/github/cross/.venv/bin/python`
2. Do **not** let PyCharm generate a new venv — it defaults to the system Python

If you see "already contains Python with version 3.9":

```bash
python3.11 -m venv --clear .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then point PyCharm at `.venv/bin/python` again.

---

## Notes

- `cross-story` is a separate private repo. If you don't have access: `mkdir ~/github/cross/story`
- Cross is on PyPI as `cross-st`: `pipx install cross-st` (no symlink script needed for PyPI installs)
- API keys reference: see [README_opensource.md](README_opensource.md)
- TTS full reference: see [README-TTS-audio.md](README-TTS-audio.md)
