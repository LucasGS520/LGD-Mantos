import { useState } from 'react'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { Badge, Btn, Card, Section, Textarea } from '../../components/UI'
import { Ico } from '../../components/Icons'
import { useNav } from '../../nav'
import { api } from '../../services/api'
import type { AgentApprovalDetail } from '../../services/types'
import { useData } from '../../hooks/useData'

type BadgeTone = 'neutral' | 'gold' | 'success' | 'danger' | 'warn' | 'info' | 'solid'

function statusBadge(status: string): { tone: BadgeTone; label: string } {
  const map: Record<string, { tone: BadgeTone; label: string }> = {
    pending:            { tone: 'warn',    label: 'Pendente'   },
    approved:           { tone: 'success', label: 'Aprovado'   },
    rejected:           { tone: 'danger',  label: 'Rejeitado'  },
    revision_requested: { tone: 'warn',    label: 'Revisão'    },
    draft:              { tone: 'neutral', label: 'Rascunho'   },
    pending_approval:   { tone: 'warn',    label: 'Aguardando' },
  }
  return map[status] ?? { tone: 'neutral', label: status }
}

function riskBadge(risk: string | null): BadgeTone {
  if (risk === 'low') return 'success'
  if (risk === 'high') return 'danger'
  return 'warn'
}

