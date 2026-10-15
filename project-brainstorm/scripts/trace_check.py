#!/usr/bin/env python3
"""Trace check for a project-brainstorm design package.

Usage: python3 trace_check.py <design-folder> [--risk-areas PATH]

Checks the eight files for: header line, ID definitions and references, endpoint and entity agreement, roadmap coverage,
requirement-to-test traceability, ADR completeness, risk-register coverage,
Mermaid limits, leftover TBDs. Prints ERROR and WARN lines; exits 1 on any ERROR.
Standard library only.
"""
import argparse
import re
import sys
from pathlib import Path

FILES = [
    "01-srs.md", "02-architecture.md", "03-data-model.md", "04-api-spec.md",
    "05-threat-model.md", "06-test-plan.md", "07-decisions.md", "08-roadmap.md",
]
ID_RE = re.compile(r"\b(NFR|FR|ADR|TC|TH|C|E)-(\d+)\b")
HEADER_RE = re.compile(
    r"^Tier:\s*(Prototype|MVP|Production)\s*[·•|-]\s*Research:\s*(No research|Standard|Deep)\s*[·•|-]\s*Version:\s*\d+(\.\d+)*\s*$"
)
STATUSES = {"mitigated", "accepted", "not relevant"}
DIAGRAM_CAP = {"Prototype": 2, "MVP": 3, "Production": 4}
MAX_NODES = 15
FORBIDDEN_MERMAID = re.compile(r"^\s*(classDef|class\s|style\s|linkStyle|note\s|%%)|%%\{", re.I)
CHARACTERISTICS = [
    "Functional suitability", "Performance efficiency", "Compatibility",
    "Interaction capability", "Reliability", "Security", "Maintainability",
    "Flexibility", "Safety",
]

errors, warns = [], []


def err(f, msg):
    errors.append(f"ERROR {f}: {msg}")


def warn(f, msg):
    warns.append(f"WARN  {f}: {msg}")


