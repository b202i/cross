#!/usr/bin/env bash
# script/push_wiki.sh — Push docs/wiki/ pages to the GitHub Wiki repo.
#
# The GitHub Wiki is a separate git repo at:
#   https://github.com/b202i/cross.wiki.git   (HTTPS — needs credential helper)
#   git@github.com:b202i/cross.wiki.git        (SSH   — preferred; set WIKI_SSH=1)
#
# This script:
#   1. Clones (or pulls) the wiki repo into /tmp/cross-wiki/
#   2. Copies all docs/wiki/*.md files into it
#   3. Commits and pushes
#
# Usage:
#   bash script/push_wiki.sh
#   bash script/push_wiki.sh "update st-man page"   # custom commit message
#   WIKI_SSH=1 bash script/push_wiki.sh             # use SSH remote (recommended)
#
# First-time setup — GitHub creates the wiki repo lazily.  Before running this
# script on a fresh repo you must initialise it once via the GitHub UI:
#   1. Go to https://github.com/b202i/cross/wiki
#   2. Click "Create the first page", save with any content
#   3. Then re-run this script — it will overwrite that placeholder page

set -euo pipefail

WIKI_HTTPS="https://github.com/b202i/cross.wiki.git"
WIKI_SSH_URL="git@github.com:b202i/cross.wiki.git"
WIKI_REPO="${WIKI_HTTPS}"
if [ "${WIKI_SSH:-0}" = "1" ]; then
    WIKI_REPO="${WIKI_SSH_URL}"
fi

WIKI_TMP="/tmp/cross-wiki"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIKI_SRC="${REPO_ROOT}/docs/wiki"
MSG="${1:-sync wiki from docs/wiki/}"

echo "→ Building auto-generated pages..."
python "${REPO_ROOT}/script/build_wiki.py"

if [ -d "${WIKI_TMP}/.git" ]; then
    echo "→ Pulling existing wiki clone..."
    git -C "${WIKI_TMP}" pull --quiet
else
    echo "→ Cloning wiki repo..."
    if ! git clone "${WIKI_REPO}" "${WIKI_TMP}" 2>&1; then
        echo ""
        echo "✗ Could not clone the GitHub Wiki repo."
        echo "  GitHub creates the wiki repo lazily — it doesn't exist until"
        echo "  you create the first page through the GitHub UI."
        echo ""
        echo "  One-time setup:"
        echo "    1. Go to https://github.com/b202i/cross/wiki"
        echo "    2. Click 'Create the first page', save with any content"
        echo "    3. Re-run:  bash script/push_wiki.sh"
        echo ""
        echo "  Tip: use SSH to avoid HTTPS credential prompts:"
        echo "    WIKI_SSH=1 bash script/push_wiki.sh"
        echo ""
        exit 1
    fi
fi

echo "→ Copying docs/wiki/*.md → ${WIKI_TMP}/"
cp "${WIKI_SRC}"/*.md "${WIKI_TMP}/"

cd "${WIKI_TMP}"
git add -A
if git diff --cached --quiet; then
    echo "→ No changes to push."
else
    git commit -m "${MSG}"
    git push
    echo "→ Wiki updated: https://github.com/b202i/cross/wiki"
fi
