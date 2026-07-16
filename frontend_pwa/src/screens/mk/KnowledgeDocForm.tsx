import { useState } from 'react'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { Btn, Input } from '../../components/UI'
import { useNav } from '../../nav'
import { api } from '../../services/api'
import type { KnowledgeDoc } from '../../services/types'

const DOC_TYPES: { value: string; label: string }[] = [
  { value: 'brand_voice',        label: 'Voz de Marca'        },
  { value: 'persona',            label: 'Persona'             },
  { value: 'commercial_rules',   label: 'Regras Comerciais'   },
  { value: 'visual_reference',   label: 'Referência Visual'   },
  { value: 'approved_caption',   label: 'Caption Aprovado'    },
  { value: 'approved_prompt',    label: 'Prompt Aprovado'     },
  { value: 'campaign_context',   label: 'Contexto de Campanha'},
  { value: 'product_style_notes',label: 'Notas de Estilo'     },
]

export default function KnowledgeDocForm() {
  const { params, back } = useNav()
  const existing = params.doc as KnowledgeDoc | undefined

  const [docType, setDocType]   = useState(existing?.doc_type ?? 'brand_voice')
  const [title, setTitle]       = useState(existing?.title ?? '')
  const [content, setContent]   = useState(existing?.content ?? '')
  const [isActive, setIsActive] = useState(existing?.is_active ?? true)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState<string | null>(null)

  const isEdit = !!existing

  const handleSubmit = async () => {
    if (!title.trim() || !content.trim()) {
      setError('Título e conteúdo são obrigatórios.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      if (isEdit) {
        await api.updateKnowledgeDoc(existing!.id, { title: title.trim(), content: content.trim(), is_active: isActive })
      } else {
        await api.createKnowledgeDoc({ doc_type: docType, title: title.trim(), content: content.trim(), is_active: isActive })
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <AppBar title={isEdit ? 'Editar Documento' : 'Novo Documento'} back />

      <ScreenBody pad={18}>
        {/* Doc type selector (only on create) */}
        {!isEdit && (
          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 8, letterSpacing: 0.2, textTransform: 'uppercase' }}>Tipo de Documento</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {DOC_TYPES.map(t => (
                <div key={t.value} onClick={() => setDocType(t.value)} style={{
                  padding: '6px 12px', borderRadius: 999, fontSize: 12, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap',
                  background: docType === t.value ? 'rgba(212,168,71,0.1)' : 'var(--bg-2)',
                  border: `1px solid ${docType === t.value ? 'var(--gold-500)' : 'var(--line-1)'}`,
                  color: docType === t.value ? 'var(--gold-300)' : 'var(--text-2)',
                }}>{t.label}</div>
              ))}
            </div>
          </div>
        )}

        {/* Title */}
        <div style={{ marginTop: 18 }}>
          <Input
            label="Título"
            value={title}
            placeholder="Ex: Tom de Voz LGD Mantos"
            onChange={e => setTitle(e.target.value)}
          />
        </div>

        {/* Content */}
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>
            Conteúdo
          </div>
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Descreva em detalhes. Os agentes usarão este texto como contexto."
            rows={8}
            style={{
              width: '100%', padding: '12px 14px', borderRadius: 12, boxSizing: 'border-box',
              background: 'var(--bg-4)', border: '1px solid var(--line-2)',
              color: 'var(--text-1)', fontSize: 14, lineHeight: 1.55, resize: 'vertical', outline: 'none',
              fontFamily: 'var(--font-sans)',
            }}
          />
        </div>

        {/* Active toggle */}
        <div style={{ marginTop: 14, display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', borderRadius: 12, background: 'var(--bg-1)', border: '1px solid var(--line-1)' }}>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>Documento ativo</div>
            <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>Apenas documentos ativos são usados pelos agentes</div>
          </div>
          <div
            onClick={() => setIsActive(v => !v)}
            style={{
              width: 44, height: 26, borderRadius: 13, cursor: 'pointer', position: 'relative', flexShrink: 0,
              background: isActive ? 'var(--gold-500)' : 'var(--bg-3)',
              border: `1px solid ${isActive ? 'var(--gold-500)' : 'var(--line-2)'}`,
              transition: 'background 0.2s',
            }}
          >
            <div style={{
              width: 18, height: 18, borderRadius: 9, background: '#fff',
              position: 'absolute', top: 3, left: isActive ? 21 : 3,
              transition: 'left 0.2s',
            }} />
          </div>
        </div>

        {error && (
          <div style={{ marginTop: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.08)', border: '1px solid rgba(232,88,79,0.25)', color: '#F5847B', fontSize: 13 }}>
            {error}
          </div>
        )}

        <div style={{ marginTop: 20, display: 'flex', gap: 10 }}>
          <Btn kind="ghost" style={{ flex: 1 }} onClick={back}>Cancelar</Btn>
          <Btn kind="primary" style={{ flex: 2 }} onClick={handleSubmit}>
            {loading ? 'Salvando…' : isEdit ? 'Salvar Alterações' : 'Criar Documento'}
          </Btn>
        </div>
      </ScreenBody>
    </>
  )
}
