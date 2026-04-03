# Cross — Publishing Platform Guide

How Cross posts content, what is implemented, what is planned, and how to add new targets.

---

## How Cross generates media

Understanding what Cross actually produces is essential before mapping it to each platform.

### Graphics — matplotlib PNGs uploaded to Discourse

`st-analyze` calls `st-plot --file_kv`, which saves three matplotlib plots as PNG files
to `tmp/`:

| Plot | Tag in report | Description |
|---|---|---|
| `evaluator_v_target` | `cross_heat_map_figure_1` | Score heatmap — evaluator vs target |
| `bar_score_evaluator` | `cross_bar_score_evaluator_figure_2` | Avg score by evaluator (fact-checker) |
| `bar_score_target` | `cross_bar_score_target_figure_3` | Avg score by target (report writer) |

`post_plot()` in `mmd_plot.py` then **uploads each PNG to Discourse** via
`MmdDiscourseClient.upload_file()`. Discourse returns a hosted URL for each image.

`embed_plot_url()` in `mmd_process_report.py` replaces the placeholder tags in the
report Markdown with standard Markdown image syntax pointing to the Discourse URL:

```markdown
![cross_heat_map_figure_1](https://forum.example.com/uploads/default/original/1X/abc123.png)
```

**The report Markdown that reaches `st-post` already has Discourse-hosted image URLs baked in.**
There are no local file references in the posted content — only `https://` URLs.

### Audio — MP3 uploaded to Discourse

`st-post` with an `.mp3` argument uploads the audio file to Discourse and inserts:

```markdown
![filename.mp3|audio](https://forum.example.com/uploads/default/original/1X/xyz.mp3)
```

This is Discourse-specific BBCode. `|audio` is a Discourse extension that renders
an in-page audio player. It is not standard Markdown.

---

## Media compatibility by platform

| Platform | PNG images | MP3 audio | How images work | Audio workaround |
|---|---|---|---|---|
| **Discourse** | ✅ Native | ✅ Native player | Discourse-hosted URL renders inline | `![file\|audio](url)` BBCode |
| **GitHub Gist** | ✅ Via URL | ❌ No player | External `https://` img tags render | Link to Discourse post URL |
| **Bluesky** | ✅ Upload required | ❌ No player | Must re-upload PNG via AT Protocol | Link to Discourse post URL |
| **Reddit** | ✅ Via URL | ❌ No player | External img tags render in some clients | Link to Discourse post URL |
| **X.com** | ✅ Upload required | ❌ No native | Must re-upload PNG via v2 media API | Link to Discourse post URL |
| **LinkedIn** | ✅ Upload required | ❌ No player | Must re-upload via Media API | Link to Discourse post URL |

### Key issues per platform

**GitHub Gist**
Images work as-is — Gist renders standard Markdown `![alt](url)` inline, and the
Discourse-hosted image URLs are plain `https://` links. The `|audio` tag will render
as broken image syntax. Fix: strip `|audio` from the embed tag and replace with a
plain link: `[Listen to audio report](mp3_url)`.

**Bluesky**
Markdown is not natively rendered in Bluesky posts — rich text uses `facets` (AT Protocol
lexicon). Images must be uploaded as `app.bsky.embed.images` blobs, not linked by URL.
The Discourse PNG URLs cannot be embedded directly; the PNG must be downloaded and
re-uploaded via the Bluesky API (max 1MB per image, max 4 images per post).
**Practical approach for analyze reports:** post title + summary + Discourse link.
The heatmap and bar charts are too data-dense to be useful at Bluesky image sizes anyway.

**Reddit**
Old Reddit and new Reddit (markdown mode) render `![alt](url)` inline for external URLs
in self-posts. The Discourse-hosted PNG URLs work. Audio: replace `|audio` embed with a
plain link. However, some subreddits block external image URLs — test per subreddit.

**X.com**
Images must be uploaded via `POST /2/media/upload` before tweeting; external URLs in
tweet text do not render as inline images. Each tweet supports up to 4 images.
For a thread post, attaching the heatmap to the first tweet is feasible.
Audio: not supported — link to Discourse post only.

---

## The publishing model

