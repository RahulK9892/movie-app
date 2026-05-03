import streamlit as st
import requests

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LUMORA",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")
TMDB_BASE    = "https://api.themoviedb.org/3"
IMG_BASE     = "https://image.tmdb.org/t/p"

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in {
    "page": "home",
    "selected_id": None,
    "search_query": "",
    "detail_tab": "Overview",
    "nav_section": "trending",
    "my_list": [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_money(val):
    if not val:
        return "N/A"
    try:
        val = float(val)
        if val >= 1_000_000_000: return f"${val/1_000_000_000:.2f}B"
        if val >= 1_000_000:     return f"${val/1_000_000:.1f}M"
        if val >= 1_000:         return f"${val/1_000:.0f}K"
        return f"${val:,.0f}"
    except (TypeError, ValueError):
        return "N/A"

def tmdb(endpoint, **params):
    if not TMDB_API_KEY:
        return {}
    params["api_key"] = TMDB_API_KEY
    try:
        r = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def poster_url(path, size="w342"):
    return f"{IMG_BASE}/{size}{path}" if path else ""

def profile_url(path, size="w185"):
    return f"{IMG_BASE}/{size}{path}" if path else ""

def youtube_embed(key):
    return f"https://www.youtube.com/embed/{key}?autoplay=0&rel=0"

def search_movies(query):
    return tmdb("/search/movie", query=query, include_adult=False).get("results", [])

def get_movie_details(movie_id):
    return tmdb(f"/movie/{movie_id}", append_to_response="credits,videos,images,similar,reviews")

def get_trending():
    return tmdb("/trending/movie/week").get("results", [])[:12]

def get_popular():
    return tmdb("/movie/popular").get("results", [])[:12]

def get_top_rated():
    return tmdb("/movie/top_rated").get("results", [])[:12]

def get_series_trending():
    return tmdb("/trending/tv/week").get("results", [])[:12]

def get_series_popular():
    return tmdb("/tv/popular").get("results", [])[:12]

def open_detail(movie_id):
    st.session_state.selected_id = movie_id
    st.session_state.page        = "detail"
    st.session_state.detail_tab  = "Overview"
    st.rerun()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Nunito+Sans:ital,wght@0,300;0,400;0,600;0,700;1,400&display=swap');

:root {
  --gold:  #c9a84c; --gold2: #f0d080;
  --dark:  #0a0a0f; --card:  #12121a; --card2: #1a1a28;
  --text:  #e8e0d0; --muted: #8a8090;
  --red:   #e53935; --green: #43a047;
}
html,body,[class*="css"]{ background:var(--dark)!important; color:var(--text); }
.stApp{ background:var(--dark)!important; }
#MainMenu,header,footer{ display:none!important; }
.block-container{ padding:0!important; max-width:100%!important; }
section[data-testid="stSidebar"]{ display:none; }

/* NAV column alignment */
div[data-testid="column"] {
  display: flex !important;
  align-items: center !important;
}

/* NAV buttons — base style (columns 2-5 = Browse, Movies, Series, My List) */
div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button,
div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button,
div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button,
div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid rgba(201,168,76,0.2) !important;
  border-radius: 20px !important;
  color: var(--text) !important;
  font-family: 'Nunito Sans', sans-serif !important;
  font-weight: 600 !important;
  font-size: .88rem !important;
  letter-spacing: .07em !important;
  padding: 7px 20px !important;
  box-shadow: none !important;
  transition: all .2s ease !important;
  cursor: pointer !important;
  width: auto !important;
}
div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button:hover,
div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button:hover,
div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button:hover,
div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button:hover {
  background: rgba(201,168,76,0.13) !important;
  border-color: rgba(201,168,76,0.55) !important;
  color: var(--gold) !important;
  box-shadow: 0 0 10px rgba(201,168,76,0.15) !important;
}

/* NAV column alignment */
div[data-testid="column"] {
  display: flex !important;
  align-items: center !important;
}

/* LOGO */
.lumora-logo{
  font-family:'Cinzel',serif; font-size:1.85rem; font-weight:900;
  color:var(--gold); letter-spacing:.16em; padding:14px 0;
}

/* HERO */
.hero-wrap{
  position:relative; min-height:88vh;
  display:flex; align-items:flex-end; overflow:hidden;
}
.hero-bg{
  position:absolute; inset:0; background-size:cover;
  background-position:center top; filter:brightness(.42);
}
.hero-gradient{
  position:absolute; inset:0;
  background:linear-gradient(90deg,rgba(10,10,15,1) 0%,rgba(10,10,15,.65) 55%,transparent 100%),
             linear-gradient(0deg,rgba(10,10,15,1) 0%,transparent 52%);
}
.hero-content{
  position:relative; z-index:2;
  max-width:620px; padding:0 56px 68px;
}
.hero-tagline{
  font-family:'Cinzel',serif; font-size:.72rem;
  letter-spacing:.32em; color:var(--gold);
  text-transform:uppercase; margin-bottom:10px;
}
.hero-title{
  font-family:'Cinzel',serif;
  font-size:clamp(2.2rem,5vw,3.8rem); font-weight:900;
  line-height:1.05; margin:0 0 14px; color:#fff;
}
.hero-meta{ display:flex; align-items:center; gap:14px; margin-bottom:12px; flex-wrap:wrap; }
.hero-rating{ color:var(--gold); font-weight:700; font-size:1rem; }
.hero-votes,.hero-year,.hero-runtime{ color:var(--muted); font-size:.88rem; }
.hero-genres{ display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }
.genre-badge{
  border:1px solid rgba(201,168,76,.4); border-radius:3px;
  padding:3px 12px; font-size:.76rem; letter-spacing:.07em;
  color:var(--gold2); background:rgba(201,168,76,.08);
}
.hero-overview{
  font-family:'Nunito Sans',sans-serif; font-size:.95rem; line-height:1.75;
  color:rgba(232,224,208,.85); margin-bottom:26px;
  display:-webkit-box; -webkit-line-clamp:4;
  -webkit-box-orient:vertical; overflow:hidden;
}

/* SECTION */
.section-wrap{ padding:36px 56px; }
.section-title{
  font-family:'Cinzel',serif; font-size:1.2rem; font-weight:700;
  color:var(--text); margin-bottom:20px;
  border-left:3px solid var(--gold); padding-left:14px;
  letter-spacing:.06em;
}

/* CARD */
.movie-card-img{
  width:100%; border-radius:7px 7px 0 0;
  display:block; aspect-ratio:2/3; object-fit:cover;
}
.movie-card-wrap{
  background:var(--card); border-radius:8px; overflow:hidden;
  margin-bottom:4px; transition:transform .2s, box-shadow .2s;
}
.movie-card-wrap:hover{ transform:translateY(-5px); box-shadow:0 16px 40px rgba(0,0,0,.6); }
.movie-card-body{ padding:8px 10px 10px; }
.movie-card-title{
  font-weight:700; font-size:.82rem;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
.movie-card-sub{ font-size:.73rem; color:var(--muted); margin-top:3px; }
.movie-card-no-img{
  width:100%; aspect-ratio:2/3; background:var(--card2);
  display:flex; align-items:center; justify-content:center;
  font-size:2.2rem; border-radius:7px 7px 0 0;
}

/* VIEW button */
div[data-testid="stButton"] > button{
  width:100%!important; background:rgba(201,168,76,.1)!important;
  border:1px solid rgba(201,168,76,.25)!important;
  color:var(--gold)!important; border-radius:0 0 8px 8px!important;
  font-size:.78rem!important; font-weight:600!important;
  padding:6px 0!important; letter-spacing:.06em!important;
}
div[data-testid="stButton"] > button:hover{
  background:rgba(201,168,76,.25)!important;
}

/* DETAIL */
.detail-wrap{ padding:36px 56px; }
.detail-title{
  font-family:'Cinzel',serif; font-size:clamp(1.8rem,3.5vw,3rem);
  font-weight:900; margin:0 0 10px; color:#fff;
}
.detail-tagline{
  font-family:'Cinzel',serif; font-size:.85rem;
  color:var(--gold); letter-spacing:.2em;
  text-transform:uppercase; margin-bottom:18px;
}
.stat-row{ display:flex; gap:28px; flex-wrap:wrap; margin-bottom:18px; }
.stat-item{ display:flex; flex-direction:column; }
.stat-label{ font-size:.68rem; letter-spacing:.12em; color:var(--muted); text-transform:uppercase; margin-bottom:3px; }
.stat-value{ font-family:'Nunito Sans',sans-serif; font-weight:700; font-size:1rem; }
.stat-value.green{ color:var(--green); }
.stat-value.red  { color:var(--red); }
.stat-value.gold { color:var(--gold); }

/* TABS */
.tab-row-wrap{
  display:flex; gap:0; border-bottom:1px solid rgba(255,255,255,.1);
  margin-bottom:26px; flex-wrap:wrap;
}
.tab-btn-item > div > button,
.tab-btn-item > div > button:hover,
.tab-btn-item > div > button:focus{
  background:transparent!important; border:none!important;
  border-bottom:2px solid transparent!important;
  color:var(--muted)!important; font-family:'Nunito Sans',sans-serif!important;
  font-size:.86rem!important; font-weight:600!important;
  padding:10px 16px!important; box-shadow:none!important;
  border-radius:0!important; letter-spacing:.04em!important;
}
.tab-btn-item > div > button:hover{ color:var(--text)!important; }
.tab-btn-active > div > button,
.tab-btn-active > div > button:hover,
.tab-btn-active > div > button:focus{
  background:transparent!important; border:none!important;
  border-bottom:2px solid var(--gold)!important;
  color:var(--gold)!important; font-family:'Nunito Sans',sans-serif!important;
  font-size:.86rem!important; font-weight:700!important;
  padding:10px 16px!important; box-shadow:none!important;
  border-radius:0!important; letter-spacing:.04em!important;
}

/* VIDEO */
.video-grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; margin-bottom:12px; }
.video-frame{ border-radius:8px; overflow:hidden; background:#000; aspect-ratio:16/9; }
.video-frame iframe{ width:100%; height:100%; border:none; display:block; }

/* SCENES */
.scenes-grid{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:12px; }
.scene-img{ border-radius:6px; overflow:hidden; aspect-ratio:16/9; }
.scene-img img{ width:100%; height:100%; object-fit:cover; display:block; transition:transform .3s; }
.scene-img:hover img{ transform:scale(1.05); }

/* CAST — 10-column HTML grid, no Streamlit columns */
.cast-outer{
  display:grid;
  grid-template-columns:repeat(10,1fr);
  gap:12px; margin-bottom:24px;
}
@media(max-width:1400px){ .cast-outer{ grid-template-columns:repeat(8,1fr); } }
@media(max-width:1100px){ .cast-outer{ grid-template-columns:repeat(6,1fr); } }
@media(max-width:800px) { .cast-outer{ grid-template-columns:repeat(4,1fr); } }
.cast-card{
  background:var(--card); border-radius:8px; overflow:hidden;
  text-align:center; transition:transform .2s;
}
.cast-card:hover{ transform:translateY(-4px); }
.cast-photo{ width:100%; aspect-ratio:2/3; object-fit:cover; display:block; }
.cast-ph{
  width:100%; aspect-ratio:2/3; background:var(--card2);
  display:flex; align-items:center; justify-content:center; font-size:2rem;
}
.cast-name{ font-size:.74rem; font-weight:700; padding:6px 6px 2px; line-height:1.25; }
.cast-char{ font-size:.65rem; color:var(--muted); padding:0 6px 8px; line-height:1.2; }

/* DIRECTOR */
.director-card{
  display:flex; align-items:center; gap:22px;
  background:var(--card2); border-radius:10px; padding:18px 22px;
  max-width:420px; margin-bottom:10px;
}
.director-photo{ width:80px; height:80px; border-radius:50%; object-fit:cover; flex-shrink:0; }
.director-ph{
  width:80px; height:80px; border-radius:50%; background:var(--card);
  display:flex; align-items:center; justify-content:center;
  font-size:2rem; flex-shrink:0;
}
.director-label{ font-size:.68rem; letter-spacing:.15em; text-transform:uppercase; color:var(--muted); }
.director-name{ font-family:'Cinzel',serif; font-size:1.12rem; font-weight:700; color:var(--gold2); }

/* REVIEW */
.review-card{ background:var(--card2); border-radius:8px; padding:18px 22px; margin-bottom:12px; }
.review-author{ font-weight:700; font-size:.9rem; margin-bottom:6px; }
.review-body{ font-size:.87rem; line-height:1.75; color:rgba(232,224,208,.8); }

/* MY LIST */
.mylist-empty{
  text-align:center; padding:80px 0;
  color:var(--muted); font-family:'Cinzel',serif; font-size:1.1rem;
}

/* SEARCH INPUT */
div[data-testid="stTextInput"] input{
  background:var(--card2)!important;
  border:1px solid rgba(201,168,76,.3)!important;
  color:var(--text)!important; border-radius:6px!important;
  font-family:'Nunito Sans',sans-serif!important;
}
.divider{ height:1px; background:rgba(255,255,255,.07); margin:6px 0 20px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  NAV — real Streamlit buttons so clicks actually work
# ─────────────────────────────────────────────────────────────────────────────
def render_nav():
    active = st.session_state.nav_section
    page   = st.session_state.page

    logo_c, br_c, mv_c, sr_c, ml_c, sp_c = st.columns([2.2, 1, 1, 1, 1.3, 3.5])

    with logo_c:
        st.markdown('<div class="lumora-logo">LUMORA</div>', unsafe_allow_html=True)

    # Inject dynamic active-state CSS based on current page/section
    browse_active = (page == "home" and active == "trending")
    movies_active = (page == "home" and active == "movies")
    series_active = (page == "home" and active == "series")
    mylist_active = (page == "mylist")

    active_css = ""
    if browse_active:
        active_css += """
        div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button {
          background: linear-gradient(135deg, rgba(201,168,76,0.22), rgba(240,208,128,0.1)) !important;
          border: 1px solid var(--gold) !important; color: var(--gold) !important;
          font-weight: 700 !important; box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
        }"""
    if movies_active:
        active_css += """
        div[data-testid="column"]:nth-child(3) div[data-testid="stButton"] > button {
          background: linear-gradient(135deg, rgba(201,168,76,0.22), rgba(240,208,128,0.1)) !important;
          border: 1px solid var(--gold) !important; color: var(--gold) !important;
          font-weight: 700 !important; box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
        }"""
    if series_active:
        active_css += """
        div[data-testid="column"]:nth-child(4) div[data-testid="stButton"] > button {
          background: linear-gradient(135deg, rgba(201,168,76,0.22), rgba(240,208,128,0.1)) !important;
          border: 1px solid var(--gold) !important; color: var(--gold) !important;
          font-weight: 700 !important; box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
        }"""
    if mylist_active:
        active_css += """
        div[data-testid="column"]:nth-child(5) div[data-testid="stButton"] > button {
          background: linear-gradient(135deg, rgba(201,168,76,0.22), rgba(240,208,128,0.1)) !important;
          border: 1px solid var(--gold) !important; color: var(--gold) !important;
          font-weight: 700 !important; box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
        }"""

    if active_css:
        st.markdown(f"<style>{active_css}</style>", unsafe_allow_html=True)

    with br_c:
        if st.button("Browse", key="nav_browse"):
            st.session_state.page = "home"
            st.session_state.nav_section = "trending"
            st.rerun()

    with mv_c:
        if st.button("Movies", key="nav_movies"):
            st.session_state.page = "home"
            st.session_state.nav_section = "movies"
            st.rerun()

    with sr_c:
        if st.button("Series", key="nav_series"):
            st.session_state.page = "home"
            st.session_state.nav_section = "series"
            st.rerun()

    with ml_c:
        n   = len(st.session_state.my_list)
        lbl = f"My List ({n})" if n else "My List"
        if st.button(lbl, key="nav_mylist"):
            st.session_state.page = "mylist"
            st.rerun()

    with sp_c:
        q = st.text_input("", placeholder="🔍  Search movies & series…",
                          key="search_input", label_visibility="collapsed")
        if q and q != st.session_state.search_query:
            st.session_state.search_query = q
            st.session_state.page = "search"
            st.rerun()
        elif not q and st.session_state.search_query:
            st.session_state.search_query = ""
            if st.session_state.page == "search":
                st.session_state.page = "home"
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  CARD GRID — unique keys via context + movie_id + index
# ─────────────────────────────────────────────────────────────────────────────
def _render_card_grid(items, context="def"):
    n = min(len(items), 12)
    if n == 0:
        return
    cols = st.columns(6)
    for i, m in enumerate(items[:n]):
        with cols[i % 6]:
            mid    = m.get("id", i)
            title  = m.get("title") or m.get("name") or "Untitled"
            p      = m.get("poster_path", "")
            year   = (m.get("release_date") or m.get("first_air_date") or "")[:4]
            rating = m.get("vote_average", 0)

            img_html = (
                f'<img class="movie-card-img" src="{poster_url(p)}">'
                if p else '<div class="movie-card-no-img">🎬</div>'
            )
            st.markdown(f"""
            <div class="movie-card-wrap">
              {img_html}
              <div class="movie-card-body">
                <div class="movie-card-title" title="{title}">{title}</div>
                <div class="movie-card-sub">★ {rating:.1f} · {year}</div>
              </div>
            </div>""", unsafe_allow_html=True)

            # KEY = context + movie_id + loop-index → guaranteed unique
            if st.button("▶ View", key=f"v_{context}_{mid}_{i}"):
                open_detail(mid)


def _section(title, items, context="s"):
    st.markdown(
        f'<div class="section-wrap"><div class="section-title">{title}</div>',
        unsafe_allow_html=True)
    _render_card_grid(items, context=context)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HERO
# ─────────────────────────────────────────────────────────────────────────────
def _render_hero(movie):
    backdrop = movie.get("backdrop_path", "")
    bg_url   = f"{IMG_BASE}/original{backdrop}" if backdrop else ""
    title    = movie.get("title") or movie.get("name") or ""
    tagline  = movie.get("tagline") or "Now Streaming"
    overview = (movie.get("overview") or "")[:280]
    year     = (movie.get("release_date") or "")[:4]
    rating   = movie.get("vote_average", 0)
    votes    = movie.get("vote_count", 0)
    runtime  = movie.get("runtime", 0)
    genres   = " ".join(
        f'<span class="genre-badge">{g["name"]}</span>'
        for g in movie.get("genres", [])[:4])

    st.markdown(f"""
    <div class="hero-wrap">
      <div class="hero-bg" style="background-image:url('{bg_url}')"></div>
      <div class="hero-gradient"></div>
      <div class="hero-content">
        <div class="hero-tagline">{tagline}</div>
        <h1 class="hero-title">{title}</h1>
        <div class="hero-meta">
          <span class="hero-rating">★ {rating:.1f}</span>
          <span class="hero-votes">({votes:,} votes)</span>
          <span class="hero-year">{year}</span>
          {'<span>·</span><span class="hero-runtime">' + str(runtime) + ' min</span>' if runtime else ''}
        </div>
        <div class="hero-genres">{genres}</div>
        <p class="hero-overview">{overview}</p>
      </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.3, 1.3, 8])
    with c1:
        if st.button("▶ Trailer", key="hero_trailer"):
            st.session_state.selected_id = movie["id"]
            st.session_state.page        = "detail"
            st.session_state.detail_tab  = "Trailer & Videos"
            st.rerun()
    with c2:
        if st.button("ℹ More Info", key="hero_info"):
            open_detail(movie["id"])


# ─────────────────────────────────────────────────────────────────────────────
#  CAST GRID — pure HTML (10 per row), no Streamlit widgets → zero key issues
# ─────────────────────────────────────────────────────────────────────────────
def _cast_html_grid(people, label_field="character"):
    cards = ""
    for p in people:
        ph    = profile_url(p.get("profile_path", ""))
        name  = p.get("name", "")
        lbl   = p.get(label_field, "")
        photo = (f'<img class="cast-photo" src="{ph}" loading="lazy">'
                 if ph else '<div class="cast-ph">👤</div>')
        cards += f"""<div class="cast-card">
          {photo}
          <div class="cast-name">{name}</div>
          <div class="cast-char">{lbl}</div>
        </div>"""
    return f'<div class="cast-outer">{cards}</div>'


# ─────────────────────────────────────────────────────────────────────────────
#  DETAIL PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_detail(movie_id):
    d = get_movie_details(movie_id)
    if not d:
        st.error("Could not load movie details.")
        return

    # Hero
    backdrop = d.get("backdrop_path", "")
    if backdrop:
        bg_url = f"{IMG_BASE}/original{backdrop}"
        title  = d.get("title") or d.get("name") or ""
        tg     = d.get("tagline") or "Now Streaming"
        ov     = (d.get("overview") or "")[:280]
        yr     = (d.get("release_date") or "")[:4]
        rt     = d.get("vote_average", 0)
        vc     = d.get("vote_count", 0)
        rm     = d.get("runtime", 0)
        gn     = " ".join(
            f'<span class="genre-badge">{g["name"]}</span>'
            for g in d.get("genres", [])[:4])
        st.markdown(f"""
        <div class="hero-wrap">
          <div class="hero-bg" style="background-image:url('{bg_url}')"></div>
          <div class="hero-gradient"></div>
          <div class="hero-content">
            <div class="hero-tagline">{tg}</div>
            <h1 class="hero-title">{title}</h1>
            <div class="hero-meta">
              <span class="hero-rating">★ {rt:.1f}</span>
              <span class="hero-votes">({vc:,} votes)</span>
              <span class="hero-year">{yr}</span>
              {'<span>·</span><span class="hero-runtime">' + str(rm) + ' min</span>' if rm else ''}
            </div>
            <div class="hero-genres">{gn}</div>
            <p class="hero-overview">{ov}</p>
          </div>
        </div>""", unsafe_allow_html=True)

    # Back + My List
    st.markdown('<div class="detail-wrap">', unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 1.6, 8])
    with b1:
        if st.button("← Back", key="det_back"):
            st.session_state.page = "home"
            st.session_state.selected_id = None
            st.rerun()
    with b2:
        ml      = st.session_state.my_list
        in_list = any(m["id"] == movie_id for m in ml)
        lbl     = "✓ In My List" if in_list else "+ My List"
        if st.button(lbl, key="det_mylist"):
            if in_list:
                st.session_state.my_list = [m for m in ml if m["id"] != movie_id]
            else:
                st.session_state.my_list.append({
                    "id": d.get("id"),
                    "title": d.get("title") or d.get("name", ""),
                    "poster_path": d.get("poster_path", ""),
                    "vote_average": d.get("vote_average", 0),
                    "release_date": d.get("release_date", ""),
                })
            st.rerun()

    # Tabs
    st.markdown('<div class="tab-row-wrap">', unsafe_allow_html=True)
    tabs     = ["Overview", "Trailer & Videos", "Scenes", "Cast & Crew", "Reviews", "Similar"]
    tab_cols = st.columns(len(tabs))
    for i, t in enumerate(tabs):
        with tab_cols[i]:
            css = "tab-btn-active" if st.session_state.detail_tab == t else "tab-btn-item"
            st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
            if st.button(t, key=f"det_tab_{t}"):
                st.session_state.detail_tab = t
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    tab = st.session_state.detail_tab

    # ── OVERVIEW ──────────────────────────────────────────────────────────────
    if tab == "Overview":
        pp = d.get("poster_path", "")
        cp, ci = st.columns([1, 2.8])
        with cp:
            if pp:
                st.markdown(
                    f'<img src="{poster_url(pp,"w500")}" '
                    'style="width:100%;border-radius:10px;box-shadow:0 20px 60px rgba(0,0,0,.7)">',
                    unsafe_allow_html=True)
        with ci:
            st.markdown(f'<h1 class="detail-title">{d.get("title","")}</h1>', unsafe_allow_html=True)
            if d.get("tagline"):
                st.markdown(f'<div class="detail-tagline">{d["tagline"]}</div>', unsafe_allow_html=True)

            budget  = d.get("budget") or 0
            revenue = d.get("revenue") or 0
            profit  = revenue - budget if revenue and budget else None
            pcls    = "green" if profit and profit > 0 else ("red" if profit else "")

            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-item">
                <span class="stat-label">Rating</span>
                <span class="stat-value gold">★ {d.get('vote_average',0):.1f}/10</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Year</span>
                <span class="stat-value">{(d.get('release_date','') or '')[:4]}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Runtime</span>
                <span class="stat-value">{d.get('runtime',0)} min</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Budget</span>
                <span class="stat-value">{fmt_money(budget)}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Revenue</span>
                <span class="stat-value">{fmt_money(revenue)}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Profit</span>
                <span class="stat-value {pcls}">{fmt_money(profit)}</span>
              </div>
            </div>
            <div style="font-family:'Nunito Sans',sans-serif;line-height:1.8;
                        color:rgba(232,224,208,.9);max-width:700px;margin-bottom:18px;">
              {d.get('overview','')}
            </div>""", unsafe_allow_html=True)

            genres = " ".join(
                f'<span class="genre-badge">{g["name"]}</span>'
                for g in d.get("genres", []))
            st.markdown(f'<div class="hero-genres">{genres}</div>', unsafe_allow_html=True)

            comps = ", ".join(c["name"] for c in d.get("production_companies", [])[:4])
            if comps:
                st.markdown(f"""
                <div style="margin-top:14px;font-size:.84rem;color:var(--muted)">
                  <span style="letter-spacing:.1em;text-transform:uppercase;font-size:.68rem">Studio</span><br>
                  <span style="color:var(--text);font-weight:600">{comps}</span>
                </div>""", unsafe_allow_html=True)

    # ── TRAILER & VIDEOS ──────────────────────────────────────────────────────
    elif tab == "Trailer & Videos":
        st.markdown('<div class="section-title">Trailers & Videos</div>', unsafe_allow_html=True)
        videos  = d.get("videos", {}).get("results", [])
        yt_vids = [v for v in videos if v.get("site") == "YouTube"]
        yt_vids.sort(key=lambda v: (v.get("type") != "Trailer", not v.get("official", False)))
        if not yt_vids:
            st.info("No trailers available.")
        else:
            st.markdown('<div class="video-grid">', unsafe_allow_html=True)
            for v in yt_vids[:8]:
                st.markdown(f"""
                <div>
                  <div class="video-frame">
                    <iframe src="{youtube_embed(v['key'])}" allowfullscreen></iframe>
                  </div>
                  <div style="margin-top:6px;font-size:.78rem;color:var(--muted)">
                    {v.get('type','')} · {v.get('name','')}
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── SCENES ────────────────────────────────────────────────────────────────
    elif tab == "Scenes":
        st.markdown('<div class="section-title">Scenes from the Film</div>', unsafe_allow_html=True)
        backdrops = d.get("images", {}).get("backdrops", [])[:24]
        if not backdrops:
            st.info("No scene images available.")
        else:
            st.markdown('<div class="scenes-grid">', unsafe_allow_html=True)
            for img in backdrops:
                fp = img.get("file_path", "")
                if fp:
                    st.markdown(
                        f'<div class="scene-img"><img src="{IMG_BASE}/w780{fp}" loading="lazy"></div>',
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── CAST & CREW ───────────────────────────────────────────────────────────
    elif tab == "Cast & Crew":
        credits = d.get("credits", {})
        cast    = credits.get("cast", [])[:30]
        crew    = credits.get("crew", [])

        # Directors
        directors = [c for c in crew if c.get("job") == "Director"]
        if directors:
            st.markdown('<div class="section-title">Director</div>', unsafe_allow_html=True)
            dir_html = ""
            for dr in directors:
                ph    = profile_url(dr.get("profile_path", ""))
                photo = (f'<img class="director-photo" src="{ph}">'
                         if ph else '<div class="director-ph">🎬</div>')
                dir_html += f"""
                <div class="director-card">
                  {photo}
                  <div>
                    <div class="director-label">Director</div>
                    <div class="director-name">{dr.get('name','')}</div>
                    <div style="font-size:.78rem;color:var(--muted);margin-top:4px">
                      {dr.get('department','')}
                    </div>
                  </div>
                </div>"""
            st.markdown(dir_html, unsafe_allow_html=True)

        # Key crew
        key_jobs = ["Producer", "Executive Producer", "Screenplay", "Writer",
                    "Director of Photography", "Original Music Composer", "Editor"]
        key_crew = [c for c in crew if c.get("job") in key_jobs][:10]
        if key_crew:
            st.markdown('<div class="section-title" style="margin-top:28px">Key Crew</div>',
                        unsafe_allow_html=True)
            st.markdown(_cast_html_grid(key_crew, "job"), unsafe_allow_html=True)

        # Full cast — pure HTML 10-per-row grid
        if cast:
            st.markdown('<div class="section-title" style="margin-top:28px">Full Cast</div>',
                        unsafe_allow_html=True)
            st.markdown(_cast_html_grid(cast, "character"), unsafe_allow_html=True)

    # ── REVIEWS ───────────────────────────────────────────────────────────────
    elif tab == "Reviews":
        st.markdown('<div class="section-title">Audience Reviews</div>', unsafe_allow_html=True)
        reviews = d.get("reviews", {}).get("results", [])
        if not reviews:
            st.info("No reviews available.")
        for rv in reviews[:6]:
            r_val = rv.get("author_details", {}).get("rating")
            r_str = f"★ {r_val}/10" if r_val else ""
            body  = (rv.get("content") or "")[:600]
            ellip = "…" if len(rv.get("content") or "") > 600 else ""
            st.markdown(f"""
            <div class="review-card">
              <div class="review-author">{rv.get('author','')}
                <span style="color:var(--gold);font-size:.82rem;margin-left:10px">{r_str}</span>
              </div>
              <div class="review-body">{body}{ellip}</div>
            </div>""", unsafe_allow_html=True)

    # ── SIMILAR ───────────────────────────────────────────────────────────────
    elif tab == "Similar":
        st.markdown('<div class="section-title">You Might Also Like</div>', unsafe_allow_html=True)
        similar = d.get("similar", {}).get("results", [])[:12]
        if not similar:
            st.info("No similar titles found.")
        else:
            _render_card_grid(similar, context="sim")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MY LIST
# ─────────────────────────────────────────────────────────────────────────────
def show_mylist():
    st.markdown(
        '<div class="section-wrap"><div class="section-title">⭐ My List</div>',
        unsafe_allow_html=True)
    ml = st.session_state.my_list
    if not ml:
        st.markdown(
            '<div class="mylist-empty">Your list is empty.<br>'
            'Browse and tap + My List on any title.</div>',
            unsafe_allow_html=True)
    else:
        _render_card_grid(ml, context="ml")
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if not TMDB_API_KEY:
    st.warning("""
    ⚠️ **TMDB API key not set.**
    Add to `.streamlit/secrets.toml`:
    ```toml
    TMDB_API_KEY = "your_api_key_here"
    ```
    Get a free key at [themoviedb.org](https://www.themoviedb.org/settings/api).
    """)
    st.stop()

render_nav()

page = st.session_state.page

if page == "detail" and st.session_state.selected_id:
    show_detail(st.session_state.selected_id)

elif page == "search":
    results = search_movies(st.session_state.search_query)
    st.markdown(
        f'<div class="section-wrap">'
        f'<div class="section-title">Search: "{st.session_state.search_query}"</div>',
        unsafe_allow_html=True)
    if results:
        _render_card_grid(results[:12], context="srch")
    else:
        st.info("No results found.")
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "mylist":
    show_mylist()

else:
    nav = st.session_state.nav_section

    if nav == "series":
        s_trend = get_series_trending()
        s_pop   = get_series_popular()
        if s_trend:
            hero = tmdb(f"/tv/{s_trend[0]['id']}",
                        append_to_response="credits,videos,images,similar,reviews")
            _render_hero(hero if hero else s_trend[0])
        _section("📺 Trending Series",  s_trend, context="strend")
        _section("🔥 Popular Series",   s_pop,   context="spop")

    elif nav == "movies":
        pop = get_popular()
        top = get_top_rated()
        if pop:
            hero = get_movie_details(pop[0]["id"])
            _render_hero(hero if hero else pop[0])
        _section("🎬 Popular Movies",   pop, context="mpop")
        _section("⭐ Top Rated Movies", top, context="mtop")

    else:  # trending / browse
        trending = get_trending()
        popular  = get_popular()
        top      = get_top_rated()
        if trending:
            hero = get_movie_details(trending[0]["id"])
            _render_hero(hero if hero else trending[0])
        _section("🔥 Trending This Week", trending, context="trnd")
        _section("🎬 Popular Right Now",  popular,  context="popr")
        _section("⭐ Top Rated All Time", top,       context="topr")
