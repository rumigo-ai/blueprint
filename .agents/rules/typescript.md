# TypeScript (`apps/web`)

Activation: files under `apps/web/**/*.{ts,tsx}`

## Layout

- `api/` — typed HTTP helpers (not `services/`)
- `components/` — kebab-case; auth under `components/auth/`
- `hooks/`, `lib/`, `stat/`, `styles/`, `types/`
- Entry: `main.tsx` (ClerkProvider), `app.tsx` (signed-in UI)
- Styles: `styles/index.css` from `main.tsx`, `styles/app.css` from `app.tsx`

## Types

- Strict TS; no implicit `any`
- Prefer `type` for props/DTOs; `import type` for type-only imports
- Extend `src/vite-env.d.ts` when adding `VITE_*` keys
- Alias `@/` → `src/`

## Clerk

```tsx
const key = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY
if (!key) throw new Error("Missing VITE_CLERK_PUBLISHABLE_KEY")

<ClerkProvider publishableKey={key}>
  <Show when="signed-out"><SignInPage /></Show>
  <Show when="signed-in"><AuthShell><App /></AuthShell></Show>
</ClerkProvider>
```

Do **not** add a UI fallback when keys are missing — fail loud.

## API calls

```ts
export async function fetchMe(token: string): Promise<UserDto> {
  const res = await fetch(`${apiBaseUrl()}/api/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!res.ok) throw new Error(`GET /api/me failed: ${res.status}`)
  return res.json() as Promise<UserDto>
}
```

Never hard-code `http://localhost:8000` in components.
