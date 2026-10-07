# Nameproof Kit

**A short idea → a reasoned brand shortlist → an honest evidence report.**

A small, dependency-free Python toolkit and portable agent skill for people naming products. It combines the creativity of your existing coding agent with reproducible domain observations and country-specific trademark evidence. No extra AI subscription, hosted account, or background service is required.

[简体中文](docs/README.zh-CN.md) · [Русский](docs/README.ru.md) · [Deutsch](docs/README.de.md)

> **Evidence, not clearance.** No tool can guarantee a name is legally safe worldwide. RDAP tells you about registration records, not whether a registrar will sell you a domain. This project keeps those distinctions visible instead of producing a misleading green tick.

## Quick start

Python 3.10+; no runtime dependencies. From this checkout:

```sh
python -m nameproof propose --brief examples/brief.json
python -m nameproof report --brief examples/brief.json --candidates examples/candidates.json --format markdown
python -m nameproof domain example.com --live
python -m nameproof screen --name QuillNest --countries US,EU,VN --classes 9,42
python -m nameproof logo-brief --name QuillNest --brief examples/brief.json
python -m unittest discover -s tests -v
```

Optional local installation: `python -m pip install .` then `nameproof --help`. The package is not claimed to be published on PyPI. Clone this repository or use its verified source archive.

By default, commands are offline. `--live` makes public HTTPS IANA/RDAP queries, revealing the domains you check. It never buys a domain, registers a mark, scrapes trademark databases, loads an API key, or runs a logo provider.

## What works now

