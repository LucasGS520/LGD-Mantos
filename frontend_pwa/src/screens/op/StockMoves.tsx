import { useState, useEffect } from 'react'
import { Ico, type IcoProps } from '../../components/Icons'
import { Tabs, Section } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import type { Product, Variant, StockMovement } from '../../services/types'

type MoveType = 'entrada' | 'saida' | 'ajuste'

const moveMeta: Record<MoveType, { color: string; icon: (p: IcoProps) => JSX.Element; sign: string; bg: string }> = {
  entrada: { color: '#5DD49E', icon: Ico.upload,  sign: '+', bg: 'rgba(63,184,124,0.10)'  },
  saida:   { color: '#F5847B', icon: Ico.cart,    sign: '−', bg: 'rgba(232,88,79,0.10)'   },
  ajuste:  { color: '#F5BF7A', icon: Ico.edit,    sign: '±', bg: 'rgba(232,160,74,0.10)'  },
}

const MOVE_LABELS: Record<MoveType, string> = {
  entrada: 'Entrada', saida: 'Saída', ajuste: 'Ajuste',
}

const ALL_MOVE_META: Record<string, typeof moveMeta['entrada']> = {
  ...moveMeta,
  devolucao: { color: '#8BC0E8', icon: Ico.refresh, sign: '+', bg: 'rgba(94,168,224,0.10)' },
}

const HIST_TABS = ['Tudo', 'Entrada', 'Saída', 'Ajuste']
const HIST_TAB_TYPE: Record<string, string> = {
  'Entrada': 'entrada', 'Saída': 'saida', 'Ajuste': 'ajuste',
}

function fmtMoveDate(iso: string) {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) + ' ' +
           d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  } catch { return iso }
}

