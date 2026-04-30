import streamlit as st
import requests

# ================= CONFIG =================
API_KEY = "f04c0df7"
st.set_page_config(page_title="CineScope", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
body {
    background-color: #0b0f19;
}

.title {
    font-size: 42px;
    font-weight: bold;
    color: #00f5ff;
}

.section {
    font-size: 24px;
    margin-top: 30px;
    color: #ffffff;
}

.card {
    background: rgba(255,255,255,0.05);
    padding: 12px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    text-align: center;
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 0 15px #00f5ff;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="title">🎬 CineScope</div>', unsafe_allow_html=True)
st.write("Discover movies with style ✨")

# ================= FUNCTIONS =================
@st.cache_data
def get_movie(movie):
    try:
        url = f"http://www.omdbapi.com/?t={movie}&apikey={API_KEY}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

@st.cache_data
def search_movies(movie):
    try:
        url = f"http://www.omdbapi.com/?s={movie}&apikey={API_KEY}"
        return requests.get(url, timeout=5).json()
    except:
        return {}

# ================= SEARCH =================
movie_name = st.text_input("🔍 Search any movie")

if st.button("Search"):
    if not movie_name:
        st.warning("Please enter a movie name")
    else:
        with st.spinner("Fetching movie..."):
            data = get_movie(movie_name)

        if data.get("Response") == "True":
            st.markdown("---")

            col1, col2 = st.columns([1,2])

            with col1:
                if data.get("Poster") and data["Poster"] != "N/A":
                    st.image(data["Poster"])
                else:
                    st.write("No poster available")

            with col2:
                st.markdown(f"## {data.get('Title','N/A')} ({data.get('Year','N/A')})")
                st.write(f"⭐ IMDB: {data.get('imdbRating','N/A')}")
                st.write(f"🎭 Genre: {data.get('Genre','N/A')}")
                st.write(f"🎬 Director: {data.get('Director','N/A')}")
                st.write(f"👨‍🎤 Actors: {data.get('Actors','N/A')}")
                st.write(f"📝 Plot: {data.get('Plot','N/A')}")
        else:
            st.error("Movie not found ❌")

# ================= TRENDING =================
st.markdown('<div class="section">🔥 Trending</div>', unsafe_allow_html=True)

trending = ["Avengers", "Joker", "Interstellar", "Inception", "Titanic"]
cols = st.columns(5)

for i, movie in enumerate(trending):
    data = get_movie(movie)

    with cols[i]:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if data.get("Response") == "True":
            if data.get("Poster") and data["Poster"] != "N/A":
                st.image(data["Poster"])
            else:
                st.write("No Image")

            st.write(data.get("Title", "N/A"))
            st.caption(data.get("Year", "N/A"))
        else:
            st.write("Not found")

        st.markdown('</div>', unsafe_allow_html=True)

# ================= DISCOVER =================
if movie_name:
    st.markdown('<div class="section">🎯 Discover Similar</div>', unsafe_allow_html=True)

    results = search_movies(movie_name)

    if results.get("Response") == "True":
        movies = results.get("Search", [])

        cols = st.columns(5)

        for i, movie in enumerate(movies[:10]):
            with cols[i % 5]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if movie.get("Poster") and movie["Poster"] != "N/A":
                    st.image(movie["Poster"])
                else:
                    st.write("No Image")

                st.write(movie.get("Title", "N/A"))
                st.caption(movie.get("Year", "N/A"))

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.write("No similar movies found")
