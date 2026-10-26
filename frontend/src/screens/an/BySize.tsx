import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { Card, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { fmtNum } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { BySizeItem } from '../../services/types'

export default function BySize() {
  const { data, loading, error, reload } = useData<BySizeItem[]>(() => api.get('/analytics/by-size?days=30'))

  const max = data ? Math.max(...data.map(s => s.qty), 1) : 1

  return (
    <>
      <AppBar back title="Vendas por tamanho" subtitle="Últimos 30 dias" />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <Card padding={16} style={{ marginTop: 4 }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {(data ?? []).map(s => {
                const w = (s.qty / max) * 100
                const isMax = s.qty === max
                return (
                  <div key={s.size}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 5 }}>
                      <span style={{ fontSize: 12.5, fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{s.size}</span>
                      <span className="tnum" style={{ fontSize: 11.5, color: 'var(--text-3)' }}>{s.qty} un</span>
                    </div>
                    <div style={{ height: 14, borderRadius: 7, background: 'var(--bg-3)', overflow: 'hidden' }}>
                      <div style={{ width: `${w}%`, height: '100%', borderRadius: 7, background: isMax ? 'linear-gradient(90deg, var(--gold-500), var(--gold-400))' : 'rgba(212,168,71,0.5)' }} />
                    </div>
                  </div>
                )
              })}
              {(data ?? []).length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 16 }}>Nenhum dado disponível</div>
              )}
            </div>
          </Card>

          {(data ?? []).length > 0 && (
            <Section title="Tabela detalhada" top={18}>
              <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, overflow: 'hidden' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '60px 1fr', padding: '10px 14px', background: 'var(--bg-2)', fontSize: 10, color: 'var(--text-3)', fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase' }}>
                  <span>Tam</span><span style={{ textAlign: 'right' }}>Qtd vendida</span>
                </div>
                {(data ?? []).map(s => (
                  <div key={s.size} style={{ display: 'grid', gridTemplateColumns: '60px 1fr', padding: '12px 14px', alignItems: 'center', borderTop: '1px solid var(--line-1)', fontSize: 13 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--gold-300)' }}>{s.size}</span>
                    <span className="tnum" style={{ textAlign: 'right', fontWeight: 600 }}>{fmtNum(s.qty)}</span>
                  </div>
                ))}
              </div>
            </Section>
          )}
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}