Every Cross story lives in a `.json` container. When you post, `st-post` reads
the container and sends `story_title` + `story_markdown` to the target platform.
The same data model feeds every destination — the platform adapter is the only
thing that changes.

```
story.json
  └─ story[n].title        → post title / tweet text
  └─ story[n].markdown     → full body (Markdown)
  └─ story[n].text         → plain text (strip of markdown)
  └─ story[n].topic_id     → Discourse topic ID (written back after post)
  └─ story[n].post_url     → canonical URL of the post (written back)
  └─ story[n].mp3_url      → Discourse-hosted audio URL (written back)
```

---

## Platform 1 — Discourse ✅ Implemented

### What is implemented
- `discourse.py` — `MmdDiscourseClient(DiscourseClient)` wraps `pydiscourse`
- `st-post --site <slug> -s <n> file.json` — create a new topic
- `st-post --site <slug> -s <n> -f <n> file.json` — reply with a fact-check
- `st-post --site <slug> -s <n> file.mp3 file.json` — post with MP3 audio
- `st-post --site <slug> --check` — validate credentials without posting
- Multiple sites supported via `discourse.json` → `DISCOURSE=` in `.env`
- `post_url` and `mp3_url` written back into the story JSON after posting

### Auth setup
```json
// discourse.json (excluded from git)
{
  "sites": [
    {
      "slug": "MySite",
      "url": "https://yourforum.example.com",
      "username": "your_username",
      "api_key": "your_api_key",
      "category_id": 1
    }
  ]
}
```
```bash
python3 discourse.py    # writes DISCOURSE= into .env
```

### Content limits
| Field | Limit |
|---|---|
| Title | 255 characters |
| Body | No enforced limit (Discourse default: 32,000 chars min, configurable) |
| Audio | MP3 upload supported; embed via `![file\|audio](url)` inserted automatically |
| Images | PNG upload supported; embedded as `![alt](url)` — renders inline |
| Markdown | Full CommonMark; most GitHub-flavored extensions work |

### Media notes
- **Graphics from `st-analyze`:** PNGs are uploaded to Discourse first, then the
  Discourse-hosted URLs are embedded in the report. Fully supported, renders inline.
- **Audio from `st-post --mp3`:** MP3 uploaded to Discourse, embedded with `|audio`
  BBCode. Renders an in-page audio player. Discourse-only syntax.

### Posting commands
```bash
st-post --site MySite -s 1 my_topic.json           # post story 1
st-post --site MySite -s 1 -f 2 my_topic.json      # reply with fact-check 2
st-post --site MySite -s 1 my_topic.mp3 my_topic.json  # post with audio
```

---

## Platform 2 — X.com (Twitter) 🔲 Planned (M-13)

### Status
Read-only access is implemented in `ai_url.py` (Bearer token, fetches tweet text).
Write/post access is **not yet implemented**.

### Key constraints
| Constraint | Value |
|---|---|
| Post character limit (standard account) | 280 chars |
| Post character limit (X Premium, via API) | ~4,000 chars |
| X Articles (25,000 chars) | Web UI only — not in v2 API as of 2026 |
| Cross report length | ~4,000–8,000 chars — threading required for full text |
| Audio (MP3) | Not supported — images and video only |
| API write access | $100/month (Basic tier) minimum |
| X Premium subscription | $8–16/month required for >280-char posts |

### Recommended strategy
**Option A (default) — Title + link:**
One post: `{title}\n\n{teaser_2_sentences}\n\n{discourse_post_url}`
~270 chars. No Premium required. Discourse is the canonical destination.

**Option B — Full thread (`--thread` flag):**
Split report at paragraph boundaries into ≤4,000-char chunks.
Chain via `reply_in_reply_to_tweet_id`. Requires X Premium.

### Media notes
- **Graphics:** Cannot use Discourse-hosted URLs inline. PNGs must be re-uploaded
  via `POST /2/media/upload` and attached to the tweet as `media_ids`. Max 4 images
  per tweet. Practical approach: attach the heatmap PNG to the first tweet only.
  The bar charts are lower priority.
- **Audio:** X does not support MP3. Include `mp3_url` as a plain text link:
  `🎧 Audio: {mp3_url}` or link to the full Discourse post which has the player.

