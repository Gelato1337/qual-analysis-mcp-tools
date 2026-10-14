"""Convert raw interview files to plain text that `qls ingest` reads well.

    python3 scripts/convert.py PROJECT/raw PROJECT/text

- .doc / .docx / .rtf / .odt are converted with macOS `textutil`; .txt / .md are copied.
- Speaker lines written "A= text" or "A = text" become "A: text".
- A legend at the top ("A = Haastattelija", "H=Toimitusjohtaja") is kept as a note, not as speech.
- Tape and pause markers ("Nauha: 2", "Keskeytys:") become bracketed notes, so they are never read
  as a speaker.

The original files are never changed. Rerunning overwrites text/.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

CONVERT = {".doc", ".docx", ".rtf", ".odt", ".rtfd"}
COPY = {".txt", ".md", ".srt", ".vtt"}
LEGEND = re.compile(r"^\s*([A-ZÅÄÖ])\s*=\s*(Haastattelija|Interviewer|Toimitusjohtaja|Myyntijohtaja|Director[^.]*|[A-ZÅÄÖ][\w ,-]{2,40})\s*$")
EQ_SPEAKER = re.compile(r"^\s*([A-ZÅÄÖ])\s*=\s*(?=\S)")
MARKER = re.compile(r"^\s*(Nauha|Keskeytys|Tauko|Tape|Pause)\s*:\s*(.*)$", re.I)


def normalise(text: str) -> str:
    out, in_head = [], True
    for ln in text.splitlines():
        if in_head and LEGEND.match(ln):
            m = LEGEND.match(ln)
            out.append(f"(Puhuja {m.group(1)} = {m.group(2).strip()})")
            continue
        if MARKER.match(ln):
            m = MARKER.match(ln)
            out.append(f"[{m.group(1)} {m.group(2).strip()}]".replace(" ]", "]"))
            continue
        if EQ_SPEAKER.match(ln):
            in_head = False
            ln = EQ_SPEAKER.sub(lambda m: f"{m.group(1)}: ", ln, count=1)
        elif re.match(r"^\s*[A-ZÅÄÖ][\wÅÄÖåäö]{0,14}\s*:", ln):
            in_head = False
        out.append(ln)
    return "\n".join(out) + "\n"


def main(src: str, dst: str) -> None:
    src_p, dst_p = Path(src), Path(dst)
    dst_p.mkdir(parents=True, exist_ok=True)
    for f in sorted(src_p.iterdir()):
        if f.name.startswith("."):
            continue
        ext = f.suffix.lower()
        out = dst_p / (re.sub(r"\s+", "_", f.stem) + ".txt")
        if ext in CONVERT:
            text = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(f)], capture_output=True, text=True, check=True).stdout
        elif ext in COPY:
            text = f.read_text(encoding="utf-8")
        else:
            print(f"skip {f.name} (unknown type)")
            continue
        out.write_text(normalise(text), encoding="utf-8")
        print(f"{f.name} -> {out.relative_to(dst_p.parent)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    if not shutil.which("textutil"):
        sys.exit("textutil not found (macOS only). Convert .doc/.docx to .txt another way and put them in text/.")
    main(sys.argv[1], sys.argv[2])
