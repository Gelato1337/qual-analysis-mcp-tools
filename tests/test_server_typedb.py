"""The server end to end against TypeDB. Needs a TypeDB 3 server: QLS_TYPEDB=127.0.0.1:1729."""

import asyncio
import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(not os.environ.get("QLS_TYPEDB"), reason="set QLS_TYPEDB to a TypeDB 3 server")
EX = Path(__file__).resolve().parent.parent / "examples" / "synthetic"
RQ = "How do software firms adapt delivery to client pressure?"
Q_RELEASE = "Clients now expect us to release every two weeks instead of once a year."


@pytest.fixture
def p(tmp_path):
    from qls.project import Project

    p = Project.init(tmp_path / "study", f"t{os.getpid()}_{tmp_path.name[-6:]}")
    for f in sorted(EX.glob("*.txt")):
        p.ingest(f)
    p.new_run("r1", intent={"research_question": RQ, "method": "gioia"})
    yield p
    for r in p.ledger.runs():
        p.graph.drop(p.db_name(r["id"]))
    p.graph.close()


@pytest.fixture
def s(p):
    from qls.session import Session

    Session(p, "r1", "human:t").set_stage("revise", "tests use every action")  # the stage gate has its own test
    return Session(p, "r1", "agent:a")


def concept(s, label, text, source="P01"):
    return s.act("add_concept", label=label, description=f"about {label}",
                 quotes=[{"source": source, "text": text, "reason": "says it", "prompted": "spontaneous"}])


def test_concept_and_quote_in_one_call(s):
    r = concept(s, "two-week releases", Q_RELEASE)
    assert r["ok"] and r["id"] == "C-1" and r["quotes"][0]["match"] == "exact"
    bad = concept(s, "x", "Customers want fortnightly releases.")
    assert not bad["ok"] and "not found" in bad["error"] and "closest" not in bad
    assert s.status()["objects"].get("quote") == 1  # nothing saved by the refused call
    q = s.act("add_concept", label="x", description="y", quotes=[{"source": "P01", "text": Q_RELEASE}])
    assert not q["ok"] and "reason" in q["error"]
    assert not s.act("add_concept", label="x", description="y", quotes=[])["ok"]
    interviewer = concept(s, "x", "What changes have you seen in how software is delivered?")
    assert not interviewer["ok"] and "interviewer" in interviewer["error"]
    again = concept(s, "same words again", Q_RELEASE)
    assert again["quotes"][0]["id"] == "Q-1"  # same place, same quote


def test_begin_sets_default_source(s):
    b = s.begin("P02")
    assert b["ok"] and "[P02:s005]" in b["transcript"]
    r = s.act("add_concept", label="seniors", description="d", quotes=[{"text": "Finding senior people.", "reason": "r", "prompted": "prompted"}])
    assert r["ok"] and r["quotes"][0]["source"] == "P02"
    assert s.list_sources()[1]["read_by"] == ["agent:a"]


def test_groups(s):
    c1 = concept(s, "release", Q_RELEASE)["id"]
    c2 = concept(s, "legacy", "Legacy systems.")["id"]
    c3 = concept(s, "seniors", "Finding senior people.", "P02")["id"]
    assert "at least 2" in s.act("add_theme", label="t", description="d", concepts=[{"id": c1, "reason": "r"}])["error"]
    t1 = s.act("add_theme", label="Pressure", description="d", concepts=[{"id": c1, "reason": "r"}, {"id": c2, "reason": "r"}])["id"]
    clash = s.act("add_theme", label="t", description="d", concepts=[{"id": c1, "reason": "r"}, {"id": c3, "reason": "r"}])
    assert not clash["ok"] and "already in T-1" in clash["error"]
    assert "answers" in s.act("add_dimension", label="D", description="d", themes=[{"id": t1, "reason": "r"}])["error"]
    d1 = s.act("add_dimension", label="D", description="d", themes=[{"id": t1, "reason": "r"}], answers="how")["id"]
    assert not s.remove_from_group(t1, c1, "test")["ok"]  # would leave one concept
    assert s.add_to_group(t1, c3, "same pressure")["ok"]
    assert s.remove_from_group(t1, c1, "not about pressure")["ok"]
    pack = s.pack(d1)
    assert pack["members"][0]["id"] == t1 and pack["answers"] == ["how"]
    assert {m["id"] for m in pack["members"][0]["members"]} == {c2, c3}


