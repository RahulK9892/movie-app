# 🎬 LUMORA

A sleek, Netflix-inspired movie & TV series discovery app built with **Streamlit** and the **TMDB API**. Browse trending titles, explore details, watch trailers, and curate your personal watchlist — all in a dark, cinematic UI.

---

## ✨ Features

- **Browse, Movies & Series tabs** — Switch between trending content, popular movies, and top-rated series with a single click
- **Cinematic Hero Banner** — Full-screen backdrop with title, rating, genres, and overview for the featured title
- **Movie & Series Cards** — Poster grid with rating and year, click any card to open the detail page
- **Detail Page with Tabs**
  - Overview — poster, stats (budget, revenue, profit), full description, studio info
  - Trailer & Videos — embedded YouTube trailers sorted by official relevance
  - Scenes — full backdrop image gallery
  - Cast & Crew — director card, key crew, full cast grid
  - Reviews — audience reviews with ratings
  - Similar — related titles you can click into
- **My List** — Add/remove titles to a personal watchlist that persists in session
- **Search** — Live search across movies and series
- **Fully custom dark UI** — Gold accent palette, Cinzel + Nunito Sans typography, pill-style nav buttons with active state highlighting

---

## 🖥️ Screenshots

> Deploy the app and replace this section with your own screenshots.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/lumora.git
cd lumora
```

### 2. Install dependencies

```bash
pip install streamlit requests
```

### 3. Get a free TMDB API key

1. Go to [themoviedb.org](https://www.themoviedb.org/) and create a free account
2. Navigate to **Settings → API** and request an API key (v3 auth)
3. Copy your API key

### 4. Add your API key

Create a file at `.streamlit/secrets.toml`:

```toml
TMDB_API_KEY = "your_api_key_here"
```

> ⚠️ Never commit this file to GitHub. It is already covered by the `.gitignore` below.

### 5. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. In the app settings, go to **Secrets** and add:

```toml
TMDB_API_KEY = "your_api_key_here"
```

4. Click **Deploy** — your app will be live in seconds

---

## 📁 Project Structure

```
lumora/
├── app.py                  # Main Streamlit application
├── .streamlit/
│   └── secrets.toml        # TMDB API key (local only, not committed)
├── .gitignore
└── README.md
```

---

## 🔧 Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | App framework & UI rendering |
| [TMDB API](https://www.themoviedb.org/documentation/api) | Movie & TV data, images, trailers |
| [Google Fonts](https://fonts.google.com) | Cinzel + Nunito Sans typography |
| Python `requests` | HTTP calls to TMDB |

---

## 📄 .gitignore

Create a `.gitignore` file in the root with:

```
.streamlit/secrets.toml
__pycache__/
*.pyc
.env
```

---

## 🙏 Credits

- Movie & TV data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/)
- This product uses the TMDB API but is not endorsed or certified by TMDB

---

## 📜 License

MIT License — free to use, modify, and distribute.
