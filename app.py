import streamlit as st
import requests

# ================= CONFIG =================
TMDB_API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"

st.set_page_config(page_title="LUMORA", layout="wide")

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ================= CSS =================
st.markdown("""
<style>
body {background-color:#0b0f19;}
.title {font-size:40px;font-weight:bold;color:#00f5ff;}
.card {background:rgba(255,255,255,0.05);padding:10px;border-radius:15px;
       transition:0.3s;text-align:center;}
.card:hover {transform:scale(1.05);box-shadow:0 0 15px #00f5ff;}
</style>
""", unsafe_allow_html=True)

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

def get_actor_movies(person_id):
    url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits?api_key={TMDB_API_KEY}"
    return requests.get(url).json()

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.markdown('<div class="title">🎬 LUMORA</div>', unsafe_allow_html=True)
    st.subheader("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user and pwd:
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# ================= SIDEBAR =================
menu = st.sidebar.radio("Menu", ["Home", "Watchlist", "Logout"])

if menu == "Logout":
    st.session_state.logged_in = False
    st.rerun()

# ================= WATCHLIST =================
if menu == "Watchlist":
    st.title("❤️ Your Watchlist")

    if not st.session_state.watchlist:
        st.info("Empty watchlist")
    else:
        cols = st.columns(5)
        for i, movie_id in enumerate(st.session_state.watchlist):
            data = get_movie(movie_id)
            with cols[i % 5]:
                if data.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w500{data['poster_path']}")
                st.write(data["title"])
    st.stop()

# ================= HEADER =================
st.markdown('<div class="title">🎬 LUMORA</div>', unsafe_allow_html=True)

query = st.text_input("🔍 Search movie")

# ================= SEARCH RESULTS =================
if query:
    results = search_movie(query)

    if results.get("results"):
        cols = st.columns(5)

        for i, movie in enumerate(results["results"][:10]):
            with cols[i % 5]:
                if movie.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}")
                st.write(movie["title"])

                if st.button("View", key=movie["id"]):
                    st.session_state.selected_movie = movie["id"]
                    st.rerun()

# ================= MOVIE PAGE =================
if st.session_state.selected_movie:

    movie_id = st.session_state.selected_movie
    data = get_movie(movie_id)
    credits = get_credits(movie_id)

    st.button("⬅ Back", on_click=lambda: st.session_state.update({"selected_movie": None}))

    col1, col2 = st.columns([1, 2])

    with col1:
        if data.get("poster_path"):
            st.image(f"https://image.tmdb.org/t/p/w500{data['poster_path']}")

    with col2:
        st.subheader(data["title"])
        st.write(f"⭐ {data.get('vote_average')}")
        st.write(data.get("overview"))
        st.write(f"💰 ${data.get('revenue', 0):,}")

        if st.button("❤️ Add to Watchlist"):
            if movie_id not in st.session_state.watchlist:
                st.session_state.watchlist.append(movie_id)

    # ================= TRAILER =================
    trailer = get_trailer(movie_id)
    if trailer:
        st.markdown("## 🎬 Trailer")
        st.video(trailer)

    # ================= CAST =================
    st.markdown("## 🎭 Cast")
    cast = credits.get("cast", [])[:10]

    cols = st.columns(5)
    for i, actor in enumerate(cast):
        with cols[i % 5]:
            if actor.get("profile_path"):
                st.image(f"https://image.tmdb.org/t/p/w500{actor['profile_path']}")
            st.write(actor["name"])

    # ================= DIRECTOR =================
    director = None
    for c in credits.get("crew", []):
        if c["job"] == "Director":
            director = c
            break

    if director:
        st.markdown(f"## 🎬 Director: {director['name']}")

        movies = get_actor_movies(director["id"])
        cols = st.columns(5)

        for i, m in enumerate(movies.get("crew", [])[:10]):
            if m.get("poster_path"):
                with cols[i % 5]:
                    st.image(f"https://image.tmdb.org/t/p/w500{m['poster_path']}")
                    st.write(m["title"])

    # ================= RECOMMENDATIONS =================
    st.markdown("## 🎯 Recommended")

    rec = get_recommendations(movie_id)

    if rec.get("results"):
        cols = st.columns(5)

        for i, m in enumerate(rec["results"][:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w500{m['poster_path']}")
                st.write(m["title"])

                if st.button("View", key=f"rec_{m['id']}"):
                    st.session_state.selected_movie = m["id"]
                    st.rerun()

    # ================= ACTOR MOVIES =================
    st.markdown("## 🎭 More from Cast")

    for actor in cast[:2]:
        st.markdown(f"### {actor['name']}")
        movies = get_actor_movies(actor["id"])

        cols = st.columns(5)
        for i, m in enumerate(movies.get("cast", [])[:5]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w500{m['poster_path']}")
                st.write(m["title"])
