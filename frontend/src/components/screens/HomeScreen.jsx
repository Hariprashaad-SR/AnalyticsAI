import { useAuth } from '../../context/AuthContext'

export default function HomeScreen({ onStartChat }) {
  const { authUser } = useAuth()
  const first = (authUser?.name || 'there').split(' ')[0]

  return (
    <div className="home-screen main-content">
      <div className="home-greeting">Good to see you, {first} </div>
      <h1 className="home-title">What are we<br /><span>analysing today?</span></h1>
      <p className="home-sub">Upload a file or connect a database and let AI turn your data into answers.</p>
      <button className="btn btn-primary home-start-btn" onClick={onStartChat}>
        Start Chat
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </button>
      <div className="home-pills">
        <div className="home-pill"><div className="home-pill-label mono">CSV</div><div className="home-pill-sub">Files</div></div>
        <div className="home-pill-sep" />
        <div className="home-pill"><div className="home-pill-label mono">Excel</div><div className="home-pill-sub">Spreadsheets</div></div>
        <div className="home-pill-sep" />
        <div className="home-pill"><div className="home-pill-label mono">SQL</div><div className="home-pill-sub">Databases</div></div>
      </div>
    </div>
  )
}
