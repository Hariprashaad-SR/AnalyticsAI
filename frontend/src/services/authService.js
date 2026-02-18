const AUTH_BASE = 'http://localhost:8001'

export const authService = {
  async login(email, password) {
    const res  = await fetch(`${AUTH_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Login failed')
    return data 
  },

  async signup(name, email, password) {
    const res  = await fetch(`${AUTH_BASE}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Signup failed')
    return data
  },

  startGoogleAuth() {
    window.location.href = `${AUTH_BASE}/api/auth/google`
  },
}
