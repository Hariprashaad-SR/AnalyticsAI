import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import GoogleIcon from './GoogleIcon'

export default function LoginModal({ onClose, onSwitchToSignup, onSuccess }) {
  const { login, googleAuth } = useAuth()
  const [email,   setEmail]  = useState('')
  const [pass,    setPass]   = useState('')
  const [error,   setError]  = useState('')
  const [loading, setLoading]= useState(false)

  const backdrop = e => { if (e.target === e.currentTarget) onClose() }

  const submit = async e => {
    e.preventDefault()
    setError('')
    if (!email || !pass) { setError('Please fill in all fields.'); return }
    setLoading(true)
    try { await login(email, pass); onSuccess() }
    catch(err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="modal-backdrop" onClick={backdrop}>
      <div className="modal-box">
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2 className="modal-title">Welcome back</h2>
        <p className="modal-sub">Sign in to your AnalyticsAI account</p>

        <button className="google-btn" onClick={googleAuth}><GoogleIcon /> Sign in with Google</button>
        <div className="modal-divider"><span>or continue with email</span></div>

        <form className="auth-form" onSubmit={submit}>
          <div className="auth-field">
            <label>Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" />
          </div>
          <div className="auth-field">
            <label>Password</label>
            <input type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="••••••••" autoComplete="current-password" />
          </div>
          {error && <div className="auth-error">{error}</div>}
          <button type="submit" className="btn btn-primary" style={{width:'100%'}} disabled={loading}>
            {loading ? <span className="loading"/> : 'Sign In'}
          </button>
        </form>

        <p className="modal-footer">
          Don&apos;t have an account? <button className="modal-link" onClick={onSwitchToSignup}>Sign up</button>
        </p>
      </div>
    </div>
  )
}