- **Idea-driven naming:** a transparent local metaphor/keyword baseline; bring host-agent candidates for more creative, multilingual semantic reasoning. JSON candidates contain `name` and `rationale`.
- **Repeatable shortlist:** deduplication, excluded substrings, maximum length, explicit spelling-score components and suggested domain labels. Scores concern spelling ergonomics only. They do not rank legal risk or market success.
- **Domain evidence:** IANA bootstrap → registry RDAP; registered, no-record, or unknown. Rate limits, unsupported suffixes, mismatched responses and failures remain unknown. Optional separately attributed registrar receipts support available/unavailable/reserved/premium observations.
- **Trademark triage:** exact and fuzzy Unicode text matching against records you actually supply; official manual search plans for US, EU, GB, VN, CN, DE, RU and SG. Country/class coverage is always explicit. UK is accepted as a GB alias.
- **Brand-use research:** the country catalog links separate business-register sources and explains their limits. Web usage, company names and trademark rights are distinct checks; no automated business-registry search is implied.
- **Logo handoff:** prepares a structured brief for the user-selected [op7418/logo-generator-skill](https://github.com/op7418/logo-generator-skill), pinned and reviewed in [LOGO.md](docs/LOGO.md). No artwork is fabricated or generation silently charged.
- **Agent integration:** portable `SKILL.md`, local CLI, and four read-only MCP tools. Official-format setup for Claude Code, Codex, Cursor, Antigravity and Grok **Build**; generic Grok chat has no local execution guarantee.

## Use with your coding agent

Copy the entire `skills/nameproof` folder into the appropriate project skill directory. Keep this CLI checkout accessible. Example for Codex:

```sh
mkdir -p YOUR_PROJECT/.agents/skills
cp -R skills/nameproof YOUR_PROJECT/.agents/skills/
```

Ask: “Use nameproof to name a calm research-writing editor for English and Vietnamese speakers. Compare meaningful options, check US/EU/VN evidence, and show what remains unknown.”

The skill asks the host to generate and critique diverse ideas, then passes its shortlist into the deterministic tooling. It does not replace good creative judgment with a mechanical score. See [HARNESSES.md](docs/HARNESSES.md) for vendor paths and the exact verification boundary. These formats are documented, but real discovery/execution inside all five products has not been certified.

For an MCP-capable client, configure its stdio server command as `python`, arguments `['-m', 'nameproof', 'mcp']`, working directory this checkout (or use an installed package). No HTTP port is opened. The server implements initialization, ping, tools/list and tools/call with newline-delimited JSON-RPC. Tools: `propose_names`, `check_domain`, `screen_trademarks`, `prepare_logo_brief`. Live domain requests remain explicit opt-in. No resources, prompts, sampling, or persistent state are implemented.

## Brief and evidence contracts

Start with [examples/brief.json](examples/brief.json). `idea` is required; other defaults are explicitly reported assumptions, not inferred legal facts. Set countries, actual goods/services Nice classes and domain suffixes for your project. `max_length` is a hard filter; very short constraints can yield no candidates. `avoid` excludes case/accent-normalized substrings. The English-keyword offline baseline is intentionally limited; the host-agent route provides multilingual ideation.

`--records` accepts an array with these exact fields per record:

```json
{
  "mark": "Example mark",
  "jurisdiction": "US",
  "classes": [9, 42],
  "source_url": "https://official-source.example/record",
  "observed_at": "2026-10-01T12:00:00+00:00",
  "record_id": "official-record-id",
  "status": "status copied from the source"
}
```

This is a **schema illustration, not an actual trademark record**. Importing a URL does not authenticate a record. No records means `unreviewed`; no match in a supplied subset means only `no-match-in-imported-records`. Different classes and inactive statuses are retained for review. EU rights are considered for DE and DE national rights for EU plans; other EU national systems remain a coverage gap.

A domain receipt (`domain --receipt FILE`) requires `domain`, `registrar`, `status` (`available`, `unavailable`, `reserved`, `premium`), `source_url` (HTTPS) and timezone-aware `observed_at`. Receipts older than 15 minutes or more than 30 seconds in the future cannot update the purchase observation. Recent receipts remain explicitly **user-supplied, not independently authenticated**. Contradictory RDAP/registrar evidence is a conflict, not a successful check. Price/currency, renewal cost and purchase conditions are not inferred; consult the registrar directly.

## Optional pinned logo instructions

```sh
python -m nameproof logo-source --output /path/to/new-logo-instructions --fetch
```

Downloads and SHA-256 verifies three plain-text files from the pinned upstream revision. The destination must be new; nothing is overwritten. Read `UPSTREAM_SKILL.md` explicitly with the host agent and use its design references. No executable script, dependency, template, key or provider call is fetched/executed; this is not an automatic skill installation. Without `--fetch`, the command only prints the manifest. See the [worked end-to-end example](docs/WALKTHROUGH.md).

## Important limits

- Trademark checks are preliminary screening, not legal advice or a clearance opinion. Consult an appropriate professional before consequential adoption. Text similarity misses phonetic, conceptual, transliteration, image and common-law conflicts.
- WIPO's Global Brand Database prohibits automatic querying. This tool supplies its manual link, not a scraper. Some official APIs require separate access. See [sources and existing alternatives](docs/SOURCES.md).
- Domain absence is not purchasability. Reserved, premium and aftermarket domains require registrar confirmation. A registered domain might be sold aftermarket; `not_available_for_new_registration` makes no claim about resale.
- IDNs use Python's conservative built-in IDNA support. Spellings that would silently change during encoding fail closed. Preserve Unicode spelling and verify an explicit ASCII/punycode form with the registry when necessary. This is not a complete IDNA2008 implementation.
- Live endpoints are taken only from the HTTPS IANA bootstrap. Redirects fail closed, responses are bounded, requests time out and literal/local endpoints are rejected. The registry endpoint list and system HTTPS proxy are trusted; arbitrary provider URLs are not accepted by CLI/MCP.
- Logo brief output is not a finished logo. Upstream code is neither bundled nor automatically installed. Provider credentials, data sharing, license review and generation cost require separate deliberate setup.

## Development

The suite covers CLI flows, MCP protocol handling, Unicode and malformed inputs, evidence conflicts, stale quotes, jurisdiction/class behavior, and failure-closed domain states. Tests mock network responses; live results are observations, not evergreen fixtures. CI runs Python 3.10–3.13 and verifies installed package data from outside the checkout.

MIT license applies to this repository's original code. No external logo implementation is redistributed. Contributions should add an evidenced capability, tests, examples and consistent EN/zh-CN/ru/de documentation. Never replace an unknown status with an optimistic claim to improve a demo.
