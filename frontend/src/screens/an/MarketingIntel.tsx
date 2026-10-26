import { useState } from 'react'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { LoadingBody, ErrorBody, Badge } from '../../components/UI'
import { MetricInfo } from '../../components/Analytics'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { MarketingIntelligence, MarketingVariant } from '../../services/types'
import { Ico } from '../../components/Icons'

interface GroupConfig {
  key: keyof MarketingIntelligence
  label: string
  sub: string
  badgeTone: 'success' | 'gold' | 'warn' | 'danger' | 'neutral'
  accentColor: string
  bgColor: string
  bdColor: string
  icon: (p: any) => JSX.Element
}

const GROUPS: GroupConfig[] = [
  {
    key: 'post_candidates',
    label: 'Postar agora',
    sub: 'Alta saída + estoque disponível',
    badgeTone: 'success',
    accentColor: '#5DD49E',
    bgColor: 'rgba(63,184,124,0.06)',
    bdColor: 'rgba(63,184,124,0.2)',
    icon: Ico.trend,
  },
  {
    key: 'highlight_candidates',
    label: 'Destacar',
    sub: 'Alta margem + estoque disponível',
    badgeTone: 'gold',
    accentColor: 'var(--gold-300)',
    bgColor: 'rgba(212,168,71,0.06)',
    bdColor: 'rgba(212,168,71,0.2)',
    icon: Ico.sparkle,
  },
  {
    key: 'promotion_candidates',
    label: 'Promover / queimar',
    sub: 'Sem saída — precisa girar o estoque',
    badgeTone: 'warn',
    accentColor: '#F5BF7A',
    bgColor: 'rgba(232,160,74,0.06)',
    bdColor: 'rgba(232,160,74,0.2)',
    icon: Ico.tag,
  },
]

export default function MarketingIntel() {
  const { data, loading, error, reload } = useData<MarketingIntelligence>(api.getMarketingIntelligence)

  return (
    <>
      <AppBar title="Análise de Marketing" back action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <MetricInfo
            what="Classifica automaticamente todos os produtos em 5 grupos baseado em velocidade de venda, margem e estoque atual."
            good="Use esta tela para decidir o que postar, promover ou repor a cada semana."
            action="Atualize o estoque no sistema para manter as classificações precisas."
          />
        </div>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : data ? (
        <ScreenBody>
          <div style={{ marginBottom: 14, fontSize: 13, color: 'var(--text-3)', lineHeight: 1.5 }}>
            Classificação automática baseada em velocidade de saída, margem e estoque atual. Atualizada a cada acesso.
          </div>

          {GROUPS.map(g => {
            const items = data[g.key] as MarketingVariant[]
            return (
              <Group key={g.key} config={g} items={items} />
            )
          })}
        </ScreenBody>
      ) : null}
      <BottomNav active="an" />
    </>
  )
}

function Group({ config: g, items }: { config: GroupConfig; items: MarketingVariant[] }) {
  const [open, setOpen] = useState(items.length > 0 && g.key === 'post_candidates')
  const I = g.icon

  return (
    <div style={{ marginBottom: 10, borderRadius: 14, background: g.bgColor, border: `1px solid ${g.bdColor}`, overflow: 'hidden' }}>
      {/* Header */}
      <div onClick={() => setOpen(v => !v)} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', cursor: 'pointer' }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--bg-2)', border: `1px solid ${g.bdColor}`, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
          <I size={18} stroke={g.accentColor} />
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ marginBottom: 2 }}>
            <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-1)' }}>{g.label}</span>
          </div>
          <span style={{ fontSize: 12, color: 'var(--text-3)' }}>{g.sub}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Badge tone={g.badgeTone}>{items.length}</Badge>
          <Ico.chevronDown size={14} stroke="var(--text-3)" />
        </div>
      </div>

      {/* Items */}
      {open && items.length > 0 && (
        <div style={{ padding: '0 16px 14px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {items.map((item, i) => (
            <VariantCard key={i} item={item} accentColor={g.accentColor} />
          ))}
        </div>
      )}

      {open && items.length === 0 && (
        <div style={{ padding: '0 16px 14px', fontSize: 13, color: 'var(--text-4)', fontStyle: 'italic' }}>
          Nenhum produto nesta categoria no momento.
        </div>
      )}
    </div>
  )
}

function VariantCard({ item, accentColor }: { item: MarketingVariant; accentColor: string }) {
  return (
    <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, padding: '12px 14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 6 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)', marginBottom: 2 }}>
            {item.product_name}{item.size ? ` — ${item.size}` : ''}
          </div>
          <div style={{ fontSize: 11, color: 'var(--text-4)', fontFamily: 'var(--font-mono)' }}>{item.sku}</div>
        </div>
      </div>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 6 }}>
        <Stat label="Estoque" value={`${item.stock} un`} />
        <Stat label="Margem" value={`${item.margin_pct.toFixed(0)}%`} color={item.margin_pct >= 35 ? '#5DD49E' : item.margin_pct >= 20 ? '#F5BF7A' : 'var(--text-2)'} />
        <Stat label="Vendas/30d" value={`${item.sold_30d}`} color={item.sold_30d >= 3 ? accentColor : 'var(--text-3)'} />
      </div>
      {item.reason && (
        <div style={{ marginTop: 8, fontSize: 11.5, color: 'var(--text-3)', background: 'var(--bg-2)', borderRadius: 8, padding: '6px 10px', lineHeight: 1.4 }}>
          {item.reason}
        </div>
      )}
    </div>
  )
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <span style={{ fontSize: 11.5 }}>
      <span style={{ color: 'var(--text-4)', fontWeight: 600 }}>{label}:</span>{' '}
      <span className="tnum" style={{ color: color ?? 'var(--text-1)', fontWeight: 700 }}>{value}</span>
    </span>
  )
}
