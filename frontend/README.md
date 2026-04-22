# 🎨 VoteIQ Frontend

Premium dark-theme frontend for VoteIQ — Election Process Education Assistant.

## Features

- 🧠 **AI Chat Interface** — Conversational assistant with message bubbles
- 📅 **Timeline View** — Election phases and deadlines
- 🧭 **Step Guides** — Registration, voting, documents, polling, results
- 🎬 **Onboarding Splash** — First-visit animated welcome screen
- 📱 **Responsive** — Desktop, tablet, and mobile layouts
- ✨ **Glassmorphism** — Frosted glass cards with animated background
- 🛡️ **Error Handling** — Connection status, retries, rate limit awareness

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Markup | HTML5 (semantic) |
| Styling | Vanilla CSS (custom properties, grid, flexbox) |
| Logic | Vanilla JavaScript (ES6+, Fetch API) |
| Fonts | Google Fonts (Inter, Space Grotesk) |

## Running Locally

1. Start the backend first:
```bash
cd ../backend
uvicorn app.main:app --reload
```

2. Open `index.html` in your browser, or serve it:
```bash
# Python quick server
python -m http.server 3000

# Then open http://localhost:3000
```

3. The frontend connects to `http://localhost:8000` by default.
   Change `API_BASE` in `script.js` if your backend is elsewhere.

## File Structure

```
frontend/
├── index.html      # Main HTML (semantic, accessible, SEO)
├── style.css       # Design system (dark glassmorphism theme)
├── script.js       # API integration & interactivity
└── README.md       # You are here
```
