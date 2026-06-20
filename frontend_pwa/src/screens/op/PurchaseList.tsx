import { useEffect, useState } from 'react'
import { Ico } from '../../components/Icons'
import { LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { MerchandiseEntry, Supplier } from '../../services/types'
import { useNav } from '../../nav'

function fmtDate(d: string): string {
  try { return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' }) }
  catch { return d }
}

export default function PurchaseList() {
  const { navigate } = useNav()
  const { data: entries, loading, error, reload } = useData<MerchandiseEntry[]>(() => api.get('/entries'))
  const [supMap, setSupMap] = useState<Record<string, string>>({})

  useEffect(() => {
    api.get<Supplier[]>('/suppliers')
      .then(sups => setSupMap(Object.fromEntries(sups.map(s => [s.id, s.name]))))
      .catch(() => {})
  }, [])

  const totalMonth = (entries ?? []).reduce((s, e) => s + (e.total_cost ?? 0), 0)

  return (
    <>
      <AppBar title="Entradas" subtitle={`${(entries ?? []).length} entradas · ${fmtBRL(totalMonth)} total`} />
      <OpSubNav active="purchase-list" />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
            {(entries ?? []).map(e => (
              <div key={e.id} style={{ padding: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-3)' }}>#{e.id.slice(0, 8)}</span>
                  <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{fmtDate(e.entry_date)}</span>
                </div>
                <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>
                  {e.supplier_id ? (supMap[e.supplier_id] ?? `Fornecedor #${e.supplier_id.slice(0, 6)}`) : 'Sem fornecedor'}
                </div>
                {e.notes && (
                  <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 4 }}>{e.notes}</div>
                )}
                <div style={{ fontSize: 12, color: 'var(--text-3)' }}>
                  {e.variants_added} variante(s) adicionada(s)
                </div>
                <div style={{ height: 1, background: 'var(--line-1)', margin: '10px 0' }} />
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span className="tnum" style={{ fontSize: 17, fontWeight: 800, color: 'var(--gold-300)' }}>{fmtBRL(e.total_cost)}</span>
                  <span style={{ fontSize: 11.5, color: 'var(--text-3)', fontWeight: 500 }}>custo total</span>
                </div>
              </div>
            ))}
            {(entries ?? []).length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhuma entrada registrada</div>
            )}
          </div>
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Nova entrada" onClick={() => navigate('purchase-form')} />
      <BottomNav active="op" />
    </>
  )
}
