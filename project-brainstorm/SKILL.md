---
name: project-brainstorm
description: Runs a structured, standards-based brainstorming and requirements-gathering session for a whole software project, researches current options and best practices online, and produces a complete design package (SRS, architecture, data model, API spec, threat model, test plan, decision records, roadmap). Use only when the user explicitly invokes it by typing /project-brainstorm or asks for the project-brainstorm skill by name. Never start it on your own, even when the user describes a software project or asks how to design one.
---

# Project Brainstorm

Turn a problem into a complete, buildable software design in which every relevant way the project could lose value has been dealt with, improved through research until it is the strongest design that can be found. The session ends with design documents only: no code, no repo scaffolding.

## Ground rules

- **Software only.** If the project is hardware, IoT or embedded, say this skill doesn't cover it.
- **Free only.** Every tool, library, framework, service and host must be free/open-source or a free tier. If a requirement can't be met for free, say so and give the closest free option.
- **Research, don't guess.** Network access is expected. Look up versions, limits, benchmarks, standard clauses and the current state of every tool before relying on it, and record the source. If the user chose No research or web access isn't available, use what you know and mark each unchecked fact `verify`.
- **Propose, don't interrogate.** Make the design calls yourself. Ask questions only for details that would change the design and weren't given, or when the user asks for an interview.
- **Self-contained.** Everything comes from this conversation; assume no prior knowledge of the user.
- **Missing reference file.** If a file under `references/` can't be read, continue from your own knowledge of the standards it names and tell the user the file was missing.

## Phase 1: Intake

This skill runs only when the user explicitly invoked it (`/project-brainstorm` or by name). If it was loaded any other way, don't run it; answer the user normally.

Treat any text after `/project-brainstorm` as the user's message. If there is no text, ask the user to describe the problem first.

From the user's message, pull out: the problem, the target users, the core goal, the platform(s), and any stated constraints or tech preferences.

Place the project in a tier:

| Tier | Signals | Depth |
|---|---|---|
| Prototype | hackathon, demo, proof of concept | Core flow proven; every area addressed briefly |
| MVP | course project, first release, small user base | Full core plus key supporting features; every area addressed |
| Production | public users, real data, growth expected | Full depth everywhere; measurable targets on every quality area |

Personal or sensitive data, payments, or minors as users raise security and privacy depth to Production level whatever the tier. If the tier is unclear, include it in Phase 2.

## Phase 2: Clarify

List the gaps that would change the design. Areas to check: users and roles, expected scale, platform and device limits, kind of data handled, offline needs, integrations, authentication, existing systems, success criteria, the team's known stack.

Ask only the questions this project needs, in one batch, ordered by impact. Give each a suggested default so the user can reply "defaults".

End the batch by asking how much research to do, showing these options as given:

| Option | What happens | Outcome | Time | Token use |
|---|---|---|---|---|
| No research | Design from built-in knowledge only | Complete design; unchecked facts marked `verify` | Fastest | Lowest |
| Standard | Research each design part and current standards; one improve round | Choices checked against current sources | Longer | Moderate |
| Deep (default) | Research the problem space, every design part, standards and law; the improve loop repeats until a round finds nothing new | Strongest design that can be found, every choice sourced | Longest | Highest, often several times Standard |

Then stop and wait for the answers; don't start Phase 3 until they arrive. If the session is running unattended with no one to answer, use the defaults (Deep research) and list them as assumptions. Ask a second round only if the answers open a new gap that matters. Anything left unanswered becomes a written assumption.

## Phase 3: Requirements

Read `references/standards-core.md` (Requirements section).

- **Functional (FR-n):** mark each as **core** (solves the main problem) or **supporting** (dependability and quality upgrades).
- **Non-functional (NFR-n):** grouped by the characteristics of the current ISO/IEC 25010 edition, each with a measurable target.
- Every requirement must meet the ISO/IEC/IEEE 29148 characteristics and carry the attributes listed in `references/standards-core.md`.

## Phase 4: Research

Skip this phase if the user chose No research. Otherwise, research what the design depends on:

- **The problem space:** how this kind of problem is usually solved, proven patterns, and common reasons such projects fail.
- **Each design part:** the strongest free options today, whether they are actively maintained, their current versions and limits, and known security or performance problems.
- **Standards and law:** current editions of the standards in `references/standards-core.md`, plus any domain-specific standards or data-protection law that applies.

Standard covers each design part, the standards and the law; Deep covers all three areas in full, whatever the tier. If a tool for running parallel research agents is available, give each part its own agent; otherwise research inline. Keep a source list; each finding that shapes the design must be traceable to a source.

## Phase 5: Design

Break the solution into its parts (for example client, backend, data store, auth, hosting, integrations, background jobs). For each part, record the choice, the alternatives rejected, the reason, and the sources behind it as a decision record (ADR-n). Prefer the simplest design that meets the requirements; every added component must be justified by a requirement.

## Phase 6: Risk and standards pass

Read `references/risk-areas.md`. For each area, decide whether it is relevant. If it is, either map it to a mitigation (linked to an FR, NFR or ADR) or accept it with a stated reason. Never leave an area unmarked.

List the applicable standards from `references/standards-core.md` and Phase 4 in the SRS.

## Phase 7: Improve

Review the draft design as a critic looking for its weakest points: the core flow, the top risks, and any requirement met only partly. For each weak point, find better approaches (by research unless the user chose No research) and adopt one if it is clearly stronger and still free; update the affected ADRs, requirements and risk statuses.

- **No research:** one round from built-in knowledge.
- **Standard:** one researched round.
- **Deep:** repeat rounds until a round finds no meaningful improvement.

## Phase 8: Deliverables

Read `references/templates.md`. Produce eight Markdown files:

`01-srs.md`, `02-architecture.md`, `03-data-model.md`, `04-api-spec.md`, `05-threat-model.md`, `06-test-plan.md`, `07-decisions.md`, `08-roadmap.md`

- The tier changes how deep each file goes. It never removes a file or a risk area. If a file doesn't apply (for example, no API), keep it with one line saying why.
- Diagrams are Mermaid, limited to the slots, sizes and counts set in `references/templates.md`, to keep token use low. A diagram replaces the matching table or text rather than repeating it.
- Write the files into a new folder named `<project-name>-design/` in the current working directory, and hand them to the user if the surface has a way to send files. If file tools aren't available, output each document in the chat under its file name.

## Phase 9: Trace check

Before handing over, confirm that:

- every FR and NFR maps to a design element and at least one test case;
- every risk area has a status;
- every ADR names its sources;
- nothing is left as TBD except listed assumptions;
- names and numbers match across all files, diagrams included.

Fix any gaps, then deliver with a short summary: the tier, the research option used, the core idea, what the improve phase changed, the top 3 risks, the assumptions the user should confirm, and every item marked `verify`.
