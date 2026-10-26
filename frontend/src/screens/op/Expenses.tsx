import { useState } from 'react'
import { Ico } from '../../components/Icons'
import { Badge, Section, Btn, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Expense } from '../../services/types'

const CATEGORIES = ['Frete', 'Embalagem', 'Marketing', 'Aluguel', 'Salário', 'Outros']

function fmtExpenseDate(d: string) {
  try { return new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) }
  catch { return d }
}

export default function Expenses() {
  const { data: expenses, loading, error, reload } = useData<Expense[]>(() => api.get('/expenses'))

  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [savingForm, setSavingForm] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [formDate, setFormDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [formCategory, setFormCategory] = useState('Frete')
  const [formDescription, setFormDescription] = useState('')
  const [formAmount, setFormAmount] = useState('')

  const totalMonth = (expenses ?? []).reduce((s, e) => s + e.amount, 0)

  const categoryTotals = CATEGORIES.map(cat => ({
    label: cat,
    val: (expenses ?? []).filter(e => e.category === cat).reduce((s, e) => s + e.amount, 0),
  })).filter(c => c.val > 0)

  const openCreate = () => {
    setEditingId(null)
    setFormDate(new Date().toISOString().slice(0, 10))
    setFormCategory('Frete')
    setFormDescription('')
    setFormAmount('')
    setFormError(null)
    setShowForm(v => !v)
  }

  const startEdit = (e: Expense) => {
    setEditingId(e.id)
    setFormDate(e.date)
    setFormCategory(e.category)
    setFormDescription(e.description ?? '')
    setFormAmount(String(e.amount))
    setFormError(null)
    setShowForm(true)
    setConfirmDeleteId(null)
  }

  const closeForm = () => {
    setShowForm(false)
    setEditingId(null)
  }

  const handleSaveExpense = async () => {
    if (!formDescription.trim() || !formAmount) { setFormError('Preencha todos os campos'); return }
    setSavingForm(true)
    setFormError(null)
    try {
      const body = {
        date: formDate,
        category: formCategory,
        description: formDescription.trim(),
        amount: parseFloat(formAmount.replace(',', '.')),
      }
      if (editingId) {
        await api.put(`/expenses/${editingId}`, body)
      } else {
        await api.post('/expenses', body)
      }
      closeForm()
      setFormDescription('')
      setFormAmount('')
      reload()
    } catch (e) {
      setFormError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSavingForm(false)
    }
  }

  const handleDelete = async (id: string) => {
    setDeletingId(id)
    try {
      await api.delete(`/expenses/${id}`)
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
      <AppBar title="Despesas" subtitle={loading ? '…' : `${fmtBRL(totalMonth)} no total`} />
      <OpSubNav active="expenses" />

      {!loading && !error && categoryTotals.length > 0 && (
        <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
          <div style={{ display: 'grid', gridTemplateColumns: `repeat(${Math.min(categoryTotals.length, 4)},1fr)`, gap: 6 }}>
            {categoryTotals.slice(0, 4).map(c => (
              <div key={c.label} style={{ padding: '10px 8px', background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 10, textAlign: 'center' }}>
                <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase' }}>{c.label}</div>
                <div className="tnum" style={{ fontSize: 13, fontWeight: 700, marginTop: 3 }}>{fmtBRL(c.val)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showForm && (
        <div style={{ padding: '0 18px 10px', flexShrink: 0 }}>
          <div style={{ background: 'var(--bg-1)', border: '1px solid var(--gold-500)', borderRadius: 14, padding: 14 }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 12 }}>{editingId ? 'Editar despesa' : 'Nova despesa'}</div>
            {formError && <div style={{ marginBottom: 10, fontSize: 12, color: '#F5847B' }}>{formError}</div>}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <div>
                <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Data</div>
                <input type="date" value={formDate} onChange={e => setFormDate(e.target.value)} style={{ width: '100%', height: 38, padding: '0 10px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }} />
              </div>
              <div>
                <div style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 4 }}>Categoria</div>
                <select value={formCategory} onChange={e => setFormCategory(e.target.value)} style={{ width: '100%', height: 38, padding: '0 10px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }}>
                  {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <input value={formDescription} onChange={e => setFormDescription(e.target.value)} placeholder="Descrição" style={{ width: '100%', height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0, marginBottom: 10 }} />
            <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
              <span style={{ color: 'var(--text-3)', fontSize: 14 }}>R$</span>
              <input
                type="text"
                inputMode="decimal"
                value={formAmount}
                onChange={e => setFormAmount(e.target.value.replace(/[^0-9.,]/g, ''))}
                placeholder="0,00"
                style={{ flex: 1, height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }}
              />
              <Btn kind="ghost" size="sm" onClick={closeForm}>Cancelar</Btn>
              <Btn kind="primary" size="sm" icon={Ico.check} onClick={handleSaveExpense}>{savingForm ? '…' : 'Salvar'}</Btn>
            </div>
          </div>
        </div>
      )}

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <Section title="Recentes" top={14}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {(expenses ?? []).map(e => (
                <div key={e.id} style={{ background: 'var(--bg-1)', border: `1px solid ${confirmDeleteId === e.id ? 'rgba(232,88,79,0.3)' : 'var(--line-1)'}`, borderRadius: 12, overflow: 'hidden' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12 }}>
                    <div style={{ width: 38, height: 38, borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                      <Ico.receipt size={18} stroke="var(--gold-500)" />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {e.description ?? e.category}
                      </div>
                      <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 3 }}>
                        <Badge tone="neutral">{e.category}</Badge>
                        <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{fmtExpenseDate(e.date)}</span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: '#F5847B' }}>−{fmtBRL(e.amount)}</div>
                      <div onClick={() => startEdit(e)} style={{ cursor: 'pointer', opacity: 0.5 }}>
                        <Ico.edit size={14} stroke="var(--text-2)" />
                      </div>
                      <div onClick={() => setConfirmDeleteId(confirmDeleteId === e.id ? null : e.id)} style={{ cursor: 'pointer', opacity: 0.5 }}>
                        <Ico.trash size={14} stroke="#F5847B" />
                      </div>
                    </div>
                  </div>
                  {confirmDeleteId === e.id && (
                    <div style={{ padding: '8px 12px 12px', borderTop: '1px solid rgba(232,88,79,0.2)', background: 'rgba(232,88,79,0.04)', display: 'flex', gap: 8 }}>
                      <button onClick={() => setConfirmDeleteId(null)} style={{ flex: 1, height: 34, borderRadius: 8, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}>Cancelar</button>
                      <button
                        onClick={() => handleDelete(e.id)}
                        style={{ flex: 1, height: 34, borderRadius: 8, background: 'rgba(232,88,79,0.12)', border: '1px solid rgba(232,88,79,0.3)', color: '#F5847B', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}
                      >{deletingId === e.id ? 'Removendo…' : 'Confirmar remoção'}</button>
                    </div>
                  )}
                </div>
              ))}
              {(expenses ?? []).length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhuma despesa registrada</div>
              )}
            </div>
          </Section>
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Despesa" onClick={openCreate} />
      <BottomNav active="op" />
    </>
  )
}
