import { SignIn } from '@clerk/react'
import '@/components/auth/sign-in-page.css'

export function SignInPage() {
  return (
    <main className="sign-in-page">
      <SignIn />
    </main>
  )
}
