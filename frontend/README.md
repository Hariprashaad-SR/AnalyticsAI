# AnalyticsAI — React Frontend

Natural-language data analysis frontend, built with **React 18 + Vite + Tailwind CSS**.

---

## Project Structure

```
analytics-ai/
├── index.html                   # Vite HTML entry (loads Plotly CDN)
├── vite.config.js               # Vite + dev proxy → backend :5000
├── tailwind.config.js
├── postcss.config.js
├── package.json
└── src/
    ├── index.jsx                # React root mount
    ├── index.css                # All custom CSS (tokens, animations, layout)
    ├── App.jsx                  # Root component — manages session state
    │
    ├── services/
    │   └── analyticsService.js  # All backend API calls
    │       ├── uploadFile(file)
    │       ├── initSession(connectionString)
    │       └── sendQuery(sessionId, query)
    │
    └── components/
        ├── Background.jsx        # Animated grid + glowing orbs
        ├── Header.jsx            # Logo + tagline
        ├── UploadScreen.jsx      # File upload & DB connection form
        ├── ChatScreen.jsx        # Chat container — owns message state
        ├── ChatInput.jsx         # Controlled text input + send button
        ├── MessageBubble.jsx     # Renders user / assistant / loading / error
        ├── ResultTable.jsx       # Filterable data table
        ├── ChartDisplay.jsx      # Plotly chart with show/hide toggle
        └── FollowUpChips.jsx     # Clickable follow-up question pills
```

---

## Getting Started

```bash
npm install
npm run dev        # starts on http://localhost:5173
```

> The Vite dev server proxies `/api/*` to `http://localhost:5000` — update
> `vite.config.js` if your backend runs on a different port.

---

## Data Flow

```
App (session state)
 └─ UploadScreen  →  analyticsService.uploadFile / initSession
 └─ ChatScreen    →  analyticsService.sendQuery
      └─ MessageBubble
           ├─ ResultTable     (table data)
           ├─ ChartDisplay    (Plotly spec)
           └─ FollowUpChips   (suggested questions)
```

---

## Backend Contract

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/api/upload` | POST | `FormData { file }` | `{ status, session_id, filename }` |
| `/api/init-session` | POST | `{ file_path }` | `{ status, session_id }` |
| `/api/query` | POST | `{ session_id, query }` | `{ status, summary, chart_url? }` |

`summary` shape:
```json
{
  "text": "string",
  "table": { "columns": [...], "rows": [[...], ...] },
  "followups": ["...", "..."]
}
```

`chart_url` is a JSON-stringified Plotly spec `{ data: [...], layout: {...} }`.
