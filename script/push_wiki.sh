#!/usr/bin/env env bash
# script/push_wiki.sh — Push docs/wiki/ pages to the GitHub Wiki repo.
#
# The GitHub Wiki is a separate git repo at:
#   https://github.com/b202i/cross.wiki.git
#
# This script:
#   1. Clones (or pulls) the wiki repo into /tmp/cross-wiki/
#   2. Copies all docs/wiki/*.md files into it
#   3. Commits and pushes
#
# Usage:
#   bash script/push_wiki.sh
#   bash script/push_wiki.sh "update st-man page"   # custom commit message

set -euo pipefail

WIKI_REPO="https://github.com/b202i/cross.wiki.git"
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
    git clone "${WIKI_REPO}" "${WIKI_TMP}"
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

