import type { CSSProperties, ReactNode, ChangeEvent } from 'react'
import { Ico, type IcoProps } from './Icons'

// ─── Formatters ────────────────────────────────────────────────
export const fmtBRL = (n: number) =>
  'R$ ' + Number(n).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
export const fmtBRLshort = (n: number) => {
  if (Math.abs(n) >= 1000) return 'R$ ' + (n / 1000).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + 'k'
  return fmtBRL(n)
}
export const fmtNum = (n: number) => Number(n).toLocaleString('pt-BR')

// ─── Badge ─────────────────────────────────────────────────────
type BadgeTone = 'neutral' | 'gold' | 'success' | 'danger' | 'warn' | 'info' | 'solid'
interface BadgeProps { children: ReactNode; tone?: BadgeTone; size?: 'sm' | 'lg'; dot?: boolean }

export function Badge({ children, tone = 'neutral', size = 'sm', dot }: BadgeProps) {
  const tones: Record<BadgeTone, { bg: string; fg: string; bd: string }> = {
    neutral: { bg: 'rgba(255,255,255,0.06)', fg: 'var(--text-2)', bd: 'var(--line-2)' },
    gold:    { bg: 'rgba(212,168,71,0.12)',  fg: 'var(--gold-300)', bd: 'rgba(212,168,71,0.3)' },
    success: { bg: 'rgba(63,184,124,0.12)',  fg: '#5DD49E', bd: 'rgba(63,184,124,0.3)' },
    danger:  { bg: 'rgba(232,88,79,0.12)',   fg: '#F5847B', bd: 'rgba(232,88,79,0.3)' },
    warn:    { bg: 'rgba(232,160,74,0.12)',  fg: '#F5BF7A', bd: 'rgba(232,160,74,0.3)' },
    info:    { bg: 'rgba(94,168,224,0.12)',  fg: '#8BC0E8', bd: 'rgba(94,168,224,0.3)' },
    solid:   { bg: 'var(--gold-500)', fg: '#1A1408', bd: 'var(--gold-500)' },
  }
  const t = tones[tone]
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 5,
      padding: size === 'lg' ? '5px 10px' : '3px 8px',
      borderRadius: 999, background: t.bg, color: t.fg, border: `1px solid ${t.bd}`,
      fontSize: size === 'lg' ? 12 : 10.5, fontWeight: 600, letterSpacing: 0.1, whiteSpace: 'nowrap',
    }}>
      {dot && <span style={{ width: 6, height: 6, borderRadius: 99, background: t.fg }} />}
      {children}
    </span>
  )
}

// ─── Card ──────────────────────────────────────────────────────
interface CardProps { children: ReactNode; style?: CSSProperties; padding?: number; onClick?: () => void; accent?: boolean }

export function Card({ children, style, padding = 14, onClick, accent }: CardProps) {
  return (
    <div onClick={onClick} style={{
      background: 'var(--bg-1)', border: `1px solid ${accent ? 'rgba(212,168,71,0.35)' : 'var(--line-1)'}`,
      borderRadius: 'var(--r-lg)', padding, position: 'relative', ...style,
    }}>{children}</div>
  )
}

// ─── Button ────────────────────────────────────────────────────
type BtnKind = 'primary' | 'ghost' | 'secondary' | 'danger'
type IcoFn = (props: IcoProps) => JSX.Element
interface BtnProps {
  children?: ReactNode; kind?: BtnKind; size?: 'sm' | 'md' | 'lg'
  icon?: IcoFn; full?: boolean; style?: CSSProperties; onClick?: () => void
}

export function Btn({ children, kind = 'primary', size = 'md', icon, full, style, onClick }: BtnProps) {
  const I = icon
  const sizes = {
    sm: { h: 36, fs: 13, px: 12, gap: 6, isz: 16 },
    md: { h: 46, fs: 14, px: 16, gap: 8, isz: 18 },
    lg: { h: 54, fs: 15, px: 22, gap: 10, isz: 20 },
  }[size]
  const kinds: Record<BtnKind, { bg: string; fg: string; bd: string }> = {
    primary:   { bg: 'var(--gold-500)', fg: '#1A1408', bd: 'var(--gold-500)' },
    ghost:     { bg: 'transparent', fg: 'var(--text-1)', bd: 'var(--line-2)' },
    secondary: { bg: 'var(--bg-2)', fg: 'var(--text-1)', bd: 'var(--line-2)' },
    danger:    { bg: 'rgba(232,88,79,0.1)', fg: '#F5847B', bd: 'rgba(232,88,79,0.3)' },
  }
  const k = kinds[kind]
  return (
    <button onClick={onClick} style={{
      height: sizes.h, padding: `0 ${sizes.px}px`, gap: sizes.gap,
      borderRadius: 12, background: k.bg, color: k.fg, border: `1px solid ${k.bd}`,
      fontSize: sizes.fs, fontWeight: 700, letterSpacing: 0.1,
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
      width: full ? '100%' : undefined, ...style,
    }}>
      {I && <I size={sizes.isz} stroke={k.fg} sw={kind === 'primary' ? 2.2 : 1.8} />}
      {children}
    </button>
  )
}

