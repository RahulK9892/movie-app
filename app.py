import streamlit as st
import requests

# ================= CONFIG =================
st.set_page_config(page_title="LUMORA", layout="wide", page_icon="🎬")

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
BACKDROP = "https://image.tmdb.org/t/p/w780"

# ================= PREMIUM CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Raleway:wght@300;400;500;600&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: #05080f !important;
    color: #e8e0d5 !important;
    font-family: 'Raleway', sans-serif !important;
}

/* ── ANIMATED STARFIELD BG ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(120,60,200,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(200,80,50,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(30,15,60,0.8) 0%, transparent 80%);
    pointer-events: none;
    z-index: 0;
    animation: bgShift 18s ease-in-out infinite alternate;
}

@keyframes bgShift {
    0%   { opacity: 1; transform: scale(1); }
    100% { opacity: 0.8; transform: scale(1.05); }
}

/* Grain overlay */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 1;
    opacity: 0.5;
}

/* ── HEADER ── */
h1, h2, h3, .stMarkdown h2 {
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.12em;
}

/* Main title */
.stApp [data-testid="stMarkdownContainer"] h2:first-child {
    font-family: 'Cinzel', serif !important;
    font-size: 3rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #ff9d5c 0%, #e8c97e 40%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.25em;
    text-align: center;
    text-shadow: none;
    animation: logoGlow 3s ease-in-out infinite alternate;
    margin-bottom: 0.5rem !important;
}

@keyframes logoGlow {
    0%   { filter: drop-shadow(0 0 8px rgba(255,157,92,0.4)); }
    100% { filter: drop-shadow(0 0 20px rgba(167,139,250,0.6)); }
}

/* ── SEARCH BOX ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,157,92,0.25) !important;
    border-radius: 40px !important;
    color: #e8e0d5 !important;
    padding: 14px 24px !important;
    font-family: 'Raleway', sans-serif !important;
    font-size: 15px !important;
    letter-spacing: 0.05em;
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1) !important;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 0 0 rgba(255,157,92,0);
}

.stTextInput > div > div > input:focus {
    border-color: rgba(255,157,92,0.7) !important;
    box-shadow: 0 0 0 3px rgba(255,157,92,0.12), 0 0 30px rgba(255,157,92,0.08) !important;
    background: rgba(255,255,255,0.07) !important;
}

/* ── SECTION TITLES ── */
.section-title {
    font-family: 'Cinzel', serif;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #e8c97e;
    padding: 8px 0 16px;
    position: relative;
    display: inline-block;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 8px;
    left: 0;
    width: 40px;
    height: 2px;
    background: linear-gradient(90deg, #ff9d5c, transparent);
    border-radius: 2px;
}


/* ── COLUMNS ── */
[data-testid="column"] {
    transition: transform 0.3s ease;
    position: relative;
}

/* ── POSTER CLICK OVERLAY ── */
.poster-wrap {
    position: relative;
    display: block;
    border-radius: 10px;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    transition: all 0.45s cubic-bezier(0.23, 1, 0.32, 1);
}

.poster-wrap:hover {
    transform: translateY(-10px) scale(1.04);
    box-shadow: 0 20px 50px rgba(0,0,0,0.7), 0 0 25px rgba(255,157,92,0.15);
}

.poster-wrap img {
    width: 100%;
    display: block;
    border-radius: 10px;
    transition: filter 0.4s ease;
}

.poster-wrap:hover img {
    filter: brightness(1.08) saturate(1.1);
}

/* Overlay shimmer on hover */
.poster-wrap::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,157,92,0.08), rgba(167,139,250,0.08));
    opacity: 0;
    transition: opacity 0.4s ease;
    pointer-events: none;
    border-radius: 10px;
}

.poster-wrap:hover::after {
    opacity: 1;
}

/* Movie title below poster */
.poster-title {
    font-family: 'Raleway', sans-serif;
    font-size: 11px;
    color: rgba(232,224,213,0.7);
    text-align: center;
    margin-top: 7px;
    letter-spacing: 0.04em;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Hide the invisible overlay button visually */
.poster-btn-wrap {
    position: relative;
}

.poster-btn-wrap .stButton {
    position: absolute;
    top: 0; left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
}

.poster-btn-wrap .stButton > button {
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    opacity: 0 !important;
    border-radius: 10px !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    cursor: pointer !important;
    transform: none !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,157,92,0.3) !important;
    border-radius: 30px !important;
    color: #e8c97e !important;
    font-family: 'Raleway', sans-serif !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 6px 16px !important;
    transition: all 0.35s cubic-bezier(0.23, 1, 0.32, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    backdrop-filter: blur(8px);
    width: 100% !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,157,92,0.15), rgba(167,139,250,0.1));
    opacity: 0;
    transition: opacity 0.35s ease;
}

