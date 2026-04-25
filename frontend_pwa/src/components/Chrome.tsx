import type { CSSProperties, ReactNode } from 'react'
import { Ico, type IcoProps } from './Icons'
import { useNav, type TabId } from '../nav'

// ─── AppBar ────────────────────────────────────────────────────
interface AppBarProps {
  title: string; subtitle?: string; back?: boolean
  action?: ReactNode; dense?: boolean
}
export function AppBar({ title, subtitle, back, action, dense }: AppBarProps) {
  const { back: goBack } = useNav()
  return (
    <div style={{ padding: dense ? '8px 18px 10px' : '6px 18px 14px', display: 'flex', alignItems: 'center', gap: 12, minHeight: 54, flexShrink: 0 }}>
      {back && (
        <button onClick={goBack} style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', color: 'var(--text-1)', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
          <Ico.back size={20} />
        </button>
      )}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: -0.3, color: 'var(--text-1)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{title}</div>
        {subtitle && <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>{subtitle}</div>}
      </div>
      {action}
    </div>
  )
}

// ─── BottomNav ─────────────────────────────────────────────────
const TABS: { id: TabId; label: string; icon: (p: IcoProps) => JSX.Element }[] = [
  { id: 'op',   label: 'Operação',  icon: Ico.box },
  { id: 'an',   label: 'Análise',   icon: Ico.chart },
  { id: 'mk',   label: 'Marketing', icon: Ico.megaphone },
  { id: 'mais', label: 'Mais',      icon: Ico.more },
]

export function BottomNav({ active }: { active: TabId }) {
  const { setTab } = useNav()
  return (
    <div style={{
      borderTop: '1px solid var(--line-1)',
      background: 'rgba(10,10,11,0.92)',
      backdropFilter: 'blur(18px)',
      paddingTop: 8,
      paddingBottom: 'calc(8px + env(safe-area-inset-bottom, 0px))',
      display: 'grid', gridTemplateColumns: 'repeat(4,1fr)',
      flexShrink: 0,
    }}>
      {TABS.map(t => {
        const on = t.id === active
        const I = t.icon
        return (
          <div key={t.id} onClick={() => setTab(t.id)} style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            padding: '6px 0', cursor: 'pointer',
            color: on ? 'var(--gold-500)' : 'var(--text-3)',
          }}>
            <I size={22} sw={on ? 1.8 : 1.6} />
            <span style={{ fontSize: 10.5, fontWeight: on ? 600 : 500, letterSpacing: 0.1 }}>{t.label}</span>
          </div>
        )
      })}
    </div>
  )
}

// ─── Operação sub-nav (switches between op root screens) ───────
type OpScreen = 'product-list' | 'sales-history' | 'purchase-list' | 'expenses' | 'stock-moves'
const OP_TABS: { id: OpScreen; label: string }[] = [
  { id: 'product-list',  label: 'Produtos' },
  { id: 'sales-history', label: 'Vendas' },
  { id: 'purchase-list', label: 'Compras' },
  { id: 'expenses',      label: 'Despesas' },
  { id: 'stock-moves',   label: 'Estoque' },
]

export function OpSubNav({ active }: { active: OpScreen }) {
  const { navigate } = useNav()
  return (
    <div style={{ display: 'flex', gap: 8, padding: '0 18px 10px', overflowX: 'auto', flexShrink: 0 }} className="lgd-scroll">
      {OP_TABS.map(t => (
        <div key={t.id} onClick={() => navigate(t.id)} style={{
          padding: '7px 14px', borderRadius: 999, fontSize: 12.5, fontWeight: 600, whiteSpace: 'nowrap', cursor: 'pointer',
          background: t.id === active ? 'var(--gold-500)' : 'var(--bg-2)',
          color: t.id === active ? '#1A1408' : 'var(--text-2)',
          border: t.id === active ? '1px solid var(--gold-500)' : '1px solid var(--line-1)',
        }}>{t.label}</div>
      ))}
    </div>
  )
}

// ─── FAB ───────────────────────────────────────────────────────
type IcoFn = (props: IcoProps) => JSX.Element
interface FABProps { icon?: IcoFn; label?: string; onClick?: () => void }
export function FAB({ icon = Ico.plus, label, onClick }: FABProps) {
  const I = icon
  return (
    <div onClick={onClick} style={{
      position: 'absolute', right: 18, bottom: 90, zIndex: 5,
      height: 56, minWidth: 56, padding: label ? '0 18px 0 16px' : 0,
      borderRadius: 28, background: 'var(--gold-500)',
      color: '#1A1408', display: 'flex', alignItems: 'center', gap: 8,
      boxShadow: 'var(--shadow-fab)', fontWeight: 700, fontSize: 14, cursor: 'pointer',
    }}>
      <I size={24} stroke="#1A1408" sw={2.2} />
      {label && <span>{label}</span>}
    </div>
  )
}

// ─── ScreenBody ────────────────────────────────────────────────
interface ScreenBodyProps { children: ReactNode; pad?: number; style?: CSSProperties }
export function ScreenBody({ children, pad = 18, style }: ScreenBodyProps) {
  return (
    <div className="lgd-scroll" style={{ flex: 1, overflowY: 'auto', padding: `0 ${pad}px 100px`, minHeight: 0, ...style }}>
      {children}
    </div>
  )
}
