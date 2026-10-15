import shutil, subprocess, sys, re, tempfile
from pathlib import Path

K = Path(__file__).parent
S = K.parent / "project-brainstorm"
CHK = S / "scripts" / "trace_check.py"
W = Path(tempfile.mkdtemp())
for _tier in ("Prototype", "MVP", "Production"):
    subprocess.run([sys.executable, str(K / "make_fixture.py"), str(W / f"fx-{_tier}"), _tier, str(S / "references" / "risk-areas.md")], check=True)

def run(d):
    p = subprocess.run([sys.executable, "-I", str(CHK), str(d)], capture_output=True, text=True)
    return p.returncode, p.stdout

def mutate(name, base, edits, delete=None):
    d = W / f"mut-{name}"
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(W / base, d)
    if delete:
        (d / delete).unlink()
    for f, fn in edits:
        p = d / f
        p.write_text(fn(p.read_text()), encoding="utf-8")
    return run(d)

sub = lambda a, b: (lambda t: t.replace(a, b, 1))
rx = lambda pat, b: (lambda t: re.sub(pat, b, t, count=1, flags=re.M))
big = "```mermaid\nflowchart LR\n" + "\n".join(f"  N{i}[n{i}] --> N{i+1}[n{i+1}]" for i in range(0, 16, 2)) + "\n```\n"

