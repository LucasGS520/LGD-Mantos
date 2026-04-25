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

  const handleAddExpense = async () => {
    if (!formDescription.trim() || !formAmount) { setFormError('Preencha todos os campos'); return }
    setSavingForm(true)
    setFormError(null)
    try {
      await api.post('/expenses', {
        date: formDate,
        category: formCategory,
        description: formDescription.trim(),
        amount: parseFloat(formAmount),
      })
      setShowForm(false)
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
    try {
      await api.delete(`/expenses/${id}`)
      reload()
    } catch { /* ignore */ }
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

      {/* Inline new expense form */}
      {showForm && (
        <div style={{ padding: '0 18px 10px', flexShrink: 0 }}>
          <div style={{ background: 'var(--bg-1)', border: '1px solid var(--gold-500)', borderRadius: 14, padding: 14 }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 12 }}>Nova despesa</div>
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
              <input type="number" value={formAmount} onChange={e => setFormAmount(e.target.value)} placeholder="0,00" style={{ flex: 1, height: 38, padding: '0 12px', borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, outline: 0 }} />
              <Btn kind="ghost" size="sm" onClick={() => setShowForm(false)}>Cancelar</Btn>
              <Btn kind="primary" size="sm" icon={Ico.check} onClick={handleAddExpense}>{savingForm ? '…' : 'Salvar'}</Btn>
            </div>
          </div>
        </div>
      )}

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <Section title="Recentes" top={14}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {(expenses ?? []).map(e => (
                <div key={e.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                  <div style={{ width: 38, height: 38, borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', display: 'grid', placeItems: 'center' }}>
                    <Ico.receipt size={18} stroke="var(--gold-500)" />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 3 }}>
                      <span style={{ fontSize: 13, fontWeight: 600 }}>{e.description ?? e.category}</span>
                    </div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <Badge tone="neutral">{e.category}</Badge>
                      <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{fmtExpenseDate(e.date)}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: '#F5847B' }}>−{fmtBRL(e.amount)}</div>
                    <div onClick={() => handleDelete(e.id)} style={{ cursor: 'pointer', opacity: 0.5 }}>
                      <Ico.trash size={14} stroke="#F5847B" />
                    </div>
                  </div>
                </div>
              ))}
              {(expenses ?? []).length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhuma despesa registrada</div>
              )}
            </div>
          </Section>
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Despesa" onClick={() => setShowForm(v => !v)} />
      <BottomNav active="op" />
    </>
  )
}
