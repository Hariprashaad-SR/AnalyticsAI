function hdr(token, extra = {}) {
  return { Authorization: `Bearer ${token}`, ...extra }
}

export const analyticsService = {
  async uploadFile(file, token) {
    const fd = new FormData()
    fd.append('file', file)
    const res  = await fetch('/api/upload', { method: 'POST', headers: hdr(token), body: fd })
    const data = await res.json()
    if (!res.ok || data.status !== 'success') throw new Error(data.message || 'Upload failed')
    return data
  },

  async initSession(connStr, token) {
    const res  = await fetch('/api/init-session', {
      method: 'POST',
      headers: hdr(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ file_path: connStr }),
    })
    const data = await res.json()
    if (!res.ok || data.status !== 'success') throw new Error(data.message || 'Connection failed')
    return data
  },

  async query(sessionId, query, token) {
    const res  = await fetch('/api/query', {
      method: 'POST',
      headers: hdr(token, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({ session_id: sessionId, query }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message || 'Query failed')
    return data
  },

  async getSessions(token) {
    const res = await fetch('/api/sessions', { headers: hdr(token) })
    if (!res.ok) throw new Error('Failed to load sessions')
    return res.json()
  },

  async getSessionHistory(sessionId, token) {
    const res = await fetch(`/api/sessions/${sessionId}/history`, { headers: hdr(token) })
    if (!res.ok) throw new Error('Failed to load history')
    return res.json()
  },
}
