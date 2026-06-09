import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { Card, Section, ChannelChip, LoadingBody, ErrorBody } from '../../components/UI'
import { fmtBRL, fmtNum } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { ByChannelItem, SaleChannel } from '../../services/types'

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

type ViabilityLevel = 'red' | 'amber' | 'green'
interface Viability { label: string; level: ViabilityLevel }

function getViability(feePct: number, goal: number | null, total: number): Viability {
  if (feePct > 20) return { label: 'Alto custo', level: 'red' }
  if (feePct > 10) return { label: 'Custo médio', level: 'amber' }
  if (goal && goal > 0) {
    const pct = total / goal
    if (pct < 0.5) return { label: 'Abaixo da meta', level: 'red' }
    if (pct >= 0.8) return { label: 'No ritmo', level: 'green' }
    return { label: 'Abaixo da meta', level: 'amber' }
  }
  return { label: 'Eficiente', level: 'green' }
}

const LEVEL_COLOR: Record<ViabilityLevel, string> = {
  green: '#5DD49E',
  amber: '#F5BF7A',
  red:   '#F5847B',
}
const LEVEL_BG: Record<ViabilityLevel, string> = {
  green: 'rgba(93,212,158,0.12)',
  amber: 'rgba(245,191,122,0.12)',
  red:   'rgba(245,132,123,0.12)',
}

export default function ByChannel() {
  const { data, loading, error, reload } = useData<[ByChannelItem[], SaleChannel[]]>(() =>
    Promise.all([
      api.get<ByChannelItem[]>('/analytics/by-channel?days=30'),
      api.get<SaleChannel[]>('/channels'),
    ])
  )

  const [analyticsData, channelsData] = data ?? [[], []]

  const channelMap: Record<string, SaleChannel> = {}
  for (const ch of channelsData) channelMap[ch.name] = ch

  const totalCount   = analyticsData.reduce((s, c) => s + c.count, 0)
  const totalRevenue = analyticsData.reduce((s, c) => s + c.total, 0)
  const anyFee       = analyticsData.some(c => (channelMap[c.channel]?.fee_pct ?? 0) > 0)

  let cum = 0
  const arcs = analyticsData.map(c => {
    const ch = channelMap[c.channel]
    const color = ch?.color ?? '#888888'
    const share = totalCount > 0 ? (c.count / totalCount) * 100 : 0
    const start = cum; cum += share
    const feePct = ch?.fee_pct ?? 0
    const net = c.total * (1 - feePct / 100)
    const viability = getViability(feePct, ch?.monthly_goal ?? null, c.total)
    return { ...c, share, start, end: cum, color, feePct, net, monthly_goal: ch?.monthly_goal ?? null, viability }
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
                    <span style={{ width: 8, height: 8, borderRadius: 99, background: a.color, flexShrink: 0 }} />
                    <span style={{ flex: 1, fontSize: 12.5, color: 'var(--text-2)', fontWeight: 600 }}>{a.channel}</span>
                    <span className="tnum" style={{ fontSize: 12.5, fontWeight: 700 }}>{Math.round(a.share)}%</span>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          {arcs.length > 0 && (
            <>
              <Section title="Receita por canal" top={18}>
                <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, overflow: 'hidden' }}>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: anyFee ? '1.4fr 52px 1fr 1fr' : '1.4fr 52px 1fr',
                    padding: '10px 14px', background: 'var(--bg-2)',
                    fontSize: 10, color: 'var(--text-3)', fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase',
                  }}>
                    <span>Canal</span>
                    <span>Vendas</span>
                    <span style={{ textAlign: 'right' }}>Receita</span>
                    {anyFee && <span style={{ textAlign: 'right' }}>Líquido</span>}
                  </div>
                  {arcs.map(c => (
                    <div key={c.channel} style={{
                      display: 'grid',
                      gridTemplateColumns: anyFee ? '1.4fr 52px 1fr 1fr' : '1.4fr 52px 1fr',
                      padding: '12px 14px', alignItems: 'center',
                      borderTop: '1px solid var(--line-1)', fontSize: 13,
                    }}>
                      <ChannelChip ch={c.channel} size="lg" color={c.color} />
                      <span className="tnum">{c.count}</span>
                      <span className="tnum" style={{ textAlign: 'right', fontWeight: 700 }}>{fmtBRL(c.total)}</span>
                      {anyFee && (
                        <span className="tnum" style={{ textAlign: 'right', fontWeight: 700, color: c.feePct > 0 ? '#F5847B' : 'var(--text-2)' }}>
                          {c.feePct > 0 ? fmtBRL(c.net) : '—'}
                        </span>
                      )}
                    </div>
                  ))}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: anyFee ? '1.4fr 52px 1fr 1fr' : '1.4fr 52px 1fr',
                    padding: '12px 14px', borderTop: '2px solid var(--line-2)', fontSize: 13,
                  }}>
                    <span style={{ fontWeight: 700 }}>Total</span>
                    <span className="tnum" style={{ fontWeight: 700 }}>{fmtNum(totalCount)}</span>
                    <span className="tnum" style={{ textAlign: 'right', fontWeight: 800, color: 'var(--gold-300)' }}>{fmtBRL(totalRevenue)}</span>
                    {anyFee && <span />}
                  </div>
                </div>
              </Section>

              <Section title="Viabilidade" top={18}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {arcs.map(c => {
                    const goalPct = c.monthly_goal && c.monthly_goal > 0 ? Math.min((c.total / c.monthly_goal) * 100, 100) : null
                    const vColor = LEVEL_COLOR[c.viability.level]
                    const vBg    = LEVEL_BG[c.viability.level]
                    return (
                      <div key={c.channel} style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, padding: '12px 14px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: goalPct !== null ? 10 : 0 }}>
                          <ChannelChip ch={c.channel} size="lg" color={c.color} />
                          {c.feePct > 0 && (
                            <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', background: 'var(--bg-3)', borderRadius: 6, padding: '2px 7px' }}>
                              Taxa {c.feePct}%
                            </span>
                          )}
                          <span style={{ marginLeft: 'auto', fontSize: 11, fontWeight: 700, color: vColor, background: vBg, borderRadius: 6, padding: '3px 9px' }}>
                            {c.viability.label}
                          </span>
                        </div>
                        {goalPct !== null && (
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-3)', marginBottom: 5 }}>
                              <span>Meta mensal</span>
                              <span className="tnum">{fmtBRL(c.total)} / {fmtBRL(c.monthly_goal!)}</span>
                            </div>
                            <div style={{ height: 5, borderRadius: 99, background: 'var(--bg-3)', overflow: 'hidden' }}>
                              <div style={{ height: '100%', width: `${goalPct}%`, borderRadius: 99, background: vColor, transition: 'width 0.4s' }} />
                            </div>
                            <div style={{ textAlign: 'right', fontSize: 10, color: 'var(--text-3)', marginTop: 3 }}>
                              {Math.round(goalPct)}% atingido
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </Section>
            </>
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}
