import { UserButton } from '@clerk/react'
import type { ReactNode } from 'react'

type AuthShellProps = {
  children: ReactNode
}

export function AuthShell({ children }: AuthShellProps) {
  return (
    <div className="flex min-h-svh flex-col bg-background text-foreground">
      <header className="flex items-center justify-between border-b border-border px-5 py-3">
        <span className="font-brand text-sm font-bold tracking-[0.05em] text-foreground">
          Blueprint
        </span>
        <UserButton />
      </header>
      <div className="flex flex-1 flex-col">{children}</div>
    </div>
  )
}
