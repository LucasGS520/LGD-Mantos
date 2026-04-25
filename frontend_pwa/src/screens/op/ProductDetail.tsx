import { useEffect, useState } from 'react'
import { Ico } from '../../components/Icons'
import { Badge, Card, Btn, PhotoPlaceholder, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import type { Product } from '../../services/types'
import { useNav } from '../../nav'

export default function ProductDetail() {
  const { navigate, params, back } = useNav()
  const productId = params.productId as string | undefined
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!productId) { back(); return }
    setLoading(true)
    setError(null)
    api.get<Product>(`/products/${productId}`)
      .then(setProduct)
      .catch(e => setError(e instanceof Error ? e.message : 'Erro ao carregar produto'))
      .finally(() => setLoading(false))
  }, [productId])

  const totalStock = product ? product.variants.reduce((s, v) => s + v.stock_quantity, 0) : 0
  const margin = product ? ((product.sale_price - product.cost_price) / product.sale_price * 100).toFixed(1) : '0'

  return (
    <>
      <AppBar back title="Detalhe" action={
        <button style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center' }}>
          <Ico.options size={18} stroke="var(--text-1)" />
        </button>
      } />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={() => navigate('product-detail', { productId })} /> : product ? (
        <ScreenBody pad={0}>
          <div style={{ position: 'relative', height: 280, background: 'var(--bg-2)', flexShrink: 0 }}>
            {product.photos && product.photos.length > 0
              ? <img src={product.photos[0]} style={{ width: '100%', height: '100%', objectFit: 'cover' }} alt={product.name} />
              : <PhotoPlaceholder size="100%" radius={0} label={product.sku} style={{ width: '100%', height: '100%' }} />
            }
          </div>

          <div style={{ padding: '18px' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-3)', marginBottom: 4 }}>{product.sku}</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-1)', letterSpacing: -0.4, marginBottom: 8 }}>{product.name}</div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 14, flexWrap: 'wrap' }}>
              {product.category_id && <Badge tone="gold">{product.category_id}</Badge>}
              {product.supplier_id && <Badge tone="neutral">{product.supplier_id}</Badge>}
              <Badge tone="neutral">{totalStock} unidades</Badge>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 16 }}>
              <Card padding={10}>
                <div style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 600 }}>Custo</div>
                <div className="tnum" style={{ fontSize: 14, fontWeight: 700, marginTop: 2 }}>{fmtBRL(product.cost_price)}</div>
              </Card>
              <Card padding={10}>
                <div style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 600 }}>Venda</div>
                <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: 'var(--gold-300)', marginTop: 2 }}>{fmtBRL(product.sale_price)}</div>
              </Card>
              <Card padding={10}>
                <div style={{ fontSize: 10, color: 'var(--text-3)', textTransform: 'uppercase', fontWeight: 600 }}>Margem</div>
                <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: '#5DD49E', marginTop: 2 }}>{margin}%</div>
              </Card>
            </div>

            <Section title={`Variantes · ${product.variants.length}`} action={<span style={{ fontSize: 12, fontWeight: 600, color: 'var(--gold-500)' }}>+ Adicionar</span>} top={4}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {product.variants.map(v => (
                  <div key={v.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 12px', background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 10, display: 'grid', placeItems: 'center', background: 'var(--bg-3)', color: 'var(--gold-300)', fontSize: 13, fontWeight: 800, border: '1px solid var(--line-2)' }}>{v.size}</div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 13, fontWeight: 600 }}>{v.color}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 1 }}>mín. {v.min_stock_alert}</div>
                    </div>
                    <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: v.stock_quantity === 0 ? '#F5847B' : v.stock_quantity < v.min_stock_alert ? '#F5BF7A' : 'var(--text-1)' }}>
                      {v.stock_quantity}
                    </div>
                  </div>
                ))}
                {product.variants.length === 0 && (
                  <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 16 }}>Sem variantes cadastradas</div>
                )}
              </div>
            </Section>

            {product.description && (
              <Section title="Descrição" top={18}>
                <div style={{ fontSize: 13.5, color: 'var(--text-2)', lineHeight: 1.55 }}>{product.description}</div>
              </Section>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 22 }}>
              <Btn kind="ghost" icon={Ico.edit} onClick={() => navigate('product-form', { productId: product.id })}>Editar</Btn>
              <Btn kind="primary" icon={Ico.cart} onClick={() => navigate('sale-modal', { productId: product.id })}>Vender</Btn>
            </div>
          </div>
        </ScreenBody>
      ) : null}
    </>
  )
}
