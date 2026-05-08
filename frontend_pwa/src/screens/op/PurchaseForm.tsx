import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Btn, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import type { Supplier, Product, Variant } from '../../services/types'
import { useNav } from '../../nav'

interface OrderItem {
  variant: Variant & { productName: string }
  qty: string
  unitCost: string
}

const inputStyle: React.CSSProperties = {
  height: 32, borderRadius: 8,
  background: 'var(--bg-3)', border: '1px solid var(--line-2)',
  color: 'var(--text-1)', fontSize: 13, textAlign: 'center', outline: 0,
}

export default function PurchaseForm() {
  const { back, params } = useNav()
  const purchaseId = params.purchaseId as string | undefined

  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [supplierId, setSupplierId] = useState('')
  const [notes, setNotes] = useState('')
  const [items, setItems] = useState<OrderItem[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPicker, setShowPicker] = useState(false)
  const [loadingInit, setLoadingInit] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get<Supplier[]>('/suppliers'),
      api.get<Product[]>('/products'),
    ]).then(([s, p]) => {
      setSuppliers(s)
      setProducts(p)
    }).catch(() => {}).finally(() => setLoadingInit(false))
  }, [])

  const addItem = (product: Product, variant: Variant) => {
    setItems(prev => {
      const existing = prev.findIndex(i => i.variant.id === variant.id)
      if (existing >= 0) {
        return prev.map((i, j) => j === existing
          ? { ...i, qty: String(parseInt(i.qty || '0') + 1) }
          : i)
      }
      return [...prev, {
        variant: { ...variant, productName: product.name },
        qty: '1',
        unitCost: String(product.cost_price),
      }]
    })
    setShowPicker(false)
  }

  const updateItem = (variantId: string, key: 'qty' | 'unitCost', value: string) => {
    if (key === 'qty' && (value === '' || parseInt(value) <= 0)) {
      setItems(prev => prev.filter(i => i.variant.id !== variantId))
    } else {
      setItems(prev => prev.map(i => i.variant.id === variantId ? { ...i, [key]: value } : i))
    }
  }

  const parseQty = (s: string) => Math.max(1, parseInt(s) || 1)
  const parseCost = (s: string) => parseFloat(s.replace(',', '.')) || 0

  const total = items.reduce((s, i) => s + parseQty(i.qty) * parseCost(i.unitCost), 0)
  const units = items.reduce((s, i) => s + parseQty(i.qty), 0)

  const selectedSupplier = suppliers.find(s => s.id === supplierId)

  const handleSave = async () => {
    if (!supplierId) { setError('Selecione um fornecedor'); return }
    setSaving(true)
    setError(null)
    try {
      const body = {
        supplier_id: supplierId,
        order_date: new Date().toISOString().slice(0, 10),
        notes: notes.trim() || null,
        items: items.map(i => ({
          variant_id: i.variant.id,
          quantity: parseQty(i.qty),
          unit_cost: parseCost(i.unitCost),
        })),
      }
      if (purchaseId) {
        await api.put(`/purchases/${purchaseId}/receive`, {})
      } else {
        await api.post('/purchases', body)
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
      setSaving(false)
    }
  }

  if (loadingInit) return <><AppBar back title={purchaseId ? 'Receber pedido' : 'Nova compra'} /><LoadingBody /></>

  return (
    <>
      <AppBar back title={purchaseId ? 'Receber pedido' : 'Nova compra'} action={
        <span onClick={handleSave} style={{ fontSize: 13, fontWeight: 700, color: saving ? 'var(--text-3)' : 'var(--gold-500)', cursor: 'pointer' }}>
          {saving ? 'Salvando…' : 'Salvar'}
        </span>
      } />
      <ScreenBody>
        {error && (
          <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B' }}>{error}</div>
        )}

        <Section title="Fornecedor" top={4}>
          <select
            value={supplierId}
            onChange={e => setSupplierId(e.target.value)}
            style={{ width: '100%', height: 46, padding: '0 14px', borderRadius: 12, background: 'var(--bg-1)', border: `1px solid ${supplierId ? 'var(--gold-500)' : 'var(--line-1)'}`, color: supplierId ? 'var(--text-1)' : 'var(--text-3)', fontSize: 14, fontWeight: supplierId ? 700 : 400, outline: 0 }}
          >
            <option value="">Selecionar fornecedor…</option>
            {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          {selectedSupplier?.phone && (
            <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 6 }}>
              {selectedSupplier.phone}
              {selectedSupplier.contact && ` · ${selectedSupplier.contact}`}
            </div>
          )}
        </Section>

        <Section title={`Itens · ${items.length}`} action={<span onClick={() => setShowPicker(v => !v)} style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Item</span>} top={18}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {showPicker && (
              <div style={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 12, maxHeight: 250, overflow: 'auto' }} className="lgd-scroll">
                {products.map(p => p.variants.map(v => (
                  <div key={v.id} onClick={() => addItem(p, v)} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderTop: '1px solid var(--line-1)', cursor: 'pointer' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 12, fontWeight: 600 }}>{p.name}</div>
                      <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>{v.size} · {v.color} · estoque: {v.stock_quantity}</div>
                    </div>
                    <span className="tnum" style={{ fontSize: 12, color: 'var(--text-3)' }}>{fmtBRL(p.cost_price)}</span>
                  </div>
                )))}
              </div>
            )}

            {items.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 52px 72px 28px', gap: 8, fontSize: 9.5, color: 'var(--text-4)', textTransform: 'uppercase', padding: '0 2px', letterSpacing: 0.4 }}>
                <span>Produto</span><span style={{ textAlign: 'center' }}>Qtd</span><span style={{ textAlign: 'center' }}>Custo/un</span><span />
              </div>
            )}

            {items.map((it) => (
              <div key={it.variant.id} style={{ display: 'grid', gridTemplateColumns: '1fr 52px 72px 28px', gap: 8, alignItems: 'center', padding: '8px 10px', background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{it.variant.productName}</div>
                  <div style={{ fontSize: 10.5, color: 'var(--text-3)', marginTop: 2 }}>{it.variant.size} · {it.variant.color}</div>
                </div>
                <input
                  type="text"
                  inputMode="numeric"
                  value={it.qty}
                  onChange={e => updateItem(it.variant.id, 'qty', e.target.value.replace(/[^0-9]/g, ''))}
                  style={{ ...inputStyle, width: '100%' }}
                />
                <input
                  type="text"
                  inputMode="decimal"
                  value={it.unitCost}
                  onChange={e => updateItem(it.variant.id, 'unitCost', e.target.value.replace(/[^0-9.,]/g, ''))}
                  style={{ ...inputStyle, width: '100%' }}
                />
                <div onClick={() => setItems(prev => prev.filter(i => i.variant.id !== it.variant.id))} style={{ cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                  <Ico.close size={14} stroke="var(--text-3)" />
                </div>
              </div>
            ))}
          </div>
        </Section>

        <Section title="Observações" top={18}>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="Observações do pedido…"
            rows={2}
            style={{ width: '100%', padding: '12px 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 14, resize: 'none', outline: 0, fontFamily: 'inherit' }}
          />
        </Section>

        <div style={{ marginTop: 18, padding: 14, borderRadius: 14, background: 'linear-gradient(180deg, rgba(212,168,71,0.08), rgba(212,168,71,0.02))', border: '1px solid rgba(212,168,71,0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12.5, color: 'var(--text-2)', marginBottom: 4 }}>
            <span>Itens</span><span className="tnum">{units} unidades</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
            <span style={{ fontSize: 13, fontWeight: 700 }}>Total estimado</span>
            <span className="tnum" style={{ fontSize: 22, fontWeight: 800, color: 'var(--gold-300)' }}>{fmtBRL(total)}</span>
          </div>
        </div>

        <Btn kind="primary" full size="lg" icon={Ico.check} onClick={handleSave} style={{ marginTop: 14 }}>
          {saving ? 'Salvando…' : purchaseId ? 'Confirmar recebimento' : 'Salvar pedido'}
        </Btn>
      </ScreenBody>
    </>
  )
}
