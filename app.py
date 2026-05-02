import streamlit as st
import requests
import os

# ================= CONFIG =================
st.set_page_config(page_title="LUMORA", layout="wide", page_icon="🎬")

TMDB_API_KEY = st.secrets.get("TMDB_API_KEY") or os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
BACKDROP = "https://image.tmdb.org/t/p/w780"

# ================= API =================
@st.cache_data(ttl=3600)
def fetch(url):
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        return res.json()
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
        if v.get("type") == "Trailer" and v.get("site") == "YouTube":
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
query = st.text_input("🔍 Search movie...")

# ================= HOME =================
if st.session_state.page == "home":

    # 🔍 SEARCH
    if query:
        results = search_movie(query)
        st.subheader("Results")

        cols = st.columns(5)
        for i, m in enumerate(results.get("results", [])[:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(IMG + m["poster_path"])
                st.write(m.get("title"))

                if st.button("🎬 View", key=f"search_{m['id']}"):
                    st.session_state.movie_id = m["id"]
                    st.session_state.page = "details"
                    st.rerun()

    # 🔥 TRENDING
    st.subheader("🔥 Trending")
    trending = get_trending()

    cols = st.columns(6)
    for i, m in enumerate(trending.get("results", [])[:12]):
        with cols[i % 6]:
            if m.get("poster_path"):
                st.image(IMG + m["poster_path"])
            st.write(m.get("title"))

            if st.button("🎬 View", key=f"trend_{m['id']}"):
                st.session_state.movie_id = m["id"]
                st.session_state.page = "details"
                st.rerun()

    # ❤️ WATCHLIST
    if st.session_state.watchlist:
        st.subheader("❤️ Watchlist")
        cols = st.columns(6)

        for i, m in enumerate(st.session_state.watchlist):
            with cols[i % 6]:
                if m.get("poster"):
                    st.image(IMG + m["poster"])
                st.write(m["title"])

# ================= DETAILS =================
elif st.session_state.page == "details":

    movie_id = st.session_state.movie_id

    data = get_details(movie_id)
    credits = get_credits(movie_id)
    trailer = get_trailer(movie_id)
    images = get_images(movie_id)

    if not data:
        st.error("Movie not found")
        st.stop()

    col1, col2 = st.columns([1, 2])

    with col1:
        if data.get("poster_path"):
            st.image(IMG + data["poster_path"])

    with col2:
        st.title(data.get("title"))

        st.write("⭐", data.get("vote_average"))

        genres = ", ".join([g["name"] for g in data.get("genres", [])])
        st.write(genres)

        st.write(data.get("overview"))

        # 🎭 Top Cast
        top_cast = ", ".join([c["name"] for c in credits.get("cast", [])[:3]])
        st.write("🎭 Cast:", top_cast)

        # ❤️ Watchlist
        if st.button("❤️ Add to Watchlist"):
            if not any(w["title"] == data.get("title") for w in st.session_state.watchlist):
                st.session_state.watchlist.append({
                    "title": data.get("title"),
                    "poster": data.get("poster_path")
                })
            st.rerun()

    # 🎬 TRAILER
    if trailer:
        st.subheader("🎬 Trailer")
        st.video(trailer)

    # 🖼️ SCENES
    backdrops = images.get("backdrops", [])
    if backdrops:
        st.subheader("Scenes")
        cols = st.columns(3)
        for i, img in enumerate(backdrops[:6]):
            with cols[i % 3]:
                st.image(BACKDROP + img["file_path"])

    # 🎯 RECOMMENDATIONS
    rec = get_recommendations(movie_id)
    if rec.get("results"):
        st.subheader("🎯 Recommended")

        cols = st.columns(6)
        for i, m in enumerate(rec.get("results", [])[:12]):
            with cols[i % 6]:
                if m.get("poster_path"):
                    st.image(IMG + m["poster_path"])
                st.write(m.get("title"))

                # ✅ NEW VIEW BUTTON
                if st.button("🎬 View", key=f"rec_view_{m['id']}"):
                    st.session_state.movie_id = m["id"]
                    st.rerun()

    # ⬅ BACK
    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()