.stButton > button:hover {
    border-color: rgba(255,157,92,0.7) !important;
    color: #fff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255,157,92,0.2),
                0 0 0 1px rgba(255,157,92,0.1) !important;
    background: rgba(255,157,92,0.08) !important;
}

.stButton > button:hover::before {
    opacity: 1;
}

.stButton > button:active {
    transform: translateY(0px) scale(0.97) !important;
    box-shadow: 0 2px 10px rgba(255,157,92,0.15) !important;
    transition: all 0.1s ease !important;
}

/* BACK BUTTON — special style */
.stButton > button[kind="secondary"],
.stApp .element-container:last-child .stButton > button {
    border-color: rgba(167,139,250,0.4) !important;
    color: #c4b5fd !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 20px !important;
    backdrop-filter: blur(16px);
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    position: relative;
    overflow: hidden;
}

[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,157,92,0.06) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.4s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    border-color: rgba(255,157,92,0.3);
    box-shadow: 0 12px 35px rgba(0,0,0,0.4), 0 0 20px rgba(255,157,92,0.08);
}

[data-testid="stMetric"]:hover::before {
    opacity: 1;
}

[data-testid="stMetricValue"] {
    font-family: 'Cinzel', serif !important;
    font-size: 1.4rem !important;
    color: #e8c97e !important;
}

[data-testid="stMetricLabel"] {
    font-family: 'Raleway', sans-serif !important;
    color: rgba(232,224,213,0.6) !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase;
}

/* ── MOVIE TITLE TEXT ── */
.stApp p {
    font-family: 'Raleway', sans-serif !important;
    color: rgba(232,224,213,0.8) !important;
    font-size: 12px !important;
    margin-top: 6px !important;
    line-height: 1.4 !important;
    text-align: center;
}

/* ── DETAILS PAGE ── */
.stApp h1 {
    font-family: 'Cinzel', serif !important;
    font-size: 2.2rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #fff 0%, #e8c97e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.08em;
    animation: fadeSlideIn 0.6s ease both;
}

@keyframes fadeSlideIn {
    0%  { opacity: 0; transform: translateY(20px); }
    100%{ opacity: 1; transform: translateY(0); }
}

/* Details page overview text */
.stApp [data-testid="stMarkdownContainer"] p {
    font-size: 14px !important;
    line-height: 1.8 !important;
    color: rgba(232,224,213,0.75) !important;
    text-align: left;
}

/* ── SPINNER ── */
.stSpinner > div {
    border-color: #ff9d5c transparent transparent transparent !important;
}

/* ── VIDEO ── */
.stVideo {
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.6);
    transition: transform 0.4s ease;
}

.stVideo:hover {
    transform: scale(1.01);
}

/* ── DIVIDER ── */
hr {
    border-color: rgba(255,255,255,0.05) !important;
    margin: 24px 0 !important;
}

/* ── CAPTION ── */
.stCaptionContainer {
    color: rgba(232,224,213,0.4) !important;
    font-family: 'Raleway', sans-serif !important;
    letter-spacing: 0.08em !important;
    font-size: 11px !important;
    text-transform: uppercase;
}

/* ── WATCHLIST BADGE ── */
.watchlist-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(255,157,92,0.15), rgba(167,139,250,0.15));
    border: 1px solid rgba(255,157,92,0.35);
    border-radius: 30px;
    padding: 4px 14px;
    font-size: 11px;
    color: #e8c97e;
    letter-spacing: 0.1em;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    text-transform: uppercase;
    animation: pulseBadge 2s ease-in-out infinite;
}

@keyframes pulseBadge {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,157,92,0.2); }
    50%       { box-shadow: 0 0 0 6px rgba(255,157,92,0); }
}

/* ── SCROLL REVEAL ── */
@keyframes cardReveal {
    0%  { opacity: 0; transform: translateY(30px) scale(0.95); }
    100%{ opacity: 1; transform: translateY(0) scale(1); }
}

[data-testid="column"] {
    animation: cardReveal 0.5s ease both;
}

[data-testid="column"]:nth-child(1) { animation-delay: 0.05s; }
[data-testid="column"]:nth-child(2) { animation-delay: 0.10s; }
[data-testid="column"]:nth-child(3) { animation-delay: 0.15s; }
[data-testid="column"]:nth-child(4) { animation-delay: 0.20s; }
[data-testid="column"]:nth-child(5) { animation-delay: 0.25s; }
[data-testid="column"]:nth-child(6) { animation-delay: 0.30s; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #ff9d5c, #a78bfa);
    border-radius: 3px;
}

/* ── RIPPLE ON CLICK ── */
.stButton > button:active::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
    animation: rippleEffect 0.4s ease-out;
}

