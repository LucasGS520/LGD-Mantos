import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts'
import { Ico } from '../../components/Icons'
import { Badge, Card, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { MetricInfo, SectionChart } from '../../components/Analytics'
import { fmtBRL, fmtBRLshort } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { DRE as DREData } from '../../services/types'

const MONTHS = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

const PIE_COLORS = ['#D4A847','#B68B2E','#5EA8E0','#3FB87C','#E8584F','#E8A04A','#9B59B6','#888888']

interface RowProps { label: string; val: number; accent?: boolean; bold?: boolean; neg?: boolean; info?: { what: string; good: string; action: string } }
function Row({ label, val, accent, bold, neg, info }: RowProps) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', borderTop: '1px solid var(--line-1)', ...(accent ? { background: 'rgba(212,168,71,0.05)' } : {}) }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ fontSize: bold ? 14 : 13, fontWeight: bold ? 800 : 600, color: bold ? 'var(--text-1)' : 'var(--text-2)' }}>{label}</span>
        {info && <MetricInfo {...info} />}
      </div>
      <span className="tnum" style={{ fontSize: bold ? 17 : 14, fontWeight: bold ? 800 : 700, color: accent ? 'var(--gold-300)' : neg ? '#F5847B' : 'var(--text-1)' }}>
        {neg ? '−' : ''}{fmtBRL(Math.abs(val))}
      </span>
    </div>
  )
}

