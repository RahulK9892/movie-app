import streamlit as st
import requests

# ================= CONFIG =================
TMDB_API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE_URL = "https://api.themoviedb.org/3"
IMG_URL = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="CineScope", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
body {background-color:#0b0f19;}
.title {font-size:42px;font-weight:bold;color:#00f5ff;}
.section {font-size:24px;margin-top:30px;color:#ffffff;}
.card {
    background:rgba(255,255,255,0.05);
    padding:12px;
    border-radius:15px;
    backdrop-filter:blur(10px);
    text-align:center;
    transition:0.3s;
}
.card:hover {
    transform:translateY(-5px) scale(1.03);
    box-shadow:0 0 15px #00f5ff;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="title">🎬 CineScope</div>', unsafe_allow_html=True)
st.write("Discover movies with style ✨")

# ================= API FUNCTIONS =================
def fetch_data(url):
    try:
        res = requests.get(url, timeout=5)
        return res.json()
    except:
        return None

def search_movie(query):
    url = f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    return fetch_data(url)

def trending_movies():
    url = f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}"
    return fetch_data(url)

def movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    return fetch_data(url)

# ================= SEARCH =================
movie_name = st.text_input("🔍 Search any movie")

if st.button("Search"):
    if movie_name.strip() == "":
        st.warning("Enter a movie name")
    else:
        with st.spinner("Searching..."):
            data = search_movie(movie_name)

        if data and data.get("results"):
            movie = data["results"][0]

            st.markdown("---")
            col1, col2 = st.columns([1,2])

            with col1:
                if movie.get("poster_path"):
                    st.image(IMG_URL + movie["poster_path"])

            with col2:
                st.markdown(f"## {movie.get('title')}")
                st.write(f"⭐ Rating: {movie.get('vote_average')}")
                st.write(f"📅 Release: {movie.get('release_date')}")
                st.write(f"📝 {movie.get('overview')}")
        else:
            st.warning("No results found")

# ================= TRENDING =================
st.markdown('<div class="section">🔥 Trending</div>', unsafe_allow_html=True)

trend = trending_movies()

if trend and trend.get("results"):
    cols = st.columns(5)

    for i, movie in enumerate(trend["results"][:10]):
        with cols[i % 5]:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            if movie.get("poster_path"):
                st.image(IMG_URL + movie["poster_path"])

            st.write(movie.get("title"))
            st.caption(movie.get("release_date"))

            st.markdown('</div>', unsafe_allow_html=True)

# ================= DISCOVER =================
if movie_name:
    st.markdown('<div class="section">🎯 Discover Similar</div>', unsafe_allow_html=True)

    data = search_movie(movie_name)

    if data and data.get("results"):
        cols = st.columns(5)

        for i, movie in enumerate(data["results"][:10]):
            with cols[i % 5]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if movie.get("poster_path"):
                    st.image(IMG_URL + movie["poster_path"])

                st.write(movie.get("title"))
                st.caption(movie.get("release_date"))

                st.markdown('</div>', unsafe_allow_html=True)
