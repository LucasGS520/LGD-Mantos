import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Badge, Tabs, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Purchase, Supplier } from '../../services/types'
import { useNav } from '../../nav'

type Tone = 'success' | 'info' | 'neutral'

const STATUS_LABEL: Record<string, string> = {
  rascunho: 'Em análise',
  enviado: 'Pedido feito',
  recebido: 'Recebido',
  cancelado: 'Cancelado',
}

const STATUS_TONE: Record<string, Tone> = {
  rascunho: 'neutral',
  enviado: 'info',
  recebido: 'success',
  cancelado: 'neutral',
}

const TABS = ['Todos', 'Em análise', 'Pedido feito', 'Recebido']
const TAB_STATUS: Record<string, string> = {
  'Em análise': 'rascunho',
  'Pedido feito': 'enviado',
  'Recebido': 'recebido',
}

function fmtOrderDate(d: string): string {
  try { return new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) }
  catch { return d }
}

export default function PurchaseList() {
  const { navigate } = useNav()
  const { data: purchases, loading, error, reload } = useData<Purchase[]>(() => api.get('/purchases'))
  const [activeTab, setActiveTab] = useState('Todos')
  const [supMap, setSupMap] = useState<Record<string, string>>({})

  useEffect(() => {
    api.get<Supplier[]>('/suppliers')
      .then(sups => setSupMap(Object.fromEntries(sups.map(s => [s.id, s.name]))))
      .catch(() => {})
  }, [])

  const filtered = (purchases ?? []).filter(p => {
    if (activeTab === 'Todos') return true
    return p.status === TAB_STATUS[activeTab]
  })

  const totalMonth = (purchases ?? []).reduce((s, p) => s + p.items.reduce((a, i) => a + i.quantity * i.unit_cost, 0), 0)

  return (
    <>
      <AppBar title="Compras" subtitle={`${(purchases ?? []).length} pedidos · ${fmtBRL(totalMonth)} total`} />
      <OpSubNav active="purchase-list" />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <Tabs items={TABS} active={activeTab} onChange={setActiveTab} />
      </div>

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 10 }}>
            {filtered.map(p => {
              const total = p.items.reduce((s, i) => s + i.quantity * i.unit_cost, 0)
              const units = p.items.reduce((s, i) => s + i.quantity, 0)
              const canReceive = p.status !== 'recebido' && p.status !== 'cancelado'
              return (
                <div key={p.id} style={{ padding: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)', fontWeight: 600 }}>#{p.id.slice(0, 8)}</span>
                    <Badge tone={STATUS_TONE[p.status] ?? 'neutral'} dot>{STATUS_LABEL[p.status] ?? p.status}</Badge>
                  </div>
                  <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>
                    {supMap[p.supplier_id] ?? `Fornecedor #${p.supplier_id.slice(0, 6)}`}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-3)' }}>
                    Pedido em {fmtOrderDate(p.order_date)} · {units} unidades
                  </div>
                  <div style={{ height: 1, background: 'var(--line-1)', margin: '10px 0' }} />
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <span className="tnum" style={{ fontSize: 17, fontWeight: 800, color: 'var(--gold-300)' }}>{fmtBRL(total)}</span>
                    {canReceive && (
                      <button
                        onClick={() => navigate('purchase-form', { purchaseId: p.id })}
                        style={{ height: 34, padding: '0 14px', borderRadius: 10, background: 'var(--gold-500)', color: '#1A1408', fontWeight: 700, fontSize: 12, border: 0, cursor: 'pointer' }}
                      >
                        Receber
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhum pedido encontrado</div>
            )}
          </div>
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Nova compra" onClick={() => navigate('purchase-form')} />
      <BottomNav active="op" />
    </>
  )
}
