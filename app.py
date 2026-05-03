import streamlit as st
import requests
import urllib.parse

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LUMORA",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY", "")   # put your key in Streamlit secrets
TMDB_BASE    = "https://api.themoviedb.org/3"
IMG_BASE     = "https://image.tmdb.org/t/p"

# ── HELPERS ───────────────────────────────────────────────────────────────────
def fmt_money(val):
    """Format a number as money string – safely handles None / 0."""
    if not val:
        return "N/A"
    try:
        val = float(val)
        if val >= 1_000_000_000:
            return f"${val/1_000_000_000:.2f}B"
        if val >= 1_000_000:
            return f"${val/1_000_000:.1f}M"
        if val >= 1_000:
            return f"${val/1_000:.0f}K"
        return f"${val:,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def tmdb(endpoint, **params):
    """Call TMDB API and return JSON or empty dict on error."""
    if not TMDB_API_KEY:
        return {}
    params["api_key"] = TMDB_API_KEY
    try:
        r = requests.get(f"{TMDB_BASE}{endpoint}", params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def poster_url(path, size="w500"):
    return f"{IMG_BASE}/{size}{path}" if path else ""


def profile_url(path, size="w185"):
    return f"{IMG_BASE}/{size}{path}" if path else ""


def youtube_embed(key):
    return f"https://www.youtube.com/embed/{key}?autoplay=0&rel=0"


def search_movies(query):
    data = tmdb("/search/movie", query=query, include_adult=False)
    return data.get("results", [])


def get_movie_details(movie_id):
    return tmdb(f"/movie/{movie_id}", append_to_response="credits,videos,images,similar,reviews")


def get_trending():
    data = tmdb("/trending/movie/week")
    return data.get("results", [])[:12]


def get_popular():
    data = tmdb("/movie/popular")
    return data.get("results", [])[:12]


def get_top_rated():
    data = tmdb("/movie/top_rated")
    return data.get("results", [])[:12]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Nunito+Sans:wght@300;400;600;700&display=swap');

/* ── Root & Reset ── */
:root {
  --gold:   #c9a84c;
  --gold2:  #f0d080;
  --dark:   #0a0a0f;
  --card:   #12121a;
  --card2:  #1a1a28;
  --text:   #e8e0d0;
  --muted:  #8a8090;
  --red:    #e53935;
  --green:  #43a047;
}
html, body, [class*="css"] { background: var(--dark) !important; color: var(--text); }
.stApp { background: var(--dark) !important; }

/* Hide Streamlit chrome */
#MainMenu, header, footer { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── NAV ── */
.lumora-nav {
  position: sticky; top: 0; z-index: 999;
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 56px;
  background: linear-gradient(180deg, rgba(10,10,15,0.98) 0%, rgba(10,10,15,0.0) 100%);
  backdrop-filter: blur(12px);
}
.lumora-logo {
  font-family: 'Cinzel', serif;
  font-size: 1.9rem; font-weight: 900;
  color: var(--gold);
  letter-spacing: 0.15em;
}
.nav-links { display: flex; gap: 36px; }
.nav-links a {
  font-family: 'Nunito Sans', sans-serif; font-weight: 600;
  color: var(--text); text-decoration: none; font-size: 0.95rem;
  letter-spacing: 0.08em;
  transition: color .2s;
}
.nav-links a:hover, .nav-links a.active { color: var(--gold); }

/* ── HERO ── */
.hero-wrap {
  position: relative; min-height: 88vh;
  display: flex; align-items: flex-end;
  overflow: hidden;
}
.hero-bg {
  position: absolute; inset: 0;
  background-size: cover; background-position: center top;
  filter: brightness(.45);
}
.hero-gradient {
  position: absolute; inset: 0;
  background: linear-gradient(90deg, rgba(10,10,15,1) 0%, rgba(10,10,15,.6) 55%, transparent 100%),
              linear-gradient(0deg,   rgba(10,10,15,1) 0%, transparent 50%);
}
.hero-content {
  position: relative; z-index: 2;
  max-width: 620px; padding: 0 56px 72px;
}
.hero-tagline {
  font-family: 'Cinzel', serif; font-size: .75rem;
  letter-spacing: .3em; color: var(--gold);
  text-transform: uppercase; margin-bottom: 12px;
}
.hero-title {
  font-family: 'Cinzel', serif;
  font-size: clamp(2.4rem,5vw,4rem); font-weight: 900;
  line-height: 1.05; margin: 0 0 16px;
  color: #fff;
}
.hero-meta { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; flex-wrap: wrap; }
.hero-rating { color: var(--gold); font-weight: 700; font-size: 1rem; }
.hero-votes { color: var(--muted); font-size: .85rem; }
.hero-year, .hero-runtime { color: var(--muted); font-size: .9rem; }
.hero-genres { display: flex; gap: 8px; margin-bottom: 18px; flex-wrap: wrap; }
.genre-badge {
  border: 1px solid rgba(201,168,76,.4);
  border-radius: 3px; padding: 3px 12px;
  font-size: .78rem; letter-spacing: .07em;
  color: var(--gold2); background: rgba(201,168,76,.08);
}
.hero-overview {
  font-family: 'Nunito Sans', sans-serif; font-size: .97rem; line-height: 1.7;
  color: rgba(232,224,208,.85); margin-bottom: 28px;
  display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;
}
.hero-btns { display: flex; gap: 14px; flex-wrap: wrap; }
.btn-primary {
  background: var(--gold); color: #000;
  border: none; border-radius: 4px;
  padding: 12px 28px; font-family: 'Nunito Sans', sans-serif;
  font-size: .9rem; font-weight: 700; letter-spacing: .08em;
  cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px;
  transition: background .2s, transform .1s;
}
.btn-primary:hover { background: var(--gold2); transform: translateY(-1px); }
.btn-secondary {
  background: rgba(255,255,255,.1); color: #fff;
  border: 1px solid rgba(255,255,255,.25); border-radius: 4px;
  padding: 12px 28px; font-family: 'Nunito Sans', sans-serif;
  font-size: .9rem; font-weight: 600; letter-spacing: .08em;
  cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px;
  transition: background .2s;
}
.btn-secondary:hover { background: rgba(255,255,255,.2); }

/* ── SECTION ── */
.section-wrap { padding: 40px 56px; }
.section-title {
  font-family: 'Cinzel', serif; font-size: 1.25rem; font-weight: 700;
  color: var(--text); margin-bottom: 24px;
  border-left: 3px solid var(--gold); padding-left: 14px;
  letter-spacing: .06em;
}

/* ── MOVIE CARDS ── */
.cards-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}
.movie-card {
  background: var(--card); border-radius: 8px;
  overflow: hidden; cursor: pointer;
  transition: transform .2s, box-shadow .2s;
  text-decoration: none; color: inherit;
}
.movie-card:hover { transform: translateY(-6px) scale(1.02); box-shadow: 0 16px 40px rgba(0,0,0,.6); }
.movie-card img { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; }
.movie-card-no-img {
  width: 100%; aspect-ratio: 2/3;
  background: var(--card2); display: flex; align-items: center;
  justify-content: center; color: var(--muted); font-size: 2rem;
}
.card-body { padding: 10px 12px 14px; }
.card-title {
  font-family: 'Nunito Sans', sans-serif; font-weight: 700;
  font-size: .85rem; line-height: 1.3;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.card-sub { font-size: .75rem; color: var(--muted); margin-top: 4px; }
.card-rating { color: var(--gold); font-size: .78rem; font-weight: 600; }

/* ── DETAIL PAGE ── */
.detail-wrap { padding: 40px 56px; }
.detail-grid { display: grid; grid-template-columns: 260px 1fr; gap: 48px; }
.detail-poster { border-radius: 10px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,.7); }
.detail-poster img { width: 100%; display: block; }
.detail-title {
  font-family: 'Cinzel', serif; font-size: clamp(1.8rem,3.5vw,3rem);
  font-weight: 900; margin: 0 0 12px; color: #fff;
}
.detail-tagline {
  font-family: 'Cinzel', serif; font-size: .85rem;
  color: var(--gold); letter-spacing: .2em; text-transform: uppercase;
  margin-bottom: 20px;
}
.stat-row { display: flex; gap: 32px; flex-wrap: wrap; margin-bottom: 20px; }
.stat-item { display: flex; flex-direction: column; }
.stat-label { font-size: .7rem; letter-spacing: .12em; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
.stat-value { font-family: 'Nunito Sans', sans-serif; font-weight: 700; font-size: 1.05rem; }
.stat-value.green { color: var(--green); }
.stat-value.red   { color: var(--red); }
.stat-value.gold  { color: var(--gold); }

/* ── VIDEO / IMAGES ── */
.video-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.video-frame { border-radius: 8px; overflow: hidden; background: #000; aspect-ratio: 16/9; }
.video-frame iframe { width: 100%; height: 100%; border: none; display: block; }

.scenes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
.scene-img { border-radius: 6px; overflow: hidden; aspect-ratio: 16/9; }
.scene-img img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform .3s; }
.scene-img:hover img { transform: scale(1.05); }

/* ── CAST ── */
.cast-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 16px; }
.cast-card {
  background: var(--card); border-radius: 8px; overflow: hidden; text-align: center;
  transition: transform .2s;
}
.cast-card:hover { transform: translateY(-4px); }
.cast-photo { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; background: var(--card2); }
.cast-photo-placeholder {
  width: 100%; aspect-ratio: 2/3;
  background: var(--card2); display: flex; align-items: center;
  justify-content: center; font-size: 2.5rem;
}
.cast-name { font-size: .82rem; font-weight: 700; padding: 8px 8px 2px; }
.cast-char { font-size: .72rem; color: var(--muted); padding: 0 8px 10px; }

