import streamlit as st
import requests

# ================= CONFIG =================
st.set_page_config(page_title="LUMORA", layout="wide", page_icon="🎬")

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG      = "https://image.tmdb.org/t/p/w342"
IMG_LG   = "https://image.tmdb.org/t/p/w500"
BACKDROP_SM = "https://image.tmdb.org/t/p/w1280"

# ================= CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Cinzel:wght@700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0f0f0f !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── NAVBAR ── */
.lumora-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 48px;
    height: 64px;
    background: linear-gradient(to bottom, rgba(0,0,0,0.85) 0%, transparent 100%);
    transition: background 0.3s ease;
}
.lumora-logo {
    font-family: 'Cinzel', serif;
    font-size: 1.55rem;
    font-weight: 900;
    background: linear-gradient(135deg, #ff9d5c, #e8c97e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.2em;
}
.nav-links {
    display: flex;
    gap: 32px;
    align-items: center;
}
.nav-link {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255,255,255,0.65);
    letter-spacing: 0.04em;
}
.nav-link.active { color: #fff; }
.nav-search-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    color: rgba(255,255,255,0.45);
}

/* ── SEARCH INPUT ── */
.search-wrap { padding: 80px 48px 20px; }
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #fff !important;
    padding: 12px 18px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    transition: all 0.25s ease !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.3) !important; }
.stTextInput > div > div > input:focus {
    border-color: rgba(255,157,92,0.5) !important;
    background: rgba(255,255,255,0.08) !important;
    box-shadow: 0 0 0 3px rgba(255,157,92,0.06) !important;
}
[data-testid="stTextInputRootElement"] label { display:none !important; }

/* ── HERO ── */
.hero-wrap {
    position: relative;
    width: 100%;
    height: 500px;
    overflow: hidden;
    margin-top: 64px;
}
.hero-backdrop {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center 20%;
    filter: brightness(0.42);
}
.hero-gradient {
    position: absolute;
    inset: 0;
    background:
        linear-gradient(to right, rgba(15,15,15,0.97) 0%, rgba(15,15,15,0.65) 38%, rgba(15,15,15,0.05) 70%, transparent 100%),
        linear-gradient(to top, rgba(15,15,15,1) 0%, transparent 45%);
}
.hero-content {
    position: absolute;
    bottom: 55px;
    left: 48px;
    max-width: 500px;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,157,92,0.12);
    border: 1px solid rgba(255,157,92,0.28);
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #ff9d5c;
    margin-bottom: 12px;
}
.hero-title {
    font-size: 2.7rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.1;
    margin-bottom: 10px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.4);
}
.hero-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.hero-rating { color: #f5c518; font-size: 13px; font-weight: 600; }
.hero-dot { color: rgba(255,255,255,0.2); }
.hero-year { font-size: 12px; color: rgba(255,255,255,0.5); }
.hero-overview {
    font-size: 13px;
    line-height: 1.7;
    color: rgba(255,255,255,0.6);
    margin-bottom: 20px;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* ── CONTENT SECTION ── */
.content-section { padding: 28px 48px 6px; }
.section-header { display:flex; align-items:center; margin-bottom:16px; }
.section-label {
    font-size: 15px;
    font-weight: 600;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-emoji { font-size: 14px; }

/* ── POSTER CARD ── */
.poster-card {
    position: relative;
    border-radius: 6px;
    overflow: hidden;
    background: #1c1c1c;
    cursor: pointer;
    transition: transform 0.3s cubic-bezier(0.25,0.46,0.45,0.94), box-shadow 0.3s;
    aspect-ratio: 2/3;
    width: 100%;
}
.poster-card:hover {
    transform: scale(1.05) translateY(-5px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.75), 0 0 0 1px rgba(255,255,255,0.07);
}
.poster-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.card-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 40%, transparent 70%);
    opacity: 0;
    transition: opacity 0.28s ease;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 10px;
}
.poster-card:hover .card-overlay { opacity: 1; }
.card-play {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%,-50%) scale(0.75);
    width: 42px; height: 42px;
    border-radius: 50%;
    background: rgba(255,255,255,0.93);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; color: #000;
    opacity: 0;
    transition: opacity 0.25s, transform 0.25s;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}
