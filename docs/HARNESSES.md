# Coding-harness integration

Documentation checked on 2026-10-07. This is a documented-format support matrix, **not an end-to-end certification** of every application/version. NameProof's Python CLI is the executable component. `SKILL.md` teaches the host agent when and how to use it; it does not install Python, supply a model, grant permissions, or make a chat app execute local commands.

## Minimal integration

1. Make this checkout available in the harness workspace and run `python -m nameproof --help` from the checkout root.
2. Copy the **entire** `skills/nameproof/` folder into one project skill directory below, retaining the `nameproof/SKILL.md` structure. Do not install duplicate copies into directories the same harness scans.
3. Start or refresh the harness, verify discovery, and ask it to use `nameproof` on a sample brief. If discovery fails, ask the agent to read the copied `SKILL.md` explicitly. That is a manual fallback, not verified automatic loading.
4. Keep the CLI checkout available. The skill-only copy is not a self-contained Python distribution. If it is in another repository, give the agent its absolute checkout path; never guess where it is installed.

The portable frontmatter contains only `name` and `description`, with plain Markdown instructions. We intentionally avoid host-specific tool names, shell interpolation, hooks, permissions, and model settings. This follows the [Agent Skills format](https://agentskills.io/specification).

## Support matrix

| Host | Recommended project destination | Personal destination documented by vendor | Verification and boundary |
|---|---|---|---|
| Claude Code | `.claude/skills/nameproof/SKILL.md` | `~/.claude/skills/nameproof/SKILL.md` | Check `/skills`, then invoke `/nameproof`. Local personal skills are not automatically local files in cloud/Cowork sessions; use the documented account or committed-repository route. |
| Codex | `.agents/skills/nameproof/SKILL.md` | `~/.agents/skills/nameproof/SKILL.md` | Verify in the skill selector or request the skill by name. Repository discovery walks from the current directory toward the repository root. |
| Cursor Agent | `.agents/skills/nameproof/SKILL.md` or `.cursor/skills/nameproof/SKILL.md` | `~/.agents/skills/` or `~/.cursor/skills/` | Use its skill UI or invoke by name. Local personal skills are not automatically present in remote/cloud workers; prefer committed project skills. |
| Antigravity 2.0 / standalone IDE | `.agents/skills/nameproof/SKILL.md` | `~/.gemini/config/skills/nameproof/SKILL.md` | Inspect Customizations; invoke `/nameproof` in 2.0. The legacy IDE global `~/.gemini/antigravity/skills/` remains documented. |
| Antigravity CLI | `.agents/skills/nameproof/SKILL.md` | `~/.gemini/antigravity-cli/skills/nameproof/SKILL.md` | Discover/use the local skill in the CLI. Do not assume the IDE and CLI share a global directory. |
| Grok **Build** CLI | `.grok/skills/nameproof/SKILL.md` | `~/.grok/skills/nameproof/SKILL.md` | Run `grok inspect`, check `/skills`, then `/nameproof`. Official docs also describe Claude Code compatibility, but a native `.grok/` copy is the explicit route. |
| Grok chat, generic chatbot, or raw model API | No local auto-discovery claim | Not established by this toolkit | Use the generated brief/prompt manually, or a separately implemented tool runner. A model being able to code does not imply filesystem or CLI access. |

All execution still depends on the host's workspace access, Python installation, network policy, and user-granted permissions. The same skill can yield different language-model candidate suggestions; deterministic checks should be repeatable for the same inputs and evidence.

## Official references

- [Claude Code skills and loading locations](https://code.claude.com/docs/en/skills)
- [OpenAI Codex skills](https://developers.openai.com/codex/skills/) (currently redirects to ChatGPT Learn's skill documentation)
- [Cursor Agent Skills](https://cursor.com/docs/skills)
- [Antigravity agent skills and separate IDE/CLI paths](https://antigravity.google/docs/skills)
- [Grok Build skills, plugins, and compatibility](https://docs.x.ai/build/features/skills-plugins-marketplaces)
- [Grok Build CLI reference and `inspect`](https://docs.x.ai/build/cli/reference)

Recheck these links before changing installation behavior. Vendor paths and discovery behavior can change independently of NameProof.
