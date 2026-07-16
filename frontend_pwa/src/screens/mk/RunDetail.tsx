import { useEffect, useRef, useState } from 'react'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { Badge, Btn, Card, Section } from '../../components/UI'
import { Ico } from '../../components/Icons'
import { useNav } from '../../nav'
import { api } from '../../services/api'
import type { AgentRun } from '../../services/types'

type BadgeTone = 'neutral' | 'gold' | 'success' | 'danger' | 'warn' | 'info' | 'solid'

function statusBadge(status: string): { tone: BadgeTone; label: string } {
  const map: Record<string, { tone: BadgeTone; label: string }> = {
    pending:   { tone: 'warn',    label: 'Pendente'   },
    running:   { tone: 'info',    label: 'Executando' },
    completed: { tone: 'success', label: 'Concluído'  },
    failed:    { tone: 'danger',  label: 'Falhou'     },
  }
  return map[status] ?? { tone: 'neutral', label: status }
}

const PIPELINE_STEPS = [
  { key: 'data',     label: 'DataAgent',     desc: 'Analisa estoque, vendas e oportunidades'    },
  { key: 'strategy', label: 'StrategyAgent', desc: 'Define canal, formato e ângulo de campanha' },
  { key: 'content',  label: 'ContentAgent',  desc: 'Escreve copy, legenda e variações'           },
  { key: 'creative', label: 'CreativeAgent', desc: 'Gera briefing visual e prompts de imagem'   },
]

export default function RunDetail() {
  const { params, navigate } = useNav()
  const runId = params.runId as string
  const [run, setRun] = useState<AgentRun | null>(null)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<number | null>(null)

  const fetchRun = async () => {
    try {
      const r = await api.getAgentRun(runId)
      setRun(r)
      if (r.status !== 'pending' && r.status !== 'running') {
        if (intervalRef.current) clearInterval(intervalRef.current)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao buscar run')
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }

  useEffect(() => {
    fetchRun()
    intervalRef.current = window.setInterval(fetchRun, 3000)
    return () => { if (intervalRef.current) clearInterval(intervalRef.current) }
  }, [runId])

  if (error) {
    return (
      <>
        <AppBar title="Status do Run" back />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, padding: 32 }}>
          <div style={{ fontSize: 13, color: '#F5847B', textAlign: 'center' }}>{error}</div>
        </div>
      </>
    )
  }

  if (!run) {
    return (
      <>
        <AppBar title="Status do Run" back />
        <div style={{ flex: 1, display: 'grid', placeItems: 'center' }}>
          <div style={{ width: 32, height: 32, borderRadius: '50%', border: '3px solid var(--bg-3)', borderTopColor: 'var(--gold-500)', animation: 'spin 0.8s linear infinite' }} />
        </div>
      </>
    )
  }

  const sb = statusBadge(run.status)
  const isActive = run.status === 'pending' || run.status === 'running'
  const isCompleted = run.status === 'completed'
  const isFailed = run.status === 'failed'

  return (
    <>
      <AppBar title="Status do Run" back />

      <ScreenBody pad={18}>
        {/* Status card */}
        <Card accent={isCompleted} style={{ marginTop: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.3, fontWeight: 600 }}>Objetivo</div>
              <div style={{ fontSize: 13, color: 'var(--text-1)', lineHeight: 1.5 }}>{run.objective}</div>
            </div>
            <Badge tone={sb.tone} dot size="lg">{sb.label}</Badge>
          </div>

          {isActive && (
            <div style={{ marginTop: 14, display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 10, background: 'rgba(94,168,224,0.06)', border: '1px solid rgba(94,168,224,0.2)' }}>
              <div style={{ width: 20, height: 20, borderRadius: '50%', border: '2.5px solid rgba(94,168,224,0.3)', borderTopColor: '#8BC0E8', animation: 'spin 0.8s linear infinite', flexShrink: 0 }} />
              <div style={{ fontSize: 12.5, color: '#8BC0E8' }}>Pipeline em execução. Atualização automática a cada 3s.</div>
            </div>
          )}
        </Card>

        {/* Pipeline steps */}
        <Section title="Pipeline" top={22}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {PIPELINE_STEPS.map((step, i) => {
              const done = isCompleted
              const active = isActive && !isFailed
              return (
                <div key={step.key} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 14px', borderRadius: 12, background: 'var(--bg-1)', border: `1px solid ${done ? 'rgba(63,184,124,0.25)' : 'var(--line-1)'}` }}>
                  <div style={{ width: 28, height: 28, borderRadius: 8, display: 'grid', placeItems: 'center', flexShrink: 0, background: done ? 'rgba(63,184,124,0.12)' : active ? 'rgba(94,168,224,0.1)' : 'var(--bg-2)', border: `1px solid ${done ? 'rgba(63,184,124,0.3)' : active ? 'rgba(94,168,224,0.3)' : 'var(--line-2)'}` }}>
                    {done ? <Ico.check size={14} stroke="#5DD49E" /> : active ? (
                      <div style={{ width: 14, height: 14, borderRadius: '50%', border: '2px solid rgba(94,168,224,0.3)', borderTopColor: '#8BC0E8', animation: i === 0 ? 'spin 0.8s linear infinite' : undefined }} />
                    ) : (
                      <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-4)' }}>{i + 1}</span>
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: done ? '#5DD49E' : 'var(--text-2)' }}>{step.label}</div>
                    <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 1 }}>{step.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </Section>

        {/* Result — completed */}
        {isCompleted && run.result && (
          <Section title="Resultado" top={22}>
            <Card accent>
              <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 14 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(212,168,71,0.12)', border: '1px solid rgba(212,168,71,0.3)', display: 'grid', placeItems: 'center' }}>
                  <Ico.sparkle size={18} stroke="var(--gold-500)" />
                </div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--gold-300)' }}>{run.result.campaign_name}</div>
                  <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>Campanha gerada com sucesso</div>
                </div>
              </div>
              <Btn
                full
                icon={Ico.check}
                onClick={() => navigate('mk-approval-detail', { approvalId: run.result!.approval_id })}
              >
                Revisar e Aprovar
              </Btn>
            </Card>
          </Section>
        )}

        {/* Error — failed */}
        {isFailed && (
          <Section title="Erro" top={22}>
            <div style={{ padding: '14px', borderRadius: 12, background: 'rgba(232,88,79,0.06)', border: '1px solid rgba(232,88,79,0.2)' }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: '#F5847B', marginBottom: 6 }}>O pipeline falhou</div>
              <div style={{ fontSize: 12.5, color: 'var(--text-3)', lineHeight: 1.5 }}>
                {run.error ?? 'Erro desconhecido. Tente criar um novo run.'}
              </div>
            </div>
          </Section>
        )}
      </ScreenBody>
    </>
  )
}
