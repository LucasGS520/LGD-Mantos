import { useState, useRef, useEffect } from 'react'
import { Ico, type IcoProps } from '../components/Icons'
import { AppBar, BottomNav, ScreenBody } from '../components/Chrome'
import { api } from '../services/api'

type ModeKey = 'social-copy' | 'campaign-suggestion' | 'product-description'
interface Mode { key: ModeKey; label: string; icon: (p: IcoProps) => JSX.Element; endpoint: string }
const MODES: Mode[] = [
  { key: 'social-copy',           label: 'Copy social',   icon: Ico.megaphone, endpoint: '/marketing/social-copy'           },
  { key: 'campaign-suggestion',   label: 'Campanha',      icon: Ico.sparkle,   endpoint: '/marketing/campaign-suggestion'   },
  { key: 'product-description',   label: 'Descrição',     icon: Ico.tag,       endpoint: '/marketing/product-description'   },
]

interface Message {
  role: 'user' | 'assistant'
  text: string
}

export default function Marketing() {
  const [activeMode, setActiveMode] = useState<ModeKey>('social-copy')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || sending) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text }])
    setSending(true)

    const mode = MODES.find(m => m.key === activeMode)!
    try {
      const res = await api.post<{ content: string }>(mode.endpoint, {
        message: text,
        product_ids: [],
      })
      setMessages(prev => [...prev, { role: 'assistant', text: res.content ?? 'Sem resposta do servidor.' }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: `Erro: ${e instanceof Error ? e.message : 'Falha na requisição'}`,
      }])
    } finally {
      setSending(false)
    }
  }

  return (
    <>
      <AppBar title="Marketing IA" subtitle="Assistente de copy e campanhas" action={
        <button style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center' }} onClick={() => setMessages([])}>
          <Ico.history size={18} stroke="var(--text-1)" />
        </button>
      } />

      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <div style={{ display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4 }} className="lgd-scroll">
          {MODES.map(m => {
            const I = m.icon
            const on = activeMode === m.key
            return (
              <div key={m.key} onClick={() => setActiveMode(m.key)} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '8px 14px', borderRadius: 999, whiteSpace: 'nowrap', cursor: 'pointer',
                background: on ? 'rgba(212,168,71,0.1)' : 'var(--bg-2)',
                border: `1px solid ${on ? 'var(--gold-500)' : 'var(--line-1)'}`,
                color: on ? 'var(--gold-300)' : 'var(--text-2)',
                fontSize: 12, fontWeight: 600,
              }}>
                <I size={14} stroke={on ? 'var(--gold-500)' : 'var(--text-2)'} />
                {m.label}
              </div>
            )
          })}
        </div>
      </div>

      <ScreenBody pad={18}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, marginTop: 8 }}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <div style={{ width: 48, height: 48, borderRadius: 14, background: 'rgba(212,168,71,0.1)', border: '1px solid rgba(212,168,71,0.25)', display: 'grid', placeItems: 'center', margin: '0 auto 14px' }}>
                <Ico.sparkle size={22} stroke="var(--gold-500)" />
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-1)', marginBottom: 6 }}>LGD Assistant</div>
              <div style={{ fontSize: 12.5, color: 'var(--text-3)', maxWidth: 260, margin: '0 auto', lineHeight: 1.5 }}>
                Peça copies para redes sociais, descrições de produtos ou ideias de campanha.
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '92%' }}>
              {msg.role === 'assistant' && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                  <div style={{ width: 22, height: 22, borderRadius: 7, background: 'rgba(212,168,71,0.12)', display: 'grid', placeItems: 'center', border: '1px solid rgba(212,168,71,0.3)' }}>
                    <Ico.sparkle size={12} stroke="var(--gold-500)" />
                  </div>
                  <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-300)', letterSpacing: 0.4 }}>LGD ASSISTANT</span>
                </div>
              )}
              <div style={{
                padding: 12,
                borderRadius: msg.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                background: msg.role === 'user' ? 'var(--bg-3)' : 'var(--bg-1)',
                border: '1px solid var(--line-2)',
                fontSize: 13, lineHeight: 1.55, color: 'var(--text-1)',
                whiteSpace: 'pre-wrap',
              }}>
                {msg.text}
              </div>
            </div>
          ))}

          {sending && (
            <div style={{ alignSelf: 'flex-start' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
                <div style={{ width: 22, height: 22, borderRadius: 7, background: 'rgba(212,168,71,0.12)', border: '1px solid rgba(212,168,71,0.3)', display: 'grid', placeItems: 'center' }}>
                  <Ico.sparkle size={12} stroke="var(--gold-500)" />
                </div>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-300)' }}>LGD ASSISTANT</span>
              </div>
              <div style={{ padding: '12px 16px', borderRadius: '14px 14px 14px 4px', background: 'var(--bg-1)', border: '1px solid var(--line-2)', display: 'flex', gap: 5 }}>
                {[0, 1, 2].map(j => (
                  <div key={j} style={{ width: 6, height: 6, borderRadius: 99, background: 'var(--gold-500)', opacity: 0.7, animation: `spin 1s ease-in-out ${j * 0.15}s infinite` }} />
                ))}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScreenBody>

      <div style={{ padding: '8px 14px 6px', borderTop: '1px solid var(--line-1)', background: 'var(--bg-0)', flexShrink: 0, paddingBottom: 'calc(6px + env(safe-area-inset-bottom, 0px))' }}>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', padding: '6px 6px 6px 14px', borderRadius: 22, background: 'var(--bg-2)', border: '1px solid var(--line-2)' }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Pergunte ou peça uma copy…"
            style={{ flex: 1, background: 'transparent', border: 0, outline: 0, fontSize: 14, color: 'var(--text-1)' }}
          />
          <button onClick={handleSend} disabled={!input.trim() || sending} style={{ width: 38, height: 38, borderRadius: 19, background: input.trim() ? 'var(--gold-500)' : 'var(--bg-3)', border: 0, display: 'grid', placeItems: 'center', opacity: input.trim() ? 1 : 0.5 }}>
            <Ico.send size={18} stroke={input.trim() ? '#1A1408' : 'var(--text-3)'} sw={2.2} />
          </button>
        </div>
      </div>
      <BottomNav active="mk" />
    </>
  )
}
