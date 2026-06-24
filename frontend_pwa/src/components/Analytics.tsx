import { useState, useEffect, useRef, type ReactNode } from 'react'
import { useNav } from '../nav'

// ─── Period ────────────────────────────────────────────────────
export const PERIODS = [
  { label: 'Esse mês',       value: 'current_month'  },
  { label: 'Mês passado',    value: 'last_month'     },
  { label: 'Últ. 3 meses',   value: 'last_3_months'  },
  { label: 'Últ. 6 meses',   value: 'last_6_months'  },
  { label: 'Esse ano',       value: 'current_year'   },
] as const

export type Period = typeof PERIODS[number]['value']

export function PeriodSelect({ value, onChange }: { value: Period; onChange: (p: Period) => void }) {
  return (
    <div style={{ padding: '0 18px 14px', flexShrink: 0, position: 'relative' }}>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
        <span style={{ position: 'absolute', left: 12, fontSize: 11, fontWeight: 600, color: 'var(--text-4)', textTransform: 'uppercase', letterSpacing: 0.4, pointerEvents: 'none', zIndex: 1 }}>
          Período
        </span>
        <select
          value={value}
          onChange={e => onChange(e.target.value as Period)}
          style={{
            width: '100%', padding: '8px 36px 8px 74px',
            borderRadius: 10, border: '1px solid var(--line-2)',
            background: 'var(--bg-2)', color: 'var(--text-1)',
            fontSize: 13, fontWeight: 600, cursor: 'pointer',
            appearance: 'none', WebkitAppearance: 'none',
            outline: 'none', fontFamily: 'var(--font-sans)',
          }}
        >
          {PERIODS.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        <svg style={{ position: 'absolute', right: 12, pointerEvents: 'none', flexShrink: 0 }} width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M3 5l4 4 4-4" stroke="var(--text-3)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
    </div>
  )
}

export function periodLabel(p: Period): string {
  return PERIODS.find(x => x.value === p)?.label ?? p
}

// ─── MetricInfo ────────────────────────────────────────────────
interface MetricInfoProps {
  what: string
  good: string
  action: string
}

export function MetricInfo({ what, good, action }: MetricInfoProps) {
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState({ top: 0, left: 0 })
  const btnRef = useRef<HTMLButtonElement>(null)

  const toggle = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (!open && btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect()
      const left = Math.min(rect.left, window.innerWidth - 248)
      setPos({ top: rect.bottom + 6, left: Math.max(left, 8) })
    }
    setOpen(v => !v)
  }

  useEffect(() => {
    if (!open) return
    const close = () => setOpen(false)
    document.addEventListener('click', close)
    return () => document.removeEventListener('click', close)
  }, [open])

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center' }}>
      <button ref={btnRef} onClick={toggle} style={{
        width: 17, height: 17, borderRadius: 99, border: '1px solid var(--line-2)',
        background: 'var(--bg-3)', color: 'var(--text-3)', fontSize: 10, fontWeight: 700,
        cursor: 'pointer', display: 'grid', placeItems: 'center', flexShrink: 0, lineHeight: 1,
      }}>i</button>
      {open && (
        <div style={{
          position: 'fixed', top: pos.top, left: pos.left, zIndex: 200, width: 238,
          background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 14,
          padding: 14, boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
        }}>
          <InfoBlock label="O QUE É" color="var(--text-2)" text={what} />
          <InfoBlock label="BOM VALOR" color="#5DD49E" text={good} />
          <InfoBlock label="O QUE FAZER" color="var(--gold-300)" text={action} />
        </div>
      )}
    </span>
  )
}

function InfoBlock({ label, color, text }: { label: string; color: string; text: string }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ fontSize: 9.5, fontWeight: 700, color, letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 12.5, color: 'var(--text-1)', lineHeight: 1.45 }}>{text}</div>
    </div>
  )
}

// ─── AlertRow ──────────────────────────────────────────────────
interface AlertRowProps {
  tone: 'danger' | 'warn'
  icon: ReactNode
  text: string
  cta?: string
  onCta?: () => void
}

