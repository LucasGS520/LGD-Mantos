import { Ico } from '../../components/Icons'
import { Btn, Badge, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import { useNav } from '../../nav'

interface BuyingPattern {
  category_name: string
  monthly_sales_avg: number
  coverage_days: number | null
  suggested_batch: number
  top_sizes: { size: string; pct: number }[]
  avg_margin_pct: number
}

export default function Suggestions() {
  const { navigate } = useNav()
  const { data: patterns, loading, error, reload } = useData<BuyingPattern[]>(() => api.get('/analytics/categories/buying-patterns'))

  const count = (patterns ?? []).length

  const coverageTone = (days: number | null) => {
    if (days == null) return 'neutral'
    if (days < 7) return 'danger'
    if (days < 21) return 'warn'
    return 'success'
  }

  return (
    <>
      <AppBar back title="Padrões de Compra" subtitle={`${count} categoria${count !== 1 ? 's' : ''} analisada${count !== 1 ? 's' : ''}`} action={
        <div style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid rgba(212,168,71,0.3)', background: 'rgba(212,168,71,0.08)', display: 'grid', placeItems: 'center' }}>
          <Ico.sparkle size={18} stroke="var(--gold-500)" />
        </div>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {count > 0 && (
            <div style={{ padding: '12px 14px', marginTop: 4, borderRadius: 12, background: 'rgba(212,168,71,0.08)', border: '1px solid rgba(212,168,71,0.2)', display: 'flex', gap: 10, alignItems: 'center' }}>
              <Ico.brain size={18} stroke="var(--gold-500)" />
              <span style={{ fontSize: 12, color: 'var(--text-2)' }}>Baseado nos últimos 90 dias. Cobertura calculada com velocidade dos últimos 30 dias.</span>
            </div>
          )}

          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 14 }}>
            {(patterns ?? []).map((p, i) => (
              <div key={i} style={{ padding: 14, borderRadius: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ fontSize: 15, fontWeight: 700 }}>{p.category_name}</div>
                  <Badge tone={coverageTone(p.coverage_days)} dot>
                    {p.coverage_days != null ? `${Math.round(p.coverage_days)}d cobertura` : 'Sem estoque'}
                  </Badge>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 8, marginBottom: 12 }}>
                  <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--bg-2)' }}>
                    <div style={{ fontSize: 9.5, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 700 }}>Vendas/mês</div>
                    <div className="tnum" style={{ fontSize: 14, fontWeight: 800, marginTop: 2 }}>{Math.round(p.monthly_sales_avg)}</div>
                  </div>
                  <div style={{ padding: '8px 10px', borderRadius: 8, background: 'var(--bg-2)' }}>
                    <div style={{ fontSize: 9.5, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 700 }}>Margem</div>
                    <div className="tnum" style={{ fontSize: 14, fontWeight: 800, marginTop: 2, color: '#5DD49E' }}>{p.avg_margin_pct}%</div>
                  </div>
                  <div style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(212,168,71,0.10)', border: '1px solid rgba(212,168,71,0.2)' }}>
                    <div style={{ fontSize: 9.5, color: 'var(--gold-300)', textTransform: 'uppercase', fontWeight: 700 }}>Lote sugerido</div>
                    <div className="tnum" style={{ fontSize: 14, fontWeight: 800, color: 'var(--gold-300)', marginTop: 2 }}>{p.suggested_batch}</div>
                  </div>
                </div>

                {p.top_sizes.length > 0 && (
                  <div>
                    <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, marginBottom: 6, textTransform: 'uppercase' }}>Mix de tamanhos recomendado</div>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {p.top_sizes.map(s => (
                        <div key={s.size} style={{ padding: '4px 10px', borderRadius: 8, background: 'var(--bg-2)', border: '1px solid var(--line-2)', fontSize: 12 }}>
                          <span style={{ fontWeight: 700 }}>{s.size}</span>
                          <span style={{ color: 'var(--text-3)', marginLeft: 4 }}>{s.pct}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {count === 0 && (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <div style={{ fontSize: 32, marginBottom: 12 }}></div>
                <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-2)' }}>Sem dados suficientes</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 6 }}>Registre vendas para gerar padrões de compra.</div>
              </div>
            )}
          </div>

          {count > 0 && (
            <Btn kind="primary" full size="lg" icon={Ico.plus} onClick={() => navigate('purchase-form')} style={{ marginTop: 16 }}>
              Nova entrada de mercadoria
            </Btn>
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}
