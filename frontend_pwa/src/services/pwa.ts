// Registro do Service Worker do PWA e estado de atualização, exposto para a tela
// "Status do sistema" (seção Mais). Módulo singleton — só existe um registro de SW
// por aba, então não faz sentido modelar isso como React Context; componentes leem
// o estado via usePwaUpdate() (useSyncExternalStore).
import { useSyncExternalStore } from 'react'
import { registerSW } from 'virtual:pwa-register'

interface PwaUpdateState {
  /** Há uma versão nova instalada e esperando confirmação do operador. */
  needsRefresh: boolean
  /** O app já está pronto para funcionar offline (primeira instalação do SW). */
  offlineReady: boolean
}

let state: PwaUpdateState = { needsRefresh: false, offlineReady: false }
const listeners = new Set<() => void>()

function setState(patch: Partial<PwaUpdateState>): void {
  state = { ...state, ...patch }
  listeners.forEach(fn => fn())
}

let applyUpdateFn: ((reloadPage?: boolean) => Promise<void>) | null = null

/**
 * Registra o Service Worker do PWA. Chamar uma única vez, na inicialização do
 * app (main.tsx) — nunca dentro de um componente React.
 */
export function registerServiceWorker(): void {
  // Evita quebrar em ambientes sem suporte a Service Worker (ex.: alguns runners de teste).
  if (!('serviceWorker' in navigator)) return

  applyUpdateFn = registerSW({
    onNeedRefresh() {
      setState({ needsRefresh: true })
    },
    onOfflineReady() {
      setState({ offlineReady: true })
    },
  })
}

/** Aplica a atualização pendente do Service Worker e recarrega a página. */
export async function applyServiceWorkerUpdate(): Promise<void> {
  if (!applyUpdateFn) return
  await applyUpdateFn(true)
}

function getSnapshot(): PwaUpdateState {
  return state
}

function subscribe(callback: () => void): () => void {
  listeners.add(callback)
  return () => listeners.delete(callback)
}

/** Hook para a UI (Status do sistema) observar o estado de atualização do SW. */
export function usePwaUpdate(): PwaUpdateState {
  return useSyncExternalStore(subscribe, getSnapshot)
}
