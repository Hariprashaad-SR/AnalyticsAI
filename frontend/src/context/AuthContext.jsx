import { createContext, useContext, useState, useEffect } from 'react'
import { authService } from '../services/authService'

const TOKEN_KEY = 'aai_token'
const USER_KEY  = 'aai_user'

const AuthContext = createContext(null)

function readToken() {
  return localStorage.getItem(TOKEN_KEY) || null
}
function readUser() {
  try { return JSON.parse(localStorage.getItem(USER_KEY)) || null }
  catch { return null }
}

export function AuthProvider({ children }) {
  const [authToken, setAuthToken] = useState(readToken)
  const [authUser,  setAuthUser]  = useState(readUser)

  const authReady = true

  useEffect(() => {
    const params  = new URLSearchParams(window.location.search)
    const cbToken = params.get('token')
    const cbUser  = params.get('user')
    if (!cbToken || !cbUser) return

    try {
      const user = JSON.parse(atob(cbUser))
      _persist(cbToken, user)
    } catch {
      _wipe()
    }
    window.history.replaceState({}, '', window.location.pathname)
  }, [])

  function _persist(token, user) {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    setAuthToken(token)
    setAuthUser(user)   
  }

  function _wipe() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setAuthToken(null)
    setAuthUser(null) 
  }

  async function login(email, password) {
    const { access_token, user } = await authService.login(email, password)
    _persist(access_token, user)
    return user
  }

  async function signup(name, email, password) {
    const { access_token, user } = await authService.signup(name, email, password)
    _persist(access_token, user)
    return user
  }

  function logout() {
    _wipe()
  }

  function googleAuth() {
    authService.startGoogleAuth()
  }

  return (
    <AuthContext.Provider value={{ authReady, authToken, authUser, login, signup, logout, googleAuth }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
