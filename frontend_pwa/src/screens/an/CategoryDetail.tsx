import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { LoadingBody, Card, Btn } from '../../components/UI'
import { PeriodSelect, MetricInfo, SectionChart, CovBadge, type Period } from '../../components/Analytics'
import { fmtBRLshort, fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type {
  CategoryPerformance, CategorySizeDistribution,
  BuyingPattern, TopProduct,
} from '../../services/types'
import { useNav } from '../../nav'
import { Ico } from '../../components/Icons'

export default function CategoryDetail() {
  const { params, navigate } = useNav()
  const categoryName = params.categoryName as string
  const categoryId = params.categoryId as string
  const [period, setPeriod] = useState<Period>((params.period as Period) ?? 'current_month')

  const key = `${categoryId}::${period}`

  const { data: allPerf } = useData<CategoryPerformance[]>(
    () => api.getCategoryPerformance(period), key
  )
  const { data: allSizes } = useData<CategorySizeDistribution[]>(
    () => api.getCategorySizeDistribution(period), key
  )
  const { data: allPatterns } = useData<BuyingPattern[]>(
    () => api.getCategoryBuyingPatterns(period), key
  )
  const { data: allProducts } = useData<TopProduct[]>(
    () => api.getTopProducts(period), key
  )

  const catPerf = allPerf?.find(c => c.category_id === categoryId || c.category_name === categoryName)
  const catSizes = allSizes?.find(c => c.category_name === categoryName)
  const catPattern = allPatterns?.find(c => c.category_name === categoryName)

  // Top products filtered by category name match in their product name (best effort without category_id on products)
  // We use category pattern context as the source of truth for top products within this category
  // Products endpoint doesn't filter by category, so we show category-level top sizes + pattern data
  const sizeChartData = (catSizes?.sizes ?? []).map(s => ({
    size: s.size ?? '—',
    qty: s.qty,
    pct: s.pct,
  }))

  const loading = !allPerf && !allSizes && !allPatterns

  return (
    <>
      <AppBar title={categoryName} back />
      <PeriodSelect value={period} onChange={setPeriod} />

      {loading ? <LoadingBody /> : (
        <ScreenBody>
          {/* KPIs da categoria */}
          {catPerf ? (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 16 }}>
              <KPICard label="Receita" value={fmtBRLshort(catPerf.revenue)} />
              <KPICard
                label="Margem"
                value={`${catPerf.margin_pct.toFixed(1)}%`}
                accent={catPerf.margin_pct >= 30 ? '#5DD49E' : catPerf.margin_pct >= 15 ? '#F5BF7A' : '#F5847B'}
              />
              <KPICard label="Unidades" value={`${catPerf.units}`} sub="vendidas" />
              <KPICard
                label="Velocidade"
                value={`${catPerf.daily_velocity.toFixed(1)} /dia`}
                info={{ what: 'Média de unidades vendidas por dia desta categoria.', good: 'Usar para calcular cobertura de estoque: estoque ÷ velocidade = dias.', action: 'Se a velocidade caiu vs. período anterior, pode haver problema de mix ou exposição.' }}
              />
            </div>
          ) : (
            <div style={{ padding: '16px 0', color: 'var(--text-3)', fontSize: 13 }}>Sem vendas desta categoria no período.</div>
          )}

          {/* Distribuição por tamanho */}
          <SectionChart
            title="Distribuição por tamanho"
            empty={sizeChartData.length === 0}
            emptyMsg="Sem vendas por tamanho no período"
          >
            <div style={{ height: 180 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sizeChartData} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                  <XAxis dataKey="size" tick={{ fontSize: 12, fill: 'var(--text-2)' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: 'var(--text-3)' }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                    contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number, _: string, props: any) => [`${v} un (${props.payload?.pct ?? 0}%)`, 'Vendas']}
                  />
                  <Bar dataKey="qty" radius={[6, 6, 0, 0]}>
                    {sizeChartData.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? '#D4A847' : i === 1 ? '#B68B2E' : i === 2 ? 'rgba(212,168,71,0.5)' : 'rgba(212,168,71,0.25)'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            {/* Tabela de tamanhos */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 }}>
              {sizeChartData.map(s => (
                <div key={s.size} style={{ padding: '5px 10px', borderRadius: 8, background: 'var(--bg-2)', border: '1px solid var(--line-1)', display: 'flex', gap: 6, alignItems: 'center' }}>
                  <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-400)', fontFamily: 'var(--font-mono)' }}>{s.size}</span>
                  <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{s.qty} un</span>
                  <span style={{ fontSize: 11, color: 'var(--text-2)', fontWeight: 600 }}>{s.pct}%</span>
                </div>
              ))}
            </div>
          </SectionChart>

          {/* Sugestão de compra */}
          {catPattern && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 12 }}>
                <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)', letterSpacing: 0.1, textTransform: 'uppercase' }}>Sugestão de compra</span>
              </div>
              <Card accent padding={16}>
                <div style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
                  <StatBox label="Venda/mês" value={`${catPattern.monthly_sales_avg.toFixed(0)} un`} />
                  <StatBox label="Margem méd." value={`${catPattern.avg_margin_pct.toFixed(0)}%`} accent={catPattern.avg_margin_pct >= 30 ? '#5DD49E' : '#F5BF7A'} />
                  <StatBox label="Cobertura" value={<CovBadge days={catPattern.coverage_days} />} />
                  <StatBox label="Lote sugeri." value={`${catPattern.suggested_batch} un`} accent="var(--gold-300)" />
                </div>

                {catPattern.top_sizes.length > 0 && (
                  <>
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: 0.4, marginBottom: 8 }}>Mix recomendado</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {catPattern.top_sizes.map(s => (
                        <div key={s.size} style={{ padding: '4px 10px', borderRadius: 8, background: 'rgba(212,168,71,0.1)', border: '1px solid rgba(212,168,71,0.25)', display: 'flex', gap: 5 }}>
                          <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-400)' }}>{s.size ?? '—'}</span>
                          <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{s.pct}%</span>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                <div style={{ marginTop: 14 }}>
                  <Btn full kind="ghost" icon={Ico.truck} onClick={() => navigate('purchase-form')}>
                    Nova entrada de mercadoria
                  </Btn>
                </div>
              </Card>
            </div>
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}

function KPICard({ label, value, sub, accent, info }: {
  label: string; value: string | JSX.Element; sub?: string; accent?: string
  info?: { what: string; good: string; action: string }
}) {
  return (
    <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14, padding: '12px 14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: 6 }}>
        <span style={{ fontSize: 11, color: 'var(--text-3)', fontWeight: 600, letterSpacing: 0.4, textTransform: 'uppercase' }}>{label}</span>
        {info && <MetricInfo {...info} />}
      </div>
      <div className="tnum" style={{ fontSize: 20, fontWeight: 700, letterSpacing: -0.5, color: accent ?? 'var(--text-1)', lineHeight: 1.1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 3 }}>{sub}</div>}
    </div>
  )
}

function StatBox({ label, value, accent }: { label: string; value: string | JSX.Element; accent?: string }) {
  return (
    <div style={{ flex: 1, textAlign: 'center' }}>
      <div style={{ fontSize: 9.5, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.3, marginBottom: 4 }}>{label}</div>
      <div className="tnum" style={{ fontSize: 15, fontWeight: 700, color: accent ?? 'var(--text-1)' }}>{value}</div>
    </div>
  )
}