### Auth setup (not yet in .env.example)
```env
X_API_KEY=...              # Consumer Key
X_API_SECRET=...           # Consumer Secret
X_ACCESS_TOKEN=...         # User Access Token
X_ACCESS_TOKEN_SECRET=...  # User Access Token Secret
```
Obtain from: **developer.x.com → Projects & Apps → your app → Keys and Tokens**
Requires OAuth 1.0a (not Bearer token — Bearer is read-only).

### Implementation plan
1. Add `tweepy>=4.14` to `requirements.txt`
2. Create `x_com.py` — `MmdXClient` mirroring `discourse.py` pattern
3. `post(title, text, url)` — Option A
4. `post_thread(title, text)` — Option B
5. Add `--x` flag to `st-post`; store `x_url` in story JSON

### Prerequisites
- [ ] Decide: Option A only, or both with `--thread` flag
- [ ] X account has X Premium (for Option B)
- [ ] X API Basic tier ($100/mo) registered at developer.x.com
- [ ] OAuth 1.0a credentials generated and added to `.env`

---

## Platform 3 — GitHub Gists 🔲 Planned

### Why GitHub Gists
- **Zero auth friction** — uses the same GitHub token already needed for the repo
- **Full Markdown rendering** — Gists render complete Markdown including headings,
  tables, code blocks, and images
- **No character limit** — a 5,000-word report posts in full, no threading
- **Linkable and embeddable** — each Gist gets a permanent URL and can be embedded
- **Free** — no API tier cost; included in any GitHub account
- **Cross-product fit** — the fact-check matrix and analysis tables render perfectly
- **Audience** — developers, researchers, technical readers; exactly Cross's audience

### Gist vs. GitHub Issues vs. GitHub Discussions

| Target | Best for | Markdown | Limits | Auth |
|---|---|---|---|---|
| **Gist** | Full reports, standalone reference | ✅ Full | None | PAT `gist` scope |
| **Issue** | Bug-style discussion, feedback | ✅ Full | None | PAT `repo` scope |
| **Discussion** | Community Q&A, announcements | ✅ Full | None | PAT `repo` scope |
| **Release notes** | Version-tagged content | ✅ Full | None | PAT `repo` scope |

**Recommendation: Gist** for general report publishing. Issues/Discussions for
Cross project-specific announcements.

### Auth setup
```env
GITHUB_TOKEN=...     # Personal Access Token with 'gist' scope
GITHUB_USERNAME=...  # Your GitHub username
```
Generate at: **github.com → Settings → Developer Settings → Personal Access Tokens**
Required scope: `gist` (for public gists only — no `repo` access needed)

### API — create a Gist
```
POST https://api.github.com/gists
Authorization: Bearer {GITHUB_TOKEN}

{
  "description": "{story_title}",
  "public": true,
  "files": {
    "{slug}.md": {
      "content": "{story_markdown}"
    }
  }
}
```
Returns `html_url` — the public Gist URL to store in the story JSON.

### Content model
| Field | Maps to |
|---|---|
| `description` | `story_title` |
| `files[slug].content` | `story_markdown` (with one pre-processing step — see Media notes) |
| `public` | `true` (default) or `false` (with `--private` flag) |

### Media notes
- **Graphics:** Discourse-hosted PNG URLs (`https://forum.example.com/uploads/...png`)
  render correctly in Gist as inline images — no re-upload needed. ✅
- **Audio:** The `![file.mp3|audio](url)` Discourse BBCode will render as a broken
  image in Gist. **Pre-process required:** strip `|audio` from the tag and replace
  with a plain Markdown link before posting:
  ```
  [🎧 Listen to audio report](https://forum.example.com/uploads/...mp3)
  ```
  This is a one-line regex fix in the Gist adapter.

### Implementation plan
1. Create `github_gist.py` — `MmdGistClient` with `post(title, markdown)` and
   `update(gist_id, markdown)` (for edits)
2. Add `--gist` flag to `st-post`; no new dependencies — `requests` already present
3. Store `gist_url` and `gist_id` in story JSON (gist_id needed for updates)
4. Add `GITHUB_TOKEN` and `GITHUB_USERNAME` to `.env.example`

