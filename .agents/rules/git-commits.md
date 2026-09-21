# Git commit messages

Activation: whenever creating a git commit

Only commit when the user explicitly asks.

## Format

```text
<type>(optional-scope): <imperative summary>

Optional body explaining why.
```

## Types

`feat` | `fix` | `refactor` | `chore` | `docs` | `test` | `style`

## Rules

- Imperative subject, ≤72 chars, no trailing period
- Body = why, not a file list
- One logical change per commit
- No `--no-verify` unless user asks
- No amend of pushed commits unless user asks
- Pass message via HEREDOC

## Examples

```text
feat(api): add Clerk-backed GET /api/me

Product user id is the Clerk JWT sub so SPA and API share identity.
```

```text
fix(web): require VITE_CLERK_PUBLISHABLE_KEY at startup
```

```text
chore: add shared AGENTS.md for multi-tool agents
```

```text
# ❌ BAD
Updated files and fixed stuff
```
