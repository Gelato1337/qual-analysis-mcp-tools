"""Draw the pipeline figures as standalone SVG files (no fonts or scripts loaded from outside).

    python3 scripts/figures.py            # writes docs/figures/*.svg

- stages.svg: the stages and, for each, what the model is given, what the AI does, what the system
  checks and where the researcher steps in.
- seq-<stage>.svg: one sequence diagram per stage (pipeline, AI model, MCP server, record).

The figures describe the method in general: k = interviews used for calibration, n = batch size.
Never put a run's numbers, IDs or data in them.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "figures"

INK, MUTED, LINE, CODE = "#16191f", "#5d6470", "#d5d9df", "#e9ecf1"
STOP, STOP_SOFT, CTX, CTX_SOFT = "#c2410c", "#fde7da", "#0d7d70", "#dff2ef"
SANS = "Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"

# Helvetica advance widths (per 1000 em), enough to wrap text without a font library.
_W = dict(zip("abcdefghijklmnopqrstuvwxyz",
              [556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556,
               333, 500, 278, 556, 500, 722, 500, 500, 500]))
_W.update(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
              [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778, 667, 778,
               722, 667, 611, 722, 667, 944, 667, 667, 611]))
_W.update({c: 556 for c in "0123456789"})
_W.update({" ": 278, ".": 278, ",": 278, ":": 278, ";": 278, "(": 333, ")": 333, "-": 333,
           "'": 191, '"': 355, "?": 556, "+": 584, "→": 1000, "…": 1000, "◆": 800, "↻": 900})


def width(text: str, size: float) -> float:
    return sum(_W.get(c, 600) for c in text) * size / 1000 * 1.04


def wrap(text: str, size: float, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if cur and width(trial, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur] if cur else lines


def svg(w: float, h: float, title: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" '
            f'height="{h:g}" font-family="{SANS}" font-size="13" fill="{INK}">\n'
            f'<title>{escape(title)}</title>\n'
            f'<rect width="100%" height="100%" fill="#ffffff"/>\n{body}</svg>\n')


# ---------- A: stages and what happens in each ----------

STAGES = [("Calibration", "1 session · k interviews"),
          ("1st-order concepts", "1 session per interview"),
          ("2nd-order themes", "1 session"),
          ("Aggregate dimensions", "1 session"),
          ("Revision", "1 session")]
ROWS = [
    ("Model is given", "ctx", ["Brief, method guide, k transcripts",
                               "One transcript, the codebook, earlier notes",
                               "All concepts and notes; prior research",
                               "Themes with their evidence",
                               "The whole structure"]),
    ("AI does", "ai", ["Codes concepts with quotes; proposes codebook rules; asks questions",
                       "Reuses or adds concepts; notes what does not fit",
                       "Groups concepts into themes, with a reason each",
                       "Groups themes; says how each answers the question; looks for counter-evidence",
                       "Fixes what does not hold; explains how dimensions connect"]),
    ("System checks", "check", ["Quote is word for word in the interview",
                                "Same check; no memory between interviews",
                                "2+ concepts per theme; one theme per concept",
                                "An answer to the question is required",
                                "Nothing deleted; every change logged"]),
    ("Researcher", "stop", ["Approve rules, answer questions",
                            "Review the concepts (after every batch of n, if batched)",
                            "Regroup, or group yourself",
                            "Question the answers",
                            "Accept, or fork from any stage"]),
]
CELL = {"ctx": (CTX_SOFT, CTX), "ai": ("#ffffff", INK), "check": (CODE, LINE), "stop": (STOP_SOFT, STOP)}
KEY = [("ctx", "given to the model"), ("ai", "AI (prompted)"), ("check", "checked by the system"),
       ("stop", "researcher")]
PARAMS = ("Parameters: k = interviews used for calibration; n = batch size, optional, chosen from the "
          "model's context length and the length of the interviews. Without batches, the researcher "
          "reviews once after all interviews are coded.")


def stages_figure() -> str:
    m, lab_w, col_w, gap, out_w = 24, 104, 176, 20, 128
    fs, lh, pad = 12.5, 16, 9
    xs = [m + lab_w + gap + i * (col_w + gap) for i in range(len(STAGES))]
    out_x = xs[-1] + col_w + gap
    w = out_x + out_w + m
    b, y = [], m
    for i, (name, sub) in enumerate(STAGES):
        b.append(f'<rect x="{xs[i]}" y="{y}" width="{col_w}" height="48" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>')
        b.append(f'<text x="{xs[i] + 10}" y="{y + 21}" font-family="{SERIF}" font-size="14" font-weight="600">{escape(name)}</text>')
        b.append(f'<text x="{xs[i] + 10}" y="{y + 38}" font-size="11.5" fill="{MUTED}">{escape(sub)}</text>')
        if i:
            b.append(f'<text x="{xs[i] - gap / 2}" y="{y + 29}" text-anchor="middle" font-size="16">→</text>')
    y += 48 + 10
    rows_top = y
    for label, kind, cells in ROWS:
        fill, stroke = CELL[kind]
        prefix = "◆ " if kind == "stop" else ""
        wrapped = [wrap(prefix + c, fs, col_w - 2 * pad) for c in cells]
        h = max(len(ls) for ls in wrapped) * lh + 2 * pad - 2
        b.append(f'<text x="{m}" y="{y + h / 2 + 4}" font-size="10.5" font-weight="700" letter-spacing="0.6" fill="{MUTED}">{escape(label.upper())}</text>')
        for x, ls in zip(xs, wrapped):
            b.append(f'<rect x="{x}" y="{y}" width="{col_w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
            for j, line in enumerate(ls):
                ty = y + pad + 11 + j * lh
                if prefix and j == 0:
                    line = f'<tspan fill="{STOP}">◆</tspan>{escape(line[1:])}'
                else:
                    line = escape(line)
                b.append(f'<text x="{x + pad}" y="{ty}" font-size="{fs}">{line}</text>')
        y += h + 8
    rows_bottom = y - 8
    out_h = 3 * 18 + 40
    out_y = (rows_top + rows_bottom) / 2 - out_h / 2
    b.append(f'<text x="{out_x - gap / 2}" y="{out_y + out_h / 2 + 5}" text-anchor="middle" font-size="16">→</text>')
    b.append(f'<rect x="{out_x}" y="{out_y}" width="{out_w}" height="{out_h}" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>')
    for j, line in enumerate(["Output", "Data structure", "Claim → quote table", "Full log"]):
        weight = ' font-weight="700"' if j == 0 else ""
        b.append(f'<text x="{out_x + out_w / 2}" y="{out_y + 26 + j * 18}" text-anchor="middle" font-size="{fs}"{weight}>{escape(line)}</text>')
    y += 10
    kx = m + lab_w + gap
    for kind, text in KEY:
        fill, stroke = CELL[kind]
        if kind == "stop":
            b.append(f'<rect x="{kx + 3}" y="{y + 2}" width="9" height="9" fill="{STOP}" transform="rotate(45 {kx + 7.5} {y + 6.5})"/>')
        else:
            b.append(f'<rect x="{kx}" y="{y}" width="16" height="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        b.append(f'<text x="{kx + 24}" y="{y + 11}" font-size="12" fill="{MUTED}">{escape(text)}</text>')
        kx += 24 + width(text, 12) + 26
    y += 30
    for j, line in enumerate(wrap(PARAMS, 12, w - 2 * m - lab_w - gap)):
        b.append(f'<text x="{m + lab_w + gap}" y="{y + j * 17}" font-size="12" fill="{MUTED}">{escape(line)}</text>')
        y_end = y + j * 17
    return svg(w, y_end + m, "Pipeline stages and what happens in each", "\n".join(b) + "\n")


# ---------- S: one sequence diagram per stage ----------

LANES = [("Pipeline", "code"), ("AI model", "in Claude Code"), ("MCP server", "checks"), ("Record", "database + log")]
P, A, S, R = 0, 1, 2, 3


def msg(f, t, text, ret=False):
    return {"k": "m", "f": f, "t": t, "text": text, "ret": ret}


SEQ = {
    "calibrate": ("Calibration", "Stop: the researcher approves rules, answers the questions, or forks.", [
        msg(P, A, '"Calibrate on interviews 1 … k"'),
        msg(A, S, "read the brief, method guide, how-to guides"), msg(S, A, "brief, guides", True),
        {"k": "loop", "label": "for each of the k interviews", "steps": [
            msg(A, S, "open the interview"), msg(S, A, "transcript by segment", True),
            msg(A, S, "add concept + quote + reason"),
            {"k": "alt", "label": "if the quote is not in the interview", "steps": [msg(S, A, "refused, nothing saved", True)]},
            msg(S, R, "save + log"),
            msg(A, S, "notes: who, what did not fit, doubts")]},
        msg(A, S, "propose codebook rules"),
        msg(A, S, "checkpoint: summary + questions"), msg(S, R, "run waits; writes blocked")]),
    "first_order": ("1st-order (interview i)", "Next interview: a new session with no memory. It reads the record instead.", [
        msg(P, A, '"Code interview i"'),
        msg(A, S, "ask for the codebook and transcript"), msg(S, A, "rules, earlier notes, transcript of i", True),
        msg(A, S, "add concept + quote + reason"),
        {"k": "alt", "label": "if the quote is not in interview i", "steps": [
            msg(S, A, "refused, nothing saved", True), msg(A, S, "re-read, try again with the exact words")]},
        msg(S, R, "save + log the event"),
        msg(A, S, "same idea as an earlier concept? add the quote to it"),
        msg(A, S, "write notes on interview i"), msg(A, P, "done", True)]),
    "batch": ("Batch tidy-up (optional)", "Stop: the researcher reviews the batch and approves rules.", [
        msg(P, A, '"Tidy up batch b (n interviews)"'),
        msg(A, S, "read interview notes and what did not fit"), msg(S, A, "notes", True),
        msg(A, S, "find near-duplicate concepts"), msg(S, A, "evidence for each", True),
        msg(A, S, "merge duplicates, with a reason"), msg(S, R, "merged; the old ones stay in the history"),
        msg(A, S, "propose rules for what keeps recurring"),
        msg(A, S, "batch note"),
        {"k": "alt", "label": "if it cites no interview notes", "steps": [msg(S, A, "refused", True)]},
        msg(A, S, "checkpoint"), msg(S, R, "run waits")]),
    "themes": ("2nd-order themes", "Stop: the researcher regroups, groups by hand, or forks.", [
        msg(P, A, '"Build the themes"'),
        msg(A, S, "read the brief, incl. prior research; how-to"), msg(S, A, "brief, guide", True),
        msg(A, S, "list all concepts and notes"), msg(S, A, "all concepts", True),
        {"k": "loop", "label": "for each group of concepts", "steps": [
            msg(A, S, "evidence for unclear concepts"), msg(S, A, "quotes + notes", True),
            msg(A, S, "add theme + concepts + a reason each"),
            {"k": "alt", "label": "if fewer than 2, or a concept is already placed", "steps": [msg(S, A, "refused", True)]},
            msg(S, R, "save + log")]},
        msg(A, S, "notes on concepts that fit nowhere"),
        msg(A, S, "checkpoint"), msg(S, R, "run waits")]),
    "dimensions": ("Aggregate dimensions", "Stop: the researcher questions the answers, or forks.", [
        msg(P, A, '"Build the dimensions"'),
        msg(A, S, "list the themes"), msg(S, A, "all themes", True),
        {"k": "loop", "label": "for each dimension", "steps": [
            msg(A, S, "add dimension + themes + how it answers the question"),
            {"k": "alt", "label": "if there is no answer to the question", "steps": [msg(S, A, "refused", True)]},
            msg(S, R, "save + log"),
            msg(A, S, "search the interviews for counter-evidence"), msg(S, A, "passages", True),
            msg(A, S, "counter-evidence note")]},
        msg(A, S, "checkpoint"), msg(S, R, "run waits")]),
    "revise": ("Revision", "The log alone rebuilds the identical result, and any stage can be forked.", [
        msg(P, A, '"Revise the whole structure"'),
        {"k": "loop", "label": "for each dimension, top-down", "steps": [
            msg(A, S, "everything behind it: themes, concepts, quotes"), msg(S, A, "evidence pack", True),
            msg(A, S, "fix what does not hold, with a reason"), msg(S, R, "new version; the old one kept")]},
        msg(A, S, "anything still open?"), msg(S, A, "list of open items", True),
        msg(A, S, "final note: how the dimensions connect"),
        msg(A, S, "checkpoint"), msg(S, R, "run waits")]),
}
X, STEP = [115, 345, 575, 805], 34


def sequence_figure(name: str, end: str, steps: list) -> str:
    out: list[str] = []
    y = 80

    def block(steps, depth):
        nonlocal y
        for s in steps:
            if s["k"] == "m":
                x1, x2 = X[s["f"]], X[s["t"]]
                d = 1 if x2 > x1 else -1
                dash = ' stroke-dasharray="5 4"' if s["ret"] else ""
                out.append(f'<line x1="{x1}" y1="{y}" x2="{x2 - 2 * d}" y2="{y}" stroke="{INK}" stroke-width="1.5"{dash} marker-end="url(#ah)"/>')
                out.append(f'<text x="{(x1 + x2) / 2:g}" y="{y - 7}" text-anchor="middle">{escape(s["text"])}</text>')
                y += STEP
                continue
            alt = s["k"] == "alt"
            top = y - 18
            y += 20
            start = len(out)
            block(s["steps"], depth + 1)
            bot = y - 18
            inset = 12 * depth
            wide = s["k"] == "loop" or any(z["k"] == "m" and R in (z["f"], z["t"]) for z in s["steps"])
            left, right = 250 + inset, (880 if wide else 660) - inset
            if alt:
                frame = [f'<rect x="{left}" y="{top}" width="{right - left}" height="{bot - top + 6}" rx="4" fill="{STOP_SOFT}" stroke="{STOP}" stroke-width="1.2"/>',
                         f'<text x="{left + 8}" y="{top + 14}" font-size="12" font-weight="700" fill="{STOP}">{escape(s["label"])}</text>']
            else:
                frame = [f'<rect x="{left}" y="{top}" width="{right - left}" height="{bot - top + 6}" rx="4" fill="none" stroke="{MUTED}" stroke-width="1.2"/>',
                         f'<text x="{left + 8}" y="{top + 14}" font-size="12" font-weight="700" fill="{MUTED}">↻ {escape(s["label"])}</text>']
            out[start:start] = frame
            y += 10

    block(steps, 0)
    h = y + 50
    head = [f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>']
    for i, (lane, sub) in enumerate(LANES):
        head += [f'<rect x="{X[i] - 75}" y="10" width="150" height="44" fill="#ffffff" stroke="{INK}" stroke-width="1.5"/>',
                 f'<text x="{X[i]}" y="31" text-anchor="middle" font-weight="700">{lane}</text>',
                 f'<text x="{X[i]}" y="47" text-anchor="middle" font-size="12" fill="{MUTED}">{escape(sub)}</text>',
                 f'<line x1="{X[i]}" y1="54" x2="{X[i]}" y2="{h - 50}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 4"/>']
    fill, stroke = (STOP_SOFT, STOP) if end.startswith("Stop") else (CODE, LINE)
    foot = [f'<rect x="40" y="{h - 44}" width="840" height="36" rx="3" fill="{fill}" stroke="{stroke}"/>',
            f'<text x="460" y="{h - 21}" text-anchor="middle">{escape(end)}</text>']
    return svg(900, h, f"Sequence: {name}", "\n".join(head + out + foot) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stages.svg").write_text(stages_figure())
    for key, (name, end, steps) in SEQ.items():
        (OUT / f"seq-{key}.svg").write_text(sequence_figure(name, end, steps))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