export default function ApprovalDetailScreen() {
  const { params, back } = useNav()
  const approvalId = params.approvalId as string
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [decided, setDecided] = useState<AgentApprovalDetail | null>(null)

  const { data, loading, error, reload } = useData<AgentApprovalDetail>(
    () => api.getApprovalDetail(approvalId),
    approvalId,
  )

  const approval = decided ?? data
  const isPending = approval?.status === 'pending'

  const handle = async (action: 'approve' | 'reject' | 'revision') => {
    if (action !== 'approve' && !comment.trim()) {
      setActionError('Comentário obrigatório para esta ação.')
      return
    }
    setSubmitting(true)
    setActionError(null)
    try {
      let result: AgentApprovalDetail
      if (action === 'approve')   result = await api.approveApproval(approvalId, comment.trim() || undefined)
      else if (action === 'reject') result = await api.rejectApproval(approvalId, comment.trim())
      else                         result = await api.requestRevision(approvalId, comment.trim())
      setDecided(result)
    } catch (e) {
      setActionError(e instanceof Error ? e.message : 'Erro ao processar')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <>
        <AppBar title="Aprovação" back />
        <div style={{ flex: 1, display: 'grid', placeItems: 'center' }}>
          <div style={{ width: 32, height: 32, borderRadius: '50%', border: '3px solid var(--bg-3)', borderTopColor: 'var(--gold-500)', animation: 'spin 0.8s linear infinite' }} />
        </div>
      </>
    )
  }

  if (error || !approval) {
    return (
      <>
        <AppBar title="Aprovação" back />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, padding: 32 }}>
          <div style={{ fontSize: 13, color: '#F5847B', textAlign: 'center' }}>{error ?? 'Não encontrado'}</div>
          <button onClick={reload} style={{ padding: '8px 20px', borderRadius: 10, background: 'var(--bg-2)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 13, fontWeight: 600 }}>Tentar novamente</button>
        </div>
      </>
    )
  }

  const { campaign } = approval
  const post = campaign?.posts?.[0]
  const brief = campaign?.creative_briefs?.[0]
  const sb = statusBadge(approval.status)

  return (
    <>
      <AppBar title="Aprovação" subtitle={campaign?.name} back />

      <ScreenBody pad={18}>
        {/* Status row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 12, padding: '10px 14px', borderRadius: 12, background: 'var(--bg-1)', border: '1px solid var(--line-1)' }}>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <Ico.check size={16} stroke="var(--text-3)" />
            <span style={{ fontSize: 13, color: 'var(--text-2)' }}>Status da aprovação</span>
          </div>
          <Badge tone={sb.tone} dot size="lg">{sb.label}</Badge>
        </div>

        {approval.comment && !isPending && (
          <div style={{ marginTop: 8, padding: '10px 14px', borderRadius: 10, background: 'var(--bg-2)', border: '1px solid var(--line-2)', fontSize: 12.5, color: 'var(--text-2)', lineHeight: 1.5 }}>
            <span style={{ fontWeight: 600, color: 'var(--text-1)' }}>Comentário: </span>{approval.comment}
          </div>
        )}

        {/* Campaign info */}
        {campaign && (
          <Section title="Campanha" top={20}>
            <Card>
              <div style={{ display: 'grid', gap: 8 }}>
                <Row label="Nome"    value={campaign.name} />
                <Row label="Canal"   value={campaign.channel}   />
                <Row label="Formato" value={campaign.format}    />
                <Row label="CTA"     value={campaign.cta}       />
                {campaign.risk_level && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: 12, color: 'var(--text-3)' }}>Risco</span>
                    <Badge tone={riskBadge(campaign.risk_level)}>{campaign.risk_level}</Badge>
                  </div>
                )}
              </div>
              {campaign.angle && (
                <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--line-1)' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 0.3, fontWeight: 600 }}>Ângulo</div>
                  <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.5 }}>{campaign.angle}</div>
                </div>
              )}
            </Card>
          </Section>
        )}

        {/* Copy */}
        {post && (
          <Section title="Copy" top={20}>
            <Card>
              {post.headline && <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--gold-300)', lineHeight: 1.3, marginBottom: 10 }}>{post.headline}</div>}
              {post.caption  && <div style={{ fontSize: 13, color: 'var(--text-1)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{post.caption}</div>}
              {post.cta_text && (
                <div style={{ marginTop: 12, padding: '8px 14px', borderRadius: 8, background: 'rgba(212,168,71,0.08)', border: '1px solid rgba(212,168,71,0.2)', fontSize: 13, fontWeight: 600, color: 'var(--gold-300)' }}>
                  CTA: {post.cta_text}
                </div>
              )}

              {post.copy_variations && post.copy_variations.length > 0 && (
                <div style={{ marginTop: 14 }}>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 0.3, fontWeight: 600 }}>Variações</div>
                  {post.copy_variations.map((v, i) => (
                    <div key={i} style={{ padding: '10px 12px', borderRadius: 10, background: 'var(--bg-2)', border: '1px solid var(--line-1)', marginBottom: 6 }}>
                      <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 4, fontWeight: 600 }}>Variação {i + 1} · {v.style}</div>
                      <div style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-1)', marginBottom: 4 }}>{v.headline}</div>
                      <div style={{ fontSize: 12.5, color: 'var(--text-2)', lineHeight: 1.5 }}>{v.caption}</div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </Section>
        )}

        {/* Creative brief */}
        {brief && (
          <Section title="Briefing Criativo" top={20}>
            <Card>
              {brief.visual_briefing && (
                <>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.3, fontWeight: 600 }}>Direção Visual</div>
                  <div style={{ fontSize: 13, color: 'var(--text-1)', lineHeight: 1.6, marginBottom: 12, whiteSpace: 'pre-wrap' }}>{brief.visual_briefing}</div>
                </>
              )}
              {brief.image_prompt && (
                <>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.3, fontWeight: 600 }}>Prompt de Imagem</div>
                  <div style={{ fontSize: 12.5, color: 'var(--text-2)', lineHeight: 1.5, padding: '10px 12px', background: 'var(--bg-2)', borderRadius: 8, border: '1px solid var(--line-1)', fontStyle: 'italic', marginBottom: 12 }}>{brief.image_prompt}</div>
                </>
              )}
              {brief.carousel_idea && (
                <>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.3, fontWeight: 600 }}>Ideia de Carrossel</div>
                  <div style={{ fontSize: 13, color: 'var(--text-2)', lineHeight: 1.5 }}>{brief.carousel_idea}</div>
                </>
              )}
            </Card>
          </Section>
        )}

        {/* Decision panel */}
        {isPending && (
          <Section title="Decisão" top={24}>
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>
                Comentário
              </div>
              <textarea
                value={comment}
                onChange={e => setComment(e.target.value)}
                placeholder="Obrigatório para solicitar revisão ou rejeitar…"
                rows={3}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: 12, boxSizing: 'border-box',
                  background: 'var(--bg-4)', border: '1px solid var(--line-2)',
                  color: 'var(--text-1)', fontSize: 14, lineHeight: 1.5, resize: 'none', outline: 'none',
                  fontFamily: 'var(--font-sans)',
                }}
              />
            </div>

            {actionError && (
              <div style={{ padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.08)', border: '1px solid rgba(232,88,79,0.25)', color: '#F5847B', fontSize: 13, marginTop: 8 }}>
                {actionError}
              </div>
            )}

            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <Btn kind="danger" style={{ flex: 1 }} onClick={() => handle('reject')}>
                Rejeitar
              </Btn>
              <Btn kind="secondary" style={{ flex: 1 }} onClick={() => handle('revision')}>
                Revisão
              </Btn>
              <Btn kind="primary" style={{ flex: 1 }} icon={Ico.check} onClick={() => handle('approve')}>
                Aprovar
              </Btn>
            </div>
            {submitting && <div style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-3)', marginTop: 8 }}>Processando…</div>}
          </Section>
        )}

        {!isPending && (
          <div style={{ marginTop: 24, marginBottom: 8 }}>
            <Btn kind="ghost" full onClick={back}>Voltar</Btn>
          </div>
        )}
      </ScreenBody>
    </>
  )
}

function Row({ label, value }: { label: string; value?: string | null }) {
  if (!value) return null
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
      <span style={{ fontSize: 12, color: 'var(--text-3)', flexShrink: 0 }}>{label}</span>
      <span style={{ fontSize: 13, color: 'var(--text-1)', fontWeight: 500, textAlign: 'right' }}>{value}</span>
    </div>
  )
}
