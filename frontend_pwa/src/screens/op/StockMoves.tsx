import { useState } from 'react'
import { Ico, type IcoProps } from '../../components/Icons'
import { Tabs, Section, Btn } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useNav } from '../../nav'

type MoveType = 'entrada' | 'saida' | 'devolucao' | 'ajuste'
const moveMeta: Record<MoveType, { color: string; icon: (p: IcoProps) => JSX.Element; sign: string; bg: string }> = {
  entrada:   { color: '#5DD49E', icon: Ico.upload,  sign: '+', bg: 'rgba(63,184,124,0.10)'  },
  saida:     { color: '#F5847B', icon: Ico.cart,    sign: '−', bg: 'rgba(232,88,79,0.10)'   },
  devolucao: { color: '#8BC0E8', icon: Ico.refresh, sign: '+', bg: 'rgba(94,168,224,0.10)'  },
  ajuste:    { color: '#F5BF7A', icon: Ico.edit,    sign: '',  bg: 'rgba(232,160,74,0.10)'  },
}

const MOVE_TYPES: MoveType[] = ['entrada', 'saida', 'devolucao', 'ajuste']
const LABELS: Record<MoveType, string> = {
  entrada: 'Entrada', saida: 'Saída', devolucao: 'Devolução', ajuste: 'Ajuste',
}

export default function StockMoves() {
  const [showForm, setShowForm] = useState(false)
  const [moveType, setMoveType] = useState<MoveType>('entrada')
  const [variantId, setVariantId] = useState('')
  const [qty, setQty] = useState('1')
  const [unitCost, setUnitCost] = useState('0')
  const [notes, setNotes] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSave = async () => {
    if (!variantId.trim()) { setError('Informe o ID da variante'); return }
    setSaving(true)
    setError(null)
    try {
      await api.post('/stock/movements', {
        variant_id: variantId.trim(),
        movement_type: moveType,
        quantity: parseInt(qty) || 1,
        unit_cost: parseFloat(unitCost) || 0,
        notes: notes.trim() || null,
      })
      setSuccess(true)
      setShowForm(false)
      setVariantId('')
      setQty('1')
      setNotes('')
      setTimeout(() => setSuccess(false), 3000)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <AppBar title="Movimentações" subtitle="Histórico de estoque" />
      <OpSubNav active="stock-moves" />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <Tabs items={['Tudo', 'Entrada', 'Saída', 'Ajuste']} active="Tudo" />
      </div>

      {showForm && (
        <div style={{ padding: '0 18px 10px', flexShrink: 0 }}>
          <div style={{ background: 'var(--bg-1)', border: '1px solid var(--gold-500)', borderRadius: 14, padding: 14 }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 12 }}>Nova movimentação</div>
            {error && <div style={{ marginBottom: 10, fontSize: 12, color: '#F5847B' }}>{error}</div>}
            <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
              {MOVE_TYPES.map(t => (
                <div key={t} onClick={() => setMoveType(t)} style={{
                  padding: '6px 12px', borderRadius: 999, fontSize: 12, fontWeight: 700, cursor: 'pointer',
                  background: moveType === t ? moveMeta[t].bg : 'var(--bg-3)',
                  border: `1px solid ${moveType === t ? moveMeta[t].color : 'var(--line-2)'}`,
                  color: moveType === t ? moveMeta[t].color : 'var(--text-3)',
                }}>{LABELS[t]}</div>
              ))}
            </div>
            <input value={variantId} onChange={e => setVariantId(e.target.value)} placeholder="ID da variante" style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0, marginBottom: 10 }} />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Quantidade</div>
                <input type="number" value={qty} onChange={e => setQty(e.target.value)} min={1} style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }} />
              </div>
              <div>
                <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Custo unit.</div>
                <input type="number" value={unitCost} onChange={e => setUnitCost(e.target.value)} min={0} style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }} />
              </div>
            </div>
            <input value={notes} onChange={e => setNotes(e.target.value)} placeholder="Observações (opcional)" style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0, marginBottom: 10 }} />
            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
              <Btn kind="ghost" size="sm" onClick={() => setShowForm(false)}>Cancelar</Btn>
              <Btn kind="primary" size="sm" icon={Ico.check} onClick={handleSave}>{saving ? '…' : 'Registrar'}</Btn>
            </div>
          </div>
        </div>
      )}

      <ScreenBody>
        {success && (
          <div style={{ padding: 12, marginBottom: 10, borderRadius: 12, background: 'rgba(63,184,124,0.12)', border: '1px solid rgba(63,184,124,0.3)', fontSize: 13, fontWeight: 600, color: '#5DD49E', textAlign: 'center' }}>
            Movimentação registrada com sucesso!
          </div>
        )}
        <Section title="Histórico" top={14}>
          <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 24 }}>
            Selecione uma variante específica para ver o histórico de movimentações.
          </div>
        </Section>
      </ScreenBody>

      <FAB icon={Ico.plus} label="Movimentar" onClick={() => setShowForm(v => !v)} />
      <BottomNav active="op" />
    </>
  )
}
