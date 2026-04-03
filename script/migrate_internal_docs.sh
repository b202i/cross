#!/usr/bin/env bash
# script/migrate_internal_docs.sh
#
# Moves internal working files from the public cross/ repo to a private
# cross-internal/ companion repo.
#
# Prerequisites:
#   1. Create the private repo on GitHub first:
#      gh repo create b202i/cross-internal --private \
#         --description "Cross internal development notes"
#   2. Run this script from the cross/ project root:
#      bash script/migrate_internal_docs.sh
#
# What it does:
#   - Clones cross-internal next to cross/ (~/github/cross-internal)
#   - Copies all 50 internal files into cross-internal/
#   - Commits and pushes cross-internal
#   - git rm's the files from the public cross/ repo
#   - The caller must then: git commit + git push in cross/
#
# Safe to re-run: skips files already removed from cross/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CROSS_DIR="$(dirname "$SCRIPT_DIR")"
INTERNAL_DIR="$(dirname "$CROSS_DIR")/cross-internal"

INTERNAL_REMOTE="https://github.com/b202i/cross-internal.git"

# ── List of files to migrate ────────────────────────────────────────────────
INTERNAL_FILES=(
  # Bug fix logs
  BUG_FIX_DOTENV_LOADING.txt
  BUG_FIX_SUMMARY.txt
  BUGFIX_STORY_STRUCTURE.md
  BUGFIX_st_fact_all_cached.md

  # Feature planning
  FEATURE_AI_CAPTION.md
  FEATURE_fact_check_current_all_ai.md
  PHASE1_IMPLEMENTATION.md

  # Implementation / design notes
  AI_CAPTION_AUTH_FIX.md
  AI_CAPTION_FIX_SUMMARY.txt
  AI_CAPTION_FRAMEWORK_CLARIFICATION.md
  AI_CAPTION_FRAMEWORK_VERIFICATION.txt
  AI_CAPTION_IMPLEMENTATION.txt
  AI_CAPTION_NOTE.txt
  AI_CAPTION_READY.txt
  AI_HUMAN_READABLE_FIX.md
  AI_OPTIONS_FIX_FILTER.md
  AI_OPTIONS_INDEX.md
  AI_OPTIONS_STATUS.md
  AI_OPTIONS_SUMMARY.md
  AI_SHORT_COMPLETE.txt
  AI_SHORT_FEATURE.txt
  AI_SHORT_QUICKSTART.txt
  AI_SHORT_TROUBLESHOOTING.txt
  AI_STORY_PROMPT_IMPROVEMENT.md
  IMPLEMENTATION_AI_OPTIONS.md
  IMPLEMENTATION_error_handling.md
  KEY_CHOICE_at_symbol.md
  REFACTORING_COMPLETE.md
  WORD_COUNT_IMPROVEMENTS.txt

  # Testing notes
  REGRESSION_TESTS_CAPTION.txt
  REGRESSION_TESTS_SUMMARY.txt
  TESTING_AI_OPTIONS.md
  TESTING_QUICKSTART.md
  TESTING_ROADMAP.md
  TESTING_SUMMARY.md

  # Speed / timing working notes
  ST_SPEED_COMPLETE.txt
  ST_SPEED_ENHANCEMENT.md
  ST_SPEED_FINAL.txt
  ST_SPEED_STATUS.md
  TIMING_QUICKREF.txt
  TIMING_RERUN_ANSWER.md
  TIMING_RERUN_COMPLETE.txt
  TIMING_VERSIONING_ISSUE.md

  # Historical / branding decisions
  README_app_name.md
  README_namechange.md
  README_rebrand_cross.md
  README_yakyak.md
)

# ── Step 1: Clone or pull cross-internal ────────────────────────────────────
echo "==> Setting up cross-internal at $INTERNAL_DIR"
if [ -d "$INTERNAL_DIR/.git" ]; then
  echo "    Already cloned — pulling latest"
  git -C "$INTERNAL_DIR" pull --ff-only
else
  echo "    Cloning $INTERNAL_REMOTE"
  git clone "$INTERNAL_REMOTE" "$INTERNAL_DIR"
fi

# ── Step 2: Copy files to cross-internal ────────────────────────────────────
echo "==> Copying files to cross-internal"
COPIED=0
MISSING=0
for f in "${INTERNAL_FILES[@]}"; do
  src="$CROSS_DIR/$f"
  if [ -f "$src" ]; then
    cp "$src" "$INTERNAL_DIR/$f"
    echo "    copied  $f"
    COPIED=$((COPIED + 1))
  else
    echo "    missing $f  (already removed or never existed)"
    MISSING=$((MISSING + 1))
  fi
done
echo "    $COPIED copied, $MISSING already gone"

# ── Step 3: Commit and push cross-internal ───────────────────────────────────
echo "==> Committing to cross-internal"
cd "$INTERNAL_DIR"
git add -A
if git diff --cached --quiet; then
  echo "    Nothing new to commit in cross-internal"
else
  git commit -m "Archive internal working files from cross/ public repo"
  git push
  echo "    Pushed to cross-internal"
fi

# ── Step 4: Remove files from public cross/ repo ────────────────────────────
echo "==> Removing files from public cross/ repo"
cd "$CROSS_DIR"
REMOVED=0
for f in "${INTERNAL_FILES[@]}"; do
  if [ -f "$f" ]; then
    git rm --cached "$f" 2>/dev/null || true
    rm -f "$f"
    echo "    removed $f"
    REMOVED=$((REMOVED + 1))
  fi
done
echo "    $REMOVED file(s) removed"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "==> Done. Next steps in cross/:"
echo "    git status"
echo "    git add -A"
echo "    git commit -m 'Remove internal working files (moved to cross-internal)'"
echo "    git push"

