---
name: project-brainstorm
description: Grills the user relentlessly about a software project idea, walking the whole design tree one round of questions at a time with a researched recommendation for each, until every decision is settled, then writes a complete standards-based design package (SRS, architecture, data model, API spec, threat model, test plan, decision records, roadmap). Use only when the user explicitly invokes it by typing /project-brainstorm or asks for the project-brainstorm skill by name. Never start it on your own, even when the user describes a software project or asks how to design one.
---

# Project Brainstorm

Brainstorm a software project by grilling the user. Map every decision the project needs as a design tree, and work through it with the user until nothing is left assumed. Then turn the settled decisions into a complete design package. The session ends with design documents only: no code, no repo scaffolding.

## Start

This skill runs only when the user explicitly invoked it (`/project-brainstorm` or by name). If it was loaded any other way, don't run it; answer the user normally.

Treat any text after `/project-brainstorm` as the project idea or problem. If there is none, ask for it and wait.

## Ground rules

- **Decisions are the user's; facts are yours.** Never ask the user anything you can look up. Research facts yourself (how others solved this problem, tool options, versions, limits, known issues, standards, law), using parallel research agents when available, and use them to make each recommendation. Put every decision to the user and wait.
- **Recommend the strongest option.** Every question carries your recommended answer and one line on why. Recommend only what the research supports.
- **Push back once.** If an answer weakens the design (security, performance, resource use, reliability, privacy), say how in one or two lines with the better option. If the user keeps their choice, record it and move on.
- **Software only.** If the project is hardware, IoT or embedded, say this skill doesn't cover it.
- **Free only.** Recommend only free/open-source tools and free tiers. If a need can't be met for free, say so and give the closest free option.
- **No invented facts.** Versions, limits, benchmarks and standard clauses must be researched and sourced. If the user chose No research or web access isn't available, mark each unchecked fact `verify`.
- **Self-contained.** Everything comes from this conversation; assume no prior knowledge of the user.
- **Missing reference file.** If a file under `references/` can't be read, continue from your own knowledge of the standards it names and tell the user the file was missing.

## The design tree

Build the tree from the idea. Each decision branches into the decisions that depend on it. Always include these branches, and add any the project needs:

- **Problem:** what exactly is wrong, who has it, the root cause, what success looks like, what is out of scope.
- **Users and roles:** who uses it and what each can do.
- **Solution concept:** the overall shape of the solution. Present several genuinely different approaches as the choices.
- **Core features:** what solves the main problem.
- **Supporting features:** dependability and quality upgrades that raise the overall product.
- **Each part of the solution:** platform and client, backend, data, authentication, integrations, hosting, background work. For each, how it should work and what it contains.
- **Quality and risk:** one branch per relevant area in `references/risk-areas.md` (security, response time, CPU, memory, reliability, privacy and the rest), deciding how the design protects against it. A group with nothing relevant is closed with one line.
- **Tier:** Prototype, MVP or Production. The tier sets document depth only; it never removes a branch. Personal or sensitive data, payments, or minors as users raise security and privacy depth to Production level whatever the tier.

## Rounds

The **frontier** is every open decision whose prerequisites are settled. Each round, ask the whole frontier at once, numbered, each with your recommendation. A question that depends on another question still open in the same round waits for a later round.

Format each question like this:

```
**Q1 · <short title>**
<the question; for a choice, list the options with a one-line trade-off each>
➡️ Recommended: <answer>, because <one line>
```

Word each question so "yes" accepts the recommendation. The user can answer "yes to all", answer some, or override any.

The first round always includes: the problem framing as you understand it, the tier, and how much research should back your recommendations:

| Option | What happens | Outcome | Time | Token use |
|---|---|---|---|---|
| No research | Recommendations from built-in knowledge only | Unchecked facts marked `verify` | Fastest | Lowest |
| Standard | Each part of the solution and the current standards researched | Recommendations checked against current sources | Longer | Moderate |
| Deep (recommended) | Problem space, every part, standards and law researched; the improve loop repeats until nothing new | Strongest recommendations, every one sourced | Longest | Highest, often several times Standard |

After each round, record the decisions, recompute the frontier and ask the next round. While research for a question is still running, ask the rest of the frontier and hold only the questions that depend on it.

If the session is running unattended with no one to answer, accept every recommendation and record each as an assumption.

## End of the grill

The grill is done when the frontier is empty: every branch visited, every relevant risk area decided, nothing silently assumed. Then show every decision grouped by branch, and ask the user to confirm you share the same understanding. Don't write any document until they confirm.

## Build the design package

After confirmation:

1. **Requirements.** Read `references/standards-core.md`. Turn the decisions into functional requirements (FR-n, marked core or supporting) and non-functional requirements (NFR-n, grouped by ISO/IEC 25010 characteristic, each with a measurable target), meeting the ISO/IEC/IEEE 29148 characteristics and attributes.
2. **Risk and standards pass.** Read `references/risk-areas.md`. Give every area a status (Mitigated, linked to an FR, NFR or ADR; Accepted, with reason; or Not relevant, with reason). List the applicable standards in the SRS, researching domain-specific ones.
3. **Improve.** Review the whole design as a critic looking for weak points: the core flow, the top risks, any requirement met only partly. Research better approaches. Put each proposed change to the user as one more round; never change a decision on their behalf. No research and Standard run one improve round; Deep repeats until a round finds nothing new.
4. **Deliverables.** Read `references/templates.md`. Write eight Markdown files into a new `<project-name>-design/` folder in the current working directory: `01-srs.md`, `02-architecture.md`, `03-data-model.md`, `04-api-spec.md`, `05-threat-model.md`, `06-test-plan.md`, `07-decisions.md`, `08-roadmap.md`. Each decision from the grill becomes an ADR recording the options considered, the user's choice and the sources. The tier sets depth; a file that doesn't apply keeps one line saying why. Diagrams are Mermaid, within the limits in `templates.md`. Hand the files to the user if the surface can send files; without file tools, output each document in the chat under its file name.
5. **Trace check.** Confirm every FR and NFR maps to a design element and at least one test case; every risk area has a status; every ADR names its sources; nothing is TBD except listed assumptions; names and numbers match across all files, diagrams included. Fix any gaps.

Finish with a short summary: the tier, the research option used, the core idea, what the improve step changed, the top 3 risks, the assumptions to confirm, and every item marked `verify`.