export default function DRE() {
  const now = new Date()
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [year, setYear] = useState(now.getFullYear())

  const { data, loading, error, reload } = useData<DREData>(
    () => api.getDRE(month, year),
    `${month}-${year}`,
  )

  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(y => y - 1) }
    else setMonth(m => m - 1)
  }
  const nextMonth = () => {
    if (month === 12) { setMonth(1); setYear(y => y + 1) }
    else setMonth(m => m + 1)
  }

  const pLabel = `${MONTHS[month - 1]}/${String(year).slice(-2)}`

  // Break-even progress
  const beProgress = data?.break_even && data.break_even > 0
    ? Math.min((data.revenue / data.break_even) * 100, 100)
    : null

  // Evolution chart
  const evoData = (data?.evolution ?? []).map(e => ({
    period: e.period,
    receita: e.revenue,
    lucro: e.net_profit,
  }))

  // Expense pie
  const expData = (data?.expenses_by_category ?? []).filter(e => e.total > 0)

  return (
    <>
      <AppBar back title="DRE" subtitle="Demonstrativo de resultado" action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <button onClick={prevMonth} style={{ width: 34, height: 34, borderRadius: 10, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center', cursor: 'pointer' }}>
            <Ico.back size={15} stroke="var(--text-2)" />
          </button>
          <div style={{ height: 34, padding: '0 10px', borderRadius: 10, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'flex', alignItems: 'center', fontSize: 12, fontWeight: 700, minWidth: 68, justifyContent: 'center', color: 'var(--text-1)' }}>
            {pLabel}
          </div>
          <button onClick={nextMonth} style={{ width: 34, height: 34, borderRadius: 10, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center', cursor: 'pointer' }}>
            <Ico.chevron size={15} stroke="var(--text-2)" />
          </button>
        </div>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : data ? (
        <ScreenBody>
          {/* Hero */}
          <div style={{ padding: 18, borderRadius: 18, marginBottom: 16, background: data.net_profit >= 0 ? 'linear-gradient(140deg, rgba(63,184,124,0.18), rgba(63,184,124,0.04) 60%)' : 'linear-gradient(140deg, rgba(232,88,79,0.18), rgba(232,88,79,0.04) 60%)', border: `1px solid ${data.net_profit >= 0 ? 'rgba(63,184,124,0.25)' : 'rgba(232,88,79,0.25)'}` }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: data.net_profit >= 0 ? '#5DD49E' : '#F5847B', textTransform: 'uppercase', letterSpacing: 1.5 }}>Lucro líquido</div>
            <div className="tnum" style={{ fontSize: 36, fontWeight: 800, letterSpacing: -1, marginTop: 4, color: 'var(--text-1)' }}>{fmtBRL(data.net_profit)}</div>
            <div style={{ display: 'flex', gap: 12, marginTop: 8, flexWrap: 'wrap' }}>
              <Badge tone={data.margin_pct >= 20 ? 'success' : data.margin_pct >= 0 ? 'warn' : 'danger'} size="lg" dot>
                Margem {data.margin_pct.toFixed(1)}%
              </Badge>
              <Badge tone="info" size="lg">Margem bruta {data.gross_margin_pct?.toFixed(1) ?? '—'}%</Badge>
            </div>
          </div>

          {/* Demonstrativo */}
          <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14, overflow: 'hidden', marginBottom: 16 }}>
            <div style={{ padding: '12px 16px', fontSize: 11, color: 'var(--text-3)', fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase' }}>Demonstrativo</div>
            <Row label="Receita bruta" val={data.revenue} />
            <Row label="(−) CMV — Custo das mercadorias" val={data.cogs} neg
              info={{ what: 'Custo total dos produtos vendidos (preço de custo × quantidade).', good: 'Deve ser entre 40–65% da receita para varejo de moda.', action: 'Se o CMV está muito alto, negocie preços de compra com fornecedores.' }} />
            <Row label="= Lucro bruto" val={data.gross_profit} bold
              info={{ what: 'Receita menos custo dos produtos. Ainda não desconta despesas.', good: 'Margem bruta acima de 35% indica bom poder de precificação.', action: 'Se a margem bruta está baixa, revise os preços de venda.' }} />
            <Row label="(−) Despesas operacionais" val={data.expenses} neg />
            <Row label="= Lucro líquido" val={data.net_profit} bold accent />
          </div>

          {/* Break-even */}
          {data.break_even && data.break_even > 0 && (
            <Card padding={14} style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-2)', textTransform: 'uppercase', letterSpacing: 0.4 }}>Ponto de equilíbrio</span>
                <MetricInfo
                  what="Quanto você precisa vender para cobrir todos os custos (CMV + despesas) sem lucro nem prejuízo."
                  good="Quanto mais cedo no mês você atingir o break-even, maior será o lucro."
                  action="Se a receita está abaixo do break-even, você ainda está no prejuízo neste mês."
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 6 }}>
                <span style={{ color: 'var(--text-3)' }}>Receita atual: <strong style={{ color: 'var(--text-1)' }} className="tnum">{fmtBRLshort(data.revenue)}</strong></span>
                <span style={{ color: 'var(--text-3)' }}>Meta: <strong style={{ color: 'var(--gold-300)' }} className="tnum">{fmtBRLshort(data.break_even)}</strong></span>
              </div>
              <div style={{ height: 8, borderRadius: 99, background: 'var(--bg-3)', overflow: 'hidden' }}>
                <div style={{
                  height: '100%',
                  width: `${beProgress ?? 0}%`,
                  background: (beProgress ?? 0) >= 100 ? '#5DD49E' : (beProgress ?? 0) >= 70 ? '#F5BF7A' : '#F5847B',
                  borderRadius: 99, transition: 'width 0.5s ease',
                }} />
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 6 }}>
                {(beProgress ?? 0) >= 100
                  ? '✓ Break-even atingido neste mês'
                  : `${(beProgress ?? 0).toFixed(0)}% do caminho até o break-even`}
              </div>
            </Card>
          )}

          {/* Evolução 6 meses */}
          {evoData.length > 1 && (
            <SectionChart title="Evolução 6 meses">
              <div style={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={evoData} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
                    <XAxis dataKey="period" tick={{ fontSize: 10, fill: 'var(--text-3)' }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 10, fill: 'var(--text-3)' }} axisLine={false} tickLine={false} tickFormatter={(v: number) => fmtBRLshort(v)} />
                    <Tooltip
                      cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                      contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                      formatter={(v: number, name: string) => [fmtBRLshort(v), name === 'receita' ? 'Receita' : 'Lucro']}
                    />
                    <Legend formatter={(v: string) => v === 'receita' ? 'Receita' : 'Lucro'} wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
                    <Bar dataKey="receita" fill="rgba(212,168,71,0.4)" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="lucro" fill="#D4A847" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </SectionChart>
          )}

          {/* Despesas por categoria */}
          {expData.length > 0 && (
            <SectionChart title="Despesas por categoria">
              <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                <div style={{ width: 140, height: 140, flexShrink: 0 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={expData} dataKey="total" nameKey="category" cx="50%" cy="50%" outerRadius={65} strokeWidth={0}>
                        {expData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                      </Pie>
                      <Tooltip
                        contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                        formatter={(v: number) => [fmtBRLshort(v), '']}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {expData.map((e, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 2, background: PIE_COLORS[i % PIE_COLORS.length], flexShrink: 0 }} />
                      <span style={{ flex: 1, fontSize: 12, color: 'var(--text-2)' }}>{e.category}</span>
                      <span className="tnum" style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-1)' }}>{fmtBRLshort(e.total)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </SectionChart>
          )}
        </ScreenBody>
      ) : null}
    </>
  )
}
