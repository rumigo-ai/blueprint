import { SignIn } from '@clerk/react'

export function SignInPage() {
  return (
    <main className="grid min-h-svh place-items-center bg-background p-6 text-foreground">
      <SignIn />
    </main>
  )
}