def test_merge_and_withdraw(s):
    c1 = concept(s, "release", Q_RELEASE)["id"]
    c2 = concept(s, "legacy", "Legacy systems.")["id"]
    c3 = concept(s, "old systems", "Vanhat järjestelmät ovat iso ongelma.", "P03")["id"]
    t1 = s.act("add_theme", label="t", description="d", concepts=[{"id": c1, "reason": "r"}, {"id": c2, "reason": "r"}])["id"]
    m = s.memo([c3], "meaning", "Finnish for legacy")
    assert s.merge([c3], c2, "same thing in Finnish")["ok"]
    assert {x["quote"] for x in s._code_quotes(c2)} == {"Q-2", "Q-3"}
    assert c2 in s.get(m["id"])["links"][0]["with"]
    assert "merged into C-2" in s.get(c3)["error"]
    assert not s.withdraw(c1, "test")["ok"]  # T-1 would be left with one concept
    assert s.withdraw(t1, "premature")["ok"]
    assert s.withdraw(c1, "not about the question")["ok"]
    assert s.status()["objects"]["concept"] == 1


def test_memos(s):
    concept(s, "release", Q_RELEASE)
    assert not s.memo([], "meaning", "x")["ok"]
    assert not s.memo(["C-1"], "feeling", "x")["ok"]
    assert not s.memo(["Q-1"], "meaning", "x")["ok"]
    m1 = s.memo(["P01"], "informant", "team lead", level="interview")
    m2 = s.memo(["P01"], "informant", "team lead, public sector", level="interview")
    assert m2["id"] == m1["id"] and m2["updated"]
    assert not s.memo(["intent"], "summary", "batch", level="batch")["ok"]  # must cite interview memos
    assert s.memo(["intent"], "summary", "batch", level="batch", cites=[m1["id"]])["ok"]
    assert not s.memo(["C-1"], "meaning", "x" * 5000)["ok"]
    assert [o["check"] for o in s.check()["open"]] == ["concept_placed"]  # C-1 has no theme or memo; P01 was not begun


def test_checkpoint_codebook_and_human(p, s):
    from qls.session import Session
    from qls.util import QlsError

    concept(s, "release", Q_RELEASE)
    prop = s.propose_codebook("release rhythm", "how often releases go out",
                              examples=[{"source": "P01", "text": Q_RELEASE, "reason": "typical"}])
    assert prop["status"] == "proposed"
    s.checkpoint("coded P01", ["is cadence the point?"])
    assert not concept(s, "x", "Legacy systems.")["ok"]
    with pytest.raises(QlsError):
        s.approve(prop["id"])
    h = Session(p, "r1", "human:j")
    assert h.approve(prop["id"], {"use_when": "talk about cadence"})["codebook_version"] == 1
    h.answer("Yes, cadence matters.")
    h.resume()
    assert [i["action"] for i in s.feedback()["items"]] == ["approve", "answer", "resume"]
    assert concept(s, "legacy", "Legacy systems.")["ok"]
    assert s.get("C-2")["codebook-version"] == 1
    new = s.propose_codebook("release cadence", "how often", replaces=prop["id"])
    assert not s.revise(prop["id"], {"label": "x"}, "y")["ok"]  # approved entries change only via the researcher
    h.approve(new["id"])
    assert [e["id"] for e in s.codebook()["entries"]] == [new["id"]]


