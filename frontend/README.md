# AnalyticsAI — Frontend

A React + Vite single-page application for natural-language data analysis. Users upload a CSV/Excel file or connect a database, then ask plain-English questions and receive instant answers, filterable tables, and auto-generated Plotly charts.

---

## Quick Start

```bash
cd aai
npm install
npm run dev        # → http://localhost:3000
```

**Required backends:**
| Service | Default URL |
|---|---|
| Auth API (login, signup, Google OAuth) | `http://localhost:8001` |
| Analytics API (upload, query, sessions) | `http://localhost:8000` |

---

## Project Structure

```
aai/
├── index.html                          # Shell HTML — loads Plotly CDN + Google Fonts
├── vite.config.js                      # Dev server (port 3000) + API proxies
├── package.json
└── src/
    ├── main.jsx                        # React root — wraps App in AuthProvider
    ├── App.jsx                         # Root component — owns all routing + nav state
    ├── index.css                       # All styles (tokens, layout, components, animations)
    ├── context/
    │   └── AuthContext.jsx             # Global auth state (synchronous init from localStorage)
    ├── services/
    │   ├── authService.js              # Auth API calls → localhost:8001
    │   └── analyticsService.js        # Analytics API calls → localhost:8000
    └── components/
        ├── ui/
        │   ├── Background.jsx          # Animated grid + glowing orbs (CSS-only)
        │   ├── TopNav.jsx              # Fixed top bar — login/signup or user avatar + logout
        │   └── Sidebar.jsx            # Collapsible session history panel
        ├── modals/
        │   ├── LoginModal.jsx          # Email login + Google OAuth button
        │   ├── SignupModal.jsx         # Name/email/password/confirm + Google OAuth
        │   └── GoogleIcon.jsx         # Inline Google SVG logo
        └── screens/
            ├── LandingScreen.jsx       # Public homepage with hero + feature grid
            ├── HomeScreen.jsx         # Logged-in dashboard with "Start Chat" CTA
            ├── UploadScreen.jsx        # File upload + DB connection string input
            └── ChatScreen.jsx         # Full chat UI with table, chart, follow-up pills
```

---

## User Flows

### 1. Unauthenticated Visit

```
Browser opens → App reads localStorage (no token found)
    │
    ▼
LandingScreen renders
    ├── "Get Started Free" → opens SignupModal
    └── "Log In"          → opens LoginModal
```

The landing page shows a hero section ("Talk to your data like never before") with four feature cards: Natural Language, Instant Charts, Any Data Source, Follow-Up Questions.

---

### 2. Sign Up / Log In

```
LoginModal or SignupModal opens (modal-backdrop dims page behind it)
    │
    ├── Email form submitted
    │       └── authService.login() / authService.signup() → POST localhost:8001
    │               └── success: token + user stored in localStorage
    │                           AuthContext sets authUser synchronously
    │                           App.useEffect sees authUser → navigates to HomeScreen
    │
    └── "Sign in with Google" clicked
            └── window.location → localhost:8001/api/auth/google
                    └── Google redirects back to localhost:3000?token=JWT&user=base64
                            └── AuthContext.useEffect detects URL params on mount
                                parses token + user, stores in localStorage
```

---

### 3. Refresh (Logged-In User)

```
Page reloads
    │
    ▼
AuthContext initialises — reads localStorage SYNCHRONOUSLY in useState()
    │
    ▼
authUser is already set before any render
    │
    ▼
App.getInitialScreen() also reads localStorage synchronously
    │
    ▼
HomeScreen renders immediately — no flash, no loading spinner
```

This is the fix for the blank-screen-on-refresh bug. There is zero async work on startup; no server round-trip is needed before the first paint.

---

### 4. Starting an Analysis Session

```
HomeScreen → "Start Chat" button
    │
    ▼
UploadScreen
    ├── Drag & drop or "Choose File"
    │       └── analyticsService.uploadFile() → POST /api/upload
    │               └── returns { session_id, filename }
    │
    └── Database connection string → "Connect to Database"
            └── analyticsService.initSession() → POST /api/init-session
                    └── returns { session_id }
    │
    ▼  (on success, after 900ms delay to show the ✓ status)
ChatScreen (with session_id and source name in state)
```

---

### 5. Chat / Query Flow

```
ChatScreen
    │
    ├── On mount: analyticsService.getSessionHistory(sessionId)
    │       └── loads prior { query, answer } pairs from the session
    │
    └── User types query → hits Send or Enter
            │
            ▼
        User message appended to messages[]
        Loading bubble appended ("Processing your query…")
            │
            ▼
        analyticsService.query(sessionId, queryText) → POST /api/query
            │
            ▼
        Response: { status, summary: { text, table, followups }, chart_url }
            │
            ├── summary.table   → <DataTable> with filter input
            ├── summary.text    → <div className="result-text-box">
            ├── chart_url (JSON)→ <PlotlyChart> collapsible panel
            └── summary.followups → clickable pill buttons (auto-fill input)
```

---

### 6. Logout

