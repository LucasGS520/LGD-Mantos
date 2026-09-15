import { Session } from './session'
import type {
  Dashboard, DRE, TopProduct, BySizeItem, ByChannelItem,
  ProductAnalysis, DataQuality,
  CategoryPerformance, CategorySizeDistribution, CategoryCoverage, BuyingPattern, CategorySizeStock,
  ProductClassification,
  AppPreferences, AppPreferencesInput, HealthStatus,
} from './types'

// Base da API: usa VITE_API_URL quando definida (dev fora do proxy, ambientes
// especiais); caso contrário assume caminho relativo — em produção o PWA e a API
// vivem no mesmo domínio atrás do reverse proxy (Caddy), e em desenvolvimento o
// Vite encaminha /api para o backend local (ver proxy em vite.config.ts).
const ENV_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
const BASE = (ENV_BASE && ENV_BASE.length > 0
  ? ENV_BASE
  : '/api/v1').replace(/\/+$/, '')

let _onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(fn: () => void): void {
  _onUnauthorized = fn
}

// Monta a querystring para endpoints de analytics que aceitam `period` OU
// `days` (ex.: /analytics/top-products, /analytics/by-size). O backend dá
// prioridade a `period` quando ambos chegam (ver resolve_period), então aqui
// só mandamos `days` quando não há period definido.
function periodOuDiasQuery(period?: string, days?: number): string {
  const q = new URLSearchParams()
  if (period) q.set('period', period)
  else if (days !== undefined) q.set('days', String(days))
  return q.toString()
}

async function readJsonBody<T>(res: Response): Promise<T | null> {
  const text = await res.text()
  if (!text.trim()) return null
  try {
    return JSON.parse(text) as T
  } catch {
    return null
  }
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
    const d = await readJsonBody<{ detail?: unknown }>(res)
    if (d?.detail) msg = typeof d.detail === 'string' ? d.detail : JSON.stringify(d.detail)
    throw new Error(msg)
  }

  if (res.status === 204) return undefined as T
  const data = await readJsonBody<T>(res)
  if (data === null) {
    throw new Error('Resposta inválida do servidor (sem JSON). Verifique a configuração da API.')
  }
  return data
}

/**
 * Baixa um arquivo autenticado (CSV/ZIP de exportação) e dispara o download no
 * navegador. Usa fetch (não um <a href> direto) porque o download exige o header
 * Authorization — e libera a object URL logo depois de iniciar o download, para
 * não reter o arquivo inteiro em memória além do necessário.
 */
async function downloadFile(path: string, fallbackName: string): Promise<void> {
  const token = Session.load()
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, { method: 'GET', headers })

  if (res.status === 401) {
    Session.clear()
    _onUnauthorized?.()
    throw new Error('Sessão expirada. Faça login novamente.')
  }
  if (!res.ok) {
    let msg = `Erro ${res.status}`
    const d = await readJsonBody<{ detail?: unknown }>(res)
    if (d?.detail) msg = typeof d.detail === 'string' ? d.detail : JSON.stringify(d.detail)
    throw new Error(msg)
  }

  const disposition = res.headers.get('Content-Disposition') ?? ''
  const filename = disposition.match(/filename="?([^"]+)"?/)?.[1] ?? fallbackName

  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  // Pequeno atraso antes de revogar: alguns navegadores iniciam o download de forma
  // assíncrona a partir do clique — revogar cedo demais pode cancelar o download.
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export const api = {
  get: <T>(path: string) => req<T>('GET', path),
  post: <T>(path: string, body: unknown) => req<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => req<T>('PUT', path, body),
  patch: <T>(path: string, body: unknown) => req<T>('PATCH', path, body),
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
    const data = await readJsonBody<T>(res)
    if (data === null) {
      throw new Error('Resposta inválida do servidor (sem JSON). Verifique a configuração da API.')
    }
    return data
  },

  // ─── Analytics ────────────────────────────────────────────
  // `compare` acrescenta `?compare=true` — sem ele a resposta é idêntica à de antes.
  getDashboard: (compare?: boolean) =>
    req<Dashboard>('GET', `/analytics/dashboard${compare ? '?compare=true' : ''}`),

  getDRE: (month?: number, year?: number, compare?: boolean) => {
    const q = new URLSearchParams()
    if (month) q.set('month', String(month))
    if (year) q.set('year', String(year))
    if (compare) q.set('compare', 'true')
    const qs = q.toString()
    return req<DRE>('GET', `/analytics/finance/dre${qs ? `?${qs}` : ''}`)
  },

  // period tem prioridade sobre days no backend (ver resolve_period) — por isso
  // days só é enviado quando period não é informado. Aceitar os dois evita que
  // telas com janela fixa (ex.: Products.tsx, "últimos 30 dias") precisem cair
  // pra api.get() cru e perder a tipagem de retorno.
  getTopProducts: (period?: string, days?: number) =>
    req<TopProduct[]>('GET', `/analytics/top-products?${periodOuDiasQuery(period, days)}`),

  getBySize: (period?: string, days?: number) =>
    req<BySizeItem[]>('GET', `/analytics/by-size?${periodOuDiasQuery(period, days)}`),

  getByChannel: (period: string, compare?: boolean) =>
    req<ByChannelItem[]>('GET', `/analytics/by-channel?period=${period}${compare ? '&compare=true' : ''}`),

  getProductAnalysis: (period: string) =>
    req<ProductAnalysis>('GET', `/analytics/products/analysis?period=${period}`),

  getDataQuality: () =>
    req<DataQuality>('GET', '/analytics/data-quality'),

  getCategoryPerformance: (period: string) =>
    req<CategoryPerformance[]>('GET', `/analytics/categories/performance?period=${period}`),

  getCategoryStockCoverage: () =>
    req<CategoryCoverage[]>('GET', '/analytics/categories/stock-coverage'),

  getCategorySizeDistribution: (period: string) =>
    req<CategorySizeDistribution[]>('GET', `/analytics/categories/size-distribution?period=${period}`),

  getCategoryBuyingPatterns: (period: string) =>
    req<BuyingPattern[]>('GET', `/analytics/categories/buying-patterns?period=${period}`),

  getCategorySizeStock: () =>
    req<CategorySizeStock[]>('GET', '/analytics/categories/size-stock'),

  getProductClassification: () =>
    req<ProductClassification>('GET', '/analytics/product-classification'),

  // ─── Configurações e Status do sistema ───────────────────────────────────
  getPreferences: () =>
    req<AppPreferences>('GET', '/settings/preferences'),

  updatePreferences: (data: AppPreferencesInput) =>
    req<AppPreferences>('PUT', '/settings/preferences', data),

  getHealth: () =>
    req<HealthStatus>('GET', '/health'),

  exportDataset: (dataset: string) =>
    downloadFile(`/export/${dataset}`, `lgd-${dataset}.csv`),

  exportBackup: () =>
    downloadFile('/export/backup', 'lgd-backup.zip'),

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
    const payload = await readJsonBody<{ token?: string }>(res)
    if (!payload?.token) {
      throw new Error('Falha no login: resposta inválida da API. Confira VITE_API_URL.')
    }
    const { token } = payload
    Session.save(token)
    return token as string
  },
}