def table_rows(lines):
    """Yield cell lists for table body rows (skips header separator rows)."""
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        cells = [re.sub(r"[*`]", "", c).strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        yield cells


def section(text, heading_pat):
    """Lines from a heading matching heading_pat to the next heading of same or higher level."""
    lines = text.splitlines()
    out, level, on = [], 0, False
    for ln in lines:
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m:
            if on and len(m.group(1)) <= level:
                break
            if not on and len(m.group(1)) >= 2 and re.search(heading_pat, m.group(2), re.I):
                on, level = True, len(m.group(1))
                continue
        if on:
            out.append(ln)
    return out


def mermaid_blocks(text):
    return re.findall(r"```mermaid\s*\n(.*?)```", text, re.S)


def diagram_type(block):
    for ln in block.splitlines():
        s = ln.strip()
        if s:
            first = s.split()[0]
            if first in ("flowchart", "graph"):
                return "flowchart"
            return first
    return "empty"


def node_names(kind, block):
    names = set()
    lines = block.splitlines()[1:]
    if kind == "flowchart":
        for ln in lines:
            s = ln.strip()
            if not s or s == "end" or s.startswith(("subgraph", "direction")):
                continue
            s = re.sub(r'"[^"]*"', "", s)
            s = re.sub(r"\|[^|]*\|", "", s)
            prev = None
            while prev != s:
                prev = s
                s = re.sub(r"[\[\(\{][^\[\]\(\)\{\}]*[\]\)\}]", "", s)
            s = re.sub(r"[-=.~]+[>xo]?", " ", s).replace("&", " ")
            names.update(re.findall(r"[A-Za-z_]\w*", s))
    elif kind == "sequenceDiagram":
        for ln in lines:
            m = re.match(r"^\s*(?:participant|actor)\s+(\w+)", ln)
            if m:
                names.add(m.group(1))
            m = re.match(r"^\s*(\w+)\s*-{1,2}[>x)]{1,2}[+-]?\s*(\w+)\s*:", ln)
            if m:
                names.update(m.groups())
    elif kind == "erDiagram":
        for ln in lines:
            m = re.match(r"^\s*(\w+)\s+\S*--\S*\s+(\w+)\s*:", ln)
            if m:
                names.update(m.groups())
            m = re.match(r"^\s*(\w+)\s*\{\s*$", ln)
            if m:
                names.add(m.group(1))
    return names


def load_risk_areas(path):
    """Return (areas, groups): area names, and {group name: [areas]}; plus optional groups."""
    groups, cur, optional = {}, None, set()
    for ln in Path(path).read_text(encoding="utf-8-sig").splitlines():
        m = re.match(r"^##\s+(.*)", ln)
        if m:
            title = m.group(1)
            cur = re.sub(r"\s*\(.*\)\s*$", "", title).strip()
            groups[cur] = []
            if "applies when" in title.lower():
                optional.add(cur)
            continue
        if cur and ln.strip().startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if cells and cells[0] and cells[0].lower() != "area" and not re.fullmatch(r":?-+:?", cells[0]):
                groups[cur].append(cells[0])
    return groups, optional


def main():
    # Windows consoles and CI shells often use a legacy code page; never crash on non-ASCII text.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--risk-areas", default=None)
    args = ap.parse_args()
    folder = Path(args.folder)
    ra_path = Path(args.risk_areas) if args.risk_areas else Path(__file__).resolve().parent.parent / "references" / "risk-areas.md"

    texts = {}
    for f in FILES:
        p = folder / f
        if not p.is_file():
            err(f, "file missing")
            continue
        texts[f] = p.read_text(encoding="utf-8-sig")

    # 1. Header line and tier/research consistency
    tiers, researches = {}, {}
    for f, t in texts.items():
        ls = [l for l in t.splitlines() if l.strip()]
        if not ls or not ls[0].startswith("# "):
            err(f, "first line must be a '# <Doc title>: <Project name>' heading")
        m = HEADER_RE.match(ls[1].strip()) if len(ls) > 1 else None
        if not m:
            err(f, "second line must be 'Tier: <tier> · Research: <option> · Version: <n>'")
        else:
            tiers[f], researches[f] = m.group(1), m.group(2)
    if len(set(tiers.values())) > 1:
        err("all", f"tier differs across files: {sorted(set(tiers.values()))}")
    if len(set(researches.values())) > 1:
        err("all", f"research option differs across files: {sorted(set(researches.values()))}")
    tier = next(iter(tiers.values()), None)

    # 2. ID definitions
    defined = {k: set() for k in ("FR", "NFR", "C", "E", "TH", "TC", "ADR")}
    where = {"FR": "01-srs.md", "NFR": "01-srs.md", "C": "02-architecture.md", "E": "03-data-model.md",
             "TH": "05-threat-model.md", "TC": "06-test-plan.md", "ADR": "07-decisions.md"}
    for kind, f in where.items():
        t = texts.get(f, "")
        for cells in table_rows(t.splitlines()):
            m = re.fullmatch(rf"({kind})-(\d+)", cells[0]) if cells else None
            if m:
                defined[kind].add(f"{kind}-{m.group(2)}")
        for m in re.finditer(rf"^#{{2,4}}\s+({kind}-\d+)\b", t, re.M):
            defined[kind].add(m.group(1))
    all_defined = set().union(*defined.values())
    for kind, f in where.items():
        if not defined[kind] and f in texts and kind in ("FR", "NFR", "C", "E", "TC", "ADR"):
            err(f, f"no {kind}-n IDs defined (ID goes in the first table cell, or in the heading for E-n and ADR-n)")

    # 3. Undefined references
    for f, t in texts.items():
        seen = set()
        for m in ID_RE.finditer(t):
            i = f"{m.group(1)}-{m.group(2)}"
            if i not in all_defined and i not in seen:
                seen.add(i)
                err(f, f"{i} is used but never defined")

    # 4. Requirement -> test traceability
    t06 = texts.get("06-test-plan.md", "")
    matrix = {}
    for cells in table_rows(section(t06, r"traceability")):
        if cells and re.fullmatch(r"N?FR-\d+", cells[0]):
            matrix[cells[0]] = set(re.findall(r"TC-\d+", " ".join(cells[1:])))
    for r in sorted(defined["FR"] | defined["NFR"]):
        if r not in matrix:
            err("06-test-plan.md", f"{r} has no row in the traceability matrix")
        elif not matrix[r]:
            err("06-test-plan.md", f"{r} maps to no test case")
        else:
            for tc in matrix[r]:
                if tc not in defined["TC"]:
                    err("06-test-plan.md", f"{r} maps to undefined {tc}")
    for cells in table_rows(section(t06, r"test cases")):
        if cells and re.fullmatch(r"TC-\d+", cells[0]) and len(cells) > 1:
            if not re.search(r"\bN?FR-\d+\b", cells[1]):
                err("06-test-plan.md", f"{cells[0]} names no requirement")
    for cells in table_rows(section(t06, r"traceability")):
        if cells and re.fullmatch(r"N?FR-\d+", cells[0]) and len(cells) > 1:
            if not re.search(r"\b(C|E)-\d+\b|/|GET|POST|PUT|PATCH|DELETE", cells[1]):
                warn("06-test-plan.md", f"{cells[0]} names no design element (C-n, E-n or endpoint)")

    # 5. Entities owned by a component
    t02 = texts.get("02-architecture.md", "")
    for e in sorted(defined["E"]):
        if not re.search(rf"\b{e}\b", t02):
            warn("02-architecture.md", f"{e} is not mentioned in the correspondences table")

    # 6. ADR completeness
    t07 = texts.get("07-decisions.md", "")
    blocks = re.split(r"(?m)^###\s+(?=ADR-\d+)", t07)[1:]
    for b in blocks:
        adr = re.match(r"(ADR-\d+)", b).group(1)
        for field in ("Status", "Context", "Decision", "Decided by", "Alternatives rejected", "Consequences"):
            if not re.search(rf"(?m)^-\s*{field}:\s*\S", b):
                err("07-decisions.md", f"{adr} missing '{field}'")
        m = re.search(r"(?m)^-\s*Sources:\s*(.*)$", b)
        if not m or not m.group(1).strip():
            err("07-decisions.md", f"{adr} has no Sources (write 'none (No research): verify' if unresearched)")
        elif not re.search(r"https?://|verify|user preference", m.group(1), re.I):
            warn("07-decisions.md", f"{adr} Sources has no link, 'verify' or 'user preference'")

    # 7. Risk register
    t05 = texts.get("05-threat-model.md", "")
    reg_lines = section(t05, r"risk register")
    reg = {}
    for cells in table_rows(reg_lines):
        if not cells or cells[0].lower() == "area":
            continue
        reg[cells[0].lower()] = cells
        status = cells[1].lower() if len(cells) > 1 else ""
        if status not in STATUSES:
            err("05-threat-model.md", f"risk '{cells[0]}' has status '{cells[1] if len(cells) > 1 else ''}' (use Mitigated, Accepted or Not relevant)")
            continue
        if len(cells) < 4 or not cells[2]:
            err("05-threat-model.md", f"risk '{cells[0]}' has no control or reason")
        if status == "mitigated" and not (len(cells) > 3 and ID_RE.search(cells[3])):
            err("05-threat-model.md", f"risk '{cells[0]}' is Mitigated but links no FR, NFR or ADR")
    if not reg:
        err("05-threat-model.md", "risk register table not found")
    elif ra_path.is_file():
        groups, optional = load_risk_areas(ra_path)
        for g, areas in groups.items():
            gk = g.lower()
            group_row = reg.get(gk)
            if group_row and len(group_row) > 1 and group_row[1].lower() == "not relevant":
                continue
            for a in areas:
                if a.lower() not in reg:
                    (warn if g in optional else err)("05-threat-model.md", f"risk area '{a}' ({g}) has no register row")
    else:
        warn("05-threat-model.md", f"risk-areas.md not found at {ra_path}; coverage not checked")
    # 8. NFR coverage of the quality model
    t01 = texts.get("01-srs.md", "")
    for c in CHARACTERISTICS:
        if c.lower() not in t01.lower():
            warn("01-srs.md", f"ISO/IEC 25010 characteristic '{c}' not mentioned (write an NFR or say why not)")
    for cells in table_rows(section(t01, r"non-functional")):
        if cells and re.fullmatch(r"NFR-\d+", cells[0]) and len(cells) > 3:
            if not re.search(r"\d", cells[3]):
                warn("01-srs.md", f"{cells[0]} target has no number: '{cells[3]}'")

    # 9. Mermaid limits
    counts = {}
    for f, t in texts.items():
        for b in mermaid_blocks(t):
            kind = diagram_type(b)
            counts.setdefault(f, []).append(kind)
            if kind not in ("flowchart", "sequenceDiagram", "erDiagram"):
                err(f, f"unsupported diagram type '{kind}'")
                continue
            n = len(node_names(kind, b))
            if n > MAX_NODES:
                err(f, f"{kind} has {n} nodes (limit {MAX_NODES})")
            for ln in b.splitlines():
                if FORBIDDEN_MERMAID.search(ln):
                    err(f, f"{kind} uses styling, notes or comments: '{ln.strip()}'")
            if kind == "erDiagram" and re.search(r"(?m)^\s*\w+\s*\{\s*$", b):
                err(f, "erDiagram lists attributes (entity names and relationships only)")
    if tier:
        total = sum(len(v) for v in counts.values())
        if total > DIAGRAM_CAP[tier]:
            err("all", f"{total} diagrams for tier {tier} (limit {DIAGRAM_CAP[tier]})")
        want = {"02-architecture.md": ["flowchart"], "03-data-model.md": ["erDiagram"]}
        if tier in ("MVP", "Production"):
            want["02-architecture.md"].append("sequenceDiagram")
        if tier == "Production":
            want["02-architecture.md"].append("flowchart")
        for f, kinds in want.items():
            have = sorted(counts.get(f, []))
            if have != sorted(kinds):
                err(f, f"diagram slots for {tier} are {sorted(kinds)}, found {have}")
        for f, kinds in counts.items():
            if f not in want:
                err(f, f"has {len(kinds)} diagram(s); only 02 and 03 hold diagrams")

    # 10. Requirement quality (ISO/IEC/IEEE 29148: unambiguous, verifiable)
    fr_rows = {}
    for cells in table_rows(t01.splitlines()):
        if cells and re.fullmatch(r"FR-\d+", cells[0]):
            if len(cells) < 6:
                err("01-srs.md", f"{cells[0]} row has {len(cells)} columns (need 6)")
                continue
            fr_rows[cells[0]] = cells
            if cells[2].lower() not in ("core", "supporting"):
                err("01-srs.md", f"{cells[0]} priority '{cells[2]}' must be core or supporting")
            if not cells[5]:
                warn("01-srs.md", f"{cells[0]} has no verification method")
    if fr_rows and not any(c[2].lower() == "core" for c in fr_rows.values()):
        err("01-srs.md", "no core FR (the problem's main flow must be core)")
    vague = re.compile(r"\b(fast|quick(ly)?|easy|easily|user-friendly|robust|secure|scalable|flexible|intuitive|efficient|reliable|simple|modern|seamless)\b", re.I)
    for cells in table_rows(t01.splitlines()):
        if not cells:
            continue
        if re.fullmatch(r"FR-\d+", cells[0]) and len(cells) > 1 and vague.search(cells[1]):
            warn("01-srs.md", f"{cells[0]} uses a vague word '{vague.search(cells[1]).group(0)}'; state a measurable behaviour")
        if re.fullmatch(r"NFR-\d+", cells[0]) and len(cells) > 3 and vague.search(cells[2]) and not re.search(r"\d", cells[3]):
            warn("01-srs.md", f"{cells[0]} uses a vague word '{vague.search(cells[2]).group(0)}' with no numeric target")

    # 11. Endpoints agree across 02, 04 and 06
    methods = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
    ep_re = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[^\s,|`;)]*)")
    t04 = texts.get("04-api-spec.md", "")
    api = set()
    for cells in table_rows(section(t04, r"endpoints")):
        if len(cells) >= 2 and cells[0].upper() in methods:
            api.add((cells[0].upper(), cells[1]))
            if len(cells) >= 7 and not cells[6]:
                warn("04-api-spec.md", f"{cells[0]} {cells[1]} names no requirement")
    for f, pat in (("02-architecture.md", r"correspondences"), ("06-test-plan.md", r"traceability")):
        for m in ep_re.finditer("\n".join(section(texts.get(f, ""), pat))):
            if (m.group(1), m.group(2)) not in api:
                err(f, f"endpoint {m.group(1)} {m.group(2)} is not in 04-api-spec.md")

    # 12. Entities agree between the ER diagram and 03 headings
    t03 = texts.get("03-data-model.md", "")
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    heads = {norm(m.group(2)): m.group(1) for m in re.finditer(r"(?m)^#{2,4}\s+(E-\d+):\s*(.+?)\s*$", t03)}
    for e in sorted(defined["E"]):
        if e not in heads.values():
            warn("03-data-model.md", f"{e} is not written as '### {e}: <name>'")
    er_names = set()
    for b in mermaid_blocks(t03):
        if diagram_type(b) == "erDiagram":
            er_names |= {norm(n) for n in node_names("erDiagram", b)}
    for n in sorted(er_names - set(heads)):
        err("03-data-model.md", f"ER diagram entity '{n}' has no '### E-n: <name>' heading")
    for n in sorted(set(heads) - er_names):
        if er_names:
            warn("03-data-model.md", f"entity {heads[n]} is missing from the ER diagram")

    # 13. Threats use STRIDE and link a mitigation
    stride = ("spoofing", "tampering", "repudiation", "information disclosure", "denial of service", "elevation of privilege")
    th_seen = 0
    for cells in table_rows(section(t05, r"threats")):
        if cells and re.fullmatch(r"TH-\d+", cells[0]):
            th_seen += 1
            if len(cells) < 6:
                err("05-threat-model.md", f"{cells[0]} row has {len(cells)} columns (need 6)")
                continue
            if not any(s in cells[3].lower() for s in stride):
                err("05-threat-model.md", f"{cells[0]} STRIDE category '{cells[3]}' is not one of {', '.join(stride)}")
            if not ID_RE.search(cells[5]):
                err("05-threat-model.md", f"{cells[0]} links no FR, NFR or ADR")
    if not th_seen and "05-threat-model.md" in texts:
        warn("05-threat-model.md", "no threats listed")

    # 14. Roadmap schedules every requirement, core first, no dependency cycle
    t08 = texts.get("08-roadmap.md", "")
    order, ms = [], {}
    for cells in table_rows(section(t08, r"milestones")):
        if cells and cells[0].lower() != "milestone" and len(cells) >= 3:
            order.append(cells[0])
            ms[cells[0]] = (set(re.findall(r"\bN?FR-\d+\b", cells[1])), cells[2], cells[3] if len(cells) > 3 else "")
    if "08-roadmap.md" in texts:
        if not ms:
            err("08-roadmap.md", "no milestones found")
        reqs = defined["FR"] | defined["NFR"]
        for r in sorted(reqs):
            n = sum(r in v[0] for v in ms.values())
            if ms and n == 0:
                err("08-roadmap.md", f"{r} is not scheduled in any milestone")
            elif n > 1:
                warn("08-roadmap.md", f"{r} appears in {n} milestones (each should be in one)")
        deps = {}
        for name, (_, dep, _unused) in ms.items():
            toks = [t.strip() for t in re.split(r"[,;]", dep) if t.strip()]
            deps[name] = [t for t in toks if t.lower() != "none"]
            for t in deps[name]:
                if t not in ms:
                    err("08-roadmap.md", f"{name} depends on unknown milestone '{t}'")
        state = {}
        def visit(n, path):
            if state.get(n) == 1:
                err("08-roadmap.md", "dependency cycle: " + " -> ".join(path + [n]))
                return
            if state.get(n) == 2 or n not in deps:
                return
            state[n] = 1
            for d in deps[n]:
                visit(d, path + [n])
            state[n] = 2
        for n in deps:
            visit(n, [])
        supp = [i for i, m in enumerate(order) if any(fr_rows.get(r, [None, None, ""])[2].lower() == "supporting" for r in ms[m][0] if r.startswith("FR"))]
        if supp:
            for r, c in fr_rows.items():
                if c[2].lower() == "core":
                    where = [i for i, m in enumerate(order) if r in ms[m][0]]
                    if where and where[0] > supp[0]:
                        warn("08-roadmap.md", f"core {r} is scheduled after a supporting requirement")

    # 15. Leftovers
    for f, t in texts.items():
        for i, ln in enumerate(t.splitlines(), 1):
            if re.search(r"\b(TBD|TODO)\b|\?\?\?", ln) and "assum" not in ln.lower():
                err(f, f"line {i}: leftover TBD/TODO outside an assumption")
            if re.search(r"<(title|project|user|the|what|n|option)[^>\n]*>", ln, re.I) and "```" not in ln:
                warn(f, f"line {i}: template placeholder left in: {ln.strip()[:60]}")

    # Report
    verify = {f: len(re.findall(r"`?verify`?", t)) for f, t in texts.items()}
    for line in errors + warns:
        print(line)
    print(f"\nFR {len(defined['FR'])} · NFR {len(defined['NFR'])} · C {len(defined['C'])} · E {len(defined['E'])} · "
          f"TC {len(defined['TC'])} · TH {len(defined['TH'])} · ADR {len(defined['ADR'])}")
    vs = {f: n for f, n in verify.items() if n}
    print(f"`verify` marks: {sum(vs.values())}" + (f" ({', '.join(f'{f}: {n}' for f, n in vs.items())})" if vs else ""))
    print(f"{len(errors)} error(s), {len(warns)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
