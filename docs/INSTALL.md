# Install Nameproof in your coding agent

The fastest route is the [copy-paste setup prompt](../README.md#install-with-your-ai-agent). This guide is also the setup contract for the agent receiving that prompt.

## 1. Open the project and check prerequisites

Work in the **project root you want to use for naming**, not your home directory. You need Git and Python 3.10+; the standard skills installer additionally needs Node.js/npm. Check `git --version`, `python --version` and `npx --version`. If Python is named `python3` (or `py` on Windows), use that command instead throughout. Do not install missing software automatically.

Before writing, check for `.nameproof-kit` and an existing `nameproof` skill in `.agents/skills`, `.claude/skills`, `.cursor/skills`, and `.grok/skills`. If anything exists, inspect it and ask before replacing it. The skills CLI can overwrite same-name skills; `--yes` is intended here for a fresh install only. Never delete an existing checkout to make these instructions work. If the agent's identity is unclear, ask which coding agent to target.

## 2. Keep the CLI in the project

```sh
git clone https://github.com/loufengzh/nameproof-kit.git .nameproof-kit
```

The clone contains the Python CLI, examples, docs and skill. No `pip install`, API key, account, MCP server, paid model or logo provider is needed. Keep this folder available: the skill alone is not the executable. Review the source before running it. Do not automatically commit the nested checkout to your own repository.

## 3. Install the skill: choose exactly one line

Run from the **same project root**, not from `.nameproof-kit`:

```sh
# Claude Code
npx --yes skills@1.7.1 add ./.nameproof-kit --skill nameproof --agent claude-code --yes

# Codex
npx --yes skills@1.7.1 add ./.nameproof-kit --skill nameproof --agent codex --yes

# Cursor
npx --yes skills@1.7.1 add ./.nameproof-kit --skill nameproof --agent cursor --yes

# Antigravity (project path shared by IDE, 2.0 and CLI)
npx --yes skills@1.7.1 add ./.nameproof-kit --skill nameproof --agent antigravity --yes

# Grok Build CLI, not ordinary Grok chat
npx --yes skills@1.7.1 add ./.nameproof-kit --skill nameproof --agent grok --yes
```

These use the published [Vercel skills CLI](https://github.com/vercel-labs/skills), pinned to the tested version. `npx --yes` permits npm to download that CLI; the final `--yes` accepts the project skill installation. There is no `--global` flag. The local-source commands above copy the skill into the agent’s project directory shown below and write `skills-lock.json`. Installing directly from a remote source can instead use a shared `.agents/skills` copy with symlinks for Claude Code and Grok Build. It does not configure MCP or install the optional logo skill.

### No Node.js? Copy one folder instead

Ask your coding agent, or use your file manager, to copy the **whole** `.nameproof-kit/skills/nameproof` folder into the destination below. Create the parent directories first, stop if the destination already exists, and do not create duplicate skill copies.

| Your agent | Destination within your project |
|---|---|
| Claude Code | `.claude/skills/nameproof/` |
| Codex, Cursor, Antigravity | `.agents/skills/nameproof/` |
| Grok Build | `.grok/skills/nameproof/` |

The resulting folder must contain `SKILL.md`. This route needs only Git and Python and does not require the skills CLI. See [vendor documentation and discovery details](HARNESSES.md).

## 4. Verify once, then use it

In the terminal:

```sh
cd .nameproof-kit
python -m nameproof --help
python -m nameproof report --brief examples/brief.json --format markdown
cd ..
```

Success means help and a sample shortlist report are printed, with incomplete evidence still shown as unknown/unreviewed. This test is offline: it does not query domains, purchase anything or generate images. A missing executable, nonzero exit status or missing report is not a successful setup.

Open a new agent session **in the original project** and ask:

```text
Use nameproof. The CLI checkout is .nameproof-kit in this project.
Help me name [my product idea] for [audience and target countries].
Explain the shortlist and flag evidence we have not checked.
```

Verify that the agent actually reads the installed `SKILL.md`; installation success alone does not prove discovery. If the skill is missing from its picker, ask it to read the exact installed path above explicitly. Report that as manual loading rather than automatic discovery. Use the CLI from `.nameproof-kit`, keeping your own briefs/reports at explicit paths. Do not infer countries or legal classes from language alone.

If terminal/filesystem access is unavailable, these commands cannot be executed by that chat session. Open the project in a supported local coding agent or run the commands yourself. No additional paid subscription is supplied or required by Nameproof; the host agent has its own requirements.

## Verification boundary

On 2026-10-07, skills CLI 1.7.1 was tested against the public repository and separately against a freshly cloned checkout in temporary project directories for all five agent IDs. Tests checked the installed skill content, destination paths, symlink resolution, CLI help and offline report output. No personal/global agent configuration was used. The Python test suite is also run in CI.

These are **installer and CLI smoke tests**, not end-to-end tests of the five agent applications. Vendor skill paths are documented in [HARNESSES.md](HARNESSES.md). The optional [logo instructions](LOGO.md) remain a separate, explicitly requested download; no API keys or paid image calls are part of setup.