// ─── Input ─────────────────────────────────────────────────────
interface InputProps {
  label?: string; value?: string; placeholder?: string; suffix?: string
  prefix?: string; type?: string; readOnly?: boolean; error?: boolean; hint?: string
  onChange?: (e: ChangeEvent<HTMLInputElement>) => void
}
export function Input({ label, value, placeholder, suffix, prefix, type = 'text', readOnly, error, hint, onChange }: InputProps) {
  const isNumeric = type === 'number'
  return (
    <div>
      {label && <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>{label}</div>}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8, height: 46, padding: '0 14px',
        borderRadius: 12, background: 'var(--bg-4)',
        border: `1px solid ${error ? 'rgba(232,88,79,0.4)' : 'var(--line-2)'}`,
      }}>
        {prefix && <span style={{ color: 'var(--text-3)', fontSize: 14 }}>{prefix}</span>}
        <input
          type={isNumeric ? 'text' : type}
          inputMode={isNumeric ? 'decimal' : undefined}
          value={onChange ? (value ?? '') : undefined}
          defaultValue={onChange ? undefined : value}
          placeholder={placeholder}
          readOnly={readOnly}
          onChange={onChange}
          style={{ flex: 1, background: 'transparent', border: 0, outline: 'none', color: 'var(--text-1)', fontSize: 15, fontWeight: 500, minWidth: 0 }}
        />
        {suffix && <span style={{ color: 'var(--text-3)', fontSize: 13 }}>{suffix}</span>}
      </div>
      {hint && <div style={{ fontSize: 11.5, color: error ? '#F5847B' : 'var(--text-3)', marginTop: 5 }}>{hint}</div>}
    </div>
  )
}

// ─── Select ────────────────────────────────────────────────────
interface SelectProps { label?: string; value?: string; placeholder?: string }
export function Select({ label, value, placeholder = 'Selecionar' }: SelectProps) {
  return (
    <div>
      {label && <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>{label}</div>}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: 46, padding: '0 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)' }}>
        <span style={{ flex: 1, color: value ? 'var(--text-1)' : 'var(--text-3)', fontSize: 15, fontWeight: 500 }}>{value || placeholder}</span>
        <Ico.chevronDown size={18} stroke="var(--text-3)" />
      </div>
    </div>
  )
}

// ─── Textarea ──────────────────────────────────────────────────
interface TextareaProps { label?: string; value?: string; placeholder?: string; rows?: number }
export function Textarea({ label, value, placeholder, rows = 4 }: TextareaProps) {
  return (
    <div>
      {label && <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>{label}</div>}
      <div style={{ padding: '12px 14px', minHeight: rows * 22 + 24, borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: value ? 'var(--text-1)' : 'var(--text-3)', fontSize: 14, lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
        {value || placeholder}
      </div>
    </div>
  )
}

// ─── KPI tile ──────────────────────────────────────────────────
interface KPIProps { label: string; value: string; delta?: string; deltaTone?: 'success' | 'danger' | 'muted'; icon?: IcoFn; big?: boolean }
export function KPI({ label, value, delta, deltaTone = 'success', icon, big }: KPIProps) {
  const I = icon
  return (
    <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14, padding: '12px 14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 11, color: 'var(--text-3)', fontWeight: 600, letterSpacing: 0.4, textTransform: 'uppercase' }}>{label}</span>
        {I && <I size={15} stroke="var(--text-3)" />}
      </div>
      <div className="tnum" style={{ fontSize: big ? 24 : 19, fontWeight: 700, letterSpacing: -0.5, color: 'var(--text-1)', lineHeight: 1.1 }}>{value}</div>
      {delta && <div style={{ fontSize: 11, fontWeight: 600, marginTop: 4, color: deltaTone === 'success' ? '#5DD49E' : deltaTone === 'danger' ? '#F5847B' : 'var(--text-3)' }}>{delta}</div>}
    </div>
  )
}

// ─── ChannelChip ───────────────────────────────────────────────
interface ChannelChipProps { ch: string; size?: 'sm' | 'lg' }
export function ChannelChip({ ch, size = 'sm' }: ChannelChipProps) {
  const map: Record<string, { color: string }> = {
    'Loja':      { color: 'var(--gold-500)' },
    'WhatsApp':  { color: '#25D366' },
    'Instagram': { color: '#E1306C' },
    'Shopee':    { color: '#EE4D2D' },
  }
  const c = map[ch] || map['Loja']
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: size === 'lg' ? 12 : 10.5, fontWeight: 600, color: c.color, letterSpacing: 0.1 }}>
      <span style={{ width: 6, height: 6, borderRadius: 99, background: c.color }} />
      {ch}
    </span>
  )
}

