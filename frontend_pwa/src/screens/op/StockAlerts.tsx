import { Ico } from '../../components/Icons'
import { Badge, Btn, PhotoPlaceholder, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { StockAlert } from '../../services/types'
import { useNav } from '../../nav'

export default function StockAlerts() {
  const { navigate } = useNav()
  const { data: alerts, loading, error, reload } = useData<StockAlert[]>(() => api.get('/stock/alerts'))

  const critical = (alerts ?? []).filter(a => a.stock === 0)
  const low = (alerts ?? []).filter(a => a.stock > 0 && a.stock < a.min)

  return (
    <>
      <AppBar back title="Alertas de estoque" subtitle={`${(alerts ?? []).length} variantes precisam de atenção`} />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {(alerts ?? []).length > 0 && (
            <div style={{ padding: 14, marginTop: 4, borderRadius: 14, background: 'rgba(232,88,79,0.08)', border: '1px solid rgba(232,88,79,0.25)', display: 'flex', gap: 12, alignItems: 'center' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: 'rgba(232,88,79,0.18)', display: 'grid', placeItems: 'center' }}>
                <Ico.warning size={20} stroke="#F5847B" />
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700 }}>Reposição urgente recomendada</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>
                  {critical.length} em ruptura · {low.length} abaixo do mínimo
                </div>
              </div>
            </div>
          )}

          {(alerts ?? []).length === 0 && (
            <div style={{ textAlign: 'center', padding: 40 }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>✓</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#5DD49E' }}>Estoque em dia!</div>
              <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 6 }}>Nenhuma variante abaixo do mínimo.</div>
            </div>
          )}

          {(alerts ?? []).length > 0 && (
            <Section title="Crítico · ruptura ou abaixo do mínimo" top={18}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {(alerts ?? []).map((v, i) => {
                  const danger = v.stock === 0
                  return (
                    <div key={i} style={{ padding: 12, borderRadius: 12, background: 'var(--bg-1)', border: `1px solid ${danger ? 'rgba(232,88,79,0.35)' : 'var(--line-1)'}`, position: 'relative', overflow: 'hidden' }}>
                      <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 3, background: danger ? '#E8584F' : '#E8A04A' }} />
                      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginLeft: 6 }}>
                        <PhotoPlaceholder size={48} label={v.sku.slice(-3)} />
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 13.5, fontWeight: 700 }}>{v.product_name}</div>
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10.5, color: 'var(--text-3)', marginTop: 2 }}>{v.sku}</div>
                          <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
                            <Badge tone="neutral">Tam {v.size}</Badge>
                            <Badge tone="neutral">{v.color}</Badge>
                          </div>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div className="tnum" style={{ fontSize: 22, fontWeight: 800, color: danger ? '#F5847B' : '#F5BF7A', lineHeight: 1 }}>{v.stock}</div>
                          <div style={{ fontSize: 10, color: 'var(--text-3)', marginTop: 4 }}>mín. {v.min}</div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </Section>
          )}

          {(alerts ?? []).length > 0 && (
            <Btn kind="primary" full size="lg" icon={Ico.truck} onClick={() => navigate('purchase-form')} style={{ marginTop: 18 }}>
              Gerar pedido de compra
            </Btn>
          )}
        </ScreenBody>
      )}
    </>
  )
}
