import { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { toggleReport } from '../../store/reportSlice'
import { useAuth } from '../../context/AuthContext'
import { analyticsService } from '../../services/analyticsService'

function pythonLiteralToJson(src) {
  let i = 0, out = ''
  const peek = () => src[i]
  const consume = () => src[i++]

  function parseString() {
    const q = consume(); out += '"'
    while (i < src.length) {
      const ch = src[i]
      if (ch === '\\') {
        i++; const next = src[i++]
        if (next === q)    out += q === "'" ? "'" : '\\"'
        else if (next === '"') out += '\\"'
        else               out += '\\' + next
      } else if (ch === q) { i++; break
      } else if (ch === '"') { out += '\\"'; i++
      } else if (ch === '\n') { out += '\\n'; i++
      } else if (ch === '\r') { out += '\\r'; i++
      } else { out += ch; i++ }
    }
    out += '"'
  }

  function parseValue() {
    while (i < src.length && /\s/.test(src[i])) i++
    if (i >= src.length) return
    const ch = src[i]
    if (ch === "'" || ch === '"') parseString()
    else if (ch === '{') parseDict()
    else if (ch === '[') parseList()
    else if (src.slice(i,i+4)==='True')  { out+='true';  i+=4 }
    else if (src.slice(i,i+5)==='False') { out+='false'; i+=5 }
    else if (src.slice(i,i+4)==='None')  { out+='null';  i+=4 }
    else { while (i<src.length && !/[,}\]:\s]/.test(src[i])) out+=src[i++] }
    while (i < src.length && /\s/.test(src[i])) i++
  }

  function parseDict() {
    consume(); out+='{'; let first=true
    while (i<src.length && peek()!=='}') {
      while (i<src.length && /[\s,]/.test(peek())) i++
      if (peek()==='}') break
      if (!first) out+=','; first=false
      parseValue()
      while (i<src.length && /\s/.test(peek())) i++
      if (peek()===':') { consume(); out+=':' }
      parseValue()
    }
    if (peek()==='}') consume(); out+='}'
  }

  function parseList() {
    consume(); out+='['; let first=true
    while (i<src.length && peek()!==']') {
      while (i<src.length && /[\s,]/.test(peek())) i++
      if (peek()===']') break
      if (!first) out+=','; first=false
      parseValue()
    }
    if (peek()===']') consume(); out+=']'
  }

  parseValue(); return out
}

function parseChartSpec(raw) {
  if (!raw) return null
  if (typeof raw === 'object') return raw
  const str = String(raw).trim()
  if (!str || str === 'None' || str === 'null') return null
  try { return JSON.parse(str) } catch {}
  try { return JSON.parse(pythonLiteralToJson(str)) } catch {}
  return null
}

function parseSummaryDict(raw) {
  if (!raw) return null
  if (typeof raw === 'object') return raw
  const str = String(raw).trim()
  if (!str || str === 'None' || str === 'null') return null
  try { return JSON.parse(str) } catch {}
  try { return JSON.parse(pythonLiteralToJson(str)) } catch {}
  return { text: str } 
}

function parseReportHtml(raw) {
  if (!raw) return null
  const str = String(raw).trim()
  if (!str || str === 'None' || str === 'null') return null
  return str
}

function buildHistoryMessage(answer, chart_code, report, id) {
  const summary    = parseSummaryDict(answer)
  const chart_url  = parseChartSpec(chart_code)
  const reportHtml = parseReportHtml(report)

  if (!summary && !chart_url && !reportHtml) return null

  return {
    id,
    type: 'assistant',
    data: { status: 'success', summary: summary || {}, chart_url, report: reportHtml }
  }
}


function DataTable({ columns, rows }) {
  const [filter, setFilter] = useState('')
  const vis = filter
    ? rows.filter(r => r.some(c => String(c).toLowerCase().includes(filter.toLowerCase())))
    : rows
  return (
    <div style={{marginTop:'1rem'}}>
      <input className="result-filter" placeholder="Filter rows..." value={filter} onChange={e=>setFilter(e.target.value)} />
      <div className="result-table-scroll">
        <table className="result-table">
          <thead><tr>{columns.map((c,i)=><th key={i}>{c.replace(/_/g,' ').toUpperCase()}</th>)}</tr></thead>
          <tbody>{vis.map((row,ri)=><tr key={ri}>{row.map((cell,ci)=><td key={ci}>{String(cell)}</td>)}</tr>)}</tbody>
        </table>
      </div>
    </div>
  )
}

function PlotlyChart({ spec }) {
  const [show, setShow] = useState(false)
  const ref = useRef(); const done = useRef(false)
  useEffect(() => {
    if (show && !done.current && window.Plotly && ref.current) {
      done.current = true
      window.Plotly.newPlot(ref.current, spec.data, spec.layout, { responsive: true })
    }
  }, [show, spec])
  return (
    <div className="chart-toggle">
      <button className="chart-toggle-btn" onClick={() => setShow(v => !v)}>
        <span>{show ? 'Hide chart' : 'Show chart'}</span>
        <span style={{fontSize:'.75rem',opacity:.7}}>{show ? 'v' : '>'}</span>
      </button>
      {show && <div className="chart-container"><div ref={ref} className="chart-plot"/></div>}
    </div>
  )
}

function ReportToggle({ html, reportId }) {
  const dispatch = useDispatch()
  const show = useSelector(state => !!state.report.expandedReports[reportId])
  return (
    <div className="report-toggle">
      <button className="report-toggle-btn" onClick={() => dispatch(toggleReport(reportId))}>
        <span>{show ? 'Hide report' : 'Show detailed report'}</span>
        <span style={{fontSize:'.75rem',opacity:.7}}>{show ? 'v' : '>'}</span>
      </button>
      {show && (
        <div className="report-container">
          <div className="result-report-box" dangerouslySetInnerHTML={{__html: html}} />
        </div>
      )}
    </div>
  )
}