// ─── PhotoPlaceholder ──────────────────────────────────────────
interface PhotoPlaceholderProps { size?: number | string; label?: string; radius?: number; style?: CSSProperties }
export function PhotoPlaceholder({ size = 56, label, radius = 10, style }: PhotoPlaceholderProps) {
  return (
    <div style={{
      width: size, height: size, borderRadius: radius, flexShrink: 0,
      background: 'repeating-linear-gradient(45deg, #1A1A1E 0 6px, #18181B 6px 12px)',
      border: '1px solid var(--line-2)', display: 'grid', placeItems: 'center',
      color: 'var(--text-4)', fontSize: 9, fontFamily: 'var(--font-mono)', ...style,
    }}>
      {label && <span style={{ padding: 2, textAlign: 'center', lineHeight: 1.1 }}>{label}</span>}
    </div>
  )
}

// ─── Section ───────────────────────────────────────────────────
interface SectionProps { title?: string; action?: ReactNode; children: ReactNode; top?: number }
export function Section({ title, action, children, top = 18 }: SectionProps) {
  return (
    <div style={{ marginTop: top }}>
      {(title || action) && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)', letterSpacing: 0.5, textTransform: 'uppercase' }}>{title}</div>
          {action}
        </div>
      )}
      {children}
    </div>
  )
}

// ─── MiniBars ──────────────────────────────────────────────────
interface MiniBarsProps { data: number[]; height?: number; color?: string; highlight?: number }
export function MiniBars({ data, height = 60, color = 'var(--gold-500)', highlight = -1 }: MiniBarsProps) {
  const max = Math.max(...data)
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 3, height, padding: '0 2px' }}>
      {data.map((v, i) => (
        <div key={i} style={{
          flex: 1, height: `${(v / max) * 100}%`, minHeight: 2, borderRadius: 3,
          background: i === highlight ? color : 'rgba(212,168,71,0.55)',
          opacity: highlight >= 0 && highlight !== i ? 0.4 : 1,
        }} />
      ))}
    </div>
  )
}

// ─── Tabs ──────────────────────────────────────────────────────
interface TabsProps { items: string[]; active: string; onChange?: (t: string) => void }
export function Tabs({ items, active, onChange }: TabsProps) {
  return (
    <div style={{ display: 'flex', gap: 4, padding: 4, background: 'var(--bg-2)', borderRadius: 12, border: '1px solid var(--line-1)' }}>
      {items.map(t => (
        <div key={t} onClick={() => onChange?.(t)} style={{
          flex: 1, textAlign: 'center', padding: '8px 6px', borderRadius: 9, fontSize: 12.5, fontWeight: 700, cursor: 'pointer',
          background: t === active ? 'var(--bg-4)' : 'transparent',
          color: t === active ? 'var(--text-1)' : 'var(--text-3)',
          border: t === active ? '1px solid var(--line-2)' : '1px solid transparent',
        }}>{t}</div>
      ))}
    </div>
  )
}

// ─── SearchBar ─────────────────────────────────────────────────
interface SearchBarProps { placeholder?: string; value?: string; onChange?: (v: string) => void; action?: ReactNode }
export function SearchBar({ placeholder = 'Buscar...', value, onChange, action }: SearchBarProps) {
  return (
    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
      <div style={{ flex: 1, height: 44, padding: '0 14px', display: 'flex', alignItems: 'center', gap: 10, background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
        <Ico.search size={18} stroke="var(--text-3)" />
        <input
          value={value ?? ''}
          onChange={e => onChange?.(e.target.value)}
          placeholder={placeholder}
          style={{ flex: 1, background: 'transparent', border: 0, outline: 0, color: 'var(--text-1)', fontSize: 14 }}
        />
      </div>
      {action}
    </div>
  )
}

// ─── Loading / Error states ────────────────────────────────────
export function LoadingBody() {
  return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{
        width: 32, height: 32, borderRadius: '50%',
        border: '3px solid var(--bg-3)', borderTopColor: 'var(--gold-500)',
        animation: 'spin 0.8s linear infinite',
      }} />
    </div>
  )
}

interface ErrorBodyProps { msg: string; onRetry: () => void }
export function ErrorBody({ msg, onRetry }: ErrorBodyProps) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, padding: 32 }}>
      <div style={{ fontSize: 13, color: '#F5847B', textAlign: 'center', lineHeight: 1.5 }}>{msg}</div>
      <button onClick={onRetry} style={{ padding: '8px 20px', borderRadius: 10, background: 'var(--bg-2)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 13, fontWeight: 600 }}>
        Tentar novamente
      </button>
    </div>
  )
}
