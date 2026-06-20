import { AreaChart, Area, XAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { Ico } from '../../components/Icons'
import { KPI, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { NavItem, AlertRow, MetricInfo } from '../../components/Analytics'
import { fmtBRL, fmtBRLshort } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Dashboard as DashboardData, ProductAnalysis } from '../../services/types'
import { useNav } from '../../nav'

export default function Dashboard() {
  const { navigate } = useNav()
  const { data, loading, error, reload } = useData<DashboardData>(api.getDashboard)
  const { data: analysis } = useData<ProductAnalysis>(() => api.getProductAnalysis('current_month'))

  const today = new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long' })
  const chartData = (data?.daily_revenue ?? []).map(d => ({ date: d.date, value: d.value }))

  const alertCount = (analysis?.rupture_risk?.length ?? 0) + (analysis?.stopped?.length ?? 0)

  return (
    <>
      <AppBar title="Análise" subtitle={`Hoje, ${today}`} />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : data ? (
        <ScreenBody>
          {/* Hero */}
          <div style={{ padding: 18, borderRadius: 18, background: 'linear-gradient(140deg, rgba(212,168,71,0.18), rgba(212,168,71,0.04) 50%, rgba(212,168,71,0.02))', border: '1px solid rgba(212,168,71,0.25)', marginBottom: 12 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-300)', textTransform: 'uppercase', letterSpacing: 1.5 }}>Receita do mês</div>
            <div className="tnum" style={{ fontSize: 36, fontWeight: 800, letterSpacing: -1, color: 'var(--text-1)', marginTop: 4 }}>
              {fmtBRLshort(data.month_revenue)}
            </div>
            <div style={{ display: 'flex', gap: 14, marginTop: 6, flexWrap: 'wrap' }}>
              <span style={{ fontSize: 12, color: '#5DD49E', fontWeight: 700 }}>Margem {data.margin_pct.toFixed(1)}%</span>
              <span style={{ fontSize: 12, color: 'var(--text-3)', fontWeight: 500 }}>{data.total_units_sold} un vendidas</span>
              <span style={{ fontSize: 12, color: 'var(--gold-300)', fontWeight: 500 }}>Ticket médio {fmtBRLshort(data.avg_ticket)}</span>
            </div>

            {chartData.length > 1 && (
              <div style={{ marginTop: 16, height: 64 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="dgGold" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#D4A847" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="#D4A847" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" hide />
                    <Tooltip
                      cursor={{ stroke: 'rgba(255,255,255,0.12)', strokeWidth: 1 }}
                      contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                      formatter={(v: number) => [fmtBRLshort(v), 'Receita']}
                      labelStyle={{ color: 'var(--text-3)', fontSize: 11 }}
                    />
                    <Area type="monotone" dataKey="value" stroke="#D4A847" strokeWidth={2} fill="url(#dgGold)" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9.5, color: 'var(--text-4)', marginTop: 4, fontFamily: 'var(--font-mono)' }}>
                  <span>{chartData[0]?.date}</span>
                  <span>{chartData[chartData.length - 1]?.date}</span>
                </div>
              </div>
            )}
          </div>

          {/* Alertas operacionais */}
          {alertCount > 0 && (
            <div style={{ marginBottom: 12 }}>
              {(analysis?.rupture_risk?.length ?? 0) > 0 && (
                <AlertRow
                  tone="danger"
                  icon={<Ico.warning size={16} />}
                  text={`${analysis!.rupture_risk.length} variante${analysis!.rupture_risk.length > 1 ? 's' : ''} com risco de ruptura de estoque`}
                  cta="Ver alertas"
                  onCta={() => navigate('an-alertas')}
                />
              )}
              {(analysis?.stopped?.length ?? 0) > 0 && (
                <AlertRow
                  tone="warn"
                  icon={<Ico.alert size={16} />}
                  text={`${analysis!.stopped.length} produto${analysis!.stopped.length > 1 ? 's' : ''} parado${analysis!.stopped.length > 1 ? 's' : ''} (sem venda em 60 dias)`}
                  cta="Ver alertas"
                  onCta={() => navigate('an-alertas')}
                />
              )}
            </div>
          )}

          {/* KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
            <KPIInfo label="Receita hoje" value={fmtBRL(data.today_revenue)}
              delta={`${data.today_count} venda${data.today_count !== 1 ? 's' : ''}`} deltaTone="success"
              icon={Ico.cash} />
            <KPIInfo label="Lucro líquido" value={fmtBRLshort(data.net_profit)}
              delta={`margem ${data.margin_pct.toFixed(1)}%`} deltaTone={data.net_profit >= 0 ? 'success' : 'danger'}
              icon={Ico.trend} />
            <KPIInfo label="Estoque (custo)" value={fmtBRLshort(data.stock_cost_value)}
              delta={`${data.stock_units} un`} deltaTone="muted"
              icon={Ico.box}
              info={{ what: 'Valor total do estoque calculado pelo preço de custo dos produtos.', good: 'Ideal ter cobertura de 30–60 dias de vendas em estoque.', action: 'Compare com a velocidade de saída por categoria (tela Categorias) para saber se você está com excesso ou falta.' }} />
            <KPIInfo label="Potencial (venda)" value={fmtBRLshort(data.stock_sale_value)}
              delta="se vender tudo" deltaTone="muted"
              icon={Ico.tag}
              info={{ what: 'Quanto o estoque atual renderia se fosse vendido pelo preço cheio.', good: 'Deve ser bem maior que o custo — a diferença é seu lucro potencial do estoque.', action: 'Produtos com alto custo mas baixo potencial de venda podem ter margens ruins. Verifique em Categorias.' }} />
          </div>

          {/* Navegação */}
          <div style={{ borderTop: '1px solid var(--line-1)', paddingTop: 4 }}>
            <NavItem icon={<Ico.pie size={18} stroke="var(--gold-500)" />} label="Categorias" sub="Análise de desempenho por categoria" target="an-categorias" />
            <NavItem icon={<Ico.truck size={18} stroke="var(--gold-500)" />} label="Compras & Reposição" sub="Sugestões de compra baseadas em dados" target="an-compras" badge={(analysis?.rupture_risk?.length ?? 0) > 0 ? analysis!.rupture_risk.length : undefined} />
            <NavItem icon={<Ico.store size={18} stroke="var(--gold-500)" />} label="Canais de Venda" sub="Distribuição e taxas por canal" target="by-channel" />
            <NavItem icon={<Ico.doc size={18} stroke="var(--gold-500)" />} label="DRE do Mês" sub="Demonstrativo de resultado" target="dre" />
            <NavItem icon={<Ico.alert size={18} stroke="#F5847B" />} label="Alertas & Saúde" sub="Qualidade de dados e problemas operacionais" target="an-alertas" badge={alertCount > 0 ? alertCount : undefined} />
            <NavItem icon={<Ico.sparkle size={18} stroke="var(--gold-500)" />} label="Análise de Marketing" sub="O que postar, promover e destacar" target="an-marketing-intel" />
          </div>
        </ScreenBody>
      ) : null}
      <BottomNav active="an" />
    </>
  )
}

// KPI com ícone ⓘ inline
function KPIInfo({ label, value, delta, deltaTone, icon: I, info }: {
  label: string; value: string; delta?: string; deltaTone?: 'success' | 'danger' | 'muted'
  icon: (p: any) => JSX.Element
  info?: { what: string; good: string; action: string }
}) {
  return (
    <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14, padding: '12px 14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <span style={{ fontSize: 11, color: 'var(--text-3)', fontWeight: 600, letterSpacing: 0.4, textTransform: 'uppercase' }}>{label}</span>
          {info && <MetricInfo {...info} />}
        </div>
        <I size={15} stroke="var(--text-3)" />
      </div>
      <div className="tnum" style={{ fontSize: 19, fontWeight: 700, letterSpacing: -0.5, color: 'var(--text-1)', lineHeight: 1.1 }}>{value}</div>
      {delta && <div style={{ fontSize: 11, fontWeight: 600, marginTop: 4, color: deltaTone === 'success' ? '#5DD49E' : deltaTone === 'danger' ? '#F5847B' : 'var(--text-3)' }}>{delta}</div>}
    </div>
  )
}
