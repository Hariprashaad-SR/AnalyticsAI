import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import GoogleIcon from './GoogleIcon'

export default function SignupModal({ onClose, onSwitchToLogin, onSuccess }) {
  const { signup, googleAuth } = useAuth()
  const [name,    setName]   = useState('')
  const [email,   setEmail]  = useState('')
  const [pass,    setPass]   = useState('')
  const [conf,    setConf]   = useState('')
  const [error,   setError]  = useState('')
  const [loading, setLoading]= useState(false)

  const backdrop = e => { if (e.target === e.currentTarget) onClose() }

  const submit = async e => {
    e.preventDefault()
    setError('')
    if (!name || !email || !pass || !conf) { setError('Please fill in all fields.'); return }
    if (pass !== conf) { setError('Passwords do not match.'); return }
    if (pass.length < 8) { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try { await signup(name, email, pass); onSuccess() }
    catch(err) { setError(err.message) }
    finally { setLoading(false) }
  }

  return (
    <div className="modal-backdrop" onClick={backdrop}>
      <div className="modal-box">
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2 className="modal-title">Create account</h2>
        <p className="modal-sub">Start analysing your data with AI</p>

        <button className="google-btn" onClick={googleAuth}><GoogleIcon /> Sign up with Google</button>
        <div className="modal-divider"><span>or sign up with email</span></div>

        <form className="auth-form" onSubmit={submit}>
          <div className="auth-field">
            <label>Full Name</label>
            <input type="text" value={name} onChange={e=>setName(e.target.value)} placeholder="Jane Smith" autoComplete="name" />
          </div>
          <div className="auth-field">
            <label>Email</label>
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" />
          </div>
          <div className="auth-field">
            <label>Password</label>
            <input type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="Min 8 characters" autoComplete="new-password" />
          </div>
          <div className="auth-field">
            <label>Confirm Password</label>
            <input type="password" value={conf} onChange={e=>setConf(e.target.value)} placeholder="••••••••" autoComplete="new-password" />
          </div>
          {error && <div className="auth-error">{error}</div>}
          <button type="submit" className="btn btn-primary" style={{width:'100%'}} disabled={loading}>
            {loading ? <span className="loading"/> : 'Create Account'}
          </button>
        </form>

        <p className="modal-footer">
          Already have an account? <button className="modal-link" onClick={onSwitchToLogin}>Sign in</button>
        </p>
      </div>
    </div>
  )
}
