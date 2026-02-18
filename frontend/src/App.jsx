import { useState, useEffect, useCallback } from 'react'
import { useAuth } from './context/AuthContext'
import { analyticsService } from './services/analyticsService'

import Background    from './components/ui/Background'
import TopNav        from './components/ui/TopNav'
import Sidebar       from './components/ui/Sidebar'
import LoginModal    from './components/modals/LoginModal'
import SignupModal   from './components/modals/SignupModal'
import LandingScreen from './components/screens/LandingScreen'
import HomeScreen    from './components/screens/HomeScreen'
import UploadScreen  from './components/screens/UploadScreen'
import ChatScreen    from './components/screens/ChatScreen'


function getInitialScreen() {
  try {
    const user = JSON.parse(localStorage.getItem('aai_user'))
    return user ? 'home' : 'landing'
  } catch {
    return 'landing'
  }
}

export default function App() {
  const { authUser, authToken, logout } = useAuth()

  const [screen,          setScreen]          = useState(getInitialScreen)
  const [modal,           setModal]           = useState(null)
  const [sessions,        setSessions]        = useState([])
  const [sessionsLoading, setSessionsLoading] = useState(false)
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [sourceName,      setSourceName]      = useState('')

  useEffect(() => {
    if (authUser) {
      document.body.classList.add('has-sidebar')
    } else {
      document.body.classList.remove('has-sidebar', 'sb-open')
    }
  }, [authUser])

  const loadSessions = useCallback(async () => {
    if (!authToken) return
    setSessionsLoading(true)
    try {
      const data = await analyticsService.getSessions(authToken)
      setSessions(data.sessions || [])
    } catch {
      setSessions([])
    } finally {
      setSessionsLoading(false)
    }
  }, [authToken])

  useEffect(() => {
    if (authUser) {
      setScreen(prev => prev === 'landing' ? 'home' : prev)
      loadSessions()
    } else {
      setScreen('landing')
      setModal(null)
      setSessions([])
      setActiveSessionId(null)
      setSourceName('')
    }
  }, [authUser]) 

  // Modal helpers
  const openLogin  = () => setModal('login')
  const openSignup = () => setModal('signup')
  const closeModal = () => setModal(null)

  const onAuthSuccess = () => {
    closeModal()
    setScreen('home')
    loadSessions()
  }

  const handleLogout = () => logout()

  // Navigation
  const onSessionReady = (id, name) => {
    setActiveSessionId(id)
    setSourceName(name)
    loadSessions()
    setScreen('chat')
  }

  const onSelectSession = (id, label) => {
    setActiveSessionId(id)
    setSourceName(label)
    setScreen('chat')
  }

  const onReset = () => {
    setActiveSessionId(null)
    setSourceName('')
    setScreen('home')
  }

  return (
    <>
      <Background />

      {authUser && (
        <Sidebar
          sessions={sessions}
          loading={sessionsLoading}
          activeSessionId={activeSessionId}
          onNewChat={() => setScreen('upload')}
          onSelectSession={onSelectSession}
        />
      )}

      
      <TopNav
        onOpenLogin={openLogin}
        onOpenSignup={openSignup}
        onLogout={handleLogout}
      />

      {/* Page content */}
      {screen === 'landing' && (
        <LandingScreen onOpenLogin={openLogin} onOpenSignup={openSignup} />
      )}
      {screen === 'home' && (
        <HomeScreen onStartChat={() => setScreen('upload')} />
      )}
      {screen === 'upload' && (
        <UploadScreen onSessionReady={onSessionReady} />
      )}
      {screen === 'chat' && (
        <ChatScreen sessionId={activeSessionId} sourceName={sourceName} onReset={onReset} />
      )}

      {/* Modals */}
      {modal === 'login' && (
        <LoginModal
          onClose={closeModal}
          onSwitchToSignup={() => setModal('signup')}
          onSuccess={onAuthSuccess}
        />
      )}
      {modal === 'signup' && (
        <SignupModal
          onClose={closeModal}
          onSwitchToLogin={() => setModal('login')}
          onSuccess={onAuthSuccess}
        />
      )}
    </>
  )
}
