import { Ico } from '../../components/Icons'
import { Badge, Btn, PhotoPlaceholder, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Suggestion } from '../../services/types'
import { useNav } from '../../nav'

export default function Suggestions() {
  const { navigate } = useNav()
  const { data: suggestions, loading, error, reload } = useData<Suggestion[]>(() => api.get('/analytics/purchase-suggestions'))

  const count = (suggestions ?? []).length

  return (
    <>
      <AppBar back title="Sugestões de compra" subtitle={`${count} sugestão${count !== 1 ? 'ões' : ''} gerada${count !== 1 ? 's' : ''}`} action={
        <div style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid rgba(212,168,71,0.3)', background: 'rgba(212,168,71,0.08)', display: 'grid', placeItems: 'center' }}>
          <Ico.sparkle size={18} stroke="var(--gold-500)" />
        </div>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {count > 0 && (
            <div style={{ padding: '12px 14px', marginTop: 4, borderRadius: 12, background: 'rgba(212,168,71,0.08)', border: '1px solid rgba(212,168,71,0.2)', display: 'flex', gap: 10, alignItems: 'center' }}>
              <Ico.brain size={18} stroke="var(--gold-500)" />
              <span style={{ fontSize: 12, color: 'var(--text-2)' }}>Baseado em vendas dos últimos 30 dias e estoque atual.</span>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 14 }}>
            {(suggestions ?? []).map((s, i) => {
              const urg = s.urgency === 'alta'
              return (
                <div key={i} style={{ padding: 14, borderRadius: 14, background: 'var(--bg-1)', border: `1px solid ${urg ? 'rgba(232,88,79,0.3)' : 'var(--line-1)'}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <Badge tone={urg ? 'danger' : 'warn'} dot>{urg ? 'Urgência alta' : 'Urgência média'}</Badge>
                    <span className="tnum" style={{ fontSize: 11.5, color: 'var(--text-3)' }}>
                      {s.stock === 0 ? 'em ruptura' : s.days_remaining != null ? `~${Math.round(s.days_remaining)}d restantes` : '—'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                    <PhotoPlaceholder size={48} label={s.sku.slice(-3)} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13.5, fontWeight: 700 }}>{s.product_name}</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10.5, color: 'var(--text-3)', marginTop: 2 }}>
                        {s.sku} · {s.size} · {s.color}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginTop: 12 }}>
                    <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--bg-2)' }}>
                      <div style={{ fontSize: 9.5, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 700 }}>Atual</div>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 800, marginTop: 2 }}>{s.stock}</div>
                    </div>
                    <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--bg-2)' }}>
                      <div style={{ fontSize: 9.5, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 700 }}>Vendas/30d</div>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 800, marginTop: 2 }}>{s.sold_30d}</div>
                    </div>
                    <div style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(212,168,71,0.1)', border: '1px solid rgba(212,168,71,0.2)' }}>
                      <div style={{ fontSize: 9.5, color: 'var(--gold-300)', textTransform: 'uppercase', fontWeight: 700 }}>Sugerido</div>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 800, color: 'var(--gold-300)', marginTop: 2 }}>+{s.suggested_qty}</div>
                    </div>
                  </div>
                </div>
              )
            })}

            {count === 0 && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <div style={{ fontSize: 32, marginBottom: 12 }}>✓</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: '#5DD49E' }}>Estoque bem abastecido!</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 6 }}>Nenhuma reposição necessária no momento.</div>
              </div>
            )}
          </div>

          {count > 0 && (
            <Btn kind="primary" full size="lg" icon={Ico.truck} onClick={() => navigate('purchase-form')} style={{ marginTop: 16 }}>
              Criar pedido de reposição
            </Btn>
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}
