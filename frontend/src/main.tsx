import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { NavProvider } from './app/nav'
import './styles/global.css'
import './styles/tokens.css'
import './styles/workspace.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <NavProvider>
      <App />
    </NavProvider>
  </StrictMode>,
)
