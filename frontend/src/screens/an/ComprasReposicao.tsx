import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { LoadingBody, ErrorBody, Btn, Card } from '../../components/UI'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { BuyingPattern, CategoryCoverage, CategorySizeStock } from '../../services/types'
import { useNav } from '../../nav'
import { Ico } from '../../components/Icons'

// ─── Classificação de grupo ──────────────────────────────────────────────────

type GroupId = 'repor' | 'momento' | 'renovar'

const GROUP_META: Record<GroupId, {
  label: string
  sub: string
  color: string
  bg: string
  bd: string
  icon: string
}> = {
  repor: {
    label: 'Repor agora',
    sub: 'Estoque crítico, tamanho zerado ou variedade baixa',
    color: '#F5847B',
    bg: 'rgba(232,88,79,0.06)',
    bd: 'rgba(232,88,79,0.22)',
    icon: '⚠',
  },
  momento: {
    label: 'Aproveitar o momento',
    sub: 'Vendendo bem — vale trazer mais enquanto há demanda',
    color: '#F5BF7A',
    bg: 'rgba(232,160,74,0.06)',
    bd: 'rgba(232,160,74,0.22)',
    icon: '⚡',
  },
  renovar: {
    label: 'Renovar o mix',
    sub: 'Tem estoque mas não está girando — traga novidades',
    color: '#7EB8F7',
    bg: 'rgba(100,160,240,0.06)',
    bd: 'rgba(100,160,240,0.22)',
    icon: '↺',
  },
}

type EnrichedPattern = BuyingPattern & {
  cov: number | null
  stockUnits: number
  group: GroupId
  signals: Signal[]
}

type Signal = 'zero_size' | 'low_coverage' | 'low_variety' | 'fast_sales' | 'slow_sales'

function classify(
  patterns: BuyingPattern[],
  covMap: Record<string, number | null>,
  stockUnitMap: Record<string, number>,
  sizeMap: Record<string, { size: string; stock: number }[]>,
): EnrichedPattern[] {
  if (patterns.length === 0) return []

  const velocities = patterns.map(p => p.monthly_sales_avg).filter(v => v > 0)
  const avgVelocity = velocities.length > 0
    ? velocities.reduce((a, b) => a + b, 0) / velocities.length
    : 0

  const result: EnrichedPattern[] = []

  for (const p of patterns) {
    const cov = covMap[p.category_name] ?? p.coverage_days
    const stockUnits = stockUnitMap[p.category_name] ?? 0
    const sizes = sizeMap[p.category_name] ?? []

    const isVirtuallyDead = p.monthly_sales_avg < 0.1
    const hasAmpleStock = cov != null && cov > 60
    const isFast = avgVelocity > 0 && p.monthly_sales_avg >= avgVelocity * 1.2
    const isSlow = avgVelocity > 0 && p.monthly_sales_avg < avgVelocity * 0.5

    // Categorias mortas: sem vendas há muito tempo + estoque folgado → Alertas, não aqui
    if (isVirtuallyDead && hasAmpleStock) continue
    // Sem vendas de jeito nenhum → não há base para sugestão
    if (p.monthly_sales_avg < 0.1) continue

    const hasZeroSize = sizes.some(s => s.stock === 0)
    const hasLowVariety = p.active_product_count > 0 && p.active_product_count <= 3
    const coverageCritical = cov != null && cov < 14

    // Sinalização descritiva para o card
    const signals: Signal[] = []
    if (hasZeroSize) signals.push('zero_size')
    if (coverageCritical) signals.push('low_coverage')
    if (hasLowVariety) signals.push('low_variety')
    if (isFast && !coverageCritical && !hasZeroSize) signals.push('fast_sales')
    if (isSlow) signals.push('slow_sales')

    // Classificação em grupo — ordem de prioridade
    let group: GroupId

    if (coverageCritical || hasZeroSize || hasLowVariety) {
      group = 'repor'
    } else if (isFast) {
      group = 'momento'
    } else if (isSlow && stockUnits > 0) {
      group = 'renovar'
    } else {
      // Estoque ok, velocidade normal, sem urgência → não exibir
      continue
    }

    result.push({ ...p, cov, stockUnits, group, signals })
  }

  return result
}

// ─── Componente principal ────────────────────────────────────────────────────