### Posting commands (proposed)
```bash
st-post --gist -s 1 my_topic.json          # publish to Gist
st-post --gist --private -s 1 my_topic.json  # secret Gist
```

---

## Platform 4 — LinkedIn 🔲 Future consideration

### Why LinkedIn fits Cross
- Long-form posts up to **3,000 characters** (Articles: unlimited)
- Markdown-like formatting in articles (`#`, `**bold**`, lists)
- Professional audience — researchers, analysts, knowledge workers
- Cross-product fact-checking is directly relevant to professional publishing

### Constraints
| Constraint | Value |
|---|---|
| Standard post limit | 3,000 characters |
| Article (newsletter) limit | Unlimited |
| API access | LinkedIn Marketing API — requires Partner Program approval |
| Approval | **Restricted** — requires business justification and review |
| Auth | OAuth 2.0, `w_member_social` scope |

### Verdict
**Not practical for an open-source CLI tool** at this stage. LinkedIn's API access
requires Partner Program approval with a business use-case review — not available
to individual developers. An unofficial scraping approach is fragile and violates ToS.

**Revisit when:** Cross has an organizational presence (company or non-profit).

---

## Platform 5 — Bluesky (AT Protocol) 🔲 Future consideration

### Why Bluesky fits Cross
- **Open protocol (AT Protocol)** — no approval process, no API tier fees
- Post limit: **300 characters** (similar to X, but open)
- Lexicon supports **long-form posts** via `app.bsky.feed.post` with `facets`
- Growing technical/academic audience
- **Free API** — no rate-limit tiers for posting
- `atproto` Python SDK is well-maintained

### Constraints
| Constraint | Value |
|---|---|
| Standard post limit | 300 characters |
| Long-form (via lexicon) | Up to ~100,000 chars (Markdown rendered as rich text) |
| Audio | No native audio; link only |
| API cost | Free |
| Auth | App password (not main password) — simple to set up |

### Auth setup (proposed)
```env
BLUESKY_HANDLE=you.bsky.social
BLUESKY_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### Verdict
**Good candidate for a near-term addition** after X.com and Gist are done.
Lower friction than X (free, no tiers) and growing technical audience.
`pip install atproto` is the only dependency.

### Media notes
- **Graphics:** Bluesky does not render external image URLs inline. Images must be
  uploaded as binary blobs via `client.upload_blob()` and attached as
  `app.bsky.embed.images`. Max 1MB per image, max 4 per post. The heatmap PNG from
  `st-analyze` would need to be downloaded from Discourse and re-uploaded.
  For the initial implementation, **skip image embedding** — post title + teaser +
  Discourse link. Add image support in a v2 pass.
- **Audio:** Not supported. Link to Discourse post URL.

---

## Platform 6 — Reddit 🔲 Future consideration

### Why Reddit fits Cross
- Subreddits for nearly every Cross topic domain (r/MachineLearning, r/datascience,
  r/technology, r/investing, etc.)
- Self-posts (text posts) support full Markdown, no length limit
- **Free API** for low-volume posting (OAuth 2.0, `PRAW` library)
- Post can link to the Discourse version for discussion continuity

### Constraints
| Constraint | Value |
|---|---|
| Text post limit | 40,000 characters |
| Title limit | 300 characters |
| API cost | Free (60 requests/min) |
| Auth | OAuth 2.0 `script` app — simple 2-credential setup |
| Audience fit | High for technical topics; lower for general interest |
| Spam risk | Subreddit rules vary; cross-posting may be restricted |

### Auth setup (proposed)
```env
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
```

### Verdict
**Good fit for topic-specific posts** where a matching subreddit exists.
Blanket posting to Reddit without subreddit targeting would be spam.
Needs a `--subreddit` argument. `pip install praw` is the only dependency.

### Media notes
- **Graphics:** Reddit self-posts (text posts) render `![alt](url)` in Markdown
  mode for external `https://` URLs — the Discourse-hosted PNG URLs work in theory.
  In practice, **new Reddit's markdown renderer is inconsistent** with external images
  and some subreddits block them. Safest approach: include the Discourse post URL
  so readers can see the plots there.
