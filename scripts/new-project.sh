#!/usr/bin/env bash
# Make a new, self-contained qls project from a folder of interview files.
#
#   scripts/new-project.sh NAME FOLDER [INTERVIEWER_LABEL ...]
#
# Projects are made in $QLS_PROJECTS (default ~/coding/qls-projects), one folder each.
#
#   NAME     project folder name (letters, digits, - and _), e.g. my-study-gioia
#   FOLDER   where the interview files are now (copied into NAME/raw, never changed)
#   labels   speaker labels used for the interviewer(s), e.g. A E
#            (everyone else is treated as an informant)
#
# Result: NAME/raw (originals, copied), NAME/reference (put anything the agent must never see here),
# NAME/text (converted), NAME/intent.yaml (write the brief), its own qls.db and TypeDB databases.
# Nothing is ingested from reference/. Check `qls sources` before creating a run.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
QLS="${QLS:-$HERE/../.venv/bin/qls}"
NAME="$1"; SRC="$(cd "$2" && pwd)"; shift 2
mkdir -p "${QLS_PROJECTS:-$HOME/coding/qls-projects}" && cd "${QLS_PROJECTS:-$HOME/coding/qls-projects}"
[[ "$NAME" =~ ^[A-Za-z0-9_-]+$ ]] || { echo "bad project name: $NAME"; exit 1; }
[ -e "$NAME" ] && { echo "$NAME already exists"; exit 1; }
[ -d "$SRC" ] || { echo "no folder $SRC"; exit 1; }

export PYTHONWARNINGS=ignore
"$QLS" init "$NAME" --name "$NAME" >/dev/null
mkdir -p "$NAME/raw" "$NAME/reference" "$NAME/text"
cp -p "$SRC"/* "$NAME/raw/" 2>/dev/null || true
rm -f "$NAME/raw/.DS_Store"

if [ "$#" -gt 0 ]; then   # this project's interviewer labels replace the defaults
  labels=$(printf '"%s", ' "$@"); labels="[${labels%, }]"
  sed -i '' "s/^interviewer_labels = .*/interviewer_labels = $labels/" "$NAME/qls.toml"
fi

echo "Project $NAME created. Next:"
echo "  1. move anything the agent must not see (original analyses, papers) from $NAME/raw to $NAME/reference"
echo "  2. python3 $HERE/convert.py $NAME/raw $NAME/text"
echo "  3. cd $NAME && $QLS ingest text/*.txt && $QLS sources"
echo "  4. write $NAME/intent.yaml, then: $QLS run new r1"
