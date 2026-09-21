import { UserButton } from '@clerk/react'
import type { ReactNode } from 'react'
import '@/components/auth/auth-shell.css'

type AuthShellProps = {
  children: ReactNode
}

export function AuthShell({ children }: AuthShellProps) {
  return (
    <div className="auth-shell">
      <header className="auth-shell__header">
        <span className="auth-shell__title">Blueprint</span>
        <UserButton />
      </header>
      <div className="auth-shell__body">{children}</div>
    </div>
  )
}
