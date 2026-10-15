import re, sys
from pathlib import Path

out = Path(sys.argv[1]); tier = sys.argv[2] if len(sys.argv) > 2 else "Prototype"
ra = Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
H = lambda t: f"# {t}: Habit Tracker\nTier: {tier} · Research: Standard · Version: 1.0\n\n"

def w(name, body): (out / name).write_text(body, encoding="utf-8")

w("01-srs.md", H("Software Requirements Specification") + """## 1. Introduction
Purpose and scope. Web app for daily habit streaks.

## 3. Functional requirements

| ID | Requirement | Priority (core / supporting) | Source | Rationale | Verification |
|---|---|---|---|---|---|
| FR-1 | The user can mark a habit done for today. | core | Q3 | Main flow | test |
| FR-2 | The user can see the current streak per habit. | core | Q3 | Motivation | test |
| FR-3 | The user can export data as JSON. | supporting | Q7 | Portability | test |

## 4. Non-functional requirements

| ID | Characteristic | Requirement | Target | Verification |
|---|---|---|---|---|
| NFR-1 | Functional suitability | Streaks are computed correctly. | 100% on test set | test |
| NFR-2 | Performance efficiency | Mark-done responds fast. | p95 under 300 ms | test |
| NFR-3 | Compatibility | Works in current browsers. | 2 latest versions | test |
| NFR-4 | Interaction capability | Accessible UI. | WCAG 2.2 AA | inspection |
| NFR-5 | Reliability | Data survives restarts. | RPO 24 h | test |
| NFR-6 | Security | Logins are protected. | Argon2id, rate limit 5/min | test |
| NFR-7 | Maintainability | Modular code. | 80% unit coverage | analysis |
| NFR-8 | Flexibility | Moves host without code change. | config only | inspection |
| NFR-9 | Safety | Not applicable: no harm path. | n/a (0 hazards) | inspection |

## 5. Applicable standards

| Standard | Why it applies |
|---|---|
| ISO/IEC/IEEE 29148 | Requirements |

Assumptions to confirm: TBD hosting region (assumption A1).
""")

comp_nodes = "\n".join(["flowchart LR", "  subgraph client", "    U[Browser]", "  end", "  subgraph server", "    A[API]", "    D[(DB)]", "  end", "  U --> A", "  A --> D"])
seq = "\n".join(["sequenceDiagram", "  U->>A: mark done", "  A->>D: write", "  D-->>A: ok", "  A-->>U: streak"])
dep = "\n".join(["flowchart LR", "  H[Host]", "  C[Container]", "  H --> C"])
diagrams02 = f"```mermaid\n{comp_nodes}\n```\n"
if tier in ("MVP", "Production"): diagrams02 += f"\n```mermaid\n{seq}\n```\n"
if tier == "Production": diagrams02 += f"\n```mermaid\n{dep}\n```\n"
w("02-architecture.md", H("Architecture and Design") + f"""## 2. Component diagram

{diagrams02}
## 3. Components

| ID | Component | Responsibility | Technology (free) | Requirements served |
|---|---|---|---|---|
| C-1 | Browser UI | Show habits | HTML/JS | FR-1, FR-2, NFR-4 |
| C-2 | API | Rules and storage | Flask | FR-1, FR-2, FR-3, NFR-1, NFR-2, NFR-6 |

## 7. Correspondences

| Component | Entities owned | Endpoints served |
|---|---|---|
| C-2 | E-1, E-2, E-3 | POST /habits/{{id}}/done, GET /habits |
""")

w("03-data-model.md", H("Data Model") + """## 1. Entity relationships

```mermaid
erDiagram
  USER ||--o{ HABIT : owns
  HABIT ||--o{ CHECKIN : has
```

## 2. Entities

### E-1: Habit

| Field | Type | Constraints | Personal data (Y/N) | Notes |
|---|---|---|---|---|
| id | int | PK | N | |

### E-3: User

| Field | Type | Constraints | Personal data (Y/N) | Notes |
|---|---|---|---|---|
| email | text | unique | Y | |

### E-2: Checkin

| Field | Type | Constraints | Personal data (Y/N) | Notes |
|---|---|---|---|---|
| day | date | unique per habit | N | |
""")