- **Audio:** Not supported. Link to Discourse post URL.

---

## Platform comparison summary

| Platform | Status | Full report? | Audio? | Cost | Auth complexity |
|---|---|---|---|---|---|
| **Discourse** | ✅ Done | ✅ Yes | ✅ MP3 embed | Free (self-host) | API key |
| **GitHub Gist** | 🔲 Next | ✅ Yes | Link only | Free | PAT (gist scope) |
| **Bluesky** | 🔲 Soon | ✅ Long-form | Link only | Free | App password |
| **Reddit** | 🔲 Soon | ✅ 40k chars | Link only | Free | OAuth script |
| **X.com** | 🔲 Planned | ⚠️ Thread/link | Link only | $100/mo API | OAuth 1.0a (4 tokens) |
| **LinkedIn** | ❌ Blocked | ✅ Articles | No | Partner approval | OAuth 2.0 |

---

## Recommended build order

1. **GitHub Gist** — zero new dependencies, uses existing PAT, full Markdown, no limits.
   Best immediate value for the developer audience.
2. **Bluesky** — free, open, growing. One `pip install atproto`. Simple auth.
3. **Reddit** — `pip install praw`. High reach for topic-specific content.
4. **X.com** — $100/month API cost; do after the free platforms are proven.
5. **LinkedIn** — blocked on Partner approval; defer indefinitely.

---

## Shared design principles for new adapters

All platform adapters should follow the `discourse.py` / `MmdDiscourseClient` pattern:

1. **One file per platform** — `github_gist.py`, `x_com.py`, `bluesky.py`, `reddit.py`
2. **One client class** — `MmdGistClient`, `MmdXClient`, etc.
3. **Consistent method signature** — `post(title, markdown, url=None)`
4. **Write-back** — store the resulting URL in `story[n].{platform}_url` in the JSON
5. **`.env` credentials** — all auth via environment variables; no hardcoded values
6. **`--check` flag** — validate credentials without posting (like `st-post --check`)
7. **No new required dependencies** if avoidable — use `requests` where possible

### Media pre-processing (required for non-Discourse platforms)

The `story_markdown` field contains Discourse-specific syntax that must be cleaned
before posting elsewhere. Add a `clean_for_platform(markdown, mp3_url)` helper:

```python
import re

def clean_for_platform(markdown, mp3_url=None):
    """
    Remove Discourse-specific media syntax from story markdown.
    Call this before posting to any non-Discourse platform.

    - Strips  ![file.mp3|audio](url)  — Discourse audio player tag
    - Leaves  ![alt](url)  image tags intact (external URLs render on most platforms)
    - Optionally appends a plain-text audio link if mp3_url is provided
    """
    # Remove Discourse audio player embeds  (|audio suffix is Discourse-only)
    cleaned = re.sub(r'!\[[^\]]*\|audio\]\([^)]*\)\n?', '', markdown)

    # Append a plain audio link if we have one
    if mp3_url:
        cleaned = cleaned.rstrip() + f'\n\n🎧 [Audio version]({mp3_url})\n'

    return cleaned
```

This belongs in `mmd_process_report.py` alongside `add_mp3_player()`.

### `st-post` flag convention (proposed)
```
st-post --site MySite   # Discourse (existing)
st-post --gist          # GitHub Gist (next)
st-post --bluesky       # Bluesky
st-post --reddit --subreddit MachineLearning   # Reddit
st-post --x             # X.com
```
Multiple flags can be combined to post to several platforms in one command:
```bash
st-post --site MySite --gist --bluesky -s 1 my_topic.json
```

---

## Story JSON write-back (proposed additions)

```json
"story[n]": {
  "topic_id":     12345,
  "post_url":     "https://forum.example.com/t/slug/12345",
  "mp3_url":      "https://forum.example.com/uploads/file.mp3",
  "gist_url":     "https://gist.github.com/b202i/abc123",
  "gist_id":      "abc123",
  "x_url":        "https://x.com/b202i/status/987654321",
  "bluesky_url":  "https://bsky.app/profile/you.bsky.social/post/xyz",
  "reddit_url":   "https://reddit.com/r/subreddit/comments/abc/title"
}
```

