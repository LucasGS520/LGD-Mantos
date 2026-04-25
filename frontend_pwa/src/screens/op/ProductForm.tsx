import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Input, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import type { Product, Supplier } from '../../services/types'
import { useNav } from '../../nav'

interface VariantRow { size: string; color: string; qty: string; min: string }

export default function ProductForm() {
  const { back, params } = useNav()
  const productId = params.productId as string | undefined

  const [loading, setLoading] = useState(!!productId)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [suppliers, setSuppliers] = useState<Supplier[]>([])

  const [sku, setSku] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [supplierId, setSupplierId] = useState('')
  const [costPrice, setCostPrice] = useState('')
  const [salePrice, setSalePrice] = useState('')
  const [variants, setVariants] = useState<VariantRow[]>([
    { size: 'P', color: 'Preto', qty: '0', min: '3' },
    { size: 'M', color: 'Preto', qty: '0', min: '3' },
    { size: 'G', color: 'Preto', qty: '0', min: '3' },
  ])

  useEffect(() => {
    api.get<Supplier[]>('/suppliers').then(setSuppliers).catch(() => {})
    if (productId) {
      api.get<Product>(`/products/${productId}`)
        .then(p => {
          setSku(p.sku)
          setName(p.name)
          setDescription(p.description ?? '')
          setCategoryId(p.category_id ?? '')
          setSupplierId(p.supplier_id ?? '')
          setCostPrice(String(p.cost_price))
          setSalePrice(String(p.sale_price))
          setVariants(p.variants.map(v => ({
            size: v.size,
            color: v.color,
            qty: String(v.stock_quantity),
            min: String(v.min_stock_alert),
          })))
        })
        .catch(e => setError(e instanceof Error ? e.message : 'Erro'))
        .finally(() => setLoading(false))
    }
  }, [productId])

  const margin = costPrice && salePrice
    ? (((parseFloat(salePrice) - parseFloat(costPrice)) / parseFloat(salePrice)) * 100).toFixed(0)
    : '—'

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const body = {
        sku: sku.trim(),
        name: name.trim(),
        description: description.trim() || null,
        category_id: categoryId.trim() || null,
        supplier_id: supplierId.trim() || null,
        cost_price: parseFloat(costPrice) || 0,
        sale_price: parseFloat(salePrice) || 0,
        variants: variants.map(v => ({
          size: v.size.trim(),
          color: v.color.trim(),
          stock_quantity: parseInt(v.qty) || 0,
          min_stock_alert: parseInt(v.min) || 0,
        })),
      }
      if (productId) {
        await api.put(`/products/${productId}`, body)
      } else {
        await api.post('/products', body)
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const addVariant = () => setVariants(prev => [...prev, { size: '', color: '', qty: '0', min: '3' }])
  const removeVariant = (i: number) => setVariants(prev => prev.filter((_, j) => j !== i))
  const updateVariant = (i: number, key: keyof VariantRow, val: string) =>
    setVariants(prev => prev.map((v, j) => j === i ? { ...v, [key]: val } : v))

  if (loading) return <><AppBar back title={productId ? 'Editar produto' : 'Novo produto'} /><LoadingBody /></>

  return (
    <>
      <AppBar back title={productId ? 'Editar produto' : 'Novo produto'} action={
        <span onClick={handleSave} style={{ fontSize: 13, fontWeight: 700, color: saving ? 'var(--text-3)' : 'var(--gold-500)', cursor: 'pointer' }}>
          {saving ? 'Salvando…' : 'Salvar'}
        </span>
      } />
      <ScreenBody>
        {error && (
          <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B', fontWeight: 600 }}>
            {error}
          </div>
        )}

        <Section title="Identificação" top={4}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Input label="SKU" value={sku} onChange={e => setSku(e.target.value)} placeholder="LGD-CAM-001" />
            <Input label="Nome" value={name} onChange={e => setName(e.target.value)} placeholder="Nome do produto" />
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>Descrição</div>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Descrição do produto…"
                rows={3}
                style={{ width: '100%', padding: '12px 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 14, resize: 'none', outline: 0, fontFamily: 'inherit' }}
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <Input label="Categoria" value={categoryId} onChange={e => setCategoryId(e.target.value)} placeholder="Ex: Camisetas" />
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>Fornecedor</div>
                <select
                  value={supplierId}
                  onChange={e => setSupplierId(e.target.value)}
                  style={{ width: '100%', height: 46, padding: '0 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: supplierId ? 'var(--text-1)' : 'var(--text-3)', fontSize: 15, outline: 0, appearance: 'none' }}
                >
                  <option value="">Selecionar</option>
                  {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>
            </div>
          </div>
        </Section>

        <Section title="Preço" top={20}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <Input label="Custo" prefix="R$" value={costPrice} onChange={e => setCostPrice(e.target.value)} placeholder="0,00" type="number" />
            <Input label="Preço venda" prefix="R$" value={salePrice} onChange={e => setSalePrice(e.target.value)} placeholder="0,00" hint={`Margem ${margin}%`} type="number" />
          </div>
        </Section>

        <Section title="Variantes" action={<span onClick={addVariant} style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Linha</span>} top={20}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 56px 56px 28px', gap: 8, fontSize: 9.5, color: 'var(--text-4)', textTransform: 'uppercase', padding: '0 10px', letterSpacing: 0.4 }}>
              <span>Tamanho</span><span>Cor</span><span>Qtd</span><span>Mín</span><span />
            </div>
            {variants.map((v, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 56px 56px 28px', gap: 8, alignItems: 'center', padding: 10, background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                <input value={v.size} onChange={e => updateVariant(i, 'size', e.target.value)} placeholder="P" style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--gold-300)', fontSize: 13, fontWeight: 700, textAlign: 'center', outline: 0 }} />
                <input value={v.color} onChange={e => updateVariant(i, 'color', e.target.value)} placeholder="Preto" style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 13, textAlign: 'center', outline: 0, padding: '0 6px' }} />
                <input value={v.qty} onChange={e => updateVariant(i, 'qty', e.target.value)} type="number" style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, fontWeight: 700, textAlign: 'center', outline: 0 }} />
                <input value={v.min} onChange={e => updateVariant(i, 'min', e.target.value)} type="number" style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-3)', fontSize: 13, textAlign: 'center', outline: 0 }} />
                <div onClick={() => removeVariant(i)} style={{ cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                  <Ico.close size={16} stroke="var(--text-3)" />
                </div>
              </div>
            ))}
          </div>
        </Section>
      </ScreenBody>
    </>
  )
}
