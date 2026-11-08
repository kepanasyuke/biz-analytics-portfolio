import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@portfolio/ui/styles.css'
import { App } from './App'

const container = document.getElementById('root')

createRoot(container as HTMLElement).render(
  <StrictMode>
    <App />
  </StrictMode>
)
