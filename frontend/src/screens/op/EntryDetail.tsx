import { useEffect, useState } from 'react'
import { KPI, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import type { MerchandiseEntry, Supplier, Product } from '../../services/types'
import { useNav } from '../../nav'

interface VariantInfo { productName: string; size: string; color: string }

function fmtDate(d: string): string {
  try { return new Date(d + 'T00:00:00').toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' }) }
  catch { return d }
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
      <span style={{ fontSize: 12, color: 'var(--text-3)', flexShrink: 0 }}>{label}</span>
      <span style={{ fontSize: 12.5, fontWeight: 600, textAlign: 'right' }}>{value}</span>
    </div>
  )
}

export default function EntryDetail() {
  const { params, back } = useNav()
  const entry = params.entry as MerchandiseEntry | undefined
  const [variantMap, setVariantMap] = useState<Record<string, VariantInfo>>({})
  const [supName, setSupName] = useState<string>('Sem fornecedor')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!entry) { back(); return }
    Promise.all([
      api.get<Product[]>('/products'),
      api.get<Supplier[]>('/suppliers'),
    ]).then(([products, suppliers]) => {
      const vm: Record<string, VariantInfo> = {}
      for (const p of products) {
        for (const v of p.variants) {
          vm[v.id] = { productName: p.name, size: v.size, color: v.color }
        }
      }
      setVariantMap(vm)
      if (entry.supplier_id) {
        const sup = suppliers.find(s => s.id === entry.supplier_id)
        if (sup) setSupName(sup.name)
      }
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (!entry) return null

  const dateStr = fmtDate(entry.entry_date)

  return (
    <>
      <AppBar title={`Entrada #${entry.id.slice(0, 8)}`} subtitle={dateStr} back />

      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <KPI label="Custo total" value={fmtBRL(entry.total_cost)} big />
          <KPI label="Variantes" value={String(entry.variants_added)} big />
        </div>
      </div>

      {loading ? <LoadingBody /> : (
        <ScreenBody>
          <Section title="Detalhes" top={14}>
            <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, padding: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <Row label="Fornecedor" value={supName} />
              <Row label="Data" value={dateStr} />
              {entry.notes && <Row label="Observação" value={entry.notes} />}
            </div>
          </Section>

          <Section title={`Itens (${entry.items.length})`} top={18}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {entry.items.map(item => {
                const info = variantMap[item.variant_id]
                const subtotal = item.quantity * item.unit_cost
                return (
                  <div key={item.id} style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, padding: 12 }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 8 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: 13.5, marginBottom: 3 }}>
                          {info ? info.productName : `Variante #${item.variant_id.slice(0, 6)}`}
                        </div>
                        {info && (
                          <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginBottom: 2 }}>
                            {[info.size, info.color].filter(Boolean).join(' · ')}
                          </div>
                        )}
                        <div style={{ fontSize: 12, color: 'var(--text-3)' }}>
                          {item.quantity}× {fmtBRL(item.unit_cost)} / un
                        </div>
                      </div>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: 'var(--gold-300)', flexShrink: 0 }}>
                        {fmtBRL(subtotal)}
                      </div>
                    </div>
                  </div>
                )
              })}
              {entry.items.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 24 }}>Nenhum item registrado</div>
              )}
            </div>
          </Section>
        </ScreenBody>
      )}
    </>
  )
}
