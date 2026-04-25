import { useState } from 'react'
import { Tabs, PhotoPlaceholder, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { fmtBRLshort } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { TopProduct } from '../../services/types'

const DAY_OPTIONS = [
  { label: '7 dias',  days: 7  },
  { label: '30 dias', days: 30 },
  { label: '90 dias', days: 90 },
]

export default function TopProducts() {
  const [activeTab, setActiveTab] = useState('30 dias')
  const days = DAY_OPTIONS.find(o => o.label === activeTab)?.days ?? 30

  const { data: products, loading, error, reload } = useData<TopProduct[]>(
    () => api.get(`/analytics/top-products?days=${days}`),
    days,
  )

  return (
    <>
      <AppBar back title="Top produtos" subtitle="Ranking por receita" />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <Tabs items={DAY_OPTIONS.map(o => o.label)} active={activeTab} onChange={setActiveTab} />
      </div>

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}>
            {(products ?? []).map((t, idx) => {
              const rank = idx + 1
              return (
                <div key={t.sku} style={{
                  display: 'flex', alignItems: 'center', gap: 12, padding: 12,
                  background: 'var(--bg-1)', borderRadius: 12,
                  border: `1px solid ${rank <= 3 ? 'rgba(212,168,71,0.25)' : 'var(--line-1)'}`,
                }}>
                  <div style={{
                    width: 30, height: 30, borderRadius: 8, display: 'grid', placeItems: 'center',
                    background: rank === 1 ? 'var(--gold-500)' : rank <= 3 ? 'rgba(212,168,71,0.15)' : 'var(--bg-3)',
                    color: rank === 1 ? '#1A1408' : rank <= 3 ? 'var(--gold-300)' : 'var(--text-3)',
                    fontWeight: 800, fontSize: 13, fontFamily: 'var(--font-mono)',
                  }}>{rank}</div>
                  <PhotoPlaceholder size={42} label={t.sku.slice(-3)} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.name}</div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-3)', marginTop: 2 }}>{t.sku}</div>
                    <div style={{ fontSize: 11, color: '#5DD49E', marginTop: 4, fontWeight: 600 }}>
                      {t.qty} vendas · +{fmtBRLshort(t.profit)} lucro
                    </div>
                  </div>
                  <div className="tnum" style={{ fontSize: 14, fontWeight: 800, color: 'var(--gold-300)', textAlign: 'right' }}>
                    {fmtBRLshort(t.revenue)}
                  </div>
                </div>
              )
            })}
            {(products ?? []).length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhum dado disponível</div>
            )}
          </div>
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}
