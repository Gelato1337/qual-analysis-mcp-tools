# Projects

Projects live outside this repository, in `~/coding/qls-projects/` (or `$QLS_PROJECTS`), one folder per dataset. Each project is self-contained: its own sources, brief, ledger (`qls.db`)
and TypeDB databases (named `<prefix>_<run>`, prefix set in its `qls.toml`). Projects never share
anything, and every run inside a project has its own database, so runs are independent too.

```
qls-projects/
  my-study-gioia/
  my-study-content/
  ...
```

Tools in this repository: `scripts/new-project.sh` makes a project from a folder of interview
files; `scripts/convert.py` turns .doc/.docx into clean text (speaker lines, tape markers, legends).

Inside a project:

```
raw/          original interview files, never changed
reference/    material the agent must never see: original analyses, published papers
text/         converted transcripts (what is ingested)
intent.yaml   the study brief, frozen into each run
qls.toml      project settings: database prefix, interviewer speaker labels
qls.db        sources, runs, event log, provenance
logs/ agents/ reports/ probes/   created by runs
```

## Adding a dataset

```bash
scripts/new-project.sh NAME ~/Downloads/EXPORT A E     # A E = the interviewers' speaker labels
cd ~/coding/qls-projects
# move original analyses / papers from NAME/raw to NAME/reference
python3 ~/coding/qual-analysis-mcp-tools/scripts/convert.py NAME/raw NAME/text
cd NAME && qls ingest text/*.txt && qls sources  # check informant/interviewer roles per file
$EDITOR intent.yaml
qls run new r1
```

`qls` is `~/coding/qual-analysis-mcp-tools/.venv/bin/qls`. TypeDB must be running
(`~/.local/typedb/typedb-all-mac-arm64-3.12.1/typedb server`).

Check the speaker labels per dataset: the defaults treat `H` as an interviewer ("Haastattelija"),
which is wrong when `H` is the informant in your transcripts.
