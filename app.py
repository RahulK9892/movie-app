import streamlit as st
import requests

# ================= CONFIG =================
st.set_page_config(page_title="LUMORA", layout="wide")

# 🔐 Use Streamlit Secrets (see instructions below)
TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ================= STYLE =================
st.markdown("""
<style>
body {background-color:#0b0f19;}

.title {
    font-size:42px;
    font-weight:bold;
    color:#00f5ff;
}

.movie-card {
    transition: 0.3s;
    border-radius: 12px;
}
.movie-card:hover {
    transform: scale(1.08);
    box-shadow: 0 0 20px #00f5ff;
}

.sidebar-card {
    background: rgba(255,255,255,0.05);
    padding:10px;
    border-radius:10px;
    margin-bottom:10px;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.markdown('<div class="title">🎬 LUMORA Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid login")

    st.stop()

# ================= SIDEBAR =================
st.sidebar.title("🎛 Menu")
menu = st.sidebar.radio("", ["Home", "Watchlist", "Logout"])

# Watchlist UI (improved)
st.sidebar.markdown("## ❤️ Watchlist")
if st.session_state.watchlist:
    for movie in st.session_state.watchlist:
        st.sidebar.markdown(f'<div class="sidebar-card">{movie}</div>', unsafe_allow_html=True)
else:
    st.sidebar.write("Empty")

if menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.session_state.selected_movie = None
    st.rerun()

# ================= FUNCTIONS =================
def fetch(url):
    try:
        return requests.get(url, timeout=5).json()
    except:
        return {}

def search_movie(query):
    return fetch(f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}").get("results", [])

def get_movie(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}")

def get_cast(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}")

def get_trailer(movie_id):
    data = fetch(f"{BASE_URL}/movie/{movie_id}/videos?api_key={TMDB_API_KEY}")
    for v in data.get("results", []):
        if v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def get_recommendations(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}").get("results", [])[:10]

def get_trending():
    return fetch(f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}").get("results", [])[:10]

def format_money(amount):
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.2f} Billion"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.2f} Million"
    elif amount > 0:
        return f"${amount:,}"
    return "Not Available"

# ================= HOME =================
if menu == "Home":
    st.markdown('<div class="title">🎬 LUMORA</div>', unsafe_allow_html=True)

    query = st.text_input("🔍 Search movie")

    # ===== SEARCH =====
    if query:
        with st.spinner("Searching..."):
            results = search_movie(query)

        cols = st.columns(5)
        for i, movie in enumerate(results[:10]):
            with cols[i % 5]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if movie.get("poster_path"):
                    st.image(IMG_URL + movie["poster_path"])
                st.write(movie["title"])
                if st.button("View", key=f"s_{movie['id']}"):
                    st.session_state.selected_movie = movie["id"]
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # ===== TRENDING =====
    st.markdown("## 🔥 Trending")
    with st.spinner("Loading trending..."):
        trending = get_trending()

    cols = st.columns(5)
    for i, movie in enumerate(trending):
        with cols[i % 5]:
            if movie.get("poster_path"):
                st.image(IMG_URL + movie["poster_path"])
            if st.button("Open", key=f"t_{movie['id']}"):
                st.session_state.selected_movie = movie["id"]
                st.rerun()

# ================= WATCHLIST PAGE =================
elif menu == "Watchlist":
    st.title("❤️ Your Watchlist")
    if not st.session_state.watchlist:
        st.write("No movies yet")
    else:
        for m in st.session_state.watchlist:
            st.write("🎬", m)

# ================= MOVIE DETAILS =================
if st.session_state.selected_movie:
    movie_id = st.session_state.selected_movie

    with st.spinner("Loading movie details..."):
        data = get_movie(movie_id)
        cast_data = get_cast(movie_id)

    st.button("⬅ Back", on_click=lambda: st.session_state.update(selected_movie=None))

    col1, col2 = st.columns([1,2])

    with col1:
        if data.get("poster_path"):
            st.image(IMG_URL + data["poster_path"])

    with col2:
        st.title(data.get("title"))
        st.write(f"⭐ {data.get('vote_average')}")
        st.write(data.get("overview"))

        if st.button("❤️ Add to Watchlist"):
            if data["title"] not in st.session_state.watchlist:
                st.session_state.watchlist.append(data["title"])
                st.success("Added!")

    # ===== BOX OFFICE =====
    st.markdown("## 💰 Box Office & Budget")
    revenue = data.get("revenue", 0)
    budget = data.get("budget", 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("🌍 Box Office", format_money(revenue))
    c2.metric("🎬 Budget", format_money(budget))
    c3.metric("📈 Profit", format_money(revenue - budget if revenue and budget else 0))

    # ===== TRAILER =====
    trailer = get_trailer(movie_id)
    if trailer:
        st.markdown("## 🎬 Trailer")
        st.video(trailer)

    # ===== CAST =====
    st.markdown("## 🎭 Cast")
    cols = st.columns(5)
    for i, actor in enumerate(cast_data.get("cast", [])[:10]):
        with cols[i % 5]:
            if actor.get("profile_path"):
                st.image(IMG_URL + actor["profile_path"])
            st.caption(actor["name"])

    # ===== RECOMMENDATIONS =====
    st.markdown("## 🎯 Recommended")
    recs = get_recommendations(movie_id)

    cols = st.columns(5)
    for i, movie in enumerate(recs):
        with cols[i % 5]:
            if movie.get("poster_path"):
                st.image(IMG_URL + movie["poster_path"])
            if st.button("View", key=f"r_{movie['id']}"):
                st.session_state.selected_movie = movie["id"]
                st.rerun()
