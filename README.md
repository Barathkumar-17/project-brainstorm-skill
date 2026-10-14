# project-brainstorm

A Claude skill that turns a software problem into a complete, standards-based design package. Started with `/project-brainstorm`, it runs a requirements-gathering session, researches current options online, improves the design until no weak point is left unhandled, and writes eight design documents ready to build from.

Works on claude.ai and Claude Code.

## What a session does

1. **Intake:** captures the problem, users and platform; sizes the project as Prototype, MVP or Production.
2. **Clarify:** asks every question the design needs in one batch, each with a default, and asks how much research to do.
3. **Requirements:** functional (core and supporting) and non-functional, to ISO/IEC/IEEE 29148 and ISO/IEC 25010.
4. **Research:** the problem space, the best free option for each part, current standards and law.
5. **Design:** each part chosen with rejected alternatives and sources, recorded as decision records.
6. **Risk and standards pass:** every risk area is mitigated, accepted with a reason, or marked not relevant.
7. **Improve:** reviews the design as a critic and researches better approaches for its weak points.
8. **Deliverables:** writes the eight documents.
9. **Trace check:** every requirement maps to a design element and a test before handover.

## Research options

Chosen by the user at the end of the clarify step.

| Option | What happens | Time | Token use |
|---|---|---|---|
| No research | Built-in knowledge only; unchecked facts marked `verify` | Fastest | Lowest |
| Standard | Each design part and current standards researched; one improve round | Longer | Moderate |
| Deep (default) | Problem space, every part, standards and law; improve loop repeats until nothing new | Longest | Highest |

## Output

A `<project-name>-design/` folder with:

| File | Contents |
|---|---|
| `01-srs.md` | Software requirements specification |
| `02-architecture.md` | Components, core flow, deployment, cross-cutting design |
| `03-data-model.md` | Entities, fields, indexes, retention and backup |
| `04-api-spec.md` | Endpoints, conventions, rate limits |
| `05-threat-model.md` | STRIDE threats and the full risk register |
| `06-test-plan.md` | Strategy, test cases, traceability matrix |
| `07-decisions.md` | Architecture decision records with sources |
| `08-roadmap.md` | Milestones and build order, core first |

Diagrams are Mermaid, capped by tier to keep token use low.

## Constraints built in

- Software projects only.
- Free and open-source tools and free tiers only.
- Design documents only; no code or repo scaffolding.
- No invented facts: everything is researched and sourced, or marked `verify`.

## Install

**claude.ai**
1. Run `scripts/package.sh` to build `dist/project-brainstorm.zip`, or download the zip from Releases.
2. In claude.ai, turn on code execution and file creation, then upload the zip under Skills in settings.
3. Make sure the skill is switched on.

**Claude Code**

One command, no marketplace needed:

```sh
git clone --depth 1 https://github.com/Barathkumar-17/project-brainstorm-skill.git /tmp/pbs && mkdir -p ~/.claude/skills && cp -r /tmp/pbs/project-brainstorm ~/.claude/skills/ && rm -rf /tmp/pbs
```

To share it with everyone working in one repository instead, copy the folder to that repository's `.claude/skills/` and commit it.

If your claude.ai skills already sync to Claude Code, skip this to avoid two copies.

## Use

The skill runs only when you call it. On claude.ai or in Claude Code, type the command with your problem after it:

```
/project-brainstorm <describe your software problem>
```

Typing `/project-brainstorm` alone makes it ask for the problem first. It won't start on its own from ordinary chat.

## Repository layout

```
project-brainstorm/          the skill (upload or copy this folder)
├── SKILL.md                 workflow
└── references/
    ├── standards-core.md    built-in standards
    ├── risk-areas.md        risk checklist
    └── templates.md         layout of the eight documents
scripts/package.sh           builds the upload zip
```

## License

MIT