cases = [
    # name, base, edits, delete, expect_exit, expected substring ("" = none required)
    ("untouched", "fx-Prototype", [], None, 0, ""),
    ("matrix-row-missing", "fx-Prototype", [("06-test-plan.md", rx(r"^\| NFR-5 .*\n", ""))], None, 1, "NFR-5 has no row in the traceability matrix"),
    ("req-no-test", "fx-Prototype", [("06-test-plan.md", sub("| NFR-9 | C-1 | TC-11 |", "| NFR-9 | C-1 |  |"))], None, 1, "NFR-9 maps to no test case"),
    ("undefined-id", "fx-Prototype", [("04-api-spec.md", sub("FR-1 |", "FR-9 |"))], None, 1, "FR-9 is used but never defined"),
    ("adr-no-sources", "fx-Prototype", [("07-decisions.md", rx(r"^- Sources:.*$", "- Sources:"))], None, 1, "ADR-1 has no Sources"),
    ("adr-no-context", "fx-Prototype", [("07-decisions.md", rx(r"^- Context:.*\n", ""))], None, 1, "ADR-1 missing 'Context'"),
    ("risk-row-missing", "fx-Prototype", [("05-threat-model.md", rx(r"^\| Data loss .*\n", ""))], None, 1, "risk area 'Data loss'"),
    ("risk-bad-status", "fx-Prototype", [("05-threat-model.md", sub("| Accepted |", "| Maybe |"))], None, 1, "use Mitigated, Accepted or Not relevant"),
    ("mitigated-no-link", "fx-Prototype", [("05-threat-model.md", sub("| Mitigated | Control in design | NFR-6 |", "| Mitigated | Control in design |  |"))], None, 1, "Mitigated but links no FR"),
    ("group-collapsed-ok", "fx-Prototype", [("05-threat-model.md", lambda t: re.sub(r"^\| (Response time|CPU use|Memory use|Storage use|Network use|Startup time|Battery \(mobile\)) .*\n", "", t, flags=re.M).replace("## 4. Risk register\n\n| Area | Status (Mitigated / Accepted / Not relevant) | Control or reason | Link |\n|---|---|---|---|\n", "## 4. Risk register\n\n| Area | Status (Mitigated / Accepted / Not relevant) | Control or reason | Link |\n|---|---|---|---|\n| Performance and resources | Not relevant | Tiny single-user app | - |\n"))], None, 0, ""),
    ("diagram-too-big", "fx-Prototype", [("02-architecture.md", sub("```mermaid\nflowchart LR", big + "\n```mermaid\nflowchart LR"))], None, 1, "nodes (limit 15)"),
    ("diagram-styling", "fx-Prototype", [("02-architecture.md", sub("  U --> A", "  U --> A\n  classDef x fill:#f00"))], None, 1, "uses styling"),
    ("er-attributes", "fx-Prototype", [("03-data-model.md", sub("  HABIT ||--o{ CHECKIN : has", "  HABIT ||--o{ CHECKIN : has\n  HABIT {\n    int id\n  }"))], None, 1, "lists attributes"),
    ("diagram-in-api", "fx-Prototype", [("04-api-spec.md", lambda t: t + "\n```mermaid\nflowchart LR\n  A --> B\n```\n")], None, 1, "only 02 and 03 hold diagrams"),
    ("proto-with-sequence", "fx-MVP", [("01-srs.md", sub("Tier: MVP", "Tier: Prototype")), ("02-architecture.md", sub("Tier: MVP", "Tier: Prototype")), ("03-data-model.md", sub("Tier: MVP", "Tier: Prototype")), ("04-api-spec.md", sub("Tier: MVP", "Tier: Prototype")), ("05-threat-model.md", sub("Tier: MVP", "Tier: Prototype")), ("06-test-plan.md", sub("Tier: MVP", "Tier: Prototype")), ("07-decisions.md", sub("Tier: MVP", "Tier: Prototype")), ("08-roadmap.md", sub("Tier: MVP", "Tier: Prototype"))], None, 1, "diagrams for tier Prototype"),
    ("tier-mismatch", "fx-Prototype", [("08-roadmap.md", sub("Tier: Prototype", "Tier: MVP"))], None, 1, "tier differs across files"),
    ("bad-header", "fx-Prototype", [("04-api-spec.md", sub("Tier: Prototype · Research: Standard · Version: 1.0", "Prototype tier"))], None, 1, "second line must be"),
    ("tbd-leftover", "fx-Prototype", [("02-architecture.md", sub("Browser UI | Show habits", "Browser UI | TBD"))], None, 1, "leftover TBD/TODO"),
    ("tbd-in-assumption-ok", "fx-Prototype", [], None, 0, ""),
    ("file-missing", "fx-Prototype", [], "08-roadmap.md", 1, "08-roadmap.md: file missing"),
    ("tc-no-req", "fx-Prototype", [("06-test-plan.md", sub("| TC-11 | NFR-9 |", "| TC-11 | none |"))], None, 1, "TC-11 names no requirement"),
    ("roadmap-req-missing", "fx-Prototype", [("08-roadmap.md", sub("NFR-8, NFR-9 |", "NFR-8 |"))], None, 1, "NFR-9 is not scheduled in any milestone"),
    ("roadmap-cycle", "fx-Prototype", [("08-roadmap.md", sub("NFR-6 | none |", "NFR-6 | M2 |"))], None, 1, "dependency cycle"),
    ("roadmap-unknown-dep", "fx-Prototype", [("08-roadmap.md", sub("| M1 | TC-3 pass |", "| M9 | TC-3 pass |"))], None, 1, "unknown milestone 'M9'"),
    ("roadmap-dup", "fx-Prototype", [("08-roadmap.md", sub("| M2 | FR-3,", "| M2 | FR-3, FR-1,"))], None, 0, "FR-1 appears in 2 milestones"),
    ("core-after-supporting", "fx-Prototype", [("08-roadmap.md", sub("| M1 | FR-1, FR-2,", "| M1 | FR-3, FR-2,")), ("08-roadmap.md", sub("| M2 | FR-3,", "| M2 | FR-1,"))], None, 0, "core FR-1 is scheduled after a supporting requirement"),
    ("endpoint-mismatch", "fx-Prototype", [("02-architecture.md", sub("GET /habits", "GET /habit"))], None, 1, "GET /habit is not in 04-api-spec.md"),
    ("er-entity-mismatch", "fx-Prototype", [("03-data-model.md", sub("USER ||--o{ HABIT", "ACCOUNT ||--o{ HABIT"))], None, 1, "entity 'account' has no"),
    ("bad-stride", "fx-Prototype", [("05-threat-model.md", sub("| Spoofing |", "| Confusing |"))], None, 1, "STRIDE category 'Confusing'"),
    ("th-no-link", "fx-Prototype", [("05-threat-model.md", sub("| Rate limit | NFR-6 |", "| Rate limit |  |"))], None, 1, "TH-1 links no FR"),
    ("bad-priority", "fx-Prototype", [("01-srs.md", sub("| core | Q3 | Main flow", "| mustHave | Q3 | Main flow"))], None, 1, "must be core or supporting"),
    ("no-core-fr", "fx-Prototype", [("01-srs.md", lambda t: t.replace("| core |", "| supporting |"))], None, 1, "no core FR"),
    ("vague-fr", "fx-Prototype", [("01-srs.md", sub("The user can mark a habit done", "The user can quickly mark a habit done"))], None, 0, "vague word 'quickly'"),
    ("weak-adr-source", "fx-Prototype", [("07-decisions.md", rx(r"^- Sources:.*$", "- Sources: some blog"))], None, 0, "Sources has no link"),
    ("malformed-fr-row", "fx-Prototype", [("01-srs.md", sub("| Main flow | test |", "| Main flow |"))], None, 1, "FR-1 row has 5 columns"),
    ("bold-ids-ok", "fx-Prototype", [("01-srs.md", sub("| FR-1 |", "| **FR-1** |")), ("05-threat-model.md", sub("| Accepted |", "| **Accepted** |"))], None, 0, ""),
    ("entity-unowned", "fx-Prototype", [("02-architecture.md", sub("E-1, E-2", "E-1"))], None, 0, "E-2 is not mentioned"),
]