```
TopNav "Log Out" clicked
    │
    ▼
App.handleLogout() → calls logout() from AuthContext
    │
    ▼
AuthContext._wipe():
    localStorage.removeItem(token)
    localStorage.removeItem(user)
    setAuthToken(null)
    setAuthUser(null)          ← synchronous React state update
    │
    ▼
React re-renders all context consumers in the same batch:
    ├── TopNav sees authUser=null → shows "Log In" + "Sign Up" buttons immediately
    └── App.useEffect([authUser]) fires → setScreen('landing'), clears sessions/state
```

This is the fix for the "nav stays logged in after logout" bug. Because there is **no async background fetch** in AuthContext, nothing can call `_persist()` after logout. The state change is final on the first render.

---

## Architecture Decisions

### Authentication — Synchronous Init, No Background Verification

Previous versions fired an async `getMe()` fetch on every page load to verify the stored token against the server. This caused two bugs:

1. **Logout race:** The in-flight `getMe()` would complete *after* logout ran `setAuthUser(null)` and call `persistAuth()` again — snapping the nav back to showing the logged-in state.
2. **Refresh blank screen:** If the auth server was unreachable, the app hung waiting for a response and never set `authReady = true`.

**Current approach:** Auth state is read from `localStorage` synchronously in `useState(() => ...)`. No `useEffect`, no `Promise`, no possible race. If a stored token is expired, the analytics API returns `401` on the first query and the app can handle that gracefully. No startup penalty, no spinner, no race condition.

### Single Source of Truth for Screen Routing

`App.jsx` owns the `screen` state variable. The only thing allowed to change `screen` in response to auth is the `useEffect([authUser])` watcher:

- `authUser` → truthy: go to `'home'` (if currently on `'landing'`)
- `authUser` → null: go to `'landing'` and clear all session state

`handleLogout` does **only** `logout()` — it never calls `setScreen()` directly. This prevents double-transitions and ensures the nav and screen always update in the same render cycle.

### TopNav Always Rendered

`TopNav` is rendered **unconditionally** in `App.jsx`, never behind an auth-ready gate or loading check. It reads `authUser` directly from `useAuth()` (a context consumer), so React guarantees it re-renders the moment `authUser` changes — with no coordination, props, or callbacks needed.

### API Proxying

In development, Vite proxies `/api/*` routes to `localhost:8000` (analytics). Auth calls hit `localhost:8001` directly (no proxy) since they use an absolute URL in `authService.js`. This means you can point `AUTH_BASE` in `authService.js` at any host without touching `vite.config.js`.

---

## Screen Reference

| Screen | Route Trigger | Key Component |
|---|---|---|
| `landing` | `authUser` is null | `LandingScreen.jsx` |
| `home` | `authUser` becomes non-null | `HomeScreen.jsx` |
| `upload` | "Start Chat" or "+ New" in sidebar | `UploadScreen.jsx` |
| `chat` | Session created or selected from sidebar | `ChatScreen.jsx` |

---

## Sidebar

The sidebar is a collapsible panel (48px collapsed → 268px expanded) that shows the user's past chat sessions. It is only rendered when `authUser` is truthy. Clicking a session loads its history into `ChatScreen` via `getSessionHistory()`. The sidebar uses CSS transitions (no JS animation library) and toggles a `sb-open` class on `<body>` to shift the main content margin.

---

## Styling

All styles live in `src/index.css` — no CSS modules, no Tailwind. Key design tokens:

```css
--text:       #ffffff
--text-dim:   #a0a0a0
--border:     #333333
--sb-w:       48px          /* sidebar collapsed width */
--sb-w-open:  268px         /* sidebar expanded width */
```

The animated background is pure CSS: a `background-image` grid that translates on a 20s loop (`gridMove`) and two radial blur orbs that float on a 12–15s loop (`floatOrb`). No canvas, no WebGL.

---

## Environment / Backend Contract

### Auth API (localhost:8001)

| Endpoint | Method | Body | Response |
|---|---|---|---|
| `/api/auth/login` | POST | `{ email, password }` | `{ access_token, user }` |
| `/api/auth/signup` | POST | `{ name, email, password }` | `{ access_token, user }` |
| `/api/auth/google` | GET | — | Redirects → `/?token=JWT&user=base64` |

### Analytics API (localhost:8000, proxied via `/api/*`)

| Endpoint | Method | Body | Response |
|---|---|---|---|
| `/api/upload` | POST | `FormData { file }` | `{ status, session_id, filename }` |
| `/api/init-session` | POST | `{ file_path }` | `{ status, session_id }` |
| `/api/query` | POST | `{ session_id, query }` | `{ status, summary, chart_url }` |
| `/api/sessions` | GET | — | `{ sessions: [...] }` |
| `/api/sessions/:id/history` | GET | — | `{ history: [{ query, answer }] }` |

The `summary` object shape:
```json
{
  "text": "Plain text answer",
  "table": { "columns": ["col1", "col2"], "rows": [["a", "b"]] },
  "followups": ["What is the trend?", "Show me by region"]
}
```

`chart_url` is a JSON string of a Plotly figure spec: `{ data: [...], layout: {...} }`.
