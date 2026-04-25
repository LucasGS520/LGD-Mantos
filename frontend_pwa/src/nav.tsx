import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react'
import { Session } from './services/session'
import { setUnauthorizedHandler } from './services/api'

export type ScreenId =
  | 'login'
  | 'product-list' | 'product-detail' | 'product-form'
  | 'sale-modal' | 'sales-history'
  | 'purchase-form' | 'purchase-list'
  | 'expenses' | 'stock-moves' | 'stock-alerts'
  | 'dashboard' | 'top-products' | 'by-size' | 'by-channel' | 'suggestions' | 'dre'
  | 'marketing'
  | 'more' | 'suppliers'

export type TabId = 'op' | 'an' | 'mk' | 'mais'

export const TAB_ROOTS: Record<TabId, ScreenId> = {
  op: 'product-list',
  an: 'dashboard',
  mk: 'marketing',
  mais: 'more',
}

type NavEntry = { screen: ScreenId; params: Record<string, unknown> }

interface NavCtx {
  screen: ScreenId
  tab: TabId | null
  canGoBack: boolean
  params: Record<string, unknown>
  navigate: (screen: ScreenId, params?: Record<string, unknown>) => void
  setTab: (tab: TabId) => void
  back: () => void
  logout: () => void
}

const Nav = createContext<NavCtx | null>(null)

export function NavProvider({ children }: { children: ReactNode }) {
  const [tab, setTabState] = useState<TabId | null>(null)
  const [stack, setStack] = useState<NavEntry[]>(() => {
    const screen: ScreenId = Session.isValid() ? 'product-list' : 'login'
    return [{ screen, params: {} }]
  })

  const current = stack[stack.length - 1]
  const canGoBack = stack.length > 1

  const navigate = (s: ScreenId, p: Record<string, unknown> = {}) =>
    setStack(prev => [...prev, { screen: s, params: p }])

  const setTab = (t: TabId) => {
    setTabState(t)
    setStack([{ screen: TAB_ROOTS[t], params: {} }])
  }

  const back = () =>
    setStack(prev => (prev.length > 1 ? prev.slice(0, -1) : prev))

  const logout = useCallback(() => {
    Session.clear()
    setTabState(null)
    setStack([{ screen: 'login', params: {} }])
  }, [])

  useEffect(() => {
    setUnauthorizedHandler(logout)
  }, [logout])

  return (
    <Nav.Provider value={{
      screen: current.screen,
      tab,
      canGoBack,
      params: current.params,
      navigate,
      setTab,
      back,
      logout,
    }}>
      {children}
    </Nav.Provider>
  )
}

export function useNav(): NavCtx {
  const ctx = useContext(Nav)
  if (!ctx) throw new Error('useNav outside NavProvider')
  return ctx
}
