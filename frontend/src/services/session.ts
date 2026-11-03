const TOKEN_KEY = 'lgd_token'

/** Decodifica o payload de um JWT sem validar assinatura (uso local, exibição). */
function decodePayload(token: string): { exp?: number } | null {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    return JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
  } catch {
    return null
  }
}

export const Session = {
  save(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  },

  load(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  },

  clear(): void {
    localStorage.removeItem(TOKEN_KEY)
  },

  isValid(): boolean {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return false
    const payload = decodePayload(token)
    return typeof payload?.exp === 'number' && payload.exp * 1000 > Date.now()
  },

  /** Data de expiração da sessão atual — usada na tela Configurações (Segurança). */
  getExpiry(): Date | null {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) return null
    const payload = decodePayload(token)
    return typeof payload?.exp === 'number' ? new Date(payload.exp * 1000) : null
  },
}
