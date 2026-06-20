import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { LoadingBody, ErrorBody, Badge } from '../../components/UI'
import { PeriodSelect, SectionChart, CovBadge, type Period } from '../../components/Analytics'
import { fmtBRLshort } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { CategoryPerformance, CategoryCoverage } from '../../services/types'
import { useNav } from '../../nav'
import { Ico } from '../../components/Icons'

export default function Categorias() {
  const { navigate } = useNav()
  const [period, setPeriod] = useState<Period>('current_month')

  const { data: perf, loading, error, reload } = useData<CategoryPerformance[]>(
    () => api.getCategoryPerformance(period), period
  )
  const { data: coverage } = useData<CategoryCoverage[]>(api.getCategoryStockCoverage)

  const coverageMap = Object.fromEntries((coverage ?? []).map(c => [c.category_name, c.coverage_days]))

  const chartData = (perf ?? []).slice(0, 8).map(c => ({
    name: c.category_name.length > 14 ? c.category_name.slice(0, 13) + '…' : c.category_name,
    fullName: c.category_name,
    value: c.revenue,
  }))

  return (
    <>
      <AppBar title="Categorias" back />
      <PeriodSelect value={period} onChange={setPeriod} />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {/* Gráfico de receita */}
          <SectionChart title="Receita por categoria" loading={!perf} empty={chartData.length === 0}>
            <div style={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 8, left: 4, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11, fill: 'var(--text-2)' }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                    contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                    formatter={(v: number) => [fmtBRLshort(v), 'Receita']}
                    labelFormatter={(_: string, payload: any[]) => payload?.[0]?.payload?.fullName ?? ''}
                  />
                  <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                    {chartData.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? '#D4A847' : i === 1 ? '#B68B2E' : 'rgba(212,168,71,0.35)'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionChart>

          {/* Lista de categorias */}
          <SectionChart title="Desempenho detalhado" loading={!perf} empty={(perf?.length ?? 0) === 0}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
              {(perf ?? []).map((cat, i) => {
                const covDays = coverageMap[cat.category_name] ?? null
                return (
                  <div
                    key={cat.category_id}
                    onClick={() => navigate('an-category-detail', { categoryId: cat.category_id, categoryName: cat.category_name, period })}
                    style={{
                      padding: '14px 0', borderBottom: '1px solid var(--line-1)',
                      cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12,
                    }}
                  >
                    {/* Rank */}
                    <div style={{ width: 24, textAlign: 'center', fontSize: 12, fontWeight: 700, color: i < 3 ? 'var(--gold-400)' : 'var(--text-4)', flexShrink: 0 }}>
                      {i + 1}
                    </div>

                    {/* Dados */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-1)', marginBottom: 6 }}>{cat.category_name}</div>
                      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                        <Pill label="Receita" value={fmtBRLshort(cat.revenue)} color="var(--gold-300)" />
                        <Pill label="Margem" value={`${cat.margin_pct.toFixed(0)}%`} color={cat.margin_pct >= 30 ? '#5DD49E' : cat.margin_pct >= 15 ? '#F5BF7A' : '#F5847B'} />
                        <Pill label="Unid." value={String(cat.units)} color="var(--text-2)" />
                      </div>
                    </div>

                    {/* Cobertura + chevron */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        <span style={{ fontSize: 9.5, color: 'var(--text-4)', textTransform: 'uppercase', letterSpacing: 0.3 }}>Cob.</span>
                        <CovBadge days={covDays} />
                      </div>
                      <Ico.chevron size={14} stroke="var(--text-3)" />
                    </div>
                  </div>
                )
              })}
            </div>
          </SectionChart>
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}

function Pill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <span style={{ fontSize: 11.5, color: 'var(--text-3)' }}>
      {label}: <span style={{ color, fontWeight: 700 }} className="tnum">{value}</span>
    </span>
  )
}