/* ── DIRECTOR ── */
.director-card {
  display: flex; align-items: center; gap: 24px;
  background: var(--card2); border-radius: 10px; padding: 20px 24px;
  max-width: 480px;
}
.director-photo { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.director-info .label { font-size: .7rem; letter-spacing: .15em; text-transform: uppercase; color: var(--muted); }
.director-info .name  { font-family: 'Cinzel', serif; font-size: 1.2rem; font-weight: 700; color: var(--gold2); }

/* ── SEARCH ── */
.search-wrap { padding: 24px 56px 0; }

/* ── TABS (custom) ── */
.tabs-row { display: flex; gap: 0; margin-bottom: 28px; border-bottom: 1px solid rgba(255,255,255,.1); }
.tab-btn {
  font-family: 'Nunito Sans', sans-serif; font-size: .88rem; font-weight: 600;
  color: var(--muted); background: transparent; border: none; border-bottom: 2px solid transparent;
  padding: 10px 22px; cursor: pointer; transition: color .2s, border-color .2s;
  letter-spacing: .04em;
}
.tab-btn.active { color: var(--gold); border-bottom-color: var(--gold); }

/* ── REVIEWS ── */
.review-card {
  background: var(--card2); border-radius: 8px; padding: 20px 24px; margin-bottom: 14px;
}
.review-author { font-weight: 700; font-size: .9rem; margin-bottom: 6px; }
.review-body { font-size: .87rem; line-height: 1.7; color: rgba(232,224,208,.8); }

/* ── SIMILAR ── */
.similar-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(150px,1fr)); gap: 14px;
}

