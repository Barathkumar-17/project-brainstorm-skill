# Templates

Layout for each output file. Keep the headings and table columns exactly as given. Write in plain, short sentences.

Contents: Rules for every file · Depth by tier · Diagrams · 01-srs · 02-architecture · 03-data-model · 04-api-spec · 05-threat-model · 06-test-plan · 07-decisions · 08-roadmap

## Rules for every file

- Start with: `# <Doc title>: <Project name>`, then one line: `Tier: <tier> · Research: <No research / Standard / Deep> · Version: 1.0`.
- Use IDs consistently across files: FR-n, NFR-n, ADR-n, TC-n, TH-n (threats), C-n (components), E-n (entities).
- One fact, one place. If something is stated in another file, link to it there instead of repeating it.
- If a section doesn't apply, keep the heading with one line saying why.

## Depth by tier

| Tier | Depth |
|---|---|
| Prototype | Core FRs in full; supporting FRs as one-line entries; one NFR per characteristic; short tables |
| MVP | All FRs in full; NFRs with measurable targets; every section filled |
| Production | Everything in full, with edge cases, failure modes and measurable targets on every NFR |

## Diagrams (Mermaid)

Diagrams are kept small to limit token use.

- **Number of diagrams:** Prototype 2, MVP 3, Production 4 (see the slots below). No others.
- **Size:** at most 15 nodes per diagram. Short node IDs, short labels.
- **No styling:** no `classDef`, colours, themes, notes or comments.
- **A diagram replaces the matching text.** Show connections in the diagram only, and use tables only for what a diagram can't show (responsibilities, fields, rules).

| Slot | File | Mermaid type | Tier |
|---|---|---|---|
| Component diagram with trust boundaries as `subgraph` | 02 | `flowchart LR` | All |
| Entity relationships (entity names and relationships only) | 03 | `erDiagram` | All |
| Core flow sequence | 02 | `sequenceDiagram` | MVP, Production |
| Deployment | 02 | `flowchart LR` | Production |

---

## 01-srs.md: Software Requirements Specification

1. **Introduction:** purpose, scope (in and out), definitions.
2. **Overall description:** problem, users and roles, platform(s), assumptions, constraints.
3. **Functional requirements**

   | ID | Requirement | Priority (core / supporting) | Source | Rationale | Verification |
   |---|---|---|---|---|---|

4. **Non-functional requirements** (grouped by ISO/IEC 25010 characteristic)

   | ID | Characteristic | Requirement | Target | Verification |
   |---|---|---|---|---|

5. **Applicable standards**

   | Standard | Why it applies |
   |---|---|

## 02-architecture.md: Architecture and Design

1. **Stakeholders and concerns:** who cares about what.
2. **Component diagram** (diagram slot).
3. **Components**

   | ID | Component | Responsibility | Technology (free) | Requirements served |
   |---|---|---|---|---|

4. **Core flow sequence** (diagram slot, MVP and Production). Prototype: a numbered list of steps.
5. **Deployment** (diagram slot, Production). Other tiers: one line naming where each component runs.
6. **Cross-cutting design:** authentication, authorization, error handling, logging, configuration, caching.
7. **Correspondences:** which component owns which entity (E-n) and serves which endpoints, in one table: Component | Entities owned | Endpoints served.

## 03-data-model.md: Data Model

1. **Entity relationships** (diagram slot).
2. **Entities**, one table per entity:

   | Field | Type | Constraints | Personal data (Y/N) | Notes |
   |---|---|---|---|---|

3. **Indexes:** field(s) and the query each one serves.
4. **Retention, backup and migration:** how long data is kept, how it is backed up, and how schema changes are applied.

## 04-api-spec.md: API Specification

1. **Conventions:** base URL, versioning, authentication, error format (RFC 9457), pagination, date format.
2. **Endpoints**

   | Method | Path | Auth / role | Request | Response | Errors | Requirements |
   |---|---|---|---|---|---|---|

3. **Rate limits and quotas.**

## 05-threat-model.md: Threat Model and Risk Register

1. **Assets:** what must be protected and why.
2. **Trust boundaries:** see the component diagram in `02-architecture.md`.
3. **Threats (STRIDE)**

   | ID | Component / flow | Threat | STRIDE category | Mitigation | Link (FR / NFR / ADR) |
   |---|---|---|---|---|---|

4. **Risk register** (every area in `risk-areas.md`, plus project-specific ones)

   | Area | Status (Mitigated / Accepted / Not relevant) | Control or reason | Link |
   |---|---|---|---|

## 06-test-plan.md: Test Plan

1. **Context and scope:** what is tested and what isn't; assumptions and constraints; stakeholders.
2. **Test risks:** what could make testing fail or miss defects, and the response.
3. **Strategy:** levels (unit, integration, system, acceptance) and what each covers; techniques; completion criteria; suspension and resumption criteria.
4. **Test cases**

   | ID | Requirement | Level | What is done | Expected result | Type (functional / performance / security / accessibility) |
   |---|---|---|---|---|---|

5. **Traceability matrix**

   | Requirement | Design element (C-n / E-n / endpoint) | Test cases |
   |---|---|---|

6. **Test environment and free tools.**

## 07-decisions.md: Architecture Decision Records

One block per decision:

```
### ADR-n: <title>
- Status: Accepted
- Context: <the need, with requirement IDs>
- Decision: <what was chosen>
- Decided by: <user / recommended default (unattended run)>
- Alternatives rejected: <option: reason>, …
- Consequences: <what this makes easier and harder>
- Sources: [title](URL), …
```

## 08-roadmap.md: Build Roadmap

No dates. Order and dependencies only.

1. **Milestones** (core functionality first)

   | Milestone | Contents (FR / NFR IDs) | Depends on | Exit criteria |
   |---|---|---|---|

2. **Build order within each milestone:** a numbered list.
3. **Assumptions to confirm before building:** link to `01-srs.md`.
