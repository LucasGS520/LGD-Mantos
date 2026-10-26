import { useState } from 'react'
import { Ico } from '../components/Icons'
import { useNav } from '../nav'
import { api } from '../services/api'

export default function Login() {
  const { setTab } = useNav()
  const [password, setPassword] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleLogin = async () => {
    if (!password.trim()) return
    setLoading(true)
    setError(null)
    try {
      await api.login(password)
      setTab('op')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao fazer login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      background: 'radial-gradient(120% 60% at 50% 0%, rgba(212,168,71,0.12), transparent 60%), #0A0A0B',
    }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '0 36px' }}>
        <div style={{
          width: 140, height: 140, borderRadius: 28, display: 'grid', placeItems: 'center',
          background: 'linear-gradient(180deg, rgba(212,168,71,0.10), rgba(212,168,71,0.02))',
          border: '1px solid rgba(212,168,71,0.25)', marginBottom: 28,
        }}>
          <img src="/logo_lgd.png" style={{ width: 110, height: 110, objectFit: 'contain', filter: 'drop-shadow(0 6px 20px rgba(212,168,71,0.25))' }} alt="LGD" />
        </div>
        <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', letterSpacing: 4, textTransform: 'uppercase', marginBottom: 8 }}>
          Streetwear Ops
        </div>
        <div style={{ fontFamily: '"Bebas Neue", Inter', fontSize: 38, fontWeight: 700, letterSpacing: 1, color: 'var(--text-1)' }}>
          LGD MANTOS
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-3)', marginTop: 6, textAlign: 'center', maxWidth: 240 }}>
          Controle total da sua loja em um lugar.
        </div>
      </div>

      <div style={{ padding: '0 24px', paddingBottom: 'calc(24px + env(safe-area-inset-bottom, 0px))' }}>
        {error && (
          <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.12)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B', fontWeight: 600, textAlign: 'center' }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, height: 56, padding: '0 16px', borderRadius: 14, background: 'var(--bg-2)', border: '1px solid var(--line-2)' }}>
            <Ico.lock size={20} stroke="var(--gold-500)" />
            <input
              type={showPwd ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleLogin()}
              placeholder="Senha"
              autoComplete="current-password"
              style={{
                flex: 1, background: 'transparent', border: 0, outline: 0,
                color: 'var(--text-1)', fontSize: 16,
                letterSpacing: showPwd ? 'normal' : 4,
              }}
            />
            <div onClick={() => setShowPwd(v => !v)} style={{ cursor: 'pointer', padding: 4 }}>
              {showPwd
                ? <Ico.eyeOff size={20} stroke="var(--text-3)" />
                : <Ico.eye size={20} stroke="var(--text-3)" />
              }
            </div>
          </div>
        </div>

        <button
          onClick={handleLogin}
          disabled={loading || !password.trim()}
          style={{
            width: '100%', height: 56, borderRadius: 14,
            background: 'var(--gold-500)', color: '#1A1408', border: 0,
            fontSize: 15, fontWeight: 800, letterSpacing: 0.5,
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
            boxShadow: '0 8px 24px rgba(212,168,71,0.25)',
            opacity: loading || !password.trim() ? 0.6 : 1,
          }}
        >
          {loading ? 'Entrando…' : 'ENTRAR NA LOJA'}
          {!loading && <Ico.chevron size={18} stroke="#1A1408" sw={2.5} />}
        </button>

        <div style={{ marginTop: 18, textAlign: 'center', fontSize: 11, color: 'var(--text-4)', fontFamily: 'var(--font-mono)' }}>
          v1.0.0 · single user · offline-ready
        </div>
      </div>
    </div>
  )
}
