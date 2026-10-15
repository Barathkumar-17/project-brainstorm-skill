# project-brainstorm

A Claude skill that brainstorms a software project by grilling you. It maps every decision the project needs as a design tree and works through it with you, one round of questions at a time, each with a researched recommendation. When nothing is left assumed, it writes a complete, standards-based design package ready to build from.

Works on claude.ai and Claude Code. Runs only when you type `/project-brainstorm`.

## How a session works

1. **Start:** `/project-brainstorm <your idea or problem>`.
2. **Grill:** each round, Claude asks every question that can be decided right now, numbered, each with a recommended answer and one line on why. Reply "yes to all", answer some, or override any. Each round unlocks the questions that depended on your answers.
3. **What it covers:** the problem, users, the overall solution concept (several different approaches to pick from), core and supporting features, every part of the solution (how it works and what it contains), and every relevant risk area: security, response time, CPU, memory, reliability, privacy and more.
4. **Facts vs decisions:** Claude researches the facts itself (options, versions, limits, standards, how others solved it). You make the decisions. If your choice weakens the design, it pushes back once, then records your call.
5. **Confirm:** when every branch is settled, it shows all decisions and waits for you to confirm.
6. **Design package:** requirements, a risk and standards pass, an improve step (any proposed change comes back to you as a question), the eight documents, and a final trace check.

## Research options

Asked in the first round of questions.

| Option | What happens | Time | Token use |
|---|---|---|---|
| No research | Built-in knowledge only; unchecked facts marked `verify` | Fastest | Lowest |
| Standard | Each design part and current standards researched; one improve round | Longer | Moderate |
| Deep (recommended) | Problem space, every part, standards and law; improve loop repeats until nothing new | Longest | Highest |

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
1. Run `scripts/package.sh` to build `dist/project-brainstorm.zip`, or zip the `project-brainstorm` folder yourself so the folder sits at the top level of the zip.
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

```
/project-brainstorm <describe your software idea or problem>
```

Typing `/project-brainstorm` alone makes it ask for the idea first. It won't start on its own from ordinary chat.

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

## Credits

The grilling interview style is adapted from Matt Pocock's `grilling` skill ([mattpocock/skills](https://github.com/mattpocock/skills), MIT).

## License

MIT
