#!/usr/bin/env bash
# symbolic_links.bash — Install st-* command symlinks into .venv/bin.
#
# Usage (from any directory):
#   bash script/symbolic_links.bash
#
# The script locates itself, finds the project root (one level up), then
# creates absolute symlinks in .venv/bin.  Safe to re-run — existing
# links are removed and recreated.
#
# IMPORTANT: Run this AFTER 'pip install -r requirements.txt'.
#   pip removes unregistered scripts from bin/ during its install phase,
#   so symlinks created before pip runs will be silently deleted.
#
# PYTHON VERSION: This project requires Python 3.11.
#   pyaudio and other audio packages have unreliable wheels on 3.12+.
#   To create the venv:
#     python3.11 -m venv .venv
#     source .venv/bin/activate
#     pip install -r requirements.txt
#     bash script/symbolic_links.bash
#
# FUTURE — PyPI publish (T-04 / T-15):
#   When Cross is published as 'cross-ai' on PyPI, the [project.scripts]
#   table in pyproject.toml will declare all st-* entry points.  pip will
#   then generate the bin/ wrappers automatically on 'pip install cross-ai'
#   and this script will no longer be needed for normal installs.
#   Keep it for development installs (editable / git-clone workflow).

set -euo pipefail

# ── Locate directories ────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_BIN="${PROJECT_DIR}/.venv/bin"

if [[ ! -d "${VENV_BIN}" ]]; then
    echo "ERROR: .venv/bin not found at: ${VENV_BIN}"
    echo ""
    echo "Create the venv first (Python 3.11 required):"
    echo "  python3.11 -m venv ${PROJECT_DIR}/.venv"
    echo "  source ${PROJECT_DIR}/.venv/bin/activate"
    echo "  pip install -r ${PROJECT_DIR}/requirements.txt"
    echo "  bash ${BASH_SOURCE[0]}"
    exit 1
fi

# Confirm the venv is Python 3.11
VENV_PY_VER=$("${VENV_BIN}/python" -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>/dev/null || true)
if [[ "${VENV_PY_VER}" != "3.11" ]]; then
    echo "ERROR: .venv is Python ${VENV_PY_VER}, but 3.11 is required."
    echo ""
    echo "Recreate the venv:"
    echo "  python3.11 -m venv --clear ${PROJECT_DIR}/.venv"
    echo "  source ${PROJECT_DIR}/.venv/bin/activate"
    echo "  pip install -r ${PROJECT_DIR}/requirements.txt"
    echo "  bash ${BASH_SOURCE[0]}"
    exit 1
fi

echo "Project : ${PROJECT_DIR}"
echo "Venv bin: ${VENV_BIN}"
echo ""

# ── Commands to link ──────────────────────────────────────────────────────────
COMMANDS=(
    st-admin
    st-analyze
    st-bang
    st-cat
    st-cross
    st-domain
    st-edit
    st-fact
    st-fetch
    st-find
    st-fix
    st-gen
    st-heatmap
    st-ls
    st-man
    st-merge
    st-new
    st-plot
    st-post
    st-prep
    st-print
    st-read
    st-rm
    st-speak
    st-speed
    st-stones
    st-voice
    st-verdict
    st
)

# ── Create symlinks ───────────────────────────────────────────────────────────
for CMD in "${COMMANDS[@]}"; do
    # Source .py file (st → st.py, st-foo → st-foo.py)
    if [[ "${CMD}" == "st" ]]; then
        SRC="${PROJECT_DIR}/st.py"
    else
        SRC="${PROJECT_DIR}/${CMD}.py"
    fi

    LINK="${VENV_BIN}/${CMD}"

    if [[ ! -f "${SRC}" ]]; then
        echo "  SKIP  ${CMD}  (source not found: ${SRC})"
        continue
    fi

    # Remove stale link or file if it exists
    if [[ -e "${LINK}" || -L "${LINK}" ]]; then
        rm "${LINK}"
    fi

    ln -s "${SRC}" "${LINK}"
    echo "  OK    ${LINK} -> ${SRC}"
done

echo ""

# ── Verify ────────────────────────────────────────────────────────────────────
LINKED=$(find "${VENV_BIN}" -name "st" -o -name "st-*" | grep -v "\.py$" | wc -l | tr -d ' ')
echo "Verified: ${LINKED} symlink(s) present in ${VENV_BIN}"
echo ""
echo "Done. Try: st --help"
echo ""
echo "NOTE: Run this script AFTER 'pip install -r requirements.txt'."
echo "      pip may remove unregistered scripts from bin/ during install."