.poster-card:hover .card-play {
    opacity: 1;
    transform: translate(-50%,-50%) scale(1);
}
.card-title-text { font-size: 11px; font-weight: 600; color: #fff; margin-bottom: 3px; line-height:1.3; }
.card-meta-row { display:flex; gap:6px; align-items:center; }
.card-star { font-size: 10px; color: #f5c518; font-weight: 600; }
.card-yr { font-size: 10px; color: rgba(255,255,255,0.45); }
.no-poster {
    aspect-ratio: 2/3; width: 100%;
    background: linear-gradient(135deg, #1e1e1e, #272727);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    text-align: center; padding: 10px;
    border: 1px solid rgba(255,255,255,0.05);
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
}
.no-poster:hover { transform: scale(1.04) translateY(-4px); box-shadow: 0 16px 40px rgba(0,0,0,0.7); }
.no-poster-t { font-size: 11px; color: rgba(255,255,255,0.5); }

/* ── INVISIBLE BTN OVERLAY ── */
.poster-click-wrap { position: relative; cursor: pointer; }
.poster-click-wrap [data-testid="stButton"] {
    position: absolute !important;
    inset: 0 !important;
    z-index: 10 !important;
    height: 100% !important;
    overflow: hidden !important;
}
.poster-click-wrap [data-testid="stButton"] > button {
    position: absolute !important;
    inset: 0 !important;
    width: 100% !important; height: 100% !important;
    border: none !important;
    background: transparent !important;
    cursor: pointer !important;
    padding: 0 !important;
    border-radius: 6px !important;
    opacity: 0 !important;
    min-height: unset !important;
    font-size: 0 !important;
    line-height: 0 !important;
}
/* Kill the empty space/gap left by the button container */
.poster-click-wrap > div:last-child {
    position: absolute !important;
    inset: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    height: 100% !important;
}
/* Remove bottom margin/padding from stButton inside card wraps */
.poster-click-wrap [data-testid="stButton"] { margin: 0 !important; padding: 0 !important; }

/* CRITICAL: collapse the gap Streamlit adds after the invisible button */
.poster-click-wrap {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}
.poster-click-wrap > div {
    margin-bottom: 0 !important;
}
/* The stColumn that contains poster-click-wrap should not grow */
[data-testid="stColumn"]:has(.poster-click-wrap) {
    overflow: hidden !important;
}

/* ── NAV CLICK ROW (invisible Streamlit buttons over visual nav) ── */
.nav-click-row {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 64px !important;
    z-index: 10000 !important;
    display: flex !important;
    align-items: center !important;
    pointer-events: none !important;
    background: transparent !important;
}
/* Target the horizontal block containing nav buttons */
div:has(> .nav-click-row) { position: static !important; }

/* Make nav row buttons transparent and properly positioned */
.nav-click-row [data-testid="stHorizontalBlock"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 64px !important;
    z-index: 10000 !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 48px !important;
    background: transparent !important;
    gap: 0 !important;
    pointer-events: all !important;
}
.nav-click-row [data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    font-size: 0 !important;
    padding: 0 !important;
    min-height: 64px !important;
    width: 100% !important;
    cursor: pointer !important;
    opacity: 0 !important;
}
.nav-click-row [data-testid="stColumn"] {
    padding: 0 !important;
    flex: unset !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.nav-btn-wrap {
    display: flex;
    gap: 32px;
    align-items: center;
}
.nav-btn-wrap [data-testid="stButton"] > button {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: rgba(255,255,255,0.65) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 4px 0 !important;
    width: auto !important;
    min-height: unset !important;
    cursor: pointer !important;
    transition: color 0.2s !important;
}
.nav-btn-wrap [data-testid="stButton"] > button:hover {
    color: #fff !important;
    background: transparent !important;
    border: none !important;
}
.nav-btn-wrap .nav-active [data-testid="stButton"] > button {
    color: #fff !important;
    border-bottom: 2px solid #ff9d5c !important;
    padding-bottom: 2px !important;
}

/* ── SEARCH NAV BTN ── */
.nav-search-btn-wrap [data-testid="stButton"] > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 20px !important;
    color: rgba(255,255,255,0.45) !important;
    font-size: 12px !important;
    padding: 6px 14px !important;
    width: auto !important;
    min-height: unset !important;
}
.nav-search-btn-wrap [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
}
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 6px !important;
    color: rgba(255,255,255,0.75) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.03em !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: rgba(255,157,92,0.1) !important;
    border-color: rgba(255,157,92,0.35) !important;
    color: #fff !important;
}

/* ── PAGE COUNTER ── */
.page-counter {
    text-align: center; font-size: 11px;
    color: rgba(255,255,255,0.25);
    letter-spacing: 0.1em; text-transform: uppercase;
    margin: 18px 0 8px;
}
.active-page-num {
    text-align: center; padding: 6px 0;
    font-size: 13px; font-weight: 700;
    color: #ff9d5c;
    border-bottom: 2px solid #ff9d5c;
}

/* ── BACK BTN ── */
.back-nav-wrap {
    position: fixed;
    top: 14px; left: 48px;
    z-index: 99999;
}
.back-nav-wrap [data-testid="stButton"] > button {
    background: rgba(8,8,8,0.88) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 6px !important;
    color: rgba(255,255,255,0.75) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 8px 18px !important;
    backdrop-filter: blur(16px) !important;
    width: auto !important;
}
.back-nav-wrap [data-testid="stButton"] > button:hover {
    border-color: rgba(255,157,92,0.45) !important;
    color: #ff9d5c !important;
}

/* ── DETAIL HERO ── */
.detail-hero {
    position: relative;
    width: 100%;
    min-height: 480px;
    overflow: hidden;
    margin-top: 64px;
}
.detail-backdrop {
    position: absolute;
    inset: 0;
    background-size: cover;
    background-position: center 15%;
    filter: brightness(0.32);
}
.detail-gradient {
    position: absolute; inset: 0;
    background:
        linear-gradient(to right, rgba(15,15,15,0.97) 0%, rgba(15,15,15,0.68) 44%, rgba(15,15,15,0.06) 100%),
        linear-gradient(to top, rgba(15,15,15,1) 0%, transparent 55%);
}
.detail-content {
    position: relative;
    display: flex;
    gap: 40px;
    padding: 55px 48px 48px;
    min-height: 480px;
    align-items: flex-end;
}
.detail-poster {
    flex-shrink: 0;
    width: 185px;
    border-radius: 10px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.7);
    overflow: hidden;
    align-self: flex-end;
}
.detail-poster img { width: 100%; display: block; }
.detail-info { flex: 1; }
.detail-tagline {
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: #ff9d5c; margin-bottom: 10px;
    font-style: italic;
}
.detail-title {
    font-size: 2.9rem; font-weight: 700;
    color: #fff; line-height: 1.1;
    margin-bottom: 12px;
    text-shadow: 0 2px 30px rgba(0,0,0,0.5);
}
.detail-meta-row {
    display: flex; align-items: center;
    gap: 10px; margin-bottom: 10px; flex-wrap: wrap;
}
.d-rating { color: #f5c518; font-size: 14px; font-weight: 700; }
.d-votes { color: rgba(255,255,255,0.35); font-size: 11px; }
.d-sep { color: rgba(255,255,255,0.18); }
.d-year, .d-runtime { color: rgba(255,255,255,0.55); font-size: 13px; }
.genre-tag {
    display: inline-block;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 11px;
    color: rgba(255,255,255,0.65);
    margin: 2px 4px 2px 0;
}
.detail-overview {
    font-size: 13.5px; line-height: 1.75;
    color: rgba(255,255,255,0.65);
    margin: 12px 0 20px;
    max-width: 580px;
}

/* ── STAT CARDS ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    padding: 24px 48px;
}
.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 18px 22px;
    transition: border-color 0.25s, transform 0.25s;
}
.stat-card:hover { border-color: rgba(255,157,92,0.2); transform: translateY(-2px); }
.stat-label { font-size: 10px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: rgba(255,255,255,0.35); margin-bottom: 8px; }
.stat-value { font-family: 'Cinzel', serif; font-size: 1.45rem; font-weight: 700; color: #e8c97e; }

/* ── SECTION HEADER WITH BAR ── */
.dsh {
    display: flex; align-items: center; gap: 10px;
    padding: 24px 48px 16px;
}
.dsh-bar { flex: none; width: 3px; height: 18px; background: linear-gradient(to bottom,#ff9d5c,#e8c97e); border-radius: 2px; }
.dsh-txt { font-size: 15px; font-weight: 700; color: #fff; letter-spacing: 0.03em; }

/* ── CAST ── */
.cast-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    padding: 0 48px 28px;
}
.cast-card { text-align: center; }
.cast-img {
    width: 100%; aspect-ratio: 1;
    border-radius: 50%; object-fit: cover;
    border: 2px solid rgba(255,255,255,0.07);
    margin-bottom: 8px;
    transition: border-color 0.2s, transform 0.2s;
}
.cast-img:hover { border-color: rgba(255,157,92,0.45); transform: scale(1.05); }
.cast-no-img {
    width: 100%; aspect-ratio: 1; border-radius: 50%;
    background: rgba(255,255,255,0.05);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; margin-bottom: 8px;
    border: 2px solid rgba(255,255,255,0.05);
}
.cast-name { font-size: 11px; font-weight: 600; color: rgba(255,255,255,0.85); margin-bottom: 2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cast-role { font-size: 10px; color: rgba(255,255,255,0.3); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* ── SCENE GRID ── */
.scene-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    padding: 0 48px 28px;
}
.scene-img {
    width: 100%; aspect-ratio: 16/9;
    object-fit: cover; border-radius: 8px;
    transition: transform 0.3s, filter 0.3s;
    filter: brightness(0.88);
}
.scene-img:hover { transform: scale(1.02); filter: brightness(1); }

/* ── VIDEO ── */
.stVideo, [data-testid="stVideo"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6) !important;
}
.video-wrap { padding: 0 48px 28px; }

/* ── WL BADGE ── */
.wl-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,157,92,0.1);
    border: 1px solid rgba(255,157,92,0.28);
    border-radius: 6px; padding: 9px 18px;
    font-size: 12px; font-weight: 600; color: #ff9d5c;
    letter-spacing: 0.04em;
}

/* ── HERO ACTION BTNS AREA ── */
.hero-btn-area { padding: 0 48px 16px; display:flex; gap:12px; flex-wrap:wrap; }

/* ── FIX MISC ── */
.stApp p { font-family:'Inter',sans-serif!important; color:rgba(255,255,255,0.65)!important; font-size:13px!important; line-height:1.6!important; margin:0!important; text-align:left!important; }
.stApp h1 { font-family:'Inter',sans-serif!important; color:#fff!important; }
hr { display:none!important; }
[data-testid="stMetric"] { background:transparent!important; border:none!important; padding:0!important; }
.stSpinner > div { border-color: #ff9d5c transparent transparent transparent !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,157,92,0.35); }

/* ── FILTER TABS ── */
.filter-tab-row { padding: 80px 48px 20px; display: flex; gap: 10px; flex-wrap: wrap; }
.stButton.filter-tab > button, .stButton.filter-tab-active > button {
    border-radius: 20px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 6px 18px !important;
    min-height: unset !important;
    width: auto !important;
    letter-spacing: 0.04em !important;
}
/* Page title style */
.page-title {
    font-size: 1.8rem; font-weight: 700; color: #fff;
    padding: 80px 48px 8px;
    font-family: 'Inter', sans-serif;
}
.page-subtitle {
    font-size: 13px; color: rgba(255,255,255,0.4);
    padding: 0 48px 24px;
}
.rec-grid-wrap { padding: 0 48px 32px; }

/* ── FOOTER ── */
.lumora-footer {
    text-align:center; padding:48px 0 32px;
    color:rgba(255,255,255,0.15);
    font-size:11px; letter-spacing:0.1em;
}
</style>
""", unsafe_allow_html=True)


# ================= API =================
def fetch(url):
    try:
        return requests.get(url, timeout=10).json()
    except:
        return {}

def search_movie(query, page=1):
    return fetch(f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}&page={page}")

def get_trending(page=1):
    return fetch(f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}&page={page}")

def get_top_rated():
    return fetch(f"{BASE_URL}/movie/top_rated?api_key={TMDB_API_KEY}")

def get_now_playing():
    return fetch(f"{BASE_URL}/movie/now_playing?api_key={TMDB_API_KEY}")

def get_popular():
    return fetch(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}")

def get_details(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}")

def get_credits(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}")

def get_trailer(movie_id):
    data = fetch(f"{BASE_URL}/movie/{movie_id}/videos?api_key={TMDB_API_KEY}")
    for v in data.get("results", []):
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def get_recommendations(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}")

def get_images(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/images?api_key={TMDB_API_KEY}")

def get_upcoming(page=1):
    return fetch(f"{BASE_URL}/movie/upcoming?api_key={TMDB_API_KEY}&page={page}")

def get_top_rated_paged(page=1):
    return fetch(f"{BASE_URL}/movie/top_rated?api_key={TMDB_API_KEY}&page={page}")

def get_now_playing_paged(page=1):
    return fetch(f"{BASE_URL}/movie/now_playing?api_key={TMDB_API_KEY}&page={page}")

def get_popular_paged(page=1):
    return fetch(f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&page={page}")

# Series (TV) helpers
def get_tv_popular(page=1):
    return fetch(f"{BASE_URL}/tv/popular?api_key={TMDB_API_KEY}&page={page}")

def get_tv_top_rated(page=1):
    return fetch(f"{BASE_URL}/tv/top_rated?api_key={TMDB_API_KEY}&page={page}")

def get_tv_on_the_air(page=1):
    return fetch(f"{BASE_URL}/tv/on_the_air?api_key={TMDB_API_KEY}&page={page}")

def get_tv_trending(page=1):
    return fetch(f"{BASE_URL}/trending/tv/week?api_key={TMDB_API_KEY}&page={page}")

def get_tv_details(tv_id):
    return fetch(f"{BASE_URL}/tv/{tv_id}?api_key={TMDB_API_KEY}")

def get_tv_credits(tv_id):
    return fetch(f"{BASE_URL}/tv/{tv_id}/credits?api_key={TMDB_API_KEY}")

def get_tv_trailer(tv_id):
    data = fetch(f"{BASE_URL}/tv/{tv_id}/videos?api_key={TMDB_API_KEY}")
    for v in data.get("results", []):
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None
    if x >= 1_000_000_000: return f"${x/1e9:.2f}B"
    elif x >= 1_000_000:   return f"${x/1e6:.1f}M"
    elif x > 0:            return f"${x:,}"
    return "N/A"


# ================= SESSION STATE =================
_defaults = {
    "page": "home", "movie_id": None, "watchlist": [],
    "trend_page": 1, "search_page": 1, "rec_page": 1,
    "last_query": "", "last_movie": None,
    "active_nav": "Browse",
    "movies_page": 1, "series_page": 1,
    "movies_filter": "popular",  # popular | top_rated | now_playing | upcoming
    "series_filter": "popular",  # popular | top_rated | on_the_air
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ================= HELPERS =================
def go_home():
    st.session_state.page = "home"
    st.session_state.active_nav = "Browse"
    st.session_state.rec_page = 1
    st.session_state.last_movie = None
    st.rerun()

def go_movies():
    st.session_state.page = "movies"
    st.session_state.active_nav = "Movies"
    st.session_state.movies_page = 1
    st.rerun()

def go_series():
    st.session_state.page = "series"
    st.session_state.active_nav = "Series"
    st.session_state.series_page = 1
    st.rerun()

def go_mylist():
    st.session_state.page = "mylist"
    st.session_state.active_nav = "My List"
    st.rerun()

def go_detail(mid):
    st.session_state.movie_id = mid
    st.session_state.page = "details"
    st.session_state.rec_page = 1
    st.rerun()

def movie_card(m, btn_key):
    poster_url = IMG + m["poster_path"] if m.get("poster_path") else None
    rating = m.get("vote_average", 0)
    year = m.get("release_date", "")[:4]
    title = m.get("title", "Untitled")

    if poster_url:
        card_html = f"""<div class="poster-card">
  <img src="{poster_url}" alt="{title}" loading="lazy"/>
  <div class="card-play">&#9654;</div>
  <div class="card-overlay">
    <div class="card-title-text">{title}</div>
    <div class="card-meta-row">
      <span class="card-star">&#9733; {rating:.1f}</span>
      <span class="card-yr">{year}</span>
    </div>
  </div>
</div>"""
    else:
        card_html = f"""<div class="no-poster">
  <span class="no-poster-t">{title}</span>
</div>"""

    st.markdown('<div class="poster-click-wrap">', unsafe_allow_html=True)
    st.markdown(card_html, unsafe_allow_html=True)
    clicked = st.button("", key=btn_key, help=title)
    st.markdown('</div>', unsafe_allow_html=True)
    return clicked

def tv_card(m, btn_key):
    """Like movie_card but for TV shows (uses 'name' instead of 'title')"""
    poster_url = IMG + m["poster_path"] if m.get("poster_path") else None
    rating = m.get("vote_average", 0)
    year = (m.get("first_air_date") or "")[:4]
    title = m.get("name") or m.get("title", "Untitled")

    if poster_url:
        card_html = f"""<div class="poster-card">
  <img src="{poster_url}" alt="{title}" loading="lazy"/>
  <div class="card-play">&#9654;</div>
  <div class="card-overlay">
    <div class="card-title-text">{title}</div>
    <div class="card-meta-row">
      <span class="card-star">&#9733; {rating:.1f}</span>
      <span class="card-yr">{year}</span>
    </div>
  </div>
</div>"""
    else:
        card_html = f"""<div class="no-poster">
  <span class="no-poster-t">{title}</span>
</div>"""

    st.markdown('<div class="poster-click-wrap">', unsafe_allow_html=True)
    st.markdown(card_html, unsafe_allow_html=True)
    clicked = st.button("", key=btn_key, help=title)
    st.markdown('</div>', unsafe_allow_html=True)
    return clicked


def render_tv_row(shows, key_prefix, max_count=12, ncols=6):
    cols = st.columns(ncols)
    for i, m in enumerate(shows[:max_count]):
        with cols[i % ncols]:
            if tv_card(m, f"{key_prefix}_{m['id']}"):
                go_detail(m["id"])  # reuse detail page for TV too


def render_filter_tabs(options, current, key_prefix):
    """Render filter tab buttons, return selected value or None"""
    cols = st.columns(len(options))
    selected = None
    for i, (label, val) in enumerate(options):
        with cols[i]:
            is_active = (current == val)
            btn_style = "filter-tab-active" if is_active else "filter-tab"
            if st.button(label, key=f"{key_prefix}_filter_{val}"):
                selected = val
    return selected
    cols = st.columns(ncols)
    for i, m in enumerate(movies[:max_count]):
        with cols[i % ncols]:
            if movie_card(m, f"{key_prefix}_{m['id']}"):
                go_detail(m["id"])

def section_header(emoji, label):
    st.markdown(f"""<div class="section-header">
  <span class="section-label"><span class="section-emoji">{emoji}</span> {label}</span>
</div>""", unsafe_allow_html=True)

def dsh(label):
    st.markdown(f"""<div class="dsh">
  <div class="dsh-bar"></div>
  <div class="dsh-txt">{label}</div>
</div>""", unsafe_allow_html=True)

def render_pagination(current_page, total_pages, key_prefix):
    total_pages = min(int(total_pages), 20)
    if total_pages <= 1:
        return None
    st.markdown(f'<div class="page-counter">Page {current_page} of {total_pages}</div>', unsafe_allow_html=True)
    pages = sorted(set([1, total_pages] + list(range(max(1, current_page-2), min(total_pages+1, current_page+3)))))
    nav = ["◀"] + pages + ["▶"]
    cols = st.columns(len(nav))
    new_page = None
    for idx, item in enumerate(nav):
        with cols[idx]:
            if item == "◀":
                if st.button("◀", key=f"pg_{key_prefix}_p", disabled=(current_page==1)):
                    new_page = current_page - 1
            elif item == "▶":
                if st.button("▶", key=f"pg_{key_prefix}_n", disabled=(current_page==total_pages)):
                    new_page = current_page + 1
            else:
                if item == current_page:
                    st.markdown(f'<div class="active-page-num">{item}</div>', unsafe_allow_html=True)
                else:
                    if st.button(str(item), key=f"pg_{key_prefix}_{item}"):
                        new_page = item
    return new_page

def render_navbar(show_back=False):
    active = st.session_state.active_nav

    if show_back:
        st.markdown('<div class="back-nav-wrap">', unsafe_allow_html=True)
        if st.button("← Home", key="nav_back_home"):
            go_home()
        st.markdown('</div>', unsafe_allow_html=True)

    # Visual navbar
    active_browse = "active" if active == "Browse" else ""
    active_movies = "active" if active == "Movies" else ""
    active_series = "active" if active == "Series" else ""
    active_mylist = "active" if active == "My List" else ""
    wl_count = f" ({len(st.session_state.watchlist)})" if st.session_state.watchlist else ""

    st.markdown(f"""
<div class="lumora-nav">
  <div class="lumora-logo">LUMORA</div>
  <div class="nav-links">
    <span class="nav-link {active_browse}">Browse</span>
    <span class="nav-link {active_movies}">Movies</span>
    <span class="nav-link {active_series}">Series</span>
    <span class="nav-link {active_mylist}">My List{wl_count}</span>
  </div>
  <div class="nav-search-pill">🔍 &nbsp;Search</div>
</div>
<div class="nav-real-btns">
  <!-- Invisible real buttons rendered below via Streamlit columns -->
</div>
""", unsafe_allow_html=True)

    # Invisible real buttons that sit on top of nav visually
    st.markdown('<div class="nav-click-row">', unsafe_allow_html=True)
    nc0, nc1, nc2, nc3, nc4, nc_sp, nc5 = st.columns([2.2, 0.55, 0.55, 0.55, 0.7, 2.8, 1.0])
    with nc1:
        if st.button("Browse", key="nav_browse"):
            st.session_state.page = "home"; st.session_state.active_nav = "Browse"; st.rerun()
    with nc2:
        if st.button("Movies", key="nav_movies"):
            go_movies()
    with nc3:
        if st.button("Series", key="nav_series"):
            go_series()
    with nc4:
        if st.button("My List", key="nav_mylist"):
            go_mylist()
    with nc5:
        if st.button("🔍 Search", key="nav_search_btn"):
            st.session_state.page = "home"; st.session_state.active_nav = "Browse"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
#  HOME PAGE
# ═══════════════════════════════════════
if st.session_state.page == "home":

    render_navbar()

    # ── FETCH ──
    with st.spinner(""):
        trending_data   = get_trending(page=st.session_state.trend_page)
        nowplay_data    = get_now_playing()
        toprated_data   = get_top_rated()
        popular_data    = get_popular()

    trending_movies = trending_data.get("results", [])
    nowplay_movies  = nowplay_data.get("results", [])
    toprated_movies = toprated_data.get("results", [])
    popular_movies  = popular_data.get("results", [])

    # ── SEARCH ──
    st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
    query = st.text_input("search", placeholder="🔍  Search movies, series, actors…",
                          key="search_input", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if query != st.session_state.last_query:
        st.session_state.search_page = 1
        st.session_state.last_query  = query

    # ── SEARCH RESULTS ──
    if query:
        with st.spinner("Searching…"):
            results = search_movie(query, page=st.session_state.search_page)
        total_search  = min(results.get("total_pages", 1), 20)
        total_results = results.get("total_results", 0)
        movies = results.get("results", [])

        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        section_header("🔎", f'Results for "{query}" &nbsp;<span style="font-size:11px;color:rgba(255,255,255,0.3);font-weight:400;">{total_results:,} found</span>')
        render_movie_row(movies, f"search_{st.session_state.search_page}", max_count=12)
        st.markdown('</div>', unsafe_allow_html=True)

        new_sp = render_pagination(st.session_state.search_page, total_search, "search")
        if new_sp:
            st.session_state.search_page = new_sp
            st.rerun()

    else:
        # ── HERO ──
        hero = trending_movies[0] if trending_movies else None
        if hero:
            bd  = BACKDROP_SM + hero["backdrop_path"] if hero.get("backdrop_path") else ""
            ht  = hero.get("title", "")
            hr  = hero.get("vote_average", 0)
            hy  = hero.get("release_date", "")[:4]
            hov = (hero.get("overview", "") or "")[:210]
            hid = hero["id"]

            st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-backdrop" style="background-image:url('{bd}');"></div>
  <div class="hero-gradient"></div>
  <div class="hero-content">
    <div class="hero-badge">&#128293; Trending #1 This Week</div>
    <div class="hero-title">{ht}</div>
    <div class="hero-meta">
      <span class="hero-rating">&#9733; {hr:.1f}</span>
      <span class="hero-dot">&#8226;</span>
      <span class="hero-year">{hy}</span>
    </div>
    <div class="hero-overview">{hov}…</div>
  </div>
</div>""", unsafe_allow_html=True)

            hc1, hc2, _ = st.columns([1, 1.2, 7])
            with hc1:
                if st.button("▶  View Details", key="hero_view"):
                    go_detail(hid)
            with hc2:
                already_wl = any(w["id"] == hid for w in st.session_state.watchlist)
                lbl = "✓  In My List" if already_wl else "＋  My List"
                if st.button(lbl, key="hero_wl"):
                    if not already_wl:
                        st.session_state.watchlist.append({"id": hid, "title": ht, "poster": hero.get("poster_path")})
                        st.rerun()

        # ── TRENDING ──
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        section_header("🔥", "Trending This Week")
        render_movie_row(trending_movies, f"trend_{st.session_state.trend_page}")
        st.markdown('</div>', unsafe_allow_html=True)
        total_trend = min(trending_data.get("total_pages", 1), 20)
        new_tp = render_pagination(st.session_state.trend_page, total_trend, "trend")
        if new_tp:
            st.session_state.trend_page = new_tp
            st.rerun()

        # ── NOW IN CINEMAS ──
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        section_header("🎬", "Now In Cinemas")
        render_movie_row(nowplay_movies, "nowplay")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── TOP RATED ──
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        section_header("⭐", "Top Rated All Time")
        render_movie_row(toprated_movies, "toprated")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── POPULAR ──
        st.markdown('<div class="content-section">', unsafe_allow_html=True)
        section_header("🌟", "Popular Right Now")
        render_movie_row(popular_movies, "popular")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── MY LIST ──
        if st.session_state.watchlist:
            st.markdown('<div class="content-section">', unsafe_allow_html=True)
            section_header("❤️", f"My List &nbsp;<span style='font-size:11px;color:rgba(255,255,255,0.3);font-weight:400;'>{len(st.session_state.watchlist)} saved</span>")
            wl_cols = st.columns(6)
            for i, m in enumerate(st.session_state.watchlist):
                with wl_cols[i % 6]:
                    pu = IMG + m["poster"] if m.get("poster") else None
                    if pu:
                        ch = f"""<div class="poster-card">
  <img src="{pu}" alt="{m['title']}" loading="lazy"/>
  <div class="card-play">&#9654;</div>
  <div class="card-overlay"><div class="card-title-text">{m['title']}</div></div>
</div>"""
                        st.markdown('<div class="poster-click-wrap">', unsafe_allow_html=True)
                        st.markdown(ch, unsafe_allow_html=True)
                        if st.button("", key=f"wl_click_{m['id']}", help=m["title"]):
                            go_detail(m["id"])
                        st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="lumora-footer">LUMORA &nbsp;·&nbsp; Cinema Rediscovered &nbsp;·&nbsp; Powered by TMDB</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
#  DETAILS PAGE
# ═══════════════════════════════════════
elif st.session_state.page == "details":

    movie_id = st.session_state.movie_id
    render_navbar(show_back=True)

    if st.session_state.last_movie != movie_id:
        st.session_state.rec_page  = 1
        st.session_state.last_movie = movie_id

    with st.spinner("Loading…"):
        data    = get_details(movie_id)
        credits = get_credits(movie_id)
        trailer = get_trailer(movie_id)
        images  = get_images(movie_id)

    bd       = BACKDROP_SM + data["backdrop_path"] if data.get("backdrop_path") else ""
    pu       = IMG_LG + data["poster_path"] if data.get("poster_path") else None
    title    = data.get("title", "Untitled")
    tagline  = data.get("tagline", "")
    rating   = data.get("vote_average", 0)
    votes    = data.get("vote_count", 0)
    release  = data.get("release_date", "")
    runtime  = data.get("runtime", 0)
    genres   = data.get("genres", [])
    overview = data.get("overview", "No overview available.")
    revenue  = data.get("revenue", 0)
    budget   = data.get("budget", 0)

    genre_tags   = "".join([f'<span class="genre-tag">{g["name"]}</span>' for g in genres])
    runtime_str  = f"{runtime//60}h {runtime%60}m" if runtime else ""
    year         = release[:4] if release else ""
    poster_html  = f'<img src="{pu}" alt="{title}"/>' if pu else '<div style="height:280px;background:#1c1c1c;border-radius:10px;"></div>'

    rt_part = f'<span class="d-sep">·</span><span class="d-runtime">{runtime_str}</span>' if runtime_str else ""

    st.markdown(f"""
<div class="detail-hero">
  <div class="detail-backdrop" style="background-image:url('{bd}');"></div>
  <div class="detail-gradient"></div>
  <div class="detail-content">
    <div class="detail-poster">{poster_html}</div>
    <div class="detail-info">
      {"<div class='detail-tagline'>" + tagline + "</div>" if tagline else ""}
      <div class="detail-title">{title}</div>
      <div class="detail-meta-row">
        <span class="d-rating">&#9733; {rating:.1f}</span>
        <span class="d-votes">({votes:,} votes)</span>
        <span class="d-sep">·</span>
        <span class="d-year">{year}</span>
        {rt_part}
      </div>
      <div style="margin-bottom:10px;">{genre_tags}</div>
      <div class="detail-overview">{overview}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # Action buttons
    da1, da2, _ = st.columns([1.3, 1.5, 6])
    with da1:
        if trailer:
            st.markdown(f'<a href="{trailer}" target="_blank" style="text-decoration:none;"><div style="display:inline-flex;align-items:center;gap:8px;background:#fff;color:#000;border-radius:6px;padding:10px 22px;font-size:13px;font-weight:700;cursor:pointer;transition:background 0.2s;white-space:nowrap;">&#9654; &nbsp;Watch Trailer</div></a>', unsafe_allow_html=True)
    with da2:
        already = any(w["id"] == movie_id for w in st.session_state.watchlist)
        if already:
            st.markdown('<div class="wl-badge">&#10003; &nbsp;In My List</div>', unsafe_allow_html=True)
        else:
            if st.button("＋  Add to My List", key="detail_wl_btn"):
                st.session_state.watchlist.append({"id": movie_id, "title": title, "poster": data.get("poster_path")})
                st.rerun()

    # ── BOX OFFICE ──
    profit_val = fmt_money(revenue - budget) if revenue and budget else "N/A"
    st.markdown(f"""
<div class="stat-row">
  <div class="stat-card">
    <div class="stat-label">&#127757; Worldwide Revenue</div>
    <div class="stat-value">{fmt_money(revenue)}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">&#127916; Production Budget</div>
    <div class="stat-value">{fmt_money(budget)}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">&#128200; Box Office Profit</div>
    <div class="stat-value">{profit_val}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── CAST ──
    cast_list = credits.get("cast", [])[:12]
    if cast_list:
        dsh("🎭 Cast")
        cast_items = []
        for c in cast_list:
            if c.get("profile_path"):
                ph = f'<img class="cast-img" src="https://image.tmdb.org/t/p/w185{c["profile_path"]}" alt="{c.get("name","")}" loading="lazy"/>'
            else:
                ph = '<div class="cast-no-img">&#128100;</div>'
            cast_items.append(f'<div class="cast-card">{ph}<div class="cast-name">{c.get("name","")}</div><div class="cast-role">{c.get("character","")}</div></div>')
        st.markdown(f'<div class="cast-grid">{"".join(cast_items)}</div>', unsafe_allow_html=True)

    # ── DIRECTOR ──
    director = next((cr for cr in credits.get("crew", []) if cr.get("job") == "Director"), None)
    if director:
        dir_img = ""
        if director.get("profile_path"):
            dir_img = f'<img src="https://image.tmdb.org/t/p/w185{director["profile_path"]}" style="width:58px;height:58px;border-radius:50%;object-fit:cover;border:2px solid rgba(255,157,92,0.35);" loading="lazy"/>'
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:14px;padding:4px 48px 24px;">
  {dir_img}
  <div>
    <div style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase;color:rgba(255,255,255,0.3);margin-bottom:4px;">Director</div>
    <div style="font-size:16px;font-weight:700;color:#fff;">{director.get("name","")}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── TRAILER ──
    if trailer:
        dsh("▶ Official Trailer")
        st.markdown('<div class="video-wrap">', unsafe_allow_html=True)
        st.video(trailer)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── SCENES ──
    backdrops = images.get("backdrops", [])[:6]
    if backdrops:
        dsh("🖼 Scenes from the Film")
        scene_imgs = "".join([
            f'<img class="scene-img" src="{BACKDROP_SM}{img["file_path"]}" loading="lazy" alt="Scene"/>'
            for img in backdrops
        ])
        st.markdown(f'<div class="scene-grid">{scene_imgs}</div>', unsafe_allow_html=True)

    # ── RECOMMENDATIONS ──
    rec_data   = get_recommendations(movie_id)
    rec_movies = rec_data.get("results", [])

    if rec_movies:
        dsh("🎯 You Might Also Like")
        REC_PER = 6
        rec_tp  = max(1, (len(rec_movies) + REC_PER - 1) // REC_PER)
        rstart  = (st.session_state.rec_page - 1) * REC_PER
        rslice  = rec_movies[rstart:rstart + REC_PER]

        st.markdown('<div class="rec-grid-wrap">', unsafe_allow_html=True)
        rcols = st.columns(6)
        for i, m in enumerate(rslice):
            with rcols[i % 6]:
                key = f"rec_{movie_id}_{m['id']}_p{st.session_state.rec_page}"
                if movie_card(m, key):
                    st.session_state.movie_id  = m["id"]
                    st.session_state.last_movie = m["id"]
                    st.session_state.rec_page  = 1
                    st.session_state.page      = "details"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        new_rp = render_pagination(st.session_state.rec_page, rec_tp, f"rec_{movie_id}")
        if new_rp:
            st.session_state.rec_page = new_rp
            st.rerun()

    st.markdown('<div class="lumora-footer">LUMORA &nbsp;·&nbsp; Cinema Rediscovered &nbsp;·&nbsp; Powered by TMDB</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
#  MOVIES PAGE
# ═══════════════════════════════════════
elif st.session_state.page == "movies":

    render_navbar()

    st.markdown('<div class="page-title">Movies</div>', unsafe_allow_html=True)

    # Filter tabs
    st.markdown('<div class="filter-tab-row">', unsafe_allow_html=True)
    fcols = st.columns([1, 1, 1.1, 1, 5])
    mf_labels = ["🌟 Popular", "⭐ Top Rated", "🎬 Now Playing", "🗓 Upcoming"]
    mf_vals   = ["popular", "top_rated", "now_playing", "upcoming"]
    for i, (fl, fv) in enumerate(zip(mf_labels, mf_vals)):
        with fcols[i]:
            if st.button(fl, key=f"mf_{fv}"):
                st.session_state.movies_filter = fv
                st.session_state.movies_page = 1
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    p  = st.session_state.movies_page
    mf = st.session_state.movies_filter
    with st.spinner("Loading…"):
        if mf == "popular":
            mdata = get_popular_paged(p)
        elif mf == "top_rated":
            mdata = get_top_rated_paged(p)
        elif mf == "now_playing":
            mdata = get_now_playing_paged(p)
        else:
            mdata = get_upcoming(p)

    movies_page_list = mdata.get("results", [])
    mtotal = min(mdata.get("total_pages", 1), 20)

    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    mlabel_map = {
        "popular":     "🌟 Popular Movies",
        "top_rated":   "⭐ Top Rated Movies",
        "now_playing": "🎬 Now Playing",
        "upcoming":    "🗓 Upcoming Releases",
    }
    section_header("🎥", mlabel_map.get(mf, "Movies"))
    render_movie_row(movies_page_list, f"movies_{mf}_{p}", max_count=18, ncols=6)
    st.markdown('</div>', unsafe_allow_html=True)

    new_mp = render_pagination(p, mtotal, f"movies_{mf}")
    if new_mp:
        st.session_state.movies_page = new_mp
        st.rerun()

    st.markdown('<div class="lumora-footer">LUMORA &nbsp;·&nbsp; Cinema Rediscovered &nbsp;·&nbsp; Powered by TMDB</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
#  SERIES PAGE
# ═══════════════════════════════════════
elif st.session_state.page == "series":

    render_navbar()

    st.markdown('<div class="page-title">Series</div>', unsafe_allow_html=True)

    st.markdown('<div class="filter-tab-row">', unsafe_allow_html=True)
    sfcols = st.columns([1, 1, 1.1, 1, 5])
    sf_labels = ["🌟 Popular", "⭐ Top Rated", "📡 On The Air", "🔥 Trending"]
    sf_vals   = ["popular", "top_rated", "on_the_air", "trending"]
    for i, (sl, sv) in enumerate(zip(sf_labels, sf_vals)):
        with sfcols[i]:
            if st.button(sl, key=f"sf_{sv}"):
                st.session_state.series_filter = sv
                st.session_state.series_page = 1
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    sp2 = st.session_state.series_page
    sf  = st.session_state.series_filter
    with st.spinner("Loading…"):
        if sf == "popular":
            sdata = get_tv_popular(sp2)
        elif sf == "top_rated":
            sdata = get_tv_top_rated(sp2)
        elif sf == "on_the_air":
            sdata = get_tv_on_the_air(sp2)
        else:
            sdata = get_tv_trending(sp2)

    shows  = sdata.get("results", [])
    stotal = min(sdata.get("total_pages", 1), 20)

    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    slabel_map = {
        "popular":    "🌟 Popular Series",
        "top_rated":  "⭐ Top Rated Series",
        "on_the_air": "📡 Currently Airing",
        "trending":   "🔥 Trending Series",
    }
    section_header("📺", slabel_map.get(sf, "Series"))
    render_tv_row(shows, f"series_{sf}_{sp2}", max_count=18, ncols=6)
    st.markdown('</div>', unsafe_allow_html=True)

    new_sp3 = render_pagination(sp2, stotal, f"series_{sf}")
    if new_sp3:
        st.session_state.series_page = new_sp3
        st.rerun()

    st.markdown('<div class="lumora-footer">LUMORA &nbsp;·&nbsp; Cinema Rediscovered &nbsp;·&nbsp; Powered by TMDB</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════
#  MY LIST PAGE
# ═══════════════════════════════════════
elif st.session_state.page == "mylist":

    render_navbar()

    st.markdown('<div class="page-title">My List</div>', unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.markdown("""
<div style="text-align:center;padding:60px 48px 120px;">
  <div style="font-size:3rem;margin-bottom:16px;">🎬</div>
  <div style="font-size:18px;font-weight:600;color:#fff;margin-bottom:8px;">Your list is empty</div>
  <div style="font-size:13px;color:rgba(255,255,255,0.4);">Browse movies and series and add them to your list.</div>
</div>
""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 5])
        with c1:
            if st.button("Browse Movies", key="mylist_browse_movies"):
                go_movies()
        with c2:
            if st.button("Browse Series", key="mylist_browse_series"):
                go_series()
    else:
        st.markdown(f'<div class="page-subtitle">{len(st.session_state.watchlist)} title{"s" if len(st.session_state.watchlist)!=1 else ""} saved</div>', unsafe_allow_html=True)
        st.markdown('<div class="content-section">', unsafe_allow_html=True)

        wl_cols = st.columns(6)
        to_remove = None
        for i, m in enumerate(st.session_state.watchlist):
            with wl_cols[i % 6]:
                pu = IMG + m["poster"] if m.get("poster") else None
                if pu:
                    ch = f"""<div class="poster-card">
  <img src="{pu}" alt="{m['title']}" loading="lazy"/>
  <div class="card-play">&#9654;</div>
  <div class="card-overlay">
    <div class="card-title-text">{m['title']}</div>
  </div>
</div>"""
                    st.markdown('<div class="poster-click-wrap">', unsafe_allow_html=True)
                    st.markdown(ch, unsafe_allow_html=True)
                    if st.button("", key=f"wlp_click_{m['id']}_{i}", help=m["title"]):
                        go_detail(m["id"])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="no-poster"><span class="no-poster-t">{m["title"]}</span></div>', unsafe_allow_html=True)
                if st.button("✕ Remove", key=f"wl_remove_{m['id']}_{i}"):
                    to_remove = m["id"]

        st.markdown('</div>', unsafe_allow_html=True)

        if to_remove is not None:
            st.session_state.watchlist = [w for w in st.session_state.watchlist if w["id"] != to_remove]
            st.rerun()

        c1, _, _ = st.columns([1, 1, 5])
        with c1:
            if st.button("Continue Browsing", key="mylist_continue"):
                go_home()

    st.markdown('<div class="lumora-footer">LUMORA &nbsp;·&nbsp; Cinema Rediscovered &nbsp;·&nbsp; Powered by TMDB</div>', unsafe_allow_html=True)
