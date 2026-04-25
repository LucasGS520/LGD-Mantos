const TOKEN_KEY = 'lgd_token'

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
    try {
      const parts = token.split('.')
      if (parts.length !== 3) return false
      const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
      return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now()
    } catch {
      return false
    }
  },
}
