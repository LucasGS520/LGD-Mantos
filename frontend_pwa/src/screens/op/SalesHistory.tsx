import { useState } from 'react'
import { Ico } from '../../components/Icons'
import { KPI, ChannelChip, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Sale } from '../../services/types'
import { useNav } from '../../nav'

function fmtDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  } catch { return iso }
}

function fmtTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

function groupByDate(sales: Sale[]) {
  const map = new Map<string, Sale[]>()
  for (const s of sales) {
    const key = fmtDate(s.sold_at)
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(s)
  }
  return Array.from(map.entries())
}

export default function SalesHistory() {
  const { navigate } = useNav()
  const { data: sales, loading, error, reload } = useData<Sale[]>(() => api.get('/sales?limit=200'))
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const totalRev = (sales ?? []).reduce((s, v) => s + v.total, 0)
  const groups = groupByDate(sales ?? [])

  const handleDelete = async (id: string) => {
    setDeletingId(id)
    try {
      await api.delete(`/sales/${id}`)
      setConfirmDeleteId(null)
      reload()
    } catch {
      setConfirmDeleteId(null)
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <>
      <AppBar title="Vendas" subtitle={`Últimas ${(sales ?? []).length} vendas`} />
      <OpSubNav active="sales-history" />

      {!loading && !error && (
        <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <KPI label="Receita total" value={fmtBRL(totalRev)} big />
            <KPI label="Nº de vendas" value={String(sales?.length ?? 0)} big />
          </div>
        </div>
      )}

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {groups.map(([date, daySales], di) => (
            <Section title={date} top={di === 0 ? 14 : 18} key={date}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {daySales.map(s => (
                  <div key={s.id} style={{ background: 'var(--bg-1)', border: `1px solid ${confirmDeleteId === s.id ? 'rgba(232,88,79,0.3)' : 'var(--line-1)'}`, borderRadius: 12, overflow: 'hidden' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12 }}>
                      <div style={{ width: 38, height: 38, borderRadius: 10, display: 'grid', placeItems: 'center', background: 'var(--bg-3)', border: '1px solid var(--line-2)', flexShrink: 0 }}>
                        <Ico.cart size={18} stroke="var(--gold-500)" />
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)', fontWeight: 600 }}>#{s.id.slice(0, 8)}</span>
                          <span style={{ fontSize: 11, color: 'var(--text-3)' }}>· {fmtTime(s.sold_at)}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <ChannelChip ch={s.channel} />
                          <span style={{ fontSize: 11.5, color: 'var(--text-3)' }}>{s.items.length} {s.items.length === 1 ? 'item' : 'itens'}</span>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right', display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: 'var(--gold-300)' }}>{fmtBRL(s.total)}</div>
                        <div
                          onClick={() => setConfirmDeleteId(confirmDeleteId === s.id ? null : s.id)}
                          style={{ cursor: 'pointer', padding: 4, opacity: 0.5 }}
                        >
                          <Ico.trash size={15} stroke="var(--text-2)" />
                        </div>
                      </div>
                    </div>
                    {confirmDeleteId === s.id && (
                      <div style={{ padding: '8px 12px 12px', borderTop: '1px solid rgba(232,88,79,0.2)', background: 'rgba(232,88,79,0.04)', display: 'flex', gap: 8 }}>
                        <button onClick={() => setConfirmDeleteId(null)} style={{ flex: 1, height: 34, borderRadius: 8, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>Cancelar</button>
                        <button
                          onClick={() => handleDelete(s.id)}
                          style={{ flex: 1, height: 34, borderRadius: 8, background: 'rgba(232,88,79,0.12)', border: '1px solid rgba(232,88,79,0.3)', color: '#F5847B', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}
                        >{deletingId === s.id ? 'Removendo…' : 'Confirmar remoção'}</button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Section>
          ))}
          {groups.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhuma venda registrada</div>
          )}
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Nova venda" onClick={() => navigate('sale-modal')} />
      <BottomNav active="op" />
    </>
  )
}
