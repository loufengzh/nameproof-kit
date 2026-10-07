# Worked naming session

Input: **“A calm collaborative writing editor for independent researchers.”**

This walkthrough is a real run of the offline CLI with an explicitly authored candidate set, not a claim that a naming model or trademark service ran behind the scenes. The host agent is responsible for semantic ideation; the Python component keeps evidence and spelling checks reproducible.

## Creative comparison

The host considered three distinct directions in `examples/candidates.json`:

- **QuillNest:** a familiar writing metaphor plus a shared home. Warm and collaborative. “Quill” can feel literary or old-fashioned; check existing publishing/editor brands carefully.
- **FolioTrail:** documents plus the path through a body of research. Strongest of these three for traceable research writing, citations and an ongoing investigation. Less intimate than QuillNest and somewhat longer.
- **VerseLoom:** weaving fragments into prose. Most expressive/creative direction, but “verse” can suggest poetry and weaken academic positioning.

For this brief, the host would provisionally favor **FolioTrail** on meaning and product fit. That judgment is separate from the CLI's spelling score. No native Vietnamese pronunciation/connotation panel was consulted, and no name is declared unique or legally available.

## Reproduce the evidence stage

```sh
python -m nameproof report --brief examples/brief.json --candidates examples/candidates.json --format markdown
python -m nameproof logo-brief --name FolioTrail --brief examples/brief.json
```

The checked-in `examples/report.md` is the actual offline report. All domain purchase states remain `unknown`; US/EU/VN trademark states remain `unreviewed`, because no records were imported. Each official next-check link is visibly a task still to do, not a completed search.

A separate live integration smoke on 2026-10-07 at 13:07:55 UTC queried IANA and Verisign and returned **example.com registered**. That validates one real network path. It is not evidence about any proposed name, every TLD, or registrar purchasability.

## Continue into the selected logo skill

`examples/logo-brief.json` is the real structured handoff for FolioTrail. It specifies three original directions, a monochrome variant, legibility/spelling review, unresolved naming risk and the pinned op7418 source. No image has been generated.

The optional `logo-source` command retrieves the pinned upstream instructions as data and verifies their hash. Read them explicitly in the host agent, together with `docs/LOGO.md`; follow only the authorized logo work. The first concept stage can be host-authored editable SVG. Paid showcase API execution is a separate later step and is never triggered by this toolkit.

CLI commands, JSON-RPC stdio exchange, skill format validation and an isolated installed-package import were tested here. Automatic skill discovery inside Claude Code, Codex, Cursor, Antigravity and Grok Build was not exercised; their paths are supported by the official docs linked in `HARNESSES.md`.
