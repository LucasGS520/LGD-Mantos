import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/tokens.css'
import './styles/global.css'
import { NavProvider } from './nav'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <NavProvider>
      <App />
    </NavProvider>
  </StrictMode>,
)