def test_replay_fork_compare_report(p, s):
    from qls.analysis import compare_groups, segment_groups
    from qls.report import build, to_html, to_markdown
    from qls.session import Session

    c1 = concept(s, "release", Q_RELEASE)["id"]
    c2 = concept(s, "legacy", "Legacy systems.")["id"]
    t1 = s.act("add_theme", label="Pressure", description="d", concepts=[{"id": c1, "reason": "r"}, {"id": c2, "reason": "r"}])
    s.act("add_dimension", label="Adapting", description="d", themes=[{"id": t1["id"], "reason": "r"}], answers="how")
    assert p.replay("r1")["identical"]
    f = p.fork("r1", "r2", at=t1["event"] - 1)
    s2 = Session(p, "r2", "agent:b")
    assert s2.status()["objects"].get("theme") is None and s2.status()["objects"]["concept"] == 2
    ga, gb = segment_groups(s.G, s.db, s.m), segment_groups(s2.G, s2.db, s2.m)
    cmp = compare_groups(ga, gb, s.m.levels())
    assert cmp["selection"]["jaccard"] == 1.0 and cmp["levels"]["theme"]["segments_b"] == 0
    rep = build(Session(p, "r1", "reviewer:x"))
    md = to_markdown(rep)
    assert "| Concept | Theme | Dimension |" in md and f"“{Q_RELEASE}”" in md and RQ in md
    assert "Adapting" in to_html(rep)
    assert f["fork_at"] == t1["event"] - 1


def test_reviewer_is_read_only(p, s):
    from qls.session import Session

    r = Session(p, "r1", "reviewer:x")
    assert "add_concept" not in r.tools() and "query" in r.tools()
    assert not r.call("memo", {"about": ["P01"], "kind": "meaning", "text": "x"})["ok"]


def test_mcp_tools_from_actions(s):
    from qls.server import build_server

    tools = {t.name: t for t in asyncio.run(build_server(s).list_tools())}
    assert {"add_concept", "add_theme", "add_dimension", "begin", "memo", "checkpoint", "query"} <= set(tools)
    assert "approve" not in tools
    schema = getattr(tools["add_concept"], "input_schema", None) or tools["add_concept"].inputSchema
    assert set(schema["required"]) == {"label", "description", "quotes"}


def test_stages_gate_agents_not_researchers(p):
    from qls.session import Session

    a, h = Session(p, "r1", "agent:a"), Session(p, "r1", "human:t")
    assert a.stage() == "calibrate" and a.status()["stage"]["creates"] == ["add_concept"]
    c1 = concept(a, "release", Q_RELEASE)["id"]
    c2 = concept(a, "legacy", "Legacy systems.")["id"]
    t = a.act("add_theme", label="T", description="d", concepts=[{"id": c1, "reason": "r"}, {"id": c2, "reason": "r"}])
    assert not t["ok"] and "not part of stage calibrate" in t["error"]
    assert h.act("add_theme", label="T", description="d", concepts=[{"id": c1, "reason": "r"}, {"id": c2, "reason": "r"}])["ok"]
    assert h.set_stage("next")["stage"] == "first_order"
    assert h.set_stage("themes")["ok"]
    assert a.revise("T-1", {"label": "x"}, "r")["ok"]
    assert a.memo(["P01"], "residual", "nothing new")["ok"]
    h.set_stage("dimensions")
    r = a.revise(c1, {"label": "y"}, "r")
    assert not r["ok"] and "does not change concepts" in r["error"]
    # fork at the start of a stage: the fork is in that stage, with what came before it
    f = p.fork("r1", "r2", at_stage="themes")
    s2 = Session(p, "r2", "agent:a")
    assert s2.stage() == "themes" and s2._type("T-1") == "theme"
    # provenance is recorded, and not shown in the agent's history
    memo = next(e for e in p.ledger.events("r1") if e["action"] == "memo")
    assert memo["meta"]["stage"] == "themes"  # the stage in force when the action was taken
    assert all("ts" not in x for x in a.history("T-1")["events"])
    assert a.guide("concept")["ok"] and not a.guide("nope")["ok"]