@keyframes rippleEffect {
    0%   { transform: scale(0); opacity: 1; }
    100% { transform: scale(2.5); opacity: 0; }
}

/* Rating star */
.rating-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(232,201,126,0.1);
    border: 1px solid rgba(232,201,126,0.3);
    border-radius: 30px;
    padding: 6px 16px;
    font-family: 'Cinzel', serif;
    font-size: 1rem;
    color: #e8c97e;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
}

</style>
""", unsafe_allow_html=True)

# ================= API FUNCTIONS =================
def fetch(url):
    try:
        return requests.get(url).json()
    except:
        return {}

def search_movie(query):
    return fetch(f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}")

def get_trending():
    return fetch(f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}")

def get_details(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}")

def get_credits(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}")

def get_trailer(movie_id):
    data = fetch(f"{BASE_URL}/movie/{movie_id}/videos?api_key={TMDB_API_KEY}")
    for v in data.get("results", []):
        if v.get("type") == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def get_recommendations(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}")

def get_images(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/images?api_key={TMDB_API_KEY}")

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "movie_id" not in st.session_state:
    st.session_state.movie_id = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ================= HEADER =================
st.markdown("## 🎬 LUMORA")
st.markdown(
    "<p style='text-align:center;font-size:11px;letter-spacing:0.25em;"
    "color:rgba(232,224,213,0.35);text-transform:uppercase;"
    "font-family:Raleway,sans-serif;margin-top:-10px;margin-bottom:20px;'>"
    "Cinema Rediscovered</p>",
    unsafe_allow_html=True
)

query = st.text_input("🔍 Search for a film…", placeholder="e.g. Inception, Parasite, Dune…")

# ================= HOME =================
if st.session_state.page == "home":

    if query:
        with st.spinner("Searching the archives…"):
            results = search_movie(query)

        st.markdown('<div class="section-title">🔎 Results</div>', unsafe_allow_html=True)
        cols = st.columns(5)

        for i, m in enumerate(results.get("results", [])[:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.markdown(
                        f'<div class="poster-wrap"><img src="{IMG + m["poster_path"]}" /></div>'
                        f'<div class="poster-title">{m.get("title", "Untitled")}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown('<div class="poster-btn-wrap">', unsafe_allow_html=True)
                    if st.button("\u200b", key=f"search_{m['id']}"):
                        st.session_state.movie_id = m["id"]
                        st.session_state.page = "details"
                        st.rerun()
                    st.markdown(
                        f'<div class="poster-wrap"><img src="{IMG +m["poster_path"]}" /></div>'
                        f'<div class="poster-title">{m.get("title","Untitled")}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="poster-title">{m.get("title", "Untitled")}</div>', unsafe_allow_html=True)
                    if st.button(m.get("title", "View"), key=f"search_{m['id']}"):
                        st.session_state.movie_id = m["id"]
                        st.session_state.page = "details"
                        st.rerun()

    st.markdown('<div class="section-title">🔥 Trending This Week</div>', unsafe_allow_html=True)

    with st.spinner("Curating the reel…"):
        trending = get_trending()

    cols = st.columns(6)
    for i, m in enumerate(trending.get("results", [])[:12]):
        with cols[i % 6]:
            if m.get("poster_path"):
                st.markdown(
                    f'<div class="poster-wrap"><img src="{IMG + m["poster_path"]}" /></div>'
                    f'<div class="poster-title">{m.get("title", "Untitled")}</div>',
                    unsafe_allow_html=True
                )
                st.markdown('<div class="poster-btn-wrap">', unsafe_allow_html=True)
                if st.button("\u200b", key=f"trend_{i}"):
                    st.session_state.movie_id = m["id"]
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="poster-title">{m.get("title", "Untitled")}</div>', unsafe_allow_html=True)
                if st.button(m.get("title", "View"), key=f"trend_{i}"):
                    st.session_state.movie_id = m["id"]
                    st.session_state.page = "details"
                    st.rerun()

    if st.session_state.watchlist:
        st.markdown('<div class="section-title">❤️ Your Watchlist</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="watchlist-badge">{len(st.session_state.watchlist)} films saved</span>',
            unsafe_allow_html=True
        )
        cols = st.columns(6)

        for i, m in enumerate(st.session_state.watchlist):
            with cols[i % 6]:
                if m.get("poster"):
                    st.image(IMG + m["poster"])
                st.write(m["title"])

# ================= DETAILS =================
elif st.session_state.page == "details":

    movie_id = st.session_state.movie_id

    with st.spinner("Pulling from the vault…"):
        data     = get_details(movie_id)
        credits  = get_credits(movie_id)
        trailer  = get_trailer(movie_id)
        images   = get_images(movie_id)

    col1, col2 = st.columns([1, 2])

    with col1:
        if data.get("poster_path"):
            st.image(IMG + data["poster_path"])

    with col2:
        st.title(data.get("title", "Untitled"))

        rating = data.get("vote_average", 0)
        st.markdown(
            f'<div class="rating-pill">⭐ {rating:.1f} <span style="opacity:0.5;font-size:0.75em">/ 10</span></div>',
            unsafe_allow_html=True
        )

        genres = " · ".join([g["name"] for g in data.get("genres", [])])
        if genres:
            st.markdown(
                f'<p style="font-size:12px;letter-spacing:0.08em;color:rgba(232,224,213,0.45);">{genres}</p>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<p style="font-size:14px;line-height:1.8;color:rgba(232,224,213,0.75);text-align:left;">'
            f'{data.get("overview","No overview available.")}</p>',
            unsafe_allow_html=True
        )

        already = any(w["title"] == data.get("title") for w in st.session_state.watchlist)
        if already:
            st.markdown('<span class="watchlist-badge">❤️ In Watchlist</span>', unsafe_allow_html=True)
        else:
            if st.button("❤️ Add to Watchlist"):
                st.session_state.watchlist.append({
                    "title": data.get("title"),
                    "poster": data.get("poster_path")
                })
                st.rerun()

    # ── BOX OFFICE ──
    st.markdown("---")
    st.markdown('<div class="section-title">💰 Box Office</div>', unsafe_allow_html=True)

    revenue = data.get("revenue", 0)
    budget  = data.get("budget", 0)

    def money(x):
        if x >= 1_000_000_000: return f"${x/1e9:.2f}B"
        elif x >= 1_000_000:   return f"${x/1e6:.2f}M"
        elif x > 0:             return f"${x:,}"
        return "N/A"

    c1, c2, c3 = st.columns(3)
    c1.metric("🌍 Revenue", money(revenue))
    c2.metric("🎬 Budget",  money(budget))
    c3.metric("📈 Profit",  money(revenue - budget if revenue and budget else 0))

    # ── TRAILER ──
    if trailer:
        st.markdown("---")
        st.markdown('<div class="section-title">▶️ Official Trailer</div>', unsafe_allow_html=True)
        st.video(trailer)

    # ── SCENES ──
    backdrops = images.get("backdrops", [])
    if backdrops:
        st.markdown("---")
        st.markdown('<div class="section-title">🖼️ Scenes from the Film</div>', unsafe_allow_html=True)
        st.caption("Official stills and cinematic moments")

        cols = st.columns(3)
        for i, img in enumerate(backdrops[:6]):
            with cols[i % 3]:
                st.image(BACKDROP + img["file_path"])

    # ── CAST ──
    st.markdown("---")
    st.markdown('<div class="section-title">🎭 Cast</div>', unsafe_allow_html=True)

    cols = st.columns(6)
    for i, c in enumerate(credits.get("cast", [])[:12]):
        with cols[i % 6]:
            if c.get("profile_path"):
                st.image(IMG + c["profile_path"])
            st.write(c.get("name", ""))

    # ── DIRECTOR ──
    director = next(
        (crew for crew in credits.get("crew", []) if crew.get("job") == "Director"),
        None
    )

    if director:
        st.markdown("---")
        st.markdown('<div class="section-title">🎬 Director</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 4])
        with col1:
            if director.get("profile_path"):
                st.image("https://image.tmdb.org/t/p/w300" + director["profile_path"])
        with col2:
            st.markdown(
                f"<h3 style='font-family:Cinzel,serif;color:#e8c97e;"
                f"letter-spacing:0.1em;margin-top:20px;'>{director.get('name','')}</h3>",
                unsafe_allow_html=True
            )

    # ── RECOMMENDATIONS ──
    rec = get_recommendations(movie_id)
    if rec.get("results"):
        st.markdown("---")
        st.markdown('<div class="section-title">🎯 You Might Also Like</div>', unsafe_allow_html=True)

        cols = st.columns(6)
        for i, m in enumerate(rec.get("results", [])[:12]):
            with cols[i % 6]:
                if m.get("poster_path"):
                    st.markdown(
                        f'<div class="poster-wrap"><img src="{IMG + m["poster_path"]}" /></div>'
                        f'<div class="poster-title">{m.get("title", "")}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown('<div class="poster-btn-wrap">', unsafe_allow_html=True)
                    if st.button("\u200b", key=f"rec_{i}"):
                        st.session_state.movie_id = m["id"]
                        st.session_state.page = "details"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="poster-title">{m.get("title", "")}</div>', unsafe_allow_html=True)
                    if st.button(m.get("title", "View"), key=f"rec_{i}"):
                        st.session_state.movie_id = m["id"]
                        st.rerun()

    # ── BACK ──
    st.markdown("---")
    if st.button("⬅ Back to Home"):
        st.session_state.page = "home"
        st.rerun()
