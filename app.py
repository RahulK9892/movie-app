import streamlit as st
import requests

# ================= CONFIG =================
TMDB_API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE_URL = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
BACKDROP = "https://image.tmdb.org/t/p/original"

st.set_page_config(page_title="CineScope", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
body {background-color:#0b0f19;}
.title {font-size:45px;font-weight:bold;color:#00f5ff;}
.subtitle {color:#aaa;}
.card {
    transition:0.3s;
}
.card:hover {
    transform:scale(1.08);
}
.section {
    font-size:26px;
    margin-top:25px;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ================= API =================
def fetch(url):
    try:
        return requests.get(url, timeout=5).json()
    except:
        return None

def trending():
    return fetch(f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}")

def search_movie(q):
    return fetch(f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={q}")

def get_movie(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}")

def get_credits(movie_id):
    return fetch(f"{BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}")

def get_trailer(movie_id):
    data = fetch(f"{BASE_URL}/movie/{movie_id}/videos?api_key={TMDB_API_KEY}")
    if data:
        for vid in data["results"]:
            if vid["type"] == "Trailer" and vid["site"] == "YouTube":
                return vid["key"]
    return None

# ================= HEADER =================
st.markdown('<div class="title">🎬 CineScope</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Netflix-style movie explorer</div>', unsafe_allow_html=True)

# ================= HERO (NETFLIX STYLE) =================
trend = trending()

if trend and trend.get("results"):
    hero = trend["results"][0]

    if hero.get("backdrop_path"):
        st.image(BACKDROP + hero["backdrop_path"], use_container_width=True)

    st.markdown(f"## {hero['title']}")
    st.write(hero["overview"][:200] + "...")

    if st.button("▶️ Play Trailer"):
        trailer = get_trailer(hero["id"])
        if trailer:
            st.video(f"https://www.youtube.com/watch?v={trailer}")

# ================= SEARCH =================
st.markdown("---")
query = st.text_input("🔍 Search movies")

if query:
    data = search_movie(query)

    if data and data.get("results"):
        st.markdown('<div class="section">Search Results</div>', unsafe_allow_html=True)

        cols = st.columns(5)

        for i, movie in enumerate(data["results"][:10]):
            with cols[i % 5]:
                if movie.get("poster_path"):
                    st.image(IMG + movie["poster_path"])

                if st.button(movie["title"], key=i):
                    movie_id = movie["id"]
                    details = get_movie(movie_id)
                    credits = get_credits(movie_id)

                    st.markdown("---")
                    col1, col2 = st.columns([1,2])

                    with col1:
                        if movie.get("poster_path"):
                            st.image(IMG + movie["poster_path"])

                    with col2:
                        st.markdown(f"## {movie['title']}")
                        st.write(f"⭐ {details.get('vote_average')}")
                        st.write(f"📅 {details.get('release_date')}")
                        st.write(details.get("overview"))

                        if details.get("revenue"):
                            st.write(f"💰 Box Office: ${details['revenue']:,}")

                    # TRAILER
                    trailer = get_trailer(movie_id)
                    if trailer:
                        st.video(f"https://www.youtube.com/watch?v={trailer}")

                    # DIRECTOR
                    director = next((c for c in credits["crew"] if c["job"] == "Director"), None)
                    if director:
                        st.markdown("### 🎬 Director")
                        if director.get("profile_path"):
                            st.image(IMG + director["profile_path"], width=150)
                        st.write(director["name"])

                    # CAST
                    st.markdown("### 👨‍🎤 Cast")
                    cols2 = st.columns(5)
                    for j, actor in enumerate(credits["cast"][:10]):
                        with cols2[j % 5]:
                            if actor.get("profile_path"):
                                st.image(IMG + actor["profile_path"])
                            st.caption(actor["name"])

# ================= TRENDING ROW =================
st.markdown('<div class="section">🔥 Trending Now</div>', unsafe_allow_html=True)

if trend and trend.get("results"):
    cols = st.columns(5)

    for i, movie in enumerate(trend["results"][:10]):
        with cols[i % 5]:
            if movie.get("poster_path"):
                st.image(IMG + movie["poster_path"])
            st.caption(movie["title"])