export default function ComprasReposicao() {
  const { navigate } = useNav()

  const { data: patterns, loading, error, reload } = useData<BuyingPattern[]>(
    () => api.getCategoryBuyingPatterns('last_3_months'),
    'compras-patterns'
  )
  const { data: sizeStock } = useData<CategorySizeStock[]>(
    api.getCategorySizeStock,
    'compras-size-stock'
  )
  const { data: coverage } = useData<CategoryCoverage[]>(
    api.getCategoryStockCoverage,
    'compras-coverage'
  )

  const covMap: Record<string, number | null> = {}
  for (const c of coverage ?? []) covMap[c.category_name] = c.coverage_days

  const stockUnitMap: Record<string, number> = {}
  for (const c of coverage ?? []) stockUnitMap[c.category_name] = c.stock_units

  const sizeMap: Record<string, { size: string; stock: number }[]> = {}
  for (const c of sizeStock ?? []) sizeMap[c.category_name] = c.sizes

  const enriched = classify(patterns ?? [], covMap, stockUnitMap, sizeMap)

  const groups: GroupId[] = ['repor', 'momento', 'renovar']

  return (
    <>
      <AppBar title="Compras & Reposição" back />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {enriched.length === 0 ? (
            <Card padding={24} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 22, marginBottom: 8 }}>✓</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#5DD49E', marginBottom: 4 }}>
                Tudo em ordem
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-3)' }}>
                Nenhuma categoria com necessidade de compra no momento.
              </div>
            </Card>
          ) : (
            groups.map(gid => {
              const items = enriched.filter(e => e.group === gid)
              if (items.length === 0) return null
              const meta = GROUP_META[gid]

              // Ordenação por grupo
              const sorted = [...items].sort((a, b) => {
                if (gid === 'repor') {
                  // Mais urgente (menor cobertura) primeiro; sem cobertura vai ao final
                  const da = a.cov ?? 9999
                  const db = b.cov ?? 9999
                  return da - db
                }
                if (gid === 'momento') return b.monthly_sales_avg - a.monthly_sales_avg
                // renovar: mais valor parado primeiro
                return b.stockUnits - a.stockUnits
              })

              return (
                <div key={gid} style={{ marginBottom: 20 }}>
                  {/* Cabeçalho do grupo */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                    <span style={{ fontSize: 16 }}>{meta.icon}</span>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: meta.color }}>{meta.label}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-4)', marginTop: 1 }}>{meta.sub}</div>
                    </div>
                    <div style={{
                      marginLeft: 'auto', fontSize: 11, fontWeight: 700,
                      color: meta.color, background: `${meta.color}18`,
                      borderRadius: 20, padding: '2px 9px',
                    }}>
                      {sorted.length}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {sorted.map(cat => (
                      <CategoryCard
                        key={cat.category_name}
                        cat={cat}
                        sizes={sizeMap[cat.category_name] ?? []}
                        meta={meta}
                        isRenovar={gid === 'renovar'}
                        onBuy={() => navigate('purchase-form')}
                      />
                    ))}
                  </div>
                </div>
              )
            })
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}

// ─── Card de categoria ───────────────────────────────────────────────────────

