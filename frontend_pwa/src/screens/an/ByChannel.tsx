import { useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { Card, Section, ChannelChip, LoadingBody, ErrorBody, Badge } from '../../components/UI'
import { PeriodSelect, MetricInfo, SectionChart, type Period } from '../../components/Analytics'
import { fmtBRL, fmtBRLshort, fmtNum } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { ByChannelItem, SaleChannel } from '../../services/types'

type ViabilityLevel = 'red' | 'amber' | 'green'
interface Viability { label: string; level: ViabilityLevel }

function getViability(feePct: number, goal: number | null, total: number): Viability {
  if (feePct > 20) return { label: 'Alto custo', level: 'red' }
  if (feePct > 10) return { label: 'Custo médio', level: 'amber' }
  if (goal && goal > 0) {
    const pct = total / goal
    if (pct < 0.5) return { label: 'Abaixo da meta', level: 'red' }
    if (pct >= 0.8) return { label: 'No ritmo', level: 'green' }
    return { label: 'Próximo da meta', level: 'amber' }
  }
  return { label: 'Eficiente', level: 'green' }
}

const LEVEL_COLOR: Record<ViabilityLevel, string> = {
  green: '#5DD49E',
  amber: '#F5BF7A',
  red:   '#F5847B',
}

const CHANNEL_FALLBACK: Record<string, string> = {
  Loja: '#D4A847', WhatsApp: '#25D366', Instagram: '#E1306C', Shopee: '#EE4D2D',
}

export default function ByChannel() {
  const [period, setPeriod] = useState<Period>('current_month')

  const { data, loading, error, reload } = useData<[ByChannelItem[], SaleChannel[]]>(() =>
    Promise.all([
      api.getByChannel(period),
      api.get<SaleChannel[]>('/channels'),
    ]), period
  )

  const [analyticsData, channelsData] = data ?? [[], []]
  const channelMap: Record<string, SaleChannel> = {}
  for (const ch of channelsData) channelMap[ch.name] = ch

  const totalRevenue = analyticsData.reduce((s, c) => s + c.total, 0)
  const totalFees    = analyticsData.reduce((s, c) => s + c.total * (channelMap[c.channel]?.fee_pct ?? 0) / 100, 0)
  const totalNet     = totalRevenue - totalFees

  const pieData = analyticsData.map(c => ({
    name: c.channel,
    value: c.total,
    color: channelMap[c.channel]?.color ?? CHANNEL_FALLBACK[c.channel] ?? '#888',
  }))

  return (
    <>
      <AppBar title="Canais de Venda" back />
      <PeriodSelect value={period} onChange={setPeriod} />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {/* Resumo de taxas */}
          {totalFees > 0 && (
            <Card padding={14} style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                <MiniStat label="Receita bruta" value={fmtBRLshort(totalRevenue)} />
                <div style={{ width: 1, background: 'var(--line-1)' }} />
                <MiniStat label="Total em taxas" value={fmtBRLshort(totalFees)} color="#F5847B" />
                <div style={{ width: 1, background: 'var(--line-1)' }} />
                <MiniStat label="Líquido" value={fmtBRLshort(totalNet)} color="#5DD49E" info={{
                  what: 'Receita real depois de descontar todas as taxas de canal (Shopee, Instagram, etc).',
                  good: 'Quanto mais próximo da receita bruta, melhor. Taxas acima de 15% são altas.',
                  action: 'Se as taxas estão muito altas, considere priorizar canais com menor custo (ex: Loja física ou WhatsApp).',
                }} />
              </div>
            </Card>
          )}

          {/* Gráfico de distribuição */}
          <SectionChart title="Distribuição por canal" empty={pieData.length === 0}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ width: 140, height: 140, flexShrink: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={pieData} dataKey="value" cx="50%" cy="50%" outerRadius={65} strokeWidth={0} innerRadius={32}>
                      {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                      formatter={(v: number, _: string, props: any) => {
                        const pct = totalRevenue > 0 ? ((v / totalRevenue) * 100).toFixed(1) : '0'
                        return [`${fmtBRLshort(v)} (${pct}%)`, props.name]
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
                {analyticsData.map(c => {
                  const ch = channelMap[c.channel]
                  const pct = totalRevenue > 0 ? (c.total / totalRevenue * 100).toFixed(1) : '0'
                  const color = ch?.color ?? CHANNEL_FALLBACK[c.channel] ?? '#888'
                  return (
                    <div key={c.channel} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 2, background: color, flexShrink: 0 }} />
                      <span style={{ flex: 1, fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>{c.channel}</span>
                      <span className="tnum" style={{ fontSize: 12, color: 'var(--text-3)' }}>{pct}%</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </SectionChart>

          {/* Tabela de receita por canal */}
          <SectionChart title="Receita detalhada por canal">
            <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, overflow: 'hidden' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto auto', gap: 0, padding: '8px 14px', borderBottom: '1px solid var(--line-1)' }}>
                <ColHead>Canal</ColHead>
                <div />
                <ColHead>Vendas</ColHead>
                <ColHead>Receita</ColHead>
              </div>
              {analyticsData.map((c, i) => {
                const ch = channelMap[c.channel]
                const fee = ch?.fee_pct ?? 0
                const net = c.total * (1 - fee / 100)
                return (
                  <div key={c.channel} style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto auto', gap: '0 12px', padding: '12px 14px', borderTop: i > 0 ? '1px solid var(--line-1)' : undefined, alignItems: 'center' }}>
                    <ChannelChip ch={c.channel} color={ch?.color} />
                    <div>
                      {fee > 0 && <div style={{ fontSize: 11, color: '#F5847B', fontWeight: 600 }}>taxa {fee}% → −{fmtBRLshort(c.total * fee / 100)}</div>}
                    </div>
                    <span className="tnum" style={{ fontSize: 13, color: 'var(--text-2)', textAlign: 'right' }}>{fmtNum(c.count)}</span>
                    <div style={{ textAlign: 'right' }}>
                      <div className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--gold-300)' }}>{fmtBRLshort(c.total)}</div>
                      {fee > 0 && <div className="tnum" style={{ fontSize: 11, color: '#5DD49E' }}>líq. {fmtBRLshort(net)}</div>}
                    </div>
                  </div>
                )
              })}
              <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto auto', gap: '0 12px', padding: '12px 14px', borderTop: '1px solid var(--line-1)', background: 'rgba(212,168,71,0.04)' }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-2)', gridColumn: '1 / 3' }}>Total</span>
                <span className="tnum" style={{ fontSize: 13, fontWeight: 700, textAlign: 'right' }}>{analyticsData.reduce((s, c) => s + c.count, 0)}</span>
                <span className="tnum" style={{ fontSize: 14, fontWeight: 800, color: 'var(--gold-300)', textAlign: 'right' }}>{fmtBRLshort(totalRevenue)}</span>
              </div>
            </div>
          </SectionChart>

          {/* Viabilidade por canal */}
          <Section title="Viabilidade por canal" top={4}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {analyticsData.map(c => {
                const ch = channelMap[c.channel]
                const fee = ch?.fee_pct ?? 0
                const goal = ch?.monthly_goal ?? null
                const via = getViability(fee, goal, c.total)
                const goalPct = goal && goal > 0 ? Math.min((c.total / goal) * 100, 100) : null

                return (
                  <Card key={c.channel} padding={14}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <ChannelChip ch={c.channel} size="lg" color={ch?.color} />
                        {fee > 0 && <Badge tone="danger" size="sm">taxa {fee}%</Badge>}
                      </div>
                      <Badge tone={via.level === 'green' ? 'success' : via.level === 'amber' ? 'warn' : 'danger'} size="sm" dot>
                        {via.label}
                      </Badge>
                    </div>

                    {via.level !== 'green' && (
                      <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: fee > 0 ? 6 : 0, lineHeight: 1.4 }}>
                        {fee > 20 && 'Taxa acima de 20% — custo muito alto por venda.'}
                        {fee > 10 && fee <= 20 && 'Taxa entre 10–20% — avalie se a margem compensa.'}
                        {via.level !== 'green' && goal && goalPct !== null && goalPct < 80 && ` Meta atingida: ${goalPct.toFixed(0)}%`}
                      </div>
                    )}

                    {goalPct !== null && (
                      <>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 5 }}>
                          <span style={{ color: 'var(--text-3)' }}>{fmtBRLshort(c.total)} vendido</span>
                          <span style={{ color: 'var(--text-3)' }}>meta {fmtBRLshort(goal!)} /mês</span>
                        </div>
                        <div style={{ height: 6, borderRadius: 99, background: 'var(--bg-3)', overflow: 'hidden' }}>
                          <div style={{ height: '100%', width: `${goalPct}%`, background: LEVEL_COLOR[via.level], borderRadius: 99 }} />
                        </div>
                      </>
                    )}
                  </Card>
                )
              })}
            </div>
          </Section>
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}

function MiniStat({ label, value, color, info }: { label: string; value: string; color?: string; info?: { what: string; good: string; action: string } }) {
  return (
    <div style={{ flex: 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 3 }}>
        <span style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.3 }}>{label}</span>
        {info && <MetricInfo {...info} />}
      </div>
      <div className="tnum" style={{ fontSize: 16, fontWeight: 800, color: color ?? 'var(--text-1)' }}>{value}</div>
    </div>
  )
}

function ColHead({ children }: { children: React.ReactNode }) {
  return <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-4)', textTransform: 'uppercase', letterSpacing: 0.4 }}>{children}</span>
}
