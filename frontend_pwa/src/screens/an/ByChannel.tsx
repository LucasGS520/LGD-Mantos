import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { Card, Section, ChannelChip, LoadingBody, ErrorBody } from '../../components/UI'
import { fmtBRL, fmtNum } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { ByChannelItem } from '../../services/types'

const COLORS: Record<string, string> = {
  Loja: '#D4A847', WhatsApp: '#25D366', Instagram: '#E1306C', Shopee: '#EE4D2D',
}

function polar(pct: number, r: number): [number, number] {
  const a = (pct / 100) * 2 * Math.PI - Math.PI / 2
  return [80 + r * Math.cos(a), 80 + r * Math.sin(a)]
}
function arcPath(start: number, end: number): string {
  const [x1, y1] = polar(start, 60)
  const [x2, y2] = polar(end, 60)
  const large = (end - start) > 50 ? 1 : 0
  return `M 80 80 L ${x1} ${y1} A 60 60 0 ${large} 1 ${x2} ${y2} Z`
}

export default function ByChannel() {
  const { data, loading, error, reload } = useData<ByChannelItem[]>(() => api.get('/analytics/by-channel?days=30'))

  const totalCount = (data ?? []).reduce((s, c) => s + c.count, 0)
  const totalRevenue = (data ?? []).reduce((s, c) => s + c.total, 0)

  let cum = 0
  const arcs = (data ?? []).map(c => {
    const share = totalCount > 0 ? (c.count / totalCount) * 100 : 0
    const start = cum; cum += share
    return { ...c, share, start, end: cum, color: COLORS[c.channel] ?? '#888' }
  })

  return (
    <>
      <AppBar back title="Vendas por canal" subtitle="Últimos 30 dias" />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <Card padding={18} style={{ marginTop: 4 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 18 }}>
              {arcs.length > 0 ? (
                <svg width="160" height="160" viewBox="0 0 160 160">
                  {arcs.map((a, i) => <path key={i} d={arcPath(a.start, a.end)} fill={a.color} />)}
                  <circle cx="80" cy="80" r="38" fill="var(--bg-1)" />
                  <text x="80" y="76" textAnchor="middle" fill="var(--text-3)" fontSize="9" fontFamily="Inter">TOTAL</text>
                  <text x="80" y="94" textAnchor="middle" fill="var(--text-1)" fontSize="16" fontWeight="800" fontFamily="Inter">{fmtNum(totalCount)}</text>
                </svg>
              ) : (
                <div style={{ width: 160, height: 160, borderRadius: '50%', background: 'var(--bg-2)', display: 'grid', placeItems: 'center' }}>
                  <span style={{ fontSize: 12, color: 'var(--text-3)' }}>sem dados</span>
                </div>
              )}
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
                {arcs.map(a => (
                  <div key={a.channel} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ width: 8, height: 8, borderRadius: 99, background: a.color }} />
                    <span style={{ flex: 1, fontSize: 12.5, color: 'var(--text-2)', fontWeight: 600 }}>{a.channel}</span>
                    <span className="tnum" style={{ fontSize: 12.5, fontWeight: 700 }}>{Math.round(a.share)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {arcs.length > 0 && (
            <Section title="Tabela detalhada" top={18}>
              <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, overflow: 'hidden' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 60px 1fr', padding: '10px 14px', background: 'var(--bg-2)', fontSize: 10, color: 'var(--text-3)', fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase' }}>
                  <span>Canal</span><span>Vendas</span><span style={{ textAlign: 'right' }}>Receita</span>
                </div>
                {arcs.map(c => (
                  <div key={c.channel} style={{ display: 'grid', gridTemplateColumns: '1.4fr 60px 1fr', padding: '12px 14px', alignItems: 'center', borderTop: '1px solid var(--line-1)', fontSize: 13 }}>
                    <ChannelChip ch={c.channel} size="lg" />
                    <span className="tnum">{c.count}</span>
                    <span className="tnum" style={{ textAlign: 'right', fontWeight: 700 }}>{fmtBRL(c.total)}</span>
                  </div>
                ))}
                <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 60px 1fr', padding: '12px 14px', borderTop: '2px solid var(--line-2)', fontSize: 13 }}>
                  <span style={{ fontWeight: 700 }}>Total</span>
                  <span className="tnum" style={{ fontWeight: 700 }}>{fmtNum(totalCount)}</span>
                  <span className="tnum" style={{ textAlign: 'right', fontWeight: 800, color: 'var(--gold-300)' }}>{fmtBRL(totalRevenue)}</span>
                </div>
              </div>
            </Section>
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}