def test_content_analysis_method(tmp_path):
    from qls.project import Project
    from qls.session import Session

    p = Project.init(tmp_path / "ca", f"ca{os.getpid()}_{tmp_path.name[-6:]}")
    try:
        for f in sorted(EX.glob("*.txt")):
            p.ingest(f)
        p.new_run("c1", method="content_analysis", intent={"research_question": RQ, "method": "content_analysis"})
        a, h = Session(p, "c1", "agent:a"), Session(p, "c1", "human:t")
        assert a.stage() == "frame"
        k1 = a.act("add_category", label="External accelerating", description="d", origin="guide")
        k2 = a.act("add_category", label="Customers", description="d", origin="guide")
        assert k1["ok"] and k2["ok"] and k1["id"] == "K-1"          # a category may start empty
        bad = a.act("code_segment", label="x", quotes=[{"source": "P01", "text": Q_RELEASE, "reason": "r", "prompted": "spontaneous"}],
                    categories=[{"id": "K-1", "reason": "r"}])
        assert not bad["ok"] and "not part of stage frame" in bad["error"]
        h.set_stage("guide_coding")
        none = a.act("code_segment", label="x", quotes=[{"source": "P01", "text": Q_RELEASE, "reason": "r", "prompted": "spontaneous"}])
        assert not none["ok"] and "categories" in none["error"]
        s = a.act("code_segment", label="clients want faster releases", period="2020", direction="accelerating",
                  quotes=[{"source": "P01", "text": Q_RELEASE, "reason": "says it", "prompted": "spontaneous"}],
                  categories=[{"id": "K-1", "reason": "outside pressure"}, {"id": "K-2", "reason": "about clients"}])
        assert s["ok"] and s["categories"] == ["K-1", "K-2"]          # one passage, two categories
        assert not a.act("add_category", label="y", description="d", origin="emergent")["ok"]   # not in this stage
        h.set_stage("emergent")
        e = a.act("add_category", label="Release cadence", description="d", origin="emergent", parent="K-1")
        assert e["ok"] and a.add_to_group(e["id"], s["id"], "about cadence")["ok"]
        opn = {c["check"] for c in a.check()["open"]}                  # every check query is valid TypeQL
        assert "segment_categorised" not in opn and "case_description" in opn
    finally:
        for r in p.ledger.runs():
            p.graph.drop(p.db_name(r["id"]))
        p.graph.close()



def test_quote_labels_support_and_scope_rules(p, s):
    from qls.method import load_method

    q = {"source": "P01", "text": Q_RELEASE, "reason": "r"}
    no = s.act("add_concept", label="x", description="d", quotes=[q])
    assert not no["ok"] and "prompted" in no["error"]                       # the label is required
    bad = s.act("add_concept", label="x", description="d", quotes=[{**q, "prompted": "maybe"}])
    assert not bad["ok"] and "spontaneous, prompted or agreement" in bad["error"]
    c1 = s.act("add_concept", label="releases", description="d", quotes=[{**q, "prompted": "spontaneous"}])
    c2 = s.act("add_concept", label="seniors", description="d", quotes=[{"source": "P02", "text": "Finding senior people.", "reason": "r", "prompted": "prompted"}])
    assert c1["ok"] and c2["ok"] and c1["quotes"][0]["prompted"] == "spontaneous"
    t1 = s.act("add_theme", label="t", description="d", concepts=[{"id": c1["id"], "reason": "r"}, {"id": c2["id"], "reason": "r"}])
    sup = s.support(t1["id"])
    assert sup["ok"] and sup["quotes"] == 2 and sup["share"]["spontaneous"] == 0.5 and sup["informants"]["prompted"] == 1
    assert s.add_evidence(c1["id"], [{"source": "P03", "text": "Legacy systems.", "reason": "r"}])["ok"] is False   # label needed here too
    sc = s.propose_codebook("Slides on process models", "Answers count only where change over time is described",
                            use_when="the informant describes a change", not_when="opinions about a model shown", kind="scope")
    assert sc["ok"] and s.codebook()["entries"][0]["kind"] == "scope"
    assert not s.propose_codebook("x", "y", kind="rule")["ok"]
    # the run keeps working after its method changes: the project holds a copy of the version it was made with
    m = s.m
    stored = p.root / "methods" / m.hash.split(":")[-1][:16]
    assert stored.is_dir() and load_method(str(stored)).hash == s.run["method_hash"]
