import { Ico } from '../../components/Icons'
import { KPI, Card, MiniBars, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL, fmtBRLshort } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Dashboard as DashboardData } from '../../services/types'
import { useNav } from '../../nav'

export default function Dashboard() {
  const { navigate } = useNav()
  const { data, loading, error, reload } = useData<DashboardData>(() => api.get('/analytics/dashboard'))

  const today = new Date().toLocaleDateString('pt-BR', { day: 'numeric', month: 'long' })
  const dailyValues = (data?.daily_revenue ?? []).map(d => d.value)
  const highlightIdx = dailyValues.length > 0 ? dailyValues.length - 1 : -1

  return (
    <>
      <AppBar title="Análise" subtitle={`Hoje, ${today}`} action={
        <button style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center', position: 'relative' }}>
          <Ico.bell size={18} stroke="var(--text-1)" />
          {(data?.stock_alerts ?? 0) > 0 && (
            <span style={{ position: 'absolute', top: 6, right: 8, width: 7, height: 7, borderRadius: 99, background: '#E8584F', border: '1.5px solid var(--bg-2)' }} />
          )}
        </button>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : data ? (
        <ScreenBody>
          {/* Hero KPI */}
          <div style={{ padding: 18, borderRadius: 18, background: 'linear-gradient(140deg, rgba(212,168,71,0.18), rgba(212,168,71,0.04) 50%, rgba(212,168,71,0.02))', border: '1px solid rgba(212,168,71,0.25)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-300)', textTransform: 'uppercase', letterSpacing: 1.5 }}>Receita do mês</div>
            <div className="tnum" style={{ fontSize: 36, fontWeight: 800, letterSpacing: -1, color: 'var(--text-1)', marginTop: 4 }}>{fmtBRLshort(data.month_revenue)}</div>
            <div style={{ display: 'flex', gap: 14, marginTop: 8 }}>
              <span style={{ fontSize: 12, color: '#5DD49E', fontWeight: 700 }}>Margem {data.margin_pct.toFixed(1)}%</span>
            </div>
            {dailyValues.length > 0 && (
              <div style={{ marginTop: 14 }}>
                <MiniBars data={dailyValues} height={48} highlight={highlightIdx} />
                {data.daily_revenue.length > 1 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9.5, color: 'var(--text-4)', marginTop: 6, fontFamily: 'var(--font-mono)' }}>
                    <span>{data.daily_revenue[0].date}</span>
                    <span>{data.daily_revenue[data.daily_revenue.length - 1].date}</span>
                  </div>
                )}
              </div>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 12 }}>
            <KPI label="Receita hoje" value={fmtBRL(data.today_revenue)} delta={`${data.today_count} venda${data.today_count !== 1 ? 's' : ''}`} deltaTone="success" icon={Ico.cash} />
            <KPI label="Lucro líq. mês" value={fmtBRLshort(data.net_profit)} delta={`margem ${data.margin_pct.toFixed(1)}%`} deltaTone="success" icon={Ico.trend} />
            <KPI label="Vendas hoje" value={String(data.today_count)} deltaTone="muted" icon={Ico.cart} />
            <KPI label="Est. custo" value={fmtBRLshort(data.stock_cost_value)} delta={`${data.stock_units} un`} deltaTone="muted" icon={Ico.box} />
          </div>

          {data.stock_alerts > 0 && (
            <div onClick={() => navigate('stock-alerts')} style={{ marginTop: 12, padding: 14, borderRadius: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)', display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}>
              <div style={{ width: 42, height: 42, borderRadius: 10, background: 'rgba(232,88,79,0.12)', display: 'grid', placeItems: 'center' }}>
                <Ico.warning size={20} stroke="#F5847B" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 13.5, fontWeight: 700 }}>{data.stock_alerts} variante{data.stock_alerts !== 1 ? 's' : ''} em alerta</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>Ver detalhes</div>
              </div>
              <Ico.chevron size={18} stroke="var(--text-3)" />
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 12 }}>
            <Card padding={14}>
              <div style={{ fontSize: 11, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase' }}>Est. (custo)</div>
              <div className="tnum" style={{ fontSize: 18, fontWeight: 800, marginTop: 4 }}>{fmtBRLshort(data.stock_cost_value)}</div>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 2 }}>{data.stock_units} unidades</div>
            </Card>
            <Card padding={14}>
              <div style={{ fontSize: 11, color: 'var(--gold-300)', fontWeight: 600, textTransform: 'uppercase' }}>Est. (venda)</div>
              <div className="tnum" style={{ fontSize: 18, fontWeight: 800, color: 'var(--gold-300)', marginTop: 4 }}>{fmtBRLshort(data.stock_sale_value)}</div>
              <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 2 }}>potencial</div>
            </Card>
          </div>

          <Section title="Análise detalhada" top={20}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                { label: 'Top Produtos',       hint: 'Ranking por receita',         screen: 'top-products' as const, icon: Ico.trend    },
                { label: 'Vendas por Tamanho', hint: 'Distribuição de grade',       screen: 'by-size'      as const, icon: Ico.tshirt   },
                { label: 'Vendas por Canal',   hint: 'Loja, WhatsApp, Instagram…', screen: 'by-channel'   as const, icon: Ico.pie      },
                { label: 'Sugestões de Compra',hint: 'Reposição inteligente',       screen: 'suggestions'  as const, icon: Ico.sparkle  },
                { label: 'DRE do Mês',         hint: 'Demonstrativo de resultado',  screen: 'dre'          as const, icon: Ico.doc      },
              ].map(item => {
                const I = item.icon
                return (
                  <div key={item.screen} onClick={() => navigate(item.screen)} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, cursor: 'pointer' }}>
                    <div style={{ width: 38, height: 38, borderRadius: 10, background: 'var(--bg-3)', display: 'grid', placeItems: 'center' }}>
                      <I size={18} stroke="var(--gold-500)" />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13.5, fontWeight: 600 }}>{item.label}</div>
                      <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 1 }}>{item.hint}</div>
                    </div>
                    <Ico.chevron size={16} stroke="var(--text-3)" />
                  </div>
                )
              })}
            </div>
          </Section>
        </ScreenBody>
      ) : null}
      <BottomNav active="an" />
    </>
  )
}
