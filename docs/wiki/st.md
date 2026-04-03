# st — Interactive menu launcher

Run `st` in the directory containing your story file and you get a keyboard-driven menu that walks you through the full workflow — no flags to memorize.

```bash
st               # open the menu (auto-detects *.json in current directory)
st topic.json    # open with a specific story pre-selected
```

The menus follow the natural top-down workflow:

| Key | Menu | What it covers |
|-----|------|----------------|
| `g` | Generate | Write a prompt, generate stories, run all AIs in parallel |
| `v` | View | Inspect stories and fact-checks |
| `e` | Edit | Revise story text, title, improve with AI |
| `a` | Analyze | Fact-check, cross-check all AIs, benchmark |
| `p` | Post | Publish to Discourse, export or print PDF |
| `u` | Utility | Charts, audio, remove stories |
| `x` | Settings | Default AI, voice, editor |

Press a letter to enter a submenu, then a second letter to run the command.  Press `q` to go back, `q` again to quit.

**Related:** [Onboarding](Onboarding.md) · [st-new](st-new.md) · [st-bang](st-bang.md) · [Command Reference](Home.md)

---

## For developers

`st.py` builds shell commands only — no business logic lives here. Every action calls a `st-*.py` tool directly. You can always skip the menu and run any `st-*` command by hand.

### Adding a command to a menu

1. Add a label in the relevant submenu dict in `menus` (~line 40):
   ```python
   "k": "Description shown in menu"
   ```
2. Add the matching `case` in `execute_menu()`:
   ```python
   case "k":
       cmd = f"st-mycommand {file_json}"
   ```
3. If the command writes to the `.json` container, add its name to `POST_CMD_REFRESH` at the top of the file — this tells `st` to re-read the file after the command finishes so story/fact-check counts stay current.
