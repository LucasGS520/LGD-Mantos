import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/tokens.css'
import './styles/global.css'
import { NavProvider } from './nav'
import { registerServiceWorker } from './services/pwa'
import App from './App'

// Registra o Service Worker uma única vez, fora da árvore React — a tela "Status
// do sistema" observa o estado de atualização via usePwaUpdate() (services/pwa.ts).
registerServiceWorker()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <NavProvider>
      <App />
    </NavProvider>
  </StrictMode>,
)