export default function StockMoves() {
  const [products, setProducts] = useState<Product[]>([])
  const [showPicker, setShowPicker] = useState(false)
  const [selected, setSelected] = useState<(Variant & { productName: string }) | null>(null)
  const [moveType, setMoveType] = useState<MoveType>('ajuste')
  const [qty, setQty] = useState('1')
  const [unitCost, setUnitCost] = useState('')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [history, setHistory] = useState<StockMovement[]>([])
  const [histTab, setHistTab] = useState('Tudo')
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    api.get<Product[]>('/products').then(setProducts).catch(() => {})
  }, [])

  const loadHistory = (variantId: string) => {
    api.get<StockMovement[]>(`/stock/history/${variantId}`).then(setHistory).catch(() => {})
  }

  const selectVariant = (product: Product, variant: Variant) => {
    setSelected({ ...variant, productName: product.name })
    setShowPicker(false)
    loadHistory(variant.id)
  }

  const handleSave = async () => {
    if (!selected) { setError('Selecione uma variante'); return }
    setSaving(true)
    setError(null)
    try {
      const body: Record<string, unknown> = {
        variant_id: selected.id,
        movement_type: moveType,
        quantity: Math.max(1, parseInt(qty) || 1),
        notes: notes.trim() || null,
      }
      if (moveType === 'entrada' && unitCost) {
        body.unit_cost = parseFloat(unitCost.replace(',', '.')) || 0
      }
      await api.post('/stock/movements', body)
      setSuccess(true)
      setQty('1')
      setUnitCost('')
      setNotes('')
      loadHistory(selected.id)
      setTimeout(() => setSuccess(false), 3000)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const filteredHistory = histTab === 'Tudo'
    ? history
    : history.filter(m => m.movement_type === HIST_TAB_TYPE[histTab])

  return (
    <>
      <AppBar title="Estoque" subtitle="Movimentações manuais" />
      <OpSubNav active="stock-moves" />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <Tabs items={HIST_TABS} active={histTab} onChange={setHistTab} />
      </div>

      {showForm && (
        <div style={{ padding: '0 18px 10px', flexShrink: 0 }}>
          <div style={{ background: 'var(--bg-1)', border: '1px solid var(--gold-500)', borderRadius: 14, padding: 14 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 13 }}>Nova movimentação</div>
              <div onClick={() => setShowForm(false)} style={{ cursor: 'pointer', opacity: 0.6 }}>
                <Ico.close size={16} stroke="var(--text-2)" />
              </div>
            </div>

            {error && <div style={{ marginBottom: 10, fontSize: 12, color: '#F5847B' }}>{error}</div>}

            {/* Variant picker */}
            {selected ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', background: 'var(--bg-3)', border: '1px solid var(--line-2)', borderRadius: 10, marginBottom: 12 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{selected.productName}</div>
                  <div style={{ fontSize: 10.5, color: 'var(--text-3)', marginTop: 2 }}>{selected.size} · {selected.color} · estoque atual: <strong style={{ color: 'var(--text-1)' }}>{selected.stock_quantity}</strong></div>
                </div>
                <div onClick={() => setShowPicker(v => !v)} style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer', flexShrink: 0 }}>Trocar</div>
              </div>
            ) : (
              <div
                onClick={() => setShowPicker(v => !v)}
                style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, height: 42, marginBottom: 12, border: '1.5px dashed var(--line-3)', borderRadius: 10, cursor: 'pointer', color: 'var(--gold-500)', fontWeight: 600, fontSize: 13 }}
              >
                <Ico.plus size={15} stroke="var(--gold-500)" /> Selecionar variante
              </div>
            )}

            {showPicker && (
              <div style={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 10, maxHeight: 220, overflow: 'auto', marginBottom: 12 }} className="lgd-scroll">
                {products.map(p => p.variants.map(v => (
                  <div key={v.id} onClick={() => selectVariant(p, v)} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', borderTop: '1px solid var(--line-1)', cursor: 'pointer' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 12, fontWeight: 600 }}>{p.name}</div>
                      <div style={{ fontSize: 10.5, color: 'var(--text-3)' }}>{v.size} · {v.color}</div>
                    </div>
                    <span className="tnum" style={{ fontSize: 12, color: 'var(--text-3)' }}>est. {v.stock_quantity}</span>
                  </div>
                )))}
              </div>
            )}

            {/* Type selector */}
            <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
              {(Object.keys(MOVE_LABELS) as MoveType[]).map(t => (
                <div key={t} onClick={() => setMoveType(t)} style={{
                  flex: 1, padding: '7px 4px', borderRadius: 8, fontSize: 11.5, fontWeight: 700,
                  textAlign: 'center', cursor: 'pointer',
                  background: moveType === t ? moveMeta[t].bg : 'var(--bg-3)',
                  border: `1px solid ${moveType === t ? moveMeta[t].color : 'var(--line-2)'}`,
                  color: moveType === t ? moveMeta[t].color : 'var(--text-3)',
                }}>{MOVE_LABELS[t]}</div>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: moveType === 'entrada' ? '1fr 1fr' : '1fr', gap: 10, marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Quantidade</div>
                <input
                  type="text"
                  inputMode="numeric"
                  value={qty}
                  onChange={e => setQty(e.target.value.replace(/[^0-9]/g, ''))}
                  placeholder="1"
                  style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }}
                />
              </div>
              {moveType === 'entrada' && (
                <div>
                  <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Custo unit. (R$)</div>
                  <input
                    type="text"
                    inputMode="decimal"
                    value={unitCost}
                    onChange={e => setUnitCost(e.target.value.replace(/[^0-9.,]/g, ''))}
                    placeholder="0,00"
                    style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }}
                  />
                </div>
              )}
            </div>

            <input
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Observações (opcional)"
              style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0, marginBottom: 10 }}
            />

            <button
              onClick={handleSave}
              style={{ width: '100%', height: 40, borderRadius: 10, background: 'var(--gold-500)', color: '#1A1408', fontWeight: 700, fontSize: 13, border: 0, cursor: saving ? 'default' : 'pointer', opacity: saving ? 0.7 : 1 }}
            >
              {saving ? 'Registrando…' : 'Registrar movimentação'}
            </button>
          </div>
        </div>
      )}

      <ScreenBody>
        {success && (
          <div style={{ padding: 12, marginBottom: 10, borderRadius: 12, background: 'rgba(63,184,124,0.12)', border: '1px solid rgba(63,184,124,0.3)', fontSize: 13, fontWeight: 600, color: '#5DD49E', textAlign: 'center' }}>
            Movimentação registrada!
          </div>
        )}

        {selected ? (
          <Section title={`Histórico · ${selected.productName} ${selected.size} ${selected.color}`} top={14}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {filteredHistory.map(m => {
                const meta = ALL_MOVE_META[m.movement_type] ?? ALL_MOVE_META.ajuste
                const MoveIcon = meta.icon
                return (
                  <div key={m.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 9, background: meta.bg, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                      <MoveIcon size={16} stroke={meta.color} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12.5, fontWeight: 600, color: meta.color }}>{MOVE_LABELS[m.movement_type as MoveType] ?? m.movement_type}</div>
                      {m.notes && <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{m.notes}</div>}
                      <div style={{ fontSize: 10.5, color: 'var(--text-4)', marginTop: 2 }}>{fmtMoveDate(m.created_at)}</div>
                    </div>
                    <div className="tnum" style={{ fontSize: 15, fontWeight: 800, color: meta.color, flexShrink: 0 }}>
                      {meta.sign}{m.quantity}
                    </div>
                  </div>
                )
              })}
              {filteredHistory.length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 24 }}>
                  Nenhuma movimentação encontrada
                </div>
              )}
            </div>
          </Section>
        ) : (
          <Section title="Histórico" top={14}>
            <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>
              Registre uma movimentação para ver o histórico da variante.
            </div>
          </Section>
        )}
      </ScreenBody>

      <FAB icon={Ico.plus} label="Movimentar" onClick={() => setShowForm(v => !v)} />
      <BottomNav active="op" />
    </>
  )
}
