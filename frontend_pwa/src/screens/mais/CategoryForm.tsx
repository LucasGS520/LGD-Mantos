import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Input, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import type { Category } from '../../services/types'
import { useNav } from '../../nav'

export default function CategoryForm() {
  const { back, params } = useNav()
  const categoryId = params.categoryId as string | undefined

  const [loading, setLoading]             = useState(!!categoryId)
  const [saving, setSaving]               = useState(false)
  const [deleting, setDeleting]           = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [error, setError]                 = useState<string | null>(null)

  const [name, setName]               = useState('')
  const [description, setDescription] = useState('')

  useEffect(() => {
    if (!categoryId) return
    api.get<Category>(`/categories/${categoryId}`)
      .then(c => {
        setName(c.name)
        setDescription(c.description ?? '')
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Erro ao carregar'))
      .finally(() => setLoading(false))
  }, [categoryId])

  const handleSave = async () => {
    if (!name.trim()) { setError('O nome da categoria é obrigatório'); return }
    setSaving(true)
    setError(null)
    try {
      const body = {
        name:        name.trim(),
        description: description.trim() || null,
      }
      if (categoryId) {
        await api.put(`/categories/${categoryId}`, body)
      } else {
        await api.post('/categories', body)
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
      await api.delete(`/categories/${categoryId}`)
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao remover')
      setConfirmDelete(false)
    } finally {
      setDeleting(false)
    }
  }

  const title = categoryId ? 'Editar categoria' : 'Nova categoria'

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
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Input
              label="Nome"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Ex: Camisetas Oversized, Moletons…"
              hint="Obrigatório"
            />
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>
                Descrição
              </div>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Descreva o tipo de produto desta categoria…"
                rows={3}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: 12,
                  background: 'var(--bg-4)', border: '1px solid var(--line-2)',
                  color: 'var(--text-1)', fontSize: 14, resize: 'none',
                  outline: 0, fontFamily: 'inherit', lineHeight: 1.5,
                }}
              />
            </div>
          </div>
        </Section>

        {categoryId && (
          <div style={{ marginTop: 32 }}>
            {!confirmDelete ? (
              <button
                onClick={() => setConfirmDelete(true)}
                style={{ width: '100%', height: 44, borderRadius: 12, background: 'transparent', border: '1px solid rgba(232,88,79,0.35)', color: '#F5847B', fontSize: 13, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}
              >
                <Ico.trash size={15} stroke="#F5847B" />
                Remover categoria
              </button>
            ) : (
              <div style={{ padding: 14, borderRadius: 12, background: 'rgba(232,88,79,0.06)', border: '1px solid rgba(232,88,79,0.3)' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#F5847B', marginBottom: 4 }}>Confirmar remoção?</div>
                <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 12 }}>
                  A categoria será excluída. Os produtos vinculados ficam sem categoria, mas não são removidos.
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
