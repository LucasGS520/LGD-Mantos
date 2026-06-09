import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Input, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import type { Supplier } from '../../services/types'
import { useNav } from '../../nav'

function formatPhone(raw: string): string {
  const d = raw.replace(/\D/g, '').slice(0, 11)
  if (d.length === 0)  return ''
  if (d.length <= 2)   return `(${d}`
  if (d.length <= 6)   return `(${d.slice(0,2)}) ${d.slice(2)}`
  if (d.length <= 10)  return `(${d.slice(0,2)}) ${d.slice(2,6)}-${d.slice(6)}`
  return `(${d.slice(0,2)}) ${d.slice(2,7)}-${d.slice(7)}`
}

export default function SupplierForm() {
  const { back, params } = useNav()
  const supplierId = params.supplierId as string | undefined

  const [loading, setLoading]         = useState(!!supplierId)
  const [saving, setSaving]           = useState(false)
  const [deleting, setDeleting]       = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [error, setError]             = useState<string | null>(null)

  const [name, setName]         = useState('')
  const [contact, setContact]   = useState('')
  const [phone, setPhone]       = useState('')
  const [email, setEmail]       = useState('')
  const [notes, setNotes]       = useState('')

  useEffect(() => {
    if (!supplierId) return
    api.get<Supplier>(`/suppliers/${supplierId}`)
      .then(s => {
        setName(s.name)
        setContact(s.contact ?? '')
        setPhone(formatPhone(s.phone ?? ''))
        setEmail(s.email ?? '')
        setNotes(s.notes ?? '')
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Erro ao carregar'))
      .finally(() => setLoading(false))
  }, [supplierId])

  const handleSave = async () => {
    if (!name.trim()) { setError('O nome do fornecedor é obrigatório'); return }
    setSaving(true)
    setError(null)
    try {
      const body = {
        name:    name.trim(),
        contact: contact.trim() || null,
        phone:   phone.trim()   || null,
        email:   email.trim()   || null,
        notes:   notes.trim()   || null,
      }
      if (supplierId) {
        await api.put(`/suppliers/${supplierId}`, body)
      } else {
        await api.post('/suppliers', body)
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    try {
      await api.delete(`/suppliers/${supplierId}`)
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao remover')
      setConfirmDelete(false)
    } finally {
      setDeleting(false)
    }
  }

  const title = supplierId ? 'Editar fornecedor' : 'Novo fornecedor'

  if (loading) return <><AppBar back title={title} /><LoadingBody /></>

  return (
    <>
      <AppBar back title={title} action={
        <span
          onClick={handleSave}
          style={{ fontSize: 13, fontWeight: 700, color: saving ? 'var(--text-3)' : 'var(--gold-500)', cursor: 'pointer' }}
        >
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
          <Input
            label="Nome"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Nome do fornecedor"
            hint="Obrigatório"
          />
        </Section>

        <Section title="Contato" top={20}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Input
              label="Responsável"
              value={contact}
              onChange={e => setContact(e.target.value)}
              placeholder="Nome do contato principal"
            />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <Input
                label="Telefone / WhatsApp"
                value={phone}
                onChange={e => setPhone(formatPhone(e.target.value))}
                placeholder="(11) 99999-9999"
                inputMode="numeric"
              />
              <Input
                label="E-mail"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="email@fornecedor.com"
                type="email"
              />
            </div>
          </div>
        </Section>

        <Section title="Observações" top={20}>
          <div>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>
              Notas internas
            </div>
            <textarea
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Prazo de entrega, pedido mínimo, condições de pagamento, Instagram…"
              rows={4}
              style={{
                width: '100%', padding: '12px 14px', borderRadius: 12,
                background: 'var(--bg-4)', border: '1px solid var(--line-2)',
                color: 'var(--text-1)', fontSize: 14, resize: 'none',
                outline: 0, fontFamily: 'inherit', lineHeight: 1.5,
              }}
            />
          </div>
        </Section>

        {supplierId && (
          <div style={{ marginTop: 32 }}>
            {!confirmDelete ? (
              <button
                onClick={() => setConfirmDelete(true)}
                style={{ width: '100%', height: 44, borderRadius: 12, background: 'transparent', border: '1px solid rgba(232,88,79,0.35)', color: '#F5847B', fontSize: 13, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Ico.trash size={15} stroke="#F5847B" />
                Remover fornecedor
              </button>
            ) : (
              <div style={{ padding: 14, borderRadius: 12, background: 'rgba(232,88,79,0.06)', border: '1px solid rgba(232,88,79,0.3)' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#F5847B', marginBottom: 4 }}>Confirmar remoção?</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 12 }}>
                  O fornecedor será desativado. Produtos e compras vinculados não serão afetados.
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button
                    onClick={() => setConfirmDelete(false)}
                    style={{ flex: 1, height: 36, borderRadius: 10, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleDelete}
                    style={{ flex: 1, height: 36, borderRadius: 10, background: 'rgba(232,88,79,0.15)', border: '1px solid rgba(232,88,79,0.4)', color: '#F5847B', fontSize: 12, fontWeight: 700, cursor: 'pointer' }}
                  >
                    {deleting ? 'Removendo…' : 'Confirmar'}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </ScreenBody>
    </>
  )
}
