# FAQ

---

### How do I add a new AI?

1. Create `ai_<name>.py` following the pattern of an existing handler (e.g. `ai_openai.py`).
   Set `AI_MAKE`, `AI_MODEL`, and implement the `BaseAIHandler` interface from `base_handler.py`.
2. Register it in `ai_handler.py` — add it to `AI_HANDLER_REGISTRY`.
3. Add the API key to `.env` and document it in `.env.example`.
4. Add the key to `README_opensource.md`.

The new AI will automatically appear in all `--ai` choices, the `st-bang` parallel run,
and the `st-cross` cross-product matrix.

---

### How do I change the editor?

Use `st-admin` to set the editor — it writes the value to `.env` and both
`st-edit` and `st-new` read it automatically:

```bash
st-admin --set-editor nano    # set nano as the default editor
st-admin --set-editor code    # set VS Code
st-admin --set-editor micro   # set micro
```

Or interactively: run `st-admin` and press `E`.

The `EDITOR` setting is also honoured if set in your shell environment
(`export EDITOR=nano` in `.zshrc`), but the `st-admin` value in `.env` takes
precedence when both are present.

---

### Can I make my own prompt template?

Yes. Templates are `.prompt` files stored in the `template/` directory.
Copy the default template and edit it:

```bash
cp template/default.prompt template/my_template.prompt
```

Then use it with `st-new`:

```bash
st-new -t my_template my_topic.prompt
```

`st-new --help` shows available templates under `-t`. Only templates present in the
`template/` directory are listed — `default` is always available.

---

### Can I post to Facebook, X, or other social media?

Not directly — the app posts to [Discourse](https://www.discourse.org) forums only.

However, `st-prep` produces several ready-to-use output formats that make manual
sharing straightforward:

```bash
st-prep --all my_topic.json   # generate all formats at once
```

| Output file | Use |
|---|---|
| `my_topic.md` | Paste into any platform that renders Markdown |
| `my_topic.txt` | Plain text for Facebook, X, LinkedIn, email |
| `my_topic.mp3` | Audio for podcasts, YouTube, or social video |
| `my_topic.title` | The story headline, ready to copy |

Full social media API integration (Facebook Graph API, X API v2, etc.) would require
new `st-post` targets — a possible future contribution.

---

### How do I add graphics to my post?

Cross-product analysis plots (heatmaps, bar charts) are automatically uploaded to
Discourse and embedded in the report when you run:

```bash
st-analyze --site MySite my_topic.json
```

`st-analyze` calls `st-plot` internally, uploads the generated `.png` files to Discourse,
and replaces placeholder tags in the report with the live image URLs before posting.

**Prerequisite:** the `DISCOURSE` key must be configured in `.env`:

```env
DISCOURSE={"sites":[{"slug":"MySite","url":"https://forum.example.com","username":"you","api_key":"key","category_id":1}]}
```

The `slug` value (`MySite` above) is what you pass to `--site`.  See
`README_opensource.md` for full Discourse setup instructions and how to obtain
an API key.

For custom graphics, upload the image to Discourse manually and paste the resulting
Markdown image tag into your story with `st-edit`.

---

### Is there a way to change the TTS voice or TTS engine?

The TTS engine is [Piper](https://github.com/rhasspy/piper), running as a local server.
Voice and connection are configured in `.env` (uppercase keys):

```env
TTS_HOST=localhost
TTS_PORT=10200
TTS_VOICE=en_US-lessac-medium
```

Use `st-admin` to update the voice without editing `.env` directly:

```bash
st-admin --set-tts-voice en_US-ryan-high   # set via CLI
st-admin                                    # or: press V in the interactive menu
```

To browse available voices, download model files, and audition them:

```bash
st-voice --voices          # list all available en_US / en_GB Piper voice names
st-voice --curl | bash     # download all voice ONNX model files at once
st-voice sample.txt        # interactive shell: audition voices on a .txt file
```

Then render a story to MP3:

```bash
st-speak my_topic.json                        # uses TTS_VOICE from .env
st-speak --voice en_US-ryan-high my_topic.json  # override for this render only
```

**TTS is optional** — see `requirements-no-tts.txt` to install Cross without
audio packages.  TTS and no-TTS both work on Python 3.10–3.13.

Changing the TTS engine entirely would require replacing the `yakyak` PyPI package and
updating `st-speak.py` and `mmd_voice.py`.

---

### The fact-check shows several false claims. Can the app fix those?

Yes — that is exactly what `st-fix` does.
It reads the fact-check results for a story, extracts the `False` and `Partially_false`
claims, and asks the AI to revise the story to resolve each one:

```bash
st-fix --ai anthropic -s 1 -f 1 my_topic.json
```

- `-s 1` — story number to fix
- `-f 1` — fact-check number to use as the source of corrections
- `--ai` — which AI performs the rewrite

The fixed story is added as a new story entry in the container.
You can then fact-check it again to verify improvement, or run `st-cross` across
all versions to compare scores before and after the fix.

---

### How can I run this app on macOS?

macOS is the primary development and test platform.  Follow the Quick Start in
`README.md` — the `brew install` prerequisites line covers everything needed.

---

### How can I run this app on Linux?

Linux (x86_64) works with no code changes.  The POSIX-dependent features
(`fcntl.flock`, `termios`/`tty`, `signal`) are all native to Linux.

Replace the `brew install` line with your distro's package manager:

```bash
# Debian / Ubuntu
sudo apt install python3.11 python3.11-venv ffmpeg aspell
pip install grip        # Python tool, same on all platforms

# Fedora / RHEL
sudo dnf install python3.11 ffmpeg aspell
pip install grip
```

Then follow the standard setup from step 2 onward (`git clone`, `venv`, `pip install`,
`bash script/symbolic_links.bash`).

**Linux-specific notes:**
- `afplay` (macOS audio player used by `st-voice` interactive `s` command) is not
  available on Linux.  TTS rendering still works; only in-terminal playback is
  affected.  Replace `afplay` with `mpv`, `play` (sox), or `aplay` if needed.
- Audio packages (`soundfile`, `yakyak`) have Linux wheels and work with
  Python 3.10–3.13.  Install `libsndfile1` via your package manager first.

---

### How can I run this app on Windows?

The app is developed and tested on macOS and Linux. Several POSIX-only features
do not work natively on Windows:

- `fcntl.flock` — file locking (used in `st-fact.py`)
- `termios` / `tty` — raw keyboard input (used in `mmd_single_key.py` for the `st` menu)
- `signal.SIGINT` handling differences

**Options:**

- **WSL2 (recommended)** — Windows Subsystem for Linux gives a full Ubuntu environment
  where the app runs without modification. Install WSL2, then follow the Linux
  setup instructions above.
- **Docker** — run the app in a Linux container on any platform.
- **Native Windows port** — would require replacing `fcntl` with `msvcrt` locking and
  rewriting the keyboard input layer. A possible future contribution.

---

### Is there a cloud version of the app?

No. Cross is designed as a local, single-user command-line tool.

All AI calls go through each provider's public API (no self-hosted models required),
so the only thing running locally is the app itself and optionally the Piper TTS server.

A cloud-hosted version would need a web front-end, multi-user session management,
and secure per-user API key storage — a significant architectural change beyond
the current scope. The `mmd_web_server.py` module is an early experiment in that
direction (local browser preview only).
