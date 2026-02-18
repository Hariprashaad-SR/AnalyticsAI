import { useState, useRef } from 'react'
import { useAuth } from '../../context/AuthContext'
import { analyticsService } from '../../services/analyticsService'

export default function UploadScreen({ onSessionReady }) {
  const { authToken } = useAuth()
  const [dbConn,   setDbConn]   = useState('')
  const [status,   setStatus]   = useState(null)
  const [dragging, setDragging] = useState(false)
  const fileRef = useRef()

  async function handleFile(file) {
    if (!file) return
    setStatus({ type:'loading', msg:'Uploading…' })
    try {
      const d = await analyticsService.uploadFile(file, authToken)
      setStatus({ type:'success', msg:'✓ Uploaded successfully!' })
      setTimeout(() => onSessionReady(d.session_id, d.filename), 900)
    } catch(e) { setStatus({ type:'error', msg:'✗ '+e.message }) }
  }

  async function connectDb() {
    if (!dbConn.trim()) { alert('Please enter a connection string'); return }
    setStatus({ type:'loading', msg:'Connecting…' })
    try {
      const d = await analyticsService.initSession(dbConn.trim(), authToken)
      setStatus({ type:'success', msg:'✓ Connected successfully!' })
      setTimeout(() => onSessionReady(d.session_id, dbConn.trim()), 900)
    } catch(e) { setStatus({ type:'error', msg:'✗ '+e.message }) }
  }

  const statusStyle = status?.type==='success' ? { background:'rgba(255,255,255,.1)', border:'1px solid #fff' }
                    : status?.type==='error'   ? { background:'rgba(255,68,68,.2)',   border:'1px solid #f44' }
                    : {}

  return (
    <div className="upload-screen main-content">
      <div className="page-container">
        <div className="page-header">
          <div className="page-logo">AnalyticsAI</div>
          <div className="page-tagline">Natural language data analysis powered by AI</div>
        </div>

        <div
          className={`upload-zone${dragging?' dragover':''}`}
          onDragOver={e=>{e.preventDefault();setDragging(true)}}
          onDragLeave={()=>setDragging(false)}
          onDrop={e=>{e.preventDefault();setDragging(false);handleFile(e.dataTransfer.files[0])}}
        >
          <svg style={{display:'block',margin:'0 auto 1rem'}} width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" />
          </svg>
          <h2>Upload Your Data Source</h2>
          <p>Drop your CSV, Excel, or enter a database connection string</p>
          <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls,.webp,.png" style={{display:'none'}}
            onChange={e=>handleFile(e.target.files[0])} />
          <button className="btn btn-primary" style={{marginBottom:'1rem'}} onClick={()=>fileRef.current?.click()}>
            Choose File
          </button>
          <div className="upload-divider">— OR —</div>
          <input className="db-input" type="text" value={dbConn} onChange={e=>setDbConn(e.target.value)}
            placeholder="postgresql://user:pass@host:5432/db" />
          <button className="btn btn-secondary" onClick={connectDb}>Connect to Database</button>
        </div>

        {status && (
          <div className="upload-status" style={statusStyle}>
            {status.type==='loading'
              ? <><span className="loading" style={{display:'block',margin:'0 auto .5rem'}}/>{status.msg}</>
              : status.msg}
          </div>
        )}
      </div>
    </div>
  )
}
