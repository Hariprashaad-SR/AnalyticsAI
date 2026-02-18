import { useAuth } from '../../context/AuthContext'

const AVATAR_FALLBACK = 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'

export default function TopNav({ onOpenLogin, onOpenSignup, onLogout }) {
  const { authUser } = useAuth()

  return (
    <nav className="top-nav">
      <span className="nav-logo">AnalyticsAI</span>

      <div className="nav-actions">
        {authUser ? (
          <>
            <img
              className="nav-avatar"
              src={authUser.pic || AVATAR_FALLBACK}
              alt={authUser.name || 'User'}
              onError={e => { e.currentTarget.src = AVATAR_FALLBACK }}
            />
            <span className="nav-user">{authUser.name}</span>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
              onClick={onLogout}
            >
              Log Out
            </button>
          </>
        ) : (
          <>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
              onClick={onOpenLogin}
            >
              Log In
            </button>
            <button
              className="btn btn-primary"
              style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}
              onClick={onOpenSignup}
            >
              Sign Up
            </button>
          </>
        )}
      </div>
    </nav>
  )
}