function Answer({ data, onFollowup, messageId }) {
  const { summary, chart_url, report } = data || {}
  const hasTable   = summary?.table?.columns?.length > 0 && summary?.table?.rows?.length > 0
  const hasText    = summary?.text?.trim?.().length > 0
  const reportHtml = report || summary?.report
  const hasReport  = !!(reportHtml && String(reportHtml).trim().length > 0)
  const followups  = summary?.followups || []
  const chart      = chart_url && typeof chart_url === 'object' ? chart_url : null

  if (!hasTable && !hasText && !hasReport && !chart)
    return <span style={{color:'var(--text-dim)'}}>No results.</span>

  return (
    <>
      {hasTable  && <DataTable columns={summary.table.columns} rows={summary.table.rows} />}
      {hasText   && <div className="result-text-box">{summary.text}</div>}
      {hasReport && <ReportToggle html={reportHtml} reportId={messageId || 'default'} />}
      {chart     && <PlotlyChart spec={chart} />}
      {followups.length > 0 && (
        <div className="followups-section">
          <p className="followups-label">You can also ask:</p>
          <div className="followups-pills">
            {followups.map((q,i) => (
              <button key={i} className="followup-btn" onClick={() => onFollowup(q)}>{q}</button>
            ))}
          </div>
        </div>
      )}
    </>
  )
}


export default function ChatScreen({ sessionId, sourceName, onReset }) {
  const { authToken } = useAuth()
  const [messages,    setMessages]    = useState([])
  const [input,       setInput]       = useState('')
  const [busy,        setBusy]        = useState(false)
  const [histLoading, setHistLoading] = useState(false)
  const bottom = useRef()

  useEffect(() => { bottom.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  useEffect(() => {
    if (!sessionId) return
    setMessages([]); setHistLoading(true)
    analyticsService.getSessionHistory(sessionId, authToken)
      .then(({ history = [] }) => {
        const ordered = history[0]?.created_at
          ? [...history].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
          : history

        setMessages(ordered.flatMap(({ query, answer, chart_code, report }, i) => {
          const userMsg      = query ? { id: `u${i}`, type: 'user', content: query } : null
          const assistantMsg = buildHistoryMessage(answer, chart_code, report, `a${i}`)
          return [userMsg, assistantMsg].filter(Boolean)
        }))
      })
      .catch(() => {})
      .finally(() => setHistLoading(false))
  }, [sessionId])

  async function send(q) {
    q = q.trim(); if (!q || !sessionId || busy) return
    const uid = `u_${Date.now()}`, lid = `l_${Date.now()}`
    setMessages(p => [...p, { id: uid, type: 'user', content: q }, { id: lid, type: 'loading' }])
    setInput(''); setBusy(true)
    try {
      const d = await analyticsService.query(sessionId, q, authToken)
      setMessages(p => [
        ...p.filter(m => m.id !== lid),
        d.status === 'success'
          ? { id: `a_${Date.now()}`, type: 'assistant', data: d }
          : { id: `e_${Date.now()}`, type: 'error', content: d.message || 'Unknown error' },
      ])
    } catch(e) {
      setMessages(p => [...p.filter(m => m.id !== lid), { id: `e_${Date.now()}`, type: 'error', content: e.message }])
    } finally { setBusy(false) }
  }

  return (
    <div className="chat-screen main-content">
      <div className="page-container">
        <div className="chat-wrapper">
          <div className="chat-main">
            <div className="chat-header">
              <div className="chat-header-inner">
                <div>
                  <div className="chat-source-label">Source:</div>
                  <div className="chat-source-value">{sourceName || sessionId}</div>
                </div>
                <button className="btn btn-secondary" style={{fontSize:'.875rem'}} onClick={onReset}>
                  New Session
                </button>
              </div>
            </div>

            <div className="chat-messages">
              {histLoading ? (
                <div className="chat-empty">
                  <span className="loading" style={{display:'block',margin:'0 auto .75rem'}}/>
                  <p className="chat-empty-sub">Loading conversation...</p>
                </div>
              ) : messages.length === 0 ? (
                <div className="chat-empty">
                  <p className="chat-empty-title">Ready to analyse your data</p>
                  <p className="chat-empty-sub">Ask me anything about your data using natural language</p>
                </div>
              ) : messages.map(m => {
                if (m.type === 'user')      return <div key={m.id} className="message message-user">{m.content}</div>
                if (m.type === 'loading')   return <div key={m.id} className="message message-assistant"><span className="loading" style={{marginRight:'.5rem'}}/>Processing...</div>
                if (m.type === 'text')      return <div key={m.id} className="message message-assistant" style={{whiteSpace:'pre-wrap'}}>{m.content}</div>
                if (m.type === 'html')      return <div key={m.id} className="message message-assistant" dangerouslySetInnerHTML={{__html:m.content}}/>
                if (m.type === 'assistant') return <div key={m.id} className="message message-assistant"><Answer data={m.data} onFollowup={q=>setInput(q)} messageId={m.id}/></div>
                if (m.type === 'error')     return <div key={m.id} className="message message-assistant" style={{color:'#ff6b6b'}}>Error: {m.content}</div>
                return null
              })}
              <div ref={bottom}/>
            </div>

            <div className="chat-input-area">
              <form className="chat-input-form" onSubmit={e => { e.preventDefault(); send(input) }}>
                <input
                  className="chat-input"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="Ask a question about your data..."
                  autoComplete="off"
                  disabled={busy || histLoading}
                />
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{padding:'0 1.5rem'}}
                  disabled={busy || histLoading || !input.trim()}
                >Send</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