function CategoryCard({
  cat,
  sizes,
  meta,
  isRenovar,
  onBuy,
}: {
  cat: EnrichedPattern
  sizes: { size: string; stock: number }[]
  meta: typeof GROUP_META[GroupId]
  isRenovar: boolean
  onBuy: () => void
}) {
  const maxStock = sizes.length > 0 ? Math.max(...sizes.map(s => s.stock), 1) : 1
  const covText = cat.cov == null ? '—' : `${cat.cov}d`

  // Distribui lote sugerido pelo mix histórico
  const totalPct = cat.top_sizes.reduce((s, x) => s + x.pct, 0)
  const suggestedBySizes = cat.top_sizes.map(s => ({
    size: s.size,
    pct: s.pct,
    qty: Math.max(1, Math.round((s.pct / (totalPct || 100)) * cat.suggested_batch)),
  }))

  return (
    <div style={{
      background: meta.bg,
      border: `1px solid ${meta.bd}`,
      borderRadius: 16,
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{ padding: '13px 16px 11px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-1)' }}>
            {cat.category_name}
          </div>
          {/* Badges de sinal */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, justifyContent: 'flex-end' }}>
            {cat.signals.includes('zero_size') && <SignalBadge color="#F5847B" label="Tamanho zerado" />}
            {cat.signals.includes('low_coverage') && <SignalBadge color="#F5847B" label={`${covText} restantes`} />}
            {cat.signals.includes('low_variety') && <SignalBadge color="#7EB8F7" label={`${cat.active_product_count} produto${cat.active_product_count !== 1 ? 's' : ''}`} />}
            {cat.signals.includes('fast_sales') && <SignalBadge color="#F5BF7A" label="Alta demanda" />}
            {cat.signals.includes('slow_sales') && <SignalBadge color="#7EB8F7" label="Baixo giro" />}
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: 'flex', gap: 14, marginTop: 8, flexWrap: 'wrap' }}>
          <Stat label="Velocidade" value={`${cat.monthly_sales_avg.toFixed(0)} un/mês`} />
          <Stat
            label="Cobertura"
            value={covText}
            color={
              cat.cov == null ? 'var(--text-3)'
                : cat.cov < 7 ? '#F5847B'
                  : cat.cov < 21 ? '#F5BF7A'
                    : '#5DD49E'
            }
          />
          <Stat
            label="Margem"
            value={`${cat.avg_margin_pct.toFixed(0)}%`}
            color={
              cat.avg_margin_pct >= 30 ? '#5DD49E'
                : cat.avg_margin_pct >= 15 ? '#F5BF7A'
                  : 'var(--text-2)'
            }
          />
        </div>
      </div>

      {/* Grid de tamanhos — apenas se tiver dados de estoque por tamanho */}
      {sizes.length > 0 && (
        <div style={{ padding: '11px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-4)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 9 }}>
            Estoque atual por tamanho
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px 12px' }}>
            {sizes.map(s => {
              const pct = s.stock === 0 ? 0 : Math.max((s.stock / maxStock) * 100, 8)
              const barColor = s.stock === 0 ? '#F5847B' : s.stock <= 3 ? '#F5BF7A' : 'rgba(255,255,255,0.2)'
              const textColor = s.stock === 0 ? '#F5847B' : s.stock <= 3 ? '#F5BF7A' : 'var(--text-1)'
              return (
                <div key={s.size}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-2)' }}>{s.size}</span>
                    <span className="tnum" style={{ fontSize: 11, fontWeight: 700, color: textColor }}>
                      {s.stock === 0 ? 'ZERO' : `${s.stock} un`}
                    </span>
                  </div>
                  <div style={{ height: 4, borderRadius: 99, background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${pct}%`, borderRadius: 99, background: barColor }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Sugestão de compra — não mostra para "renovar" (o produto novo não está no histórico) */}
      {!isRenovar && suggestedBySizes.length > 0 && (
        <div style={{ padding: '11px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-4)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
              Sugestão de compra
            </div>
            <span className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--gold-300)' }}>
              {cat.suggested_batch} un
            </span>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            {suggestedBySizes.map(s => (
              <div key={s.size} style={{
                padding: '3px 9px', borderRadius: 7,
                background: 'rgba(212,168,71,0.08)', border: '1px solid rgba(212,168,71,0.2)',
                display: 'flex', gap: 4, alignItems: 'center',
              }}>
                <span style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--gold-400)' }}>{s.size}</span>
                <span className="tnum" style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--text-1)' }}>{s.qty}</span>
                <span style={{ fontSize: 10, color: 'var(--text-4)' }}>({s.pct}%)</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Aviso especial para renovar */}
      {isRenovar && (
        <div style={{ padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <div style={{ fontSize: 12, color: '#7EB8F7', lineHeight: 1.4 }}>
            Não compre mais do mesmo — traga novas estampas ou modelos para movimentar esta categoria.
          </div>
        </div>
      )}

      {/* CTA */}
      <div style={{ padding: '10px 16px 13px' }}>
        <Btn kind="ghost" size="sm" icon={Ico.truck} full onClick={onBuy}>
          {isRenovar ? 'Registrar entrada de novidade' : 'Registrar entrada desta categoria'}
        </Btn>
      </div>
    </div>
  )
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function SignalBadge({ color, label }: { color: string; label: string }) {
  return (
    <div style={{
      fontSize: 10, fontWeight: 700, padding: '2px 7px', borderRadius: 6,
      background: `${color}18`, border: `1px solid ${color}40`, color,
    }}>
      {label}
    </div>
  )
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <span style={{ fontSize: 12 }}>
      <span style={{ color: 'var(--text-4)', fontWeight: 600 }}>{label}: </span>
      <span className="tnum" style={{ color: color ?? 'var(--text-1)', fontWeight: 700 }}>{value}</span>
    </span>
  )
}
