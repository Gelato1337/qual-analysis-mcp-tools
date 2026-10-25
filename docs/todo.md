# To do

Changes to behaviour make new runs incomparable with earlier ones: batch them, and make them
before an experiment series, not during one.

## Decided

- **Prompted / spontaneous / agreement label on every quote.** A required field on each quote in
  the code-creating actions (`add_concept`, `code_segment`), refused by the MCP tool when missing or
  unknown, stored in the DB with the quote. Cross-check against the interviewer turn before the
  quote (topic overlap) and store disagreements for the researcher. Support profile per object
  (how much of its evidence is spontaneous, prompted, agreement-only) as a query, shown in the
  viewer and in `check()`.

## Under discussion (not decided)

- How the relation between the interview guide and the research question is recorded (a "guide
  map"): in the brief, as codebook entries, or as a memo. Keep the stack lean; reuse what exists.
- Withholding prior research and sensitizing concepts from the agent until the grouping stage
  (stage-aware brief, enforced by the MCP tools rather than asked in a prompt).
- A consolidation stage in Gioia: link concepts across interviews before themes.
- Surprises recorded as their own memos (recorded, not sought).
- An events category for the content-analysis coding frame.
- A store of each run's method files at creation, so editing a method never blocks forking old runs.
- A fork that replaces the brief (needed for "same data, different lens" experiments).
- JSON export of a run (the viewer already builds the data), and a redaction mode.
- A minimal own harness for OpenAI-compatible endpoints (open-weight models on vLLM).
- Agreed concept fields frozen at calibration (proposed in the design, never built).
