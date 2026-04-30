import streamlit as st
import requests

# ================= CONFIG =================
TMDB_API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="LUMORA", layout="wide")

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True   # keep auto login for now
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "page" not in st.session_state:
    st.session_state.page = "home"
if "movie_id" not in st.session_state:
    st.session_state.movie_id = None

# ================= API =================
def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    return requests.get(url).json()

def get_movie(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

def get_credits(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

def get_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    for v in data.get("results", []):
        if v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def get_recommendations(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

def get_person_movies(person_id):
    url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

# ================= SIDEBAR =================
menu = st.sidebar.radio("Menu", ["Home", "Watchlist"])

if menu == "Watchlist":
    st.title("❤️ Watchlist")
    cols = st.columns(5)

    for i, m_id in enumerate(st.session_state.watchlist):
        data = get_movie(m_id)
        with cols[i % 5]:
            if data.get("poster_path"):
                st.image(BASE_IMG + data["poster_path"])
            st.write(data["title"])

            if st.button("Open", key=f"wl_{m_id}"):
                st.session_state.movie_id = m_id
                st.session_state.page = "movie"
                st.rerun()

# ================= HOME =================
if st.session_state.page == "home":
    st.title("🎬 LUMORA")

    query = st.text_input("🔍 Search movie")

    if query:
        results = search_movie(query)

        if results.get("results"):
            cols = st.columns(5)

            for i, movie in enumerate(results["results"][:10]):
                with cols[i % 5]:
                    if movie.get("poster_path"):
                        st.image(BASE_IMG + movie["poster_path"])

                    st.write(movie["title"])

                    if st.button("View", key=f"search_{movie['id']}"):
                        st.session_state.movie_id = movie["id"]
                        st.session_state.page = "movie"
                        st.rerun()

# ================= MOVIE PAGE =================
if st.session_state.page == "movie":

    movie_id = st.session_state.movie_id
    data = get_movie(movie_id)
    credits = get_credits(movie_id)

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()

    col1, col2 = st.columns([1, 2])

    with col1:
        if data.get("poster_path"):
            st.image(BASE_IMG + data["poster_path"])

    with col2:
        st.subheader(data.get("title"))
        st.write(f"⭐ {data.get('vote_average')}")
        st.write(data.get("overview"))
        st.write(f"💰 ${data.get('revenue', 0):,}")

        if st.button("❤️ Add to Watchlist"):
            if movie_id not in st.session_state.watchlist:
                st.session_state.watchlist.append(movie_id)

    # ===== TRAILER =====
    trailer = get_trailer(movie_id)
    if trailer:
        st.markdown("## 🎬 Trailer")
        st.video(trailer)

    # ===== CAST =====
    st.markdown("## 🎭 Cast")
    cast = credits.get("cast", [])[:10]

    cols = st.columns(5)
    for i, actor in enumerate(cast):
        with cols[i % 5]:
            if actor.get("profile_path"):
                st.image(BASE_IMG + actor["profile_path"])
            st.write(actor["name"])

    # ===== DIRECTOR =====
    director = None
    for c in credits.get("crew", []):
        if c["job"] == "Director":
            director = c
            break

    if director:
        st.markdown(f"## 🎬 Director: {director['name']}")
        movies = get_person_movies(director["id"])

        cols = st.columns(5)
        for i, m in enumerate(movies.get("crew", [])[:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(BASE_IMG + m["poster_path"])
                st.write(m.get("title"))

    # ===== RECOMMENDATIONS =====
    st.markdown("## 🎯 Recommended")

    rec = get_recommendations(movie_id)

    if rec.get("results"):
        cols = st.columns(5)

        for i, m in enumerate(rec["results"][:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(BASE_IMG + m["poster_path"])

                st.write(m["title"])

                if st.button("View", key=f"rec_{m['id']}"):
                    st.session_state.movie_id = m["id"]
                    st.session_state.page = "movie"
                    st.rerun()
