import { Session } from './session'

const BASE = import.meta.env.VITE_API_URL as string

let _onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(fn: () => void): void {
  _onUnauthorized = fn
}

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const token = Session.load()
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (res.status === 401) {
    Session.clear()
    _onUnauthorized?.()
    throw new Error('Sessão expirada. Faça login novamente.')
  }

  if (!res.ok) {
    let msg = `Erro ${res.status}`
    try {
      const d = await res.json()
      if (d.detail) msg = typeof d.detail === 'string' ? d.detail : JSON.stringify(d.detail)
    } catch { /* ignore */ }
    throw new Error(msg)
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => req<T>('GET', path),
  post: <T>(path: string, body: unknown) => req<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => req<T>('PUT', path, body),
  delete: <T>(path: string) => req<T>('DELETE', path),

  async upload<T>(path: string, file: File, field = 'file'): Promise<T> {
    const token = Session.load()
    const form = new FormData()
    form.append(field, file)
    const headers: Record<string, string> = {}
    if (token) headers['Authorization'] = `Bearer ${token}`
    const res = await fetch(`${BASE}${path}`, { method: 'POST', headers, body: form })
    if (res.status === 401) {
      Session.clear()
      _onUnauthorized?.()
      throw new Error('Sessão expirada')
    }
    if (!res.ok) throw new Error(`Erro ${res.status}`)
    return res.json() as Promise<T>
  },

  async login(password: string): Promise<string> {
    const res = await fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    if (!res.ok) {
      if (res.status === 401 || res.status === 403 || res.status === 400) {
        throw new Error('Senha incorreta')
      }
      throw new Error(`Erro ${res.status}`)
    }
    const { token } = await res.json()
    Session.save(token)
    return token as string
  },
}
