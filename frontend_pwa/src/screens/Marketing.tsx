import { useState, useEffect, useCallback } from 'react'
import { AppBar, BottomNav, FAB, ScreenBody } from '../components/Chrome'
import { Badge, Card, KPI, LoadingBody, ErrorBody, Section } from '../components/UI'
import { Ico } from '../components/Icons'
import { useNav } from '../nav'
import { api } from '../services/api'
import type { AgentRun, AgentApprovalItem, OpsMetrics, KnowledgeDoc } from '../services/types'

// ─── Utilities ─────────────────────────────────────────────────────────────

type BadgeTone = 'neutral' | 'gold' | 'success' | 'danger' | 'warn' | 'info' | 'solid'

function statusBadge(status: string): { tone: BadgeTone; label: string } {
  const map: Record<string, { tone: BadgeTone; label: string }> = {
    pending:            { tone: 'warn',    label: 'Pendente'   },
    running:            { tone: 'info',    label: 'Executando' },
    completed:          { tone: 'success', label: 'Concluído'  },
    failed:             { tone: 'danger',  label: 'Falhou'     },
    approved:           { tone: 'success', label: 'Aprovado'   },
    rejected:           { tone: 'danger',  label: 'Rejeitado'  },
    revision_requested: { tone: 'warn',    label: 'Revisão'    },
    pending_approval:   { tone: 'warn',    label: 'Aguardando' },
    draft:              { tone: 'neutral', label: 'Rascunho'   },
  }
  return map[status] ?? { tone: 'neutral', label: status }
}

function fmtDt(s: string) {
  const d = new Date(s)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }) +
    ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
}

const DOC_TYPE_LABELS: Record<string, string> = {
  brand_voice: 'Voz de Marca', persona: 'Persona',
  commercial_rules: 'Regras Comerciais', visual_reference: 'Referência Visual',
  approved_caption: 'Caption Aprovado', approved_prompt: 'Prompt Aprovado',
  campaign_context: 'Contexto de Campanha', product_style_notes: 'Notas de Estilo',
}

// ─── Campanhas Tab ─────────────────────────────────────────────────────────

function CampanhasTab() {
  const { navigate } = useNav()
  const [metrics, setMetrics] = useState<OpsMetrics | null>(null)
  const [runs, setRuns] = useState<AgentRun[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [m, r] = await Promise.all([api.getOpsMetrics(), api.getAgentRuns()])
      setMetrics(m)
      setRuns(r)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao carregar')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) return <LoadingBody />
  if (error || !metrics || !runs) return <ErrorBody msg={error ?? 'Erro'} onRetry={load} />

  return (
    <>
      {/* KPIs */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginTop: 16 }}>
        <KPI label="Runs" value={String(metrics.total_runs)} delta={`${metrics.runs_running} em andamento`} deltaTone={metrics.runs_running > 0 ? 'success' : 'muted'} icon={Ico.sparkle} />
        <KPI label="Sucesso" value={`${metrics.success_rate}%`} delta={`${metrics.runs_completed} ok`} deltaTone="success" icon={Ico.check} />
        <KPI label="Aprovações" value={String(metrics.pending_approvals)} delta="pendentes" deltaTone={metrics.pending_approvals > 0 ? 'danger' : 'muted'} icon={Ico.bell} />
      </div>

      {/* Runs list */}
      <Section title="Histórico de Runs" top={22} action={
        <button onClick={load} style={{ background: 'none', border: 0, cursor: 'pointer', color: 'var(--text-3)' }}>
          <Ico.refresh size={16} />
        </button>
      }>
        {runs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 0', color: 'var(--text-3)', fontSize: 13 }}>
            Nenhum run ainda. Crie sua primeira campanha!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {runs.map(r => {
              const sb = statusBadge(r.status)
              return (
                <Card key={r.run_id} onClick={() => navigate('mk-run-detail', { runId: r.run_id })} style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)', lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                        {r.objective}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 4 }}>{fmtDt(r.created_at)}</div>
                    </div>
                    <div style={{ flexShrink: 0 }}>
                      <Badge tone={sb.tone} dot>{sb.label}</Badge>
                    </div>
                  </div>
                  {r.result?.campaign_name && (
                    <div style={{ marginTop: 8, paddingTop: 8, borderTop: '1px solid var(--line-1)', fontSize: 12, color: 'var(--text-2)' }}>
                      Campanha: <span style={{ color: 'var(--gold-300)' }}>{r.result.campaign_name}</span>
                    </div>
                  )}
                </Card>
              )
            })}
          </div>
        )}
      </Section>
    </>
  )
}

