export default function App() {
  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-6 py-10">
      <div className="space-y-2">
        <p className="font-brand text-sm font-bold tracking-[0.05em] text-muted-foreground">
          Blueprint
        </p>
        <h1 className="font-display text-4xl font-light tracking-tight text-foreground md:text-5xl">
          Hiring workflows, automated
        </h1>
        <p className="max-w-xl text-base text-muted-foreground">
          Design node-based hiring flows, run verifications and contracts, and
          watch job listings move through your pipeline.
        </p>
      </div>

      <div className="rounded-[20px] border border-border bg-card p-6 text-card-foreground shadow-none">
        <p className="text-sm text-muted-foreground">
          Theme tokens from pilot-dashboard (Rumigo parchment). Use Tailwind
          utilities like{' '}
          <code className="font-mono text-xs text-foreground">bg-background</code>
          ,{' '}
          <code className="font-mono text-xs text-foreground">font-display</code>
          , and{' '}
          <code className="font-mono text-xs text-foreground">text-muted-foreground</code>
          .
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          className="rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground"
        >
          Primary action
        </button>
        <button
          type="button"
          className="rounded-full border border-border bg-transparent px-5 py-2.5 text-sm font-medium text-foreground"
        >
          Secondary
        </button>
      </div>
    </main>
  )
}
