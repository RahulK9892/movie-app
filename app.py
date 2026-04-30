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
def get_movie(movie):
    try:
        url = f"http://www.omdbapi.com/?t={movie}&apikey={API_KEY}"
        res = requests.get(url, timeout=5).json()
        return res if res.get("Response") == "True" else None
    except:
        return None

def search_movies(movie):
    try:
        url = f"http://www.omdbapi.com/?s={movie}&apikey={API_KEY}"
        res = requests.get(url, timeout=5).json()
        return res if res.get("Response") == "True" else None
    except:
        return None

# ================= SEARCH =================
movie_name = st.text_input("🔍 Search any movie")

if st.button("Search"):
    if not movie_name:
        st.warning("Enter a movie name")
    else:
        with st.spinner("Searching..."):
            data = get_movie(movie_name)

        if data:
            st.markdown("---")

            col1, col2 = st.columns([1,2])

            with col1:
                if data.get("Poster") != "N/A":
                    st.image(data["Poster"])

            with col2:
                st.markdown(f"## {data.get('Title')} ({data.get('Year')})")
                st.write(f"⭐ IMDB: {data.get('imdbRating')}")
                st.write(f"🎭 Genre: {data.get('Genre')}")
                st.write(f"🎬 Director: {data.get('Director')}")
                st.write(f"👨‍🎤 Actors: {data.get('Actors')}")
                st.write(f"📝 Plot: {data.get('Plot')}")
        else:
            st.error("Movie not found ❌")

# ================= TRENDING (FIXED) =================
st.markdown('<div class="section">🔥 Trending</div>', unsafe_allow_html=True)

trending_movies = ["Avengers", "Batman", "Avatar", "Titanic", "Gladiator"]
cols = st.columns(5)

for i, movie in enumerate(trending_movies):
    data = get_movie(movie)

    with cols[i]:
        if data:   # ONLY SHOW IF VALID
            st.markdown('<div class="card">', unsafe_allow_html=True)

            if data.get("Poster") != "N/A":
                st.image(data["Poster"])

            st.write(data.get("Title"))
            st.caption(data.get("Year"))

            st.markdown('</div>', unsafe_allow_html=True)

# ================= DISCOVER =================
if movie_name:
    st.markdown('<div class="section">🎯 Discover Similar</div>', unsafe_allow_html=True)

    results = search_movies(movie_name)

    if results:
        cols = st.columns(5)

        for i, movie in enumerate(results["Search"][:10]):
            with cols[i % 5]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if movie.get("Poster") != "N/A":
                    st.image(movie["Poster"])

                st.write(movie.get("Title"))
                st.caption(movie.get("Year"))

                st.markdown('</div>', unsafe_allow_html=True)
