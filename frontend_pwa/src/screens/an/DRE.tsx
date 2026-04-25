import { useState } from 'react'
import { Ico } from '../../components/Icons'
import { Badge, Card, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { DRE as DREData } from '../../services/types'

interface RowProps { label: string; val: number; accent?: boolean; bold?: boolean; neg?: boolean }
function Row({ label, val, accent, bold, neg }: RowProps) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '14px 16px', borderTop: '1px solid var(--line-1)', ...(accent ? { background: 'rgba(212,168,71,0.05)' } : {}) }}>
      <span style={{ fontSize: bold ? 14 : 13, fontWeight: bold ? 800 : 600, color: bold ? 'var(--text-1)' : 'var(--text-2)' }}>{label}</span>
      <span className="tnum" style={{ fontSize: bold ? 17 : 14, fontWeight: bold ? 800 : 700, color: accent ? 'var(--gold-300)' : neg ? '#F5847B' : 'var(--text-1)' }}>
        {neg ? '−' : ''}{fmtBRL(Math.abs(val))}
      </span>
    </div>
  )
}

const MONTHS = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']

export default function DRE() {
  const now = new Date()
  const [month, setMonth] = useState(now.getMonth() + 1)
  const [year, setYear] = useState(now.getFullYear())

  const { data, loading, error, reload } = useData<DREData>(
    () => api.get(`/analytics/finance/dre?month=${month}&year=${year}`),
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

  const periodLabel = `${MONTHS[month - 1]}/${String(year).slice(-2)}`

  return (
    <>
      <AppBar back title="DRE" subtitle="Demonstrativo de resultado" action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <div onClick={prevMonth} style={{ cursor: 'pointer', padding: 6 }}>
            <Ico.back size={16} stroke="var(--text-3)" />
          </div>
          <div style={{ height: 38, padding: '0 12px', borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'flex', alignItems: 'center', fontSize: 12, fontWeight: 700, minWidth: 70, justifyContent: 'center' }}>
            {periodLabel}
          </div>
          <div onClick={nextMonth} style={{ cursor: 'pointer', padding: 6 }}>
            <Ico.chevron size={16} stroke="var(--text-3)" />
          </div>
        </div>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : data ? (
        <ScreenBody>
          <div style={{ padding: 18, borderRadius: 18, marginTop: 4, background: 'linear-gradient(140deg, rgba(63,184,124,0.18), rgba(63,184,124,0.04) 60%)', border: '1px solid rgba(63,184,124,0.25)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#5DD49E', textTransform: 'uppercase', letterSpacing: 1.5 }}>Lucro líquido</div>
            <div className="tnum" style={{ fontSize: 36, fontWeight: 800, letterSpacing: -1, marginTop: 4 }}>{fmtBRL(data.net_profit)}</div>
            <div style={{ display: 'flex', gap: 12, marginTop: 8, alignItems: 'center' }}>
              <Badge tone="success" size="lg" dot>Margem {data.margin_pct.toFixed(1)}%</Badge>
            </div>
          </div>

          <div style={{ marginTop: 16, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14, overflow: 'hidden' }}>
            <div style={{ padding: '12px 16px', fontSize: 11, color: 'var(--text-3)', fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase' }}>Demonstrativo</div>
            <Row label="Receita bruta"               val={data.revenue}      />
            <Row label="(−) CMV — Custo das mercadorias" val={data.cogs}     neg />
            <Row label="= Lucro bruto"               val={data.gross_profit} bold />
            <Row label="(−) Despesas operacionais"   val={data.expenses}     neg />
            <Row label="= Lucro líquido"              val={data.net_profit}   bold accent />
          </div>

          <Section title="Resumo" top={18}>
            <Card padding={14}>
              {[
                { l: 'Receita',    v: data.revenue,      c: 'var(--text-1)' },
                { l: 'CMV',        v: data.cogs,          c: '#F5847B'       },
                { l: 'Despesas',   v: data.expenses,      c: '#F5BF7A'       },
                { l: 'Lucro liq.', v: data.net_profit,    c: '#5DD49E'       },
              ].map((r, i) => (
                <div key={i} style={{ marginBottom: i < 3 ? 10 : 0 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                    <span style={{ color: 'var(--text-2)', fontWeight: 600 }}>{r.l}</span>
                    <span className="tnum" style={{ color: 'var(--text-3)' }}>{fmtBRL(r.v)}</span>
                  </div>
                  <div style={{ height: 6, borderRadius: 99, background: 'var(--bg-3)', overflow: 'hidden' }}>
                    <div style={{ width: `${data.revenue > 0 ? Math.min((r.v / data.revenue) * 100, 100) : 0}%`, height: '100%', background: r.c, opacity: 0.7 }} />
                  </div>
                </div>
              ))}
            </Card>
          </Section>
        </ScreenBody>
      ) : null}
    </>
  )
}