/* ── SEARCH INPUT ── */
div[data-testid="stTextInput"] input {
  background: var(--card2) !important;
  border: 1px solid rgba(201,168,76,.3) !important;
  color: var(--text) !important;
  border-radius: 6px !important;
  font-family: 'Nunito Sans', sans-serif !important;
}

/* ── MISC ── */
.divider { height: 1px; background: rgba(255,255,255,.07); margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "page"         not in st.session_state: st.session_state.page         = "home"
if "selected_id"  not in st.session_state: st.session_state.selected_id  = None
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "detail_tab"   not in st.session_state: st.session_state.detail_tab   = "Overview"

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lumora-nav">
  <span class="lumora-logo">LUMORA</span>
  <nav class="nav-links">
    <a href="#" class="active">Browse</a>
    <a href="#">Movies</a>
    <a href="#">Series</a>
    <a href="#">My List</a>
  </nav>
</div>
""", unsafe_allow_html=True)

# ── SEARCH BAR ────────────────────────────────────────────────────────────────
with st.container():
    st.markdown('<div class="search-wrap">', unsafe_allow_html=True)
    query = st.text_input("", placeholder="🔍  Search movies…", key="search_input",
                          label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

if query:
    st.session_state.search_query = query
    st.session_state.page = "search"
elif st.session_state.search_query and not query:
    st.session_state.page = "home"
    st.session_state.search_query = ""

# ────────────────────────────────────────────────────────────────────────────
#  PAGE: DETAIL
# ────────────────────────────────────────────────────────────────────────────
def show_detail(movie_id):
    d = get_movie_details(movie_id)
    if not d:
        st.error("Could not load movie details.")
        return

    # ── Hero backdrop ──
    backdrop = d.get("backdrop_path", "")
    if backdrop:
        bg_url = f"{IMG_BASE}/original{backdrop}"
        st.markdown(f"""
        <div class="hero-wrap">
          <div class="hero-bg" style="background-image:url('{bg_url}')"></div>
          <div class="hero-gradient"></div>
          <div class="hero-content">
            <div class="hero-tagline">{d.get('tagline','')}</div>
            <h1 class="hero-title">{d.get('title','')}</h1>
            <div class="hero-meta">
              <span class="hero-rating">★ {d.get('vote_average',0):.1f}</span>
              <span class="hero-votes">({d.get('vote_count',0):,} votes)</span>
              <span class="hero-year">{(d.get('release_date','') or '')[:4]}</span>
              <span>·</span>
              <span class="hero-runtime">{d.get('runtime',0)} min</span>
            </div>
            <div class="hero-genres">
              {''.join(f'<span class="genre-badge">{g["name"]}</span>' for g in d.get("genres",[]))}
            </div>
            <p class="hero-overview">{d.get('overview','')}</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Back button ──
    st.markdown('<div class="detail-wrap">', unsafe_allow_html=True)
    if st.button("← Back", key="back_btn"):
        st.session_state.page = "home"
        st.session_state.selected_id = None
        st.rerun()

    # ── TABS ──
    tabs = ["Overview", "Trailer & Videos", "Scenes", "Cast & Crew", "Reviews", "Similar"]
    cols = st.columns(len(tabs))
    for i, t in enumerate(tabs):
        if cols[i].button(t, key=f"tab_{t}",
                          type="primary" if st.session_state.detail_tab == t else "secondary"):
            st.session_state.detail_tab = t
            st.rerun()

    tab = st.session_state.detail_tab
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── OVERVIEW ──
    if tab == "Overview":
        poster_path = d.get("poster_path","")
        col_poster, col_info = st.columns([1, 2.5])
        with col_poster:
            if poster_path:
                st.markdown(f'<div class="detail-poster"><img src="{poster_url(poster_path)}"></div>',
                            unsafe_allow_html=True)
        with col_info:
            st.markdown(f'<h1 class="detail-title">{d.get("title","")}</h1>', unsafe_allow_html=True)
            if d.get("tagline"):
                st.markdown(f'<div class="detail-tagline">{d["tagline"]}</div>', unsafe_allow_html=True)

            # Stats — BUG FIX: fmt_money now properly defined above
            budget  = d.get("budget")
            revenue = d.get("revenue")
            profit  = (revenue - budget) if revenue and budget else None
            profit_str = fmt_money(profit)
            profit_class = "green" if profit and profit > 0 else "red" if profit else ""

            st.markdown(f"""
            <div class="stat-row">
              <div class="stat-item">
                <span class="stat-label">Rating</span>
                <span class="stat-value gold">★ {d.get('vote_average',0):.1f} / 10</span>
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
                <span class="stat-value {profit_class}">{profit_str}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-family:'Nunito Sans',sans-serif;line-height:1.8;color:rgba(232,224,208,.9);max-width:700px;">
              {d.get('overview','')}
            </div>
            """, unsafe_allow_html=True)

            # Genres
            genres = " ".join(f'<span class="genre-badge">{g["name"]}</span>'
                              for g in d.get("genres", []))
            st.markdown(f'<div class="hero-genres" style="margin-top:18px">{genres}</div>',
                        unsafe_allow_html=True)

            # Production companies
            comps = ", ".join(c["name"] for c in d.get("production_companies", [])[:4])
            if comps:
                st.markdown(f"""
                <div style="margin-top:16px;font-size:.84rem;color:var(--muted)">
                  <span style="letter-spacing:.1em;text-transform:uppercase;font-size:.7rem">Studio</span><br>
                  <span style="color:var(--text);font-weight:600">{comps}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── TRAILER & VIDEOS ──
    elif tab == "Trailer & Videos":
        st.markdown('<div class="section-title">Trailers & Videos</div>', unsafe_allow_html=True)
        videos = d.get("videos", {}).get("results", [])
        trailers = [v for v in videos if v.get("site") == "YouTube"]
        if not trailers:
            st.info("No trailers available for this title.")
        else:
            # Sort: official trailers first
            trailers.sort(key=lambda v: (v.get("type","") != "Trailer", v.get("official","") == False))
            st.markdown('<div class="video-grid">', unsafe_allow_html=True)
            for v in trailers[:8]:
                st.markdown(f"""
                <div>
                  <div class="video-frame">
                    <iframe src="{youtube_embed(v['key'])}" allowfullscreen></iframe>
                  </div>
                  <div style="margin-top:8px;font-size:.82rem;color:var(--muted)">{v.get('type','')} · {v.get('name','')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── SCENES (backdrops) ──
    elif tab == "Scenes":
        st.markdown('<div class="section-title">Scenes from the Film</div>', unsafe_allow_html=True)
        images   = d.get("images", {})
        backdrops = images.get("backdrops", [])
        stills   = images.get("posters", [])
        all_imgs  = backdrops[:20] + stills[:5]
        if not all_imgs:
            st.info("No scene images available.")
        else:
            st.markdown('<div class="scenes-grid">', unsafe_allow_html=True)
            for img in all_imgs:
                path = img.get("file_path","")
                if path:
                    st.markdown(f"""
                    <div class="scene-img">
                      <img src="{IMG_BASE}/w780{path}" loading="lazy">
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── CAST & CREW ──
    elif tab == "Cast & Crew":
        credits = d.get("credits", {})
        cast    = credits.get("cast", [])
        crew    = credits.get("crew", [])

        # Director(s)
        directors = [c for c in crew if c.get("job") == "Director"]
        if directors:
            st.markdown('<div class="section-title">Director</div>', unsafe_allow_html=True)
            for dr in directors:
                ph = profile_url(dr.get("profile_path",""))
                photo_html = f'<img class="director-photo" src="{ph}">' if ph else \
                             '<div class="director-photo" style="background:var(--card2);display:flex;align-items:center;justify-content:center;font-size:2rem;">🎬</div>'
                st.markdown(f"""
                <div class="director-card">
                  {photo_html}
                  <div class="director-info">
                    <div class="label">Director</div>
                    <div class="name">{dr.get('name','')}</div>
                    <div style="font-size:.8rem;color:var(--muted);margin-top:4px">{dr.get('department','')}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Key crew
        key_jobs = ["Producer", "Executive Producer", "Screenplay", "Writer",
                    "Director of Photography", "Original Music Composer"]
        key_crew = [c for c in crew if c.get("job") in key_jobs][:8]
        if key_crew:
            st.markdown('<div class="section-title" style="margin-top:32px">Key Crew</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="cast-grid">', unsafe_allow_html=True)
            for c in key_crew:
                ph = profile_url(c.get("profile_path",""))
                st.markdown(f"""
                <div class="cast-card">
                  {"<img class='cast-photo' src='" + ph + "'>" if ph else "<div class='cast-photo-placeholder'>🎥</div>"}
                  <div class="cast-name">{c.get('name','')}</div>
                  <div class="cast-char">{c.get('job','')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Full cast
        if cast:
            st.markdown('<div class="section-title" style="margin-top:36px">Full Cast</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="cast-grid">', unsafe_allow_html=True)
            for c in cast[:30]:
                ph = profile_url(c.get("profile_path",""))
                st.markdown(f"""
                <div class="cast-card">
                  {"<img class='cast-photo' src='" + ph + "'>" if ph else "<div class='cast-photo-placeholder'>👤</div>"}
                  <div class="cast-name">{c.get('name','')}</div>
                  <div class="cast-char">{c.get('character','')}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── REVIEWS ──
    elif tab == "Reviews":
        st.markdown('<div class="section-title">Audience Reviews</div>', unsafe_allow_html=True)
        reviews = d.get("reviews", {}).get("results", [])
        if not reviews:
            st.info("No reviews yet.")
        for rv in reviews[:6]:
            rating_val = rv.get("author_details", {}).get("rating")
            rating_str = f"★ {rating_val}/10" if rating_val else ""
            content    = rv.get("content","")[:600]
            st.markdown(f"""
            <div class="review-card">
              <div class="review-author">{rv.get('author','')}
                <span style="color:var(--gold);font-size:.82rem;margin-left:10px">{rating_str}</span>
              </div>
              <div class="review-body">{content}{'…' if len(rv.get('content','')) > 600 else ''}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── SIMILAR ──
    elif tab == "Similar":
        st.markdown('<div class="section-title">You Might Also Like</div>', unsafe_allow_html=True)
        similar = d.get("similar", {}).get("results", [])[:12]
        if not similar:
            st.info("No similar titles found.")
        else:
            _render_card_grid(similar)

    st.markdown('</div>', unsafe_allow_html=True)  # detail-wrap


# ────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ────────────────────────────────────────────────────────────────────────────
def _render_card_grid(movies):
    """Render a grid of movie cards with click buttons."""
    cols = st.columns(min(len(movies), 6))
    for i, m in enumerate(movies):
        with cols[i % 6]:
            p = m.get("poster_path", "")
            img_html = (f'<img src="{poster_url(p)}" style="width:100%;border-radius:6px 6px 0 0">'
                        if p else '<div class="movie-card-no-img">🎬</div>')
            year = (m.get("release_date","") or "")[:4]
            rating = m.get("vote_average", 0)
            st.markdown(f"""
            <div style="background:var(--card);border-radius:8px;overflow:hidden;margin-bottom:4px">
              {img_html}
              <div style="padding:8px 10px 12px">
                <div style="font-weight:700;font-size:.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{m.get('title','')}</div>
                <div style="font-size:.74rem;color:var(--muted);margin-top:3px">★ {rating:.1f} · {year}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View", key=f"card_{m['id']}_{i}"):
                st.session_state.selected_id = m["id"]
                st.session_state.page = "detail"
                st.session_state.detail_tab = "Overview"
                st.rerun()


def _render_hero(movie):
    """Render the big hero section for the top trending movie."""
    backdrop = movie.get("backdrop_path","")
    bg_url   = f"{IMG_BASE}/original{backdrop}" if backdrop else ""
    title    = movie.get("title","")
    tagline  = movie.get("tagline","Now Streaming")
    overview = movie.get("overview","")[:280]
    year     = (movie.get("release_date","") or "")[:4]
    rating   = movie.get("vote_average",0)
    votes    = movie.get("vote_count",0)
    genres   = " ".join(f'<span class="genre-badge">{g["name"]}</span>'
                        for g in movie.get("genres",[])[:3])
    runtime  = movie.get("runtime", 0)

    st.markdown(f"""
    <div class="hero-wrap">
      <div class="hero-bg" style="background-image:url('{bg_url}')"></div>
      <div class="hero-gradient"></div>
      <div class="hero-content">
        <div class="hero-tagline">{tagline or 'Now Streaming'}</div>
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
    </div>
    """, unsafe_allow_html=True)

    if st.button("▶ Watch Trailer", key="hero_trailer"):
        st.session_state.selected_id = movie["id"]
        st.session_state.page = "detail"
        st.session_state.detail_tab = "Trailer & Videos"
        st.rerun()
    if st.button("+ More Info", key="hero_info"):
        st.session_state.selected_id = movie["id"]
        st.session_state.page = "detail"
        st.session_state.detail_tab = "Overview"
        st.rerun()


def _section(title, movies):
    st.markdown(f'<div class="section-wrap"><div class="section-title">{title}</div>', unsafe_allow_html=True)
    _render_card_grid(movies)
    st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────────
#  MAIN ROUTER
# ────────────────────────────────────────────────────────────────────────────
if not TMDB_API_KEY:
    st.warning("""
    ⚠️ **TMDB API key not set.**

    Add your key to Streamlit secrets:
    ```toml
    # .streamlit/secrets.toml
    TMDB_API_KEY = "your_api_key_here"
    ```
    Get a free key at [themoviedb.org](https://www.themoviedb.org/settings/api).
    """)
    st.stop()

page = st.session_state.page

# ── DETAIL PAGE ──
if page == "detail" and st.session_state.selected_id:
    show_detail(st.session_state.selected_id)

# ── SEARCH RESULTS ──
elif page == "search":
    results = search_movies(st.session_state.search_query)
    st.markdown(f'<div class="section-wrap"><div class="section-title">Search: "{st.session_state.search_query}"</div>',
                unsafe_allow_html=True)
    if results:
        _render_card_grid(results[:12])
    else:
        st.info("No results found.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── HOME ──
else:
    trending = get_trending()
    popular  = get_popular()
    top      = get_top_rated()

    if trending:
        # Hero = first trending, with full details for runtime/tagline
        hero_movie = get_movie_details(trending[0]["id"])
        _render_hero(hero_movie if hero_movie else trending[0])

    _section("🔥 Trending This Week",  trending)
    _section("🎬 Popular Right Now",   popular)
    _section("⭐ Top Rated All Time",  top)
