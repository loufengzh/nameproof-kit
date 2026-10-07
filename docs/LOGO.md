# Optional logo handoff

NameProof stops at a **logo brief and prompt**. `python -m nameproof logo-brief --name NAME --brief FILE` does not generate an image, install a provider SDK, read API keys, or call an image API. Select a name before moving into logo work; an attractive logo does not resolve a naming conflict.

## User-selected upstream

- Project: [op7418/logo-generator-skill](https://github.com/op7418/logo-generator-skill)
- Reviewed revision: [`bf4e9ac4d4428bda261afcfe981871ceb92d94e6`](https://github.com/op7418/logo-generator-skill/tree/bf4e9ac4d4428bda261afcfe981871ceb92d94e6)
- Author/project attribution: op7418, logo-generator-skill
- Review date: 2026-10-07
- Integration status: referenced, **not vendored or automatically installed**

The [pinned README](https://github.com/op7418/logo-generator-skill/blob/bf4e9ac4d4428bda261afcfe981871ceb92d94e6/README.md) declares MIT. The reviewed tree has no standalone LICENSE or COPYING file, so we have not reproduced or relicensed its implementation. Before redistribution, obtain the complete upstream license notice and preserve its attribution and terms. This toolkit's own license does not cover that external repository. A source-code license also does not establish trademark clearance for generated artwork.

## Review findings

The [upstream skill](https://github.com/op7418/logo-generator-skill/blob/bf4e9ac4d4428bda261afcfe981871ceb92d94e6/SKILL.md) guides a host agent to make multiple SVG concepts, then refine a selection and optionally generate showcase images. It is not a standalone semantic logo generator. Its pinned YAML frontmatter was parsed successfully during source review. Automatic discovery and end-to-end behavior in each host have not been tested.

The [showcase script](https://github.com/op7418/logo-generator-skill/blob/bf4e9ac4d4428bda261afcfe981871ceb92d94e6/scripts/generate_showcase.py) reads `.env`, uses a Gemini API key, and can use a configured alternate endpoint. It sends the reference PNG and a prompt containing the product name/description. Its `--all-styles` branch iterates over twelve styles, despite inconsistent comments/help text, so it can make twelve generation calls. Treat provider costs, terms, data sharing, and model availability as a separate decision. The script was inspected, not executed or runtime-certified.

The [requirements](https://github.com/op7418/logo-generator-skill/blob/bf4e9ac4d4428bda261afcfe981871ceb92d94e6/requirements.txt) use lower bounds rather than a reproducible lock. PNG conversion uses CairoSVG; only render trusted, locally generated SVGs after checking for external references. The [HTML template](https://github.com/op7418/logo-generator-skill/blob/bf4e9ac4d4428bda261afcfe981871ceb92d94e6/assets/showcase_template.html) loads CDN JavaScript and web fonts, so opening that template is not an offline-only workflow.

## Retrieve instructions explicitly

`python -m nameproof logo-source --output NEW_DIRECTORY --fetch` retrieves the pinned SKILL.md and two design references with SHA-256 verification. The skill text is saved as `UPSTREAM_SKILL.md` so the output is not silently auto-discovered as an installed skill. Read it explicitly; scripts and template dependencies are omitted. No logo-provider call occurs. The default without `--fetch` prints the exact manifest only.

## Safe interface

1. Run NameProof screening and let the user select a candidate. Retain the unresolved checks and review date.
2. Generate the logo brief with the selected name, category, concept, desired audience, tone, color/style constraints, and requested deliverables. Use the CLI's output schema; do not invent provider-specific fields.
3. If the user already has the selected logo skill installed and wants to proceed, pass the brief to that skill in the host agent. Otherwise give them the prompt and the pinned upstream link. Do not fetch/install executable dependencies as an implicit side effect of naming.
4. Start with editable SVG concept work when suitable. Inspect output for broken geometry, tiny-size legibility, external resources, and resemblance concerns. Label concepts as drafts.
5. Before a paid or remote generation step, obtain approval for provider/endpoint, uploaded logo and product context, number of images and spending limit. Never ask for a key in chat or commit credentials. Do not select an alternate provider silently.
6. Return assets, attribution/provenance, and remaining checks. Never label a design unique, legally safe, trademark-cleared, or production-approved solely from generation or this toolkit's evidence.

Optional providers are adapters, not core dependencies. The naming workflow must remain usable when the logo skill, API, network, or budget is unavailable.
