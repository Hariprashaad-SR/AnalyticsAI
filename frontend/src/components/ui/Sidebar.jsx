import { useState } from 'react'

const ICONS = { csv:'📄', xlsx:'📊', xls:'📊', pdf:'📑', png:'🖼️', webp:'🖼️', postgresql:'🐘', mysql:'🐬' }
function icon(type) { return ICONS[(type||'').toLowerCase()] || '📂' }
function label(s)   { return (s.uploaded_file || 'Unnamed').split(/[/\\]/).pop() }
function ago(iso) {
  if (!iso) return ''
  const ms = Date.now() - new Date(iso)
  const m = Math.floor(ms/60000), h = Math.floor(ms/3600000), d = Math.floor(ms/86400000)
  if (m<1) return 'just now'; if (m<60) return `${m}m ago`
  if (h<24) return `${h}h ago`; if (d<30) return `${d}d ago`
  return new Date(iso).toLocaleDateString()
}

export default function Sidebar({ sessions, loading, activeSessionId, onNewChat, onSelectSession }) {
  const [open, setOpen] = useState(false)
  const toggle = () => {
    const next = !open
    setOpen(next)
    document.body.classList.toggle('sb-open', next)
  }

  return (
    <div className={`sidebar${open ? ' open' : ''}`}>
      <button className="sb-toggle" onClick={toggle}>{open ? '‹' : '›'}</button>
      <div className="sb-inner">
        <div className="sb-header">
          <span className="sb-title">Chat History</span>
          <button className="sb-new-btn" onClick={onNewChat}>+ New</button>
        </div>
        <div className="sb-list">
          {loading ? (
            <div className="sb-empty"><span className="loading" style={{ display:'block',margin:'0 auto .5rem' }} />Loading…</div>
          ) : sessions.length === 0 ? (
            <div className="sb-empty">No chats yet.<br />Start one above ↑</div>
          ) : sessions.map(s => (
            <div
              key={s.session_id}
              className={`sb-item${s.session_id === activeSessionId ? ' active' : ''}`}
              onClick={() => onSelectSession(s.session_id, label(s))}
            >
              <div className="sb-item-icon">{icon(s.file_type)}</div>
              <div className="sb-item-body">
                <div className="sb-item-name">{label(s)}</div>
                <div className="sb-item-meta">
                  <span className="sb-item-badge">{(s.file_type||'file').toUpperCase()}</span>
                  {ago(s.created_at)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
