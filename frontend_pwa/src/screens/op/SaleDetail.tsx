import { useEffect, useState } from 'react'
import { KPI, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import type { Sale, SaleChannel, Product } from '../../services/types'
import { useNav } from '../../nav'

interface VariantInfo { productName: string; size: string; color: string }

function fmtDateTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
      <span style={{ fontSize: 12, color: 'var(--text-3)', flexShrink: 0 }}>{label}</span>
      <span style={{ fontSize: 12.5, fontWeight: 600, textAlign: 'right' }}>{value}</span>
    </div>
  )
}

export default function SaleDetail() {
  const { params, back } = useNav()
  const sale = params.sale as Sale | undefined
  const [variantMap, setVariantMap] = useState<Record<string, VariantInfo>>({})
  const [channelMap, setChannelMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!sale) { back(); return }
    Promise.all([
      api.get<Product[]>('/products'),
      api.get<SaleChannel[]>('/channels'),
    ]).then(([products, channels]) => {
      const vm: Record<string, VariantInfo> = {}
      for (const p of products) {
        for (const v of p.variants) {
          vm[v.id] = { productName: p.name, size: v.size, color: v.color }
        }
      }
      setVariantMap(vm)
      setChannelMap(Object.fromEntries(channels.map(c => [c.id, c.name])))
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (!sale) return null

  const dateStr = fmtDateTime(sale.sold_at)
  const channelName = sale.sale_channel_id ? (channelMap[sale.sale_channel_id] ?? '—') : 'Sem canal'
  const totalQty = sale.items.reduce((s, i) => s + i.quantity, 0)

  return (
    <>
      <AppBar title={`Venda #${sale.id.slice(0, 8)}`} subtitle={dateStr} back />

      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <KPI label="Total" value={fmtBRL(sale.total)} big />
          <KPI label="Itens vendidos" value={String(totalQty)} big />
        </div>
      </div>

      {loading ? <LoadingBody /> : (
        <ScreenBody>
          <Section title="Detalhes" top={14}>
            <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, padding: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <Row label="Canal" value={channelName} />
              <Row label="Data" value={dateStr} />
              {sale.notes && <Row label="Observação" value={sale.notes} />}
            </div>
          </Section>

          <Section title={`Produtos (${sale.items.length})`} top={18}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {sale.items.map(item => {
                const info = variantMap[item.variant_id]
                const subtotal = item.quantity * item.unit_price
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
                          {item.quantity}× {fmtBRL(item.unit_price)}
                        </div>
                      </div>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: 'var(--gold-300)', flexShrink: 0 }}>
                        {fmtBRL(subtotal)}
                      </div>
                    </div>
                  </div>
                )
              })}
              {sale.items.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 24 }}>Nenhum item</div>
              )}
            </div>
          </Section>
        </ScreenBody>
      )}
    </>
  )
}
