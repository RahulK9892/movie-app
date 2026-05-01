import streamlit as st
import requests

# ================= CONFIG =================
st.set_page_config(page_title="LUMORA", layout="wide")

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
BASE_URL = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"

# ================= CSS (NETFLIX STYLE) =================
st.markdown("""
<style>
body {background-color:#0b0f1a; color:white;}

.movie-card {
    transition: transform 0.3s ease;
}
.movie-card:hover {
    transform: scale(1.08);
}

.section-title {
    font-size:26px;
    font-weight:bold;
    margin-top:20px;
}

.stButton>button {
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def fetch(url):
    return requests.get(url).json()

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
        if v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def get_recommendations(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}")

# ================= SESSION =================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "movie_id" not in st.session_state:
    st.session_state.movie_id = None
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ================= HEADER =================
st.markdown("## 🎬 LUMORA")

query = st.text_input("🔍 Search movie")

# ================= LOADING =================
def loading():
    with st.spinner("Loading..."):
        pass

# ================= HOME =================
if st.session_state.page == "home":

    # ===== SEARCH RESULT =====
    if query:
        loading()
        results = search_movie(query)

        st.markdown("### 🔎 Results")
        cols = st.columns(5)

        for i, m in enumerate(results.get("results", [])[:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(IMG + m["poster_path"])
                st.write(m["title"])
                if st.button("View", key=m["id"]):
                    st.session_state.movie_id = m["id"]
                    st.session_state.page = "details"
                    st.rerun()

    # ===== TRENDING CAROUSEL =====
    st.markdown('<div class="section-title">🔥 Trending</div>', unsafe_allow_html=True)
    trending = get_trending()

    cols = st.columns(6)
    for i, m in enumerate(trending.get("results", [])[:12]):
        with cols[i % 6]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            if m.get("poster_path"):
                st.image(IMG + m["poster_path"])
            st.write(m["title"])
            if st.button("View", key=f"trend{i}"):
                st.session_state.movie_id = m["id"]
                st.session_state.page = "details"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ===== WATCHLIST =====
    if st.session_state.watchlist:
        st.markdown('<div class="section-title">❤️ Watchlist</div>', unsafe_allow_html=True)
        cols = st.columns(6)
        for i, m in enumerate(st.session_state.watchlist):
            with cols[i % 6]:
                st.image(IMG + m["poster"])
                st.write(m["title"])

# ================= DETAILS =================
elif st.session_state.page == "details":

    loading()
    movie_id = st.session_state.movie_id

    data = get_details(movie_id)
    credits = get_credits(movie_id)
    trailer = get_trailer(movie_id)

    col1, col2 = st.columns([1,2])

    with col1:
        if data.get("poster_path"):
            st.image(IMG + data["poster_path"])

    with col2:
        st.title(data.get("title"))
        st.write("⭐", data.get("vote_average"))
        st.write(data.get("overview"))

        # WATCHLIST
        if st.button("❤️ Add to Watchlist"):
            st.session_state.watchlist.append({
                "title": data["title"],
                "poster": data["poster_path"]
            })

    # ===== BOX OFFICE =====
    st.markdown("## 💰 Box Office")

    revenue = data.get("revenue", 0)
    budget = data.get("budget", 0)

    def money(x):
        if x >= 1_000_000_000:
            return f"${x/1e9:.2f}B"
        elif x >= 1_000_000:
            return f"${x/1e6:.2f}M"
        return "N/A"

    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", money(revenue))
    c2.metric("Budget", money(budget))
    c3.metric("Profit", money(revenue - budget if revenue and budget else 0))

    # ===== TRAILER =====
    if trailer:
        st.markdown("## 🎬 Trailer")
        st.video(trailer)

    # ===== CAST =====
    st.markdown("## 🎭 Cast")
    cols = st.columns(6)

    for i, c in enumerate(credits.get("cast", [])[:12]):
        with cols[i % 6]:
            if c.get("profile_path"):
                st.image(IMG + c["profile_path"])
            st.write(c["name"])

    # ===== DIRECTOR =====
    st.markdown("## 🎬 Director")
    for crew in credits.get("crew", []):
        if crew["job"] == "Director":
            st.write(crew["name"])

    # ===== RECOMMENDATIONS =====
    st.markdown("## 🎯 Recommended")

    rec = get_recommendations(movie_id)
    cols = st.columns(6)

    for i, m in enumerate(rec.get("results", [])[:12]):
        with cols[i % 6]:
            if m.get("poster_path"):
                st.image(IMG + m["poster_path"])
            st.write(m["title"])
            if st.button("View", key=f"rec{i}"):
                st.session_state.movie_id = m["id"]
                st.rerun()

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()