w("04-api-spec.md", H("API Specification") + """## 2. Endpoints

| Method | Path | Auth / role | Request | Response | Errors | Requirements |
|---|---|---|---|---|---|---|
| POST | /habits/{id}/done | user | none | 204 | 404 | FR-1 |
| GET | /habits | user | none | list | 401 | FR-2, FR-3 |
""")

rows = ["| ID | Component / flow | Threat | STRIDE category | Mitigation | Link (FR / NFR / ADR) |", "|---|---|---|---|---|---|",
        "| TH-1 | C-2 login | Credential stuffing | Spoofing | Rate limit | NFR-6 |"]
reg = ["| Area | Status (Mitigated / Accepted / Not relevant) | Control or reason | Link |", "|---|---|---|---|"]
cur = None
for ln in ra.read_text().splitlines():
    m = re.match(r"^\| ([^|]+) \|", ln)
    if m and m.group(1).strip() not in ("Area",) and not set(m.group(1).strip()) <= set("-"):
        a = m.group(1).strip()
        reg.append(f"| {a} | Mitigated | Control in design | NFR-6 |" if a in ("Authentication", "Input handling") else f"| {a} | Accepted | Low stakes prototype | ADR-1 |")
w("05-threat-model.md", H("Threat Model and Risk Register") + "## 3. Threats (STRIDE)\n\n" + "\n".join(rows) + "\n\n## 4. Risk register\n\n" + "\n".join(reg) + "\n")

w("06-test-plan.md", H("Test Plan") + """## 4. Test cases

| ID | Requirement | Level | What is done | Expected result | Type (functional / performance / security / accessibility) |
|---|---|---|---|---|---|
| TC-1 | FR-1 | system | Mark done | Saved | functional |
| TC-2 | FR-2, NFR-1 | unit | Streak calc | Correct | functional |
| TC-3 | FR-3 | integration | Export | Valid JSON | functional |
| TC-4 | NFR-2 | system | Load test | p95 under 300 ms | performance |
| TC-5 | NFR-3 | system | Browser run | Pass | functional |
| TC-6 | NFR-4 | system | Axe scan | No AA issues | accessibility |
| TC-7 | NFR-5 | system | Restart | Data kept | functional |
| TC-8 | NFR-6 | system | Brute force | Blocked at 5/min | security |
| TC-9 | NFR-7 | unit | Coverage | 80% | functional |
| TC-10 | NFR-8 | system | Move host | Works | functional |
| TC-11 | NFR-9 | system | Review | No hazard | functional |

## 5. Traceability matrix

| Requirement | Design element (C-n / E-n / endpoint) | Test cases |
|---|---|---|
| FR-1 | C-1, POST /habits/{id}/done | TC-1 |
| FR-2 | C-2, E-2 | TC-2 |
| FR-3 | C-2, GET /habits | TC-3 |
| NFR-1 | C-2 | TC-2 |
| NFR-2 | C-2 | TC-4 |
| NFR-3 | C-1 | TC-5 |
| NFR-4 | C-1 | TC-6 |
| NFR-5 | E-1 | TC-7 |
| NFR-6 | C-2 | TC-8 |
| NFR-7 | C-2 | TC-9 |
| NFR-8 | C-2 | TC-10 |
| NFR-9 | C-1 | TC-11 |
""")

w("07-decisions.md", H("Architecture Decision Records") + """### ADR-1: Prototype risk stance
- Status: Accepted
- Context: Low stakes, NFR-6.
- Decision: Accept most risks.
- Decided by: user
- Alternatives rejected: Full hardening: too costly
- Consequences: Faster build
- Sources: [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
""")

w("08-roadmap.md", H("Build Roadmap") + """## 1. Milestones

| Milestone | Contents (FR / NFR IDs) | Depends on | Exit criteria |
|---|---|---|---|
| M1 | FR-1, FR-2, NFR-1, NFR-2, NFR-6 | none | TC-1, TC-2 pass |
| M2 | FR-3, NFR-3, NFR-4, NFR-5, NFR-7, NFR-8, NFR-9 | M1 | TC-3 pass |
""")
