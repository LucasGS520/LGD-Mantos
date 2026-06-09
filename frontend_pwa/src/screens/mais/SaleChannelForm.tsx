import { useState, useEffect } from 'react'
import { Input, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import type { SaleChannel } from '../../services/types'
import { useNav } from '../../nav'

const PRESET_COLORS = [
  { hex: '#D4A847', label: 'Ouro'       },
  { hex: '#25D366', label: 'Verde'       },
  { hex: '#E1306C', label: 'Rosa'        },
  { hex: '#EE4D2D', label: 'Laranja'     },
  { hex: '#1877F2', label: 'Azul'        },
  { hex: '#0088CC', label: 'Ciano'       },
  { hex: '#FF0050', label: 'Vermelho'    },
  { hex: '#9333EA', label: 'Roxo'        },
  { hex: '#5DD49E', label: 'Verde claro' },
  { hex: '#F5BF7A', label: 'Âmbar'       },
  { hex: '#6B7280', label: 'Cinza'        },
  { hex: '#EC4899', label: 'Pink'         },
]

export default function SaleChannelForm() {
  const { back, params } = useNav()
  const channelId = params.channelId as string | undefined

  const [loading, setLoading] = useState(!!channelId)
  const [saving, setSaving]   = useState(false)
  const [error, setError]     = useState<string | null>(null)

  const [name, setName]               = useState('')
  const [description, setDescription] = useState('')
  const [color, setColor]             = useState('#D4A847')

  useEffect(() => {
    if (!channelId) return
    api.get<SaleChannel>(`/channels/${channelId}`)
      .then(c => {
        setName(c.name)
        setDescription(c.description ?? '')
        setColor(c.color)
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Erro ao carregar'))
      .finally(() => setLoading(false))
  }, [channelId])

  const handleSave = async () => {
    if (!name.trim()) { setError('O nome do canal é obrigatório'); return }
    setSaving(true)
    setError(null)
    try {
      const body = { name: name.trim(), description: description.trim() || null, color }
      if (channelId) {
        await api.put(`/channels/${channelId}`, body)
      } else {
        await api.post('/channels', body)
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const title = channelId ? 'Editar canal' : 'Novo canal'

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
              placeholder="Ex: Loja física, WhatsApp, Instagram…"
              hint="Obrigatório"
            />
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>
                Descrição
              </div>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Descreva como este canal é utilizado…"
                rows={2}
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

        <Section title="Cor de identificação" top={20}>
          <div>
            <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 12 }}>
              Usada nos gráficos e nos chips de canal em todo o sistema.
            </div>

            {/* Preview */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, padding: '10px 14px', background: 'var(--bg-2)', borderRadius: 10 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: color }} />
              <span style={{ fontSize: 13, fontWeight: 700, color }}>
                <span style={{ width: 8, height: 8, borderRadius: 99, background: color, display: 'inline-block', marginRight: 6 }} />
                {name || 'Canal'}
              </span>
              <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-3)' }}>{color}</span>
            </div>

            {/* Swatches */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 8 }}>
              {PRESET_COLORS.map(p => (
                <button
                  key={p.hex}
                  onClick={() => setColor(p.hex)}
                  title={p.label}
                  style={{
                    height: 36, borderRadius: 8, background: p.hex, border: 0, cursor: 'pointer',
                    outline: color === p.hex ? `3px solid var(--text-1)` : '3px solid transparent',
                    outlineOffset: 2, transition: 'outline 0.1s',
                  }}
                />
              ))}
            </div>
          </div>
        </Section>

        {!channelId && (
          <div style={{ marginTop: 16, padding: '10px 14px', borderRadius: 10, background: 'rgba(212,168,71,0.06)', border: '1px solid rgba(212,168,71,0.2)', fontSize: 12, color: 'var(--text-3)' }}>
            Canais não podem ser excluídos — apenas desativados — para preservar o histórico de vendas.
          </div>
        )}
      </ScreenBody>
    </>
  )
}
