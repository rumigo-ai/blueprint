import { ClerkProvider, Show } from '@clerk/react'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from '@/app'
import { AuthShell } from '@/components/auth/auth-shell'
import { SignInPage } from '@/components/auth/sign-in-page'
import '@/styles/index.css'

const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!publishableKey) {
  throw new Error(
    'Missing VITE_CLERK_PUBLISHABLE_KEY. Copy apps/web/.env.example to apps/web/.env and fill in your Clerk key.',
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ClerkProvider publishableKey={publishableKey}>
      <Show when="signed-out">
        <SignInPage />
      </Show>
      <Show when="signed-in">
        <AuthShell>
          <App />
        </AuthShell>
      </Show>
    </ClerkProvider>
  </StrictMode>,
)