// ─── Aprovações Tab ────────────────────────────────────────────────────────

type ApprovalFilter = 'all' | 'pending' | 'approved' | 'rejected'
const APPROVAL_FILTERS: { id: ApprovalFilter; label: string }[] = [
  { id: 'all',      label: 'Todas'      },
  { id: 'pending',  label: 'Pendentes'  },
  { id: 'approved', label: 'Aprovadas'  },
  { id: 'rejected', label: 'Rejeitadas' },
]

function AprovacoesTab() {
  const { navigate } = useNav()
  const [filter, setFilter] = useState<ApprovalFilter>('pending')
  const [approvals, setApprovals] = useState<AgentApprovalItem[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const status = filter === 'all' ? undefined : filter
      setApprovals(await api.getApprovals(status))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao carregar')
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => { load() }, [load])

  return (
    <>
      {/* Filter pills */}
      <div style={{ display: 'flex', gap: 6, paddingTop: 14, paddingBottom: 2, overflowX: 'auto' }} className="lgd-scroll">
        {APPROVAL_FILTERS.map(f => (
          <div key={f.id} onClick={() => setFilter(f.id)} style={{
            padding: '6px 12px', borderRadius: 999, fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap', cursor: 'pointer',
            background: f.id === filter ? 'rgba(212,168,71,0.1)' : 'var(--bg-2)',
            border: `1px solid ${f.id === filter ? 'var(--gold-500)' : 'var(--line-1)'}`,
            color: f.id === filter ? 'var(--gold-300)' : 'var(--text-2)',
          }}>{f.label}</div>
        ))}
      </div>

      {loading ? <LoadingBody /> : error || !approvals ? <ErrorBody msg={error ?? 'Erro'} onRetry={load} /> : (
        <Section top={14}>
          {approvals.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '32px 0', color: 'var(--text-3)', fontSize: 13 }}>
              {filter === 'pending' ? 'Nenhuma aprovação pendente.' : 'Nenhum resultado para este filtro.'}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {approvals.map(a => {
                const sb = statusBadge(a.status)
                return (
                  <Card key={a.id} onClick={() => navigate('mk-approval-detail', { approvalId: a.id })} style={{ cursor: 'pointer' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>
                          {a.campaign_name ?? 'Campanha sem nome'}
                        </div>
                        {a.campaign_channel && (
                          <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 3 }}>{a.campaign_channel}</div>
                        )}
                        <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 3 }}>{fmtDt(a.created_at)}</div>
                      </div>
                      <Badge tone={sb.tone} dot>{sb.label}</Badge>
                    </div>
                  </Card>
                )
              })}
            </div>
          )}
        </Section>
      )}
    </>
  )
}

// ─── Conhecimento Tab ──────────────────────────────────────────────────────

