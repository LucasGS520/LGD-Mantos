import { useState } from 'react'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { Btn, Card, Section } from '../../components/UI'
import { Ico } from '../../components/Icons'
import { useNav } from '../../nav'
import { api } from '../../services/api'

const SUGGESTIONS = [
  'Gerar campanha para o produto com maior estoque parado',
  'Criar post para o manto mais vendido da semana',
  'Campanha de reposição para mantos com estoque crítico',
  'Post destacando margem alta para o Instagram',
]

export default function NewRun() {
  const { navigate, back } = useNav()
  const [objective, setObjective] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    const text = objective.trim()
    if (!text || loading) return
    setLoading(true)
    setError(null)
    try {
      const run = await api.createAgentRun(text)
      navigate('mk-run-detail', { runId: run.run_id })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao criar run')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <AppBar title="Nova Campanha" back />

      <ScreenBody pad={18}>
        {/* Icon header */}
        <div style={{ textAlign: 'center', padding: '24px 0 20px' }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: 'rgba(212,168,71,0.1)', border: '1px solid rgba(212,168,71,0.25)', display: 'grid', placeItems: 'center', margin: '0 auto 14px' }}>
            <Ico.sparkle size={26} stroke="var(--gold-500)" />
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-1)', marginBottom: 6 }}>Objetivo da Campanha</div>
          <div style={{ fontSize: 12.5, color: 'var(--text-3)', lineHeight: 1.5, maxWidth: 280, margin: '0 auto' }}>
            Descreva o objetivo. Os agentes analisarão os dados e gerarão copy e direção criativa automaticamente.
          </div>
        </div>

        {/* Objective textarea */}
        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>
            Objetivo
          </div>
          <textarea
            value={objective}
            onChange={e => setObjective(e.target.value)}
            placeholder="Ex: Gerar campanha para o manto com maior estoque parado..."
            rows={4}
            style={{
              width: '100%', padding: '12px 14px', borderRadius: 12, boxSizing: 'border-box',
              background: 'var(--bg-4)', border: '1px solid var(--line-2)',
              color: 'var(--text-1)', fontSize: 14, lineHeight: 1.5, resize: 'none', outline: 'none',
              fontFamily: 'var(--font-sans)',
            }}
          />
        </div>

        {error && (
          <div style={{ padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.08)', border: '1px solid rgba(232,88,79,0.25)', color: '#F5847B', fontSize: 13, marginTop: 8 }}>
            {error}
          </div>
        )}

        <div style={{ marginTop: 12 }}>
          <Btn full icon={loading ? undefined : Ico.sparkle} onClick={handleSubmit}>
            {loading ? 'Iniciando pipeline…' : 'Gerar Campanha'}
          </Btn>
        </div>

        {/* Quick suggestions */}
        <Section title="Sugestões rápidas" top={28}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {SUGGESTIONS.map(s => (
              <Card key={s} onClick={() => setObjective(s)} style={{ cursor: 'pointer', padding: 12 }}>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                  <Ico.sparkle size={15} stroke="var(--gold-500)" />
                  <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.4, flex: 1 }}>{s}</div>
                </div>
              </Card>
            ))}
          </div>
        </Section>

        {/* Info box */}
        <Card style={{ marginTop: 20, background: 'rgba(94,168,224,0.06)', borderColor: 'rgba(94,168,224,0.2)' }}>
          <div style={{ fontSize: 12, color: '#8BC0E8', lineHeight: 1.55 }}>
            <strong>Como funciona:</strong> DataAgent analisa estoque e vendas → StrategyAgent define canal e ângulo → ContentAgent escreve o copy → CreativeAgent gera briefing visual. O resultado aguarda sua aprovação antes de qualquer ação.
          </div>
        </Card>
      </ScreenBody>
    </>
  )
}