fail = 0
for name, base, edits, delete, want_exit, want in cases:
    code, out = mutate(name, base, edits, delete)
    ok = code == want_exit and (want in out)
    fail += not ok
    print(("PASS" if ok else "FAIL"), name, f"(exit {code}, want {want_exit}; expect '{want}')")
    if not ok:
        print(out)
import os

def run2(chk, d, env=None, cwd=None, isolate=True):
    args = [sys.executable] + (["-I"] if isolate else []) + [str(chk), str(d)]
    p = subprocess.run(args, capture_output=True, env=env, cwd=cwd)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")

extra = 0
def check(name, ok, detail=""):
    global fail, extra
    extra += 1
    fail += not ok
    print(("PASS" if ok else "FAIL"), name, detail if not ok else "")

# Portability: a clean environment, odd paths, odd encodings, odd line endings.
clean = {"PATH": os.environ.get("PATH", ""), "LC_ALL": "C"}
legacy = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "ascii", "PYTHONUTF8": "0"}  # -I would ignore these, so the encoding test runs without it

d = W / "my project தமிழ்-design"; shutil.copytree(W / "fx-Prototype", d)
code, out, err = run2(CHK, d, env=clean, cwd="/")
check("portable-unicode-and-space-path", code == 0 and "Traceback" not in err, out + err)

d = W / "tamil-text"; shutil.copytree(W / "fx-Prototype", d)
p = d / "05-threat-model.md"; p.write_text(p.read_text(encoding="utf-8").replace("| Accepted |", "| ஏற்றுக்கொள்ளப்பட்டது |", 1), encoding="utf-8")
code, out, err = run2(CHK, d, env=legacy, isolate=False)
check("portable-non-ascii-message-no-crash", code == 1 and "Traceback" not in err and "use Mitigated" in out, out + err)

d = W / "bom"; shutil.copytree(W / "fx-Prototype", d)
for f in d.glob("*.md"):
    f.write_bytes(b"\xef\xbb\xbf" + f.read_bytes())
code, out, err = run2(CHK, d)
check("portable-utf8-bom", code == 0, out + err)

d = W / "crlf"; shutil.copytree(W / "fx-Prototype", d)
for f in d.glob("*.md"):
    f.write_bytes(f.read_bytes().replace(b"\n", b"\r\n"))
code, out, err = run2(CHK, d)
check("portable-crlf", code == 0, out + err)

copy = W / "copied skill dir" / "pb"; shutil.copytree(S, copy)
code, out, err = run2(copy / "scripts" / "trace_check.py", W / "fx-MVP", env=clean, cwd="/")
check("portable-skill-copied-elsewhere", code == 0 and "risk-areas.md not found" not in out, out + err)

print(f"\n{len(cases) + extra - fail}/{len(cases) + extra} passed")
sys.exit(1 if fail else 0)