export function AlertRow({ tone, icon, text, cta, onCta }: AlertRowProps) {
  const colors = {
    danger: { bg: 'rgba(232,88,79,0.08)', bd: 'rgba(232,88,79,0.22)', fg: '#F5847B' },
    warn:   { bg: 'rgba(232,160,74,0.08)', bd: 'rgba(232,160,74,0.22)', fg: '#F5BF7A' },
  }
  const c = colors[tone]
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px',
      borderRadius: 12, background: c.bg, border: `1px solid ${c.bd}`, marginBottom: 8,
    }}>
      <span style={{ color: c.fg, display: 'flex', flexShrink: 0 }}>{icon}</span>
      <span style={{ flex: 1, fontSize: 13, color: 'var(--text-1)', lineHeight: 1.4 }}>{text}</span>
      {cta && (
        <button onClick={onCta} style={{
          fontSize: 12, fontWeight: 700, color: c.fg, background: 'transparent',
          border: 'none', cursor: 'pointer', whiteSpace: 'nowrap', padding: '2px 4px',
        }}>{cta} →</button>
      )}
    </div>
  )
}

// ─── SectionChart ──────────────────────────────────────────────
interface SectionChartProps {
  title: string
  info?: MetricInfoProps
  loading?: boolean
  empty?: boolean
  emptyMsg?: string
  children: ReactNode
  action?: ReactNode
}

export function SectionChart({ title, info, loading, empty, emptyMsg, children, action }: SectionChartProps) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)', letterSpacing: 0.1, textTransform: 'uppercase' }}>{title}</span>
          {info && <MetricInfo {...info} />}
        </div>
        {action}
      </div>
      {loading ? (
        <div style={{ height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-3)', fontSize: 13 }}>Carregando…</div>
      ) : empty ? (
        <div style={{ height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-3)', fontSize: 13 }}>{emptyMsg ?? 'Sem dados no período'}</div>
      ) : children}
    </div>
  )
}

// ─── ScoreBar ──────────────────────────────────────────────────
export function ScoreBar({ value, max = 100 }: { value: number; max?: number }) {
  const pct = Math.min((value / max) * 100, 100)
  const color = pct >= 80 ? '#5DD49E' : pct >= 50 ? '#F5BF7A' : '#F5847B'
  return (
    <div style={{ height: 8, borderRadius: 99, background: 'var(--bg-3)', overflow: 'hidden' }}>
      <div style={{ height: '100%', width: `${pct}%`, background: color, borderRadius: 99, transition: 'width 0.5s ease' }} />
    </div>
  )
}

// ─── CovBadge ──────────────────────────────────────────────────
export function CovBadge({ days }: { days: number | null }) {
  if (days === null) return <span style={{ fontSize: 12, color: 'var(--text-3)' }}>—</span>
  const tone = days < 7 ? '#F5847B' : days < 21 ? '#F5BF7A' : '#5DD49E'
  return (
    <span style={{ fontSize: 12, fontWeight: 700, color: tone }}>{Math.round(days)}d</span>
  )
}

// ─── NavItem ──────────────────────────────────────────────────
export function NavItem({ icon, label, sub, badge, target }: {
  icon: ReactNode; label: string; sub?: string; badge?: number; target: string
}) {
  const { navigate } = useNav()
  return (
    <div onClick={() => navigate(target)} style={{
      display: 'flex', alignItems: 'center', gap: 14, padding: '14px 0',
      borderBottom: '1px solid var(--line-1)', cursor: 'pointer',
    }}>
      <div style={{ width: 38, height: 38, borderRadius: 12, background: 'var(--bg-2)', border: '1px solid var(--line-1)', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
        {icon}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-1)' }}>{label}</div>
        {sub && <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 1 }}>{sub}</div>}
      </div>
      {badge !== undefined && badge > 0 && (
        <span style={{ fontSize: 11, fontWeight: 700, color: '#F5847B', background: 'rgba(232,88,79,0.12)', border: '1px solid rgba(232,88,79,0.25)', borderRadius: 99, padding: '2px 7px' }}>{badge}</span>
      )}
      <svg width="8" height="14" viewBox="0 0 8 14" fill="none"><path d="M1 1l6 6-6 6" stroke="var(--text-3)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
    </div>
  )
}