function ConhecimentoTab() {
  const { navigate } = useNav()
  const [docs, setDocs] = useState<KnowledgeDoc[] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setDocs(await api.getKnowledgeDocs())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao carregar')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id: string) => {
    try {
      await api.deleteKnowledgeDoc(id)
      setDocs(prev => prev?.filter(d => d.id !== id) ?? null)
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Erro ao remover')
    }
  }

  if (loading) return <LoadingBody />
  if (error || !docs) return <ErrorBody msg={error ?? 'Erro'} onRetry={load} />

  // Group by doc_type
  const grouped = docs.reduce<Record<string, KnowledgeDoc[]>>((acc, d) => {
    ;(acc[d.doc_type] ??= []).push(d)
    return acc
  }, {})

  return (
    <>
      {docs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-3)', fontSize: 13 }}>
          <Ico.doc size={32} stroke="var(--text-4)" />
          <div style={{ marginTop: 10 }}>Nenhum documento de marca cadastrado.</div>
          <div style={{ fontSize: 12, marginTop: 4 }}>Adicione tom de voz, persona e regras comerciais.</div>
        </div>
      ) : (
        Object.entries(grouped).map(([type, items]) => (
          <Section key={type} title={DOC_TYPE_LABELS[type] ?? type} top={18}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {items.map(doc => (
                <Card key={doc.id} style={{ opacity: doc.is_active ? 1 : 0.5 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>{doc.title}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 4, lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                        {doc.content}
                      </div>
                      {!doc.is_active && <div style={{ fontSize: 10.5, color: 'var(--text-4)', marginTop: 4 }}>Inativo</div>}
                    </div>
                    <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                      <button
                        onClick={() => navigate('mk-knowledge-form', { doc })}
                        style={{ width: 32, height: 32, borderRadius: 8, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center', cursor: 'pointer' }}
                      >
                        <Ico.edit size={14} stroke="var(--text-2)" />
                      </button>
                      <button
                        onClick={() => confirm(`Remover "${doc.title}"?`) && handleDelete(doc.id)}
                        style={{ width: 32, height: 32, borderRadius: 8, border: '1px solid rgba(232,88,79,0.3)', background: 'rgba(232,88,79,0.08)', display: 'grid', placeItems: 'center', cursor: 'pointer' }}
                      >
                        <Ico.trash size={14} stroke="#F5847B" />
                      </button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Section>
        ))
      )}
    </>
  )
}

// ─── Hub ───────────────────────────────────────────────────────────────────

type MkTab = 'campanhas' | 'aprovacoes' | 'conhecimento'
const MK_TABS: { id: MkTab; label: string }[] = [
  { id: 'campanhas',   label: 'Campanhas'  },
  { id: 'aprovacoes',  label: 'Aprovações' },
  { id: 'conhecimento',label: 'Conhecimento'},
]

export default function Marketing() {
  const { navigate } = useNav()
  const [tab, setTab] = useState<MkTab>('campanhas')

  const fabAction = () => {
    if (tab === 'campanhas')    navigate('mk-new-run')
    if (tab === 'conhecimento') navigate('mk-knowledge-form', {})
  }

  return (
    <>
      <AppBar title="Marketing Ops" subtitle="Campanhas · Aprovações · Conhecimento" />

      {/* Sub-nav tabs */}
      <div style={{ display: 'flex', gap: 4, padding: '0 18px 10px', flexShrink: 0 }}>
        {MK_TABS.map(t => (
          <div key={t.id} onClick={() => setTab(t.id)} style={{
            flex: 1, textAlign: 'center', padding: '8px 4px', borderRadius: 10, fontSize: 12, fontWeight: 700, cursor: 'pointer',
            background: t.id === tab ? 'var(--bg-3)' : 'transparent',
            color: t.id === tab ? 'var(--text-1)' : 'var(--text-3)',
            border: t.id === tab ? '1px solid var(--line-2)' : '1px solid transparent',
          }}>{t.label}</div>
        ))}
      </div>

      <ScreenBody pad={18}>
        {tab === 'campanhas'    && <CampanhasTab />}
        {tab === 'aprovacoes'   && <AprovacoesTab />}
        {tab === 'conhecimento' && <ConhecimentoTab />}
      </ScreenBody>

      {(tab === 'campanhas' || tab === 'conhecimento') && (
        <FAB
          icon={Ico.plus}
          label={tab === 'campanhas' ? 'Nova Campanha' : 'Novo Doc'}
          onClick={fabAction}
        />
      )}

      <BottomNav active="mk" />
    </>
  )
}
