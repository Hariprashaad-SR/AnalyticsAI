const FEATURES = [
  {title:'Natural Language',    desc:'Ask questions the way you think. No SQL, no code.' },
  {title:'Instant Charts',      desc:'Auto-generated Plotly charts from your questions.' },
  {title:'Any Data Source',     desc:'CSV, Excel, PostgreSQL, MySQL — connect anything.' },
  {title:'Follow-Up Questions', desc:'Drill deeper with AI-suggested follow-ups.' },
]

export default function LandingScreen({ onOpenLogin, onOpenSignup }) {
  return (
    <div className="landing-screen main-content">
      <div className="landing-hero">
        <div className="hero-badge">✦ AI-Powered Data Analysis</div>
        <h1 className="hero-title">Talk to your data<br /><em>like never before</em></h1>
        <p className="hero-sub">
          Upload a CSV, connect a database, and ask questions in plain English.
          Instant answers, auto-generated charts, zero SQL required.
        </p>
        <div className="hero-cta-row">
          <button className="btn btn-primary"   onClick={onOpenSignup}>Get Started Free</button>
          <button className="btn btn-secondary" onClick={onOpenLogin}>Log In</button>
        </div>
      </div>
      <div className="feature-grid">
        {FEATURES.map(f => (
          <div className="feature-card" key={f.title}>
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
