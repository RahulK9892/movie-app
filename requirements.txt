import streamlit as st
import requests

# ================= CONFIG =================
API_KEY = "YOUR_API_KEY_HERE"  # replace this

st.set_page_config(page_title="CineScope", layout="wide")

# ================= CUSTOM UI =================
st.markdown("""
<style>
body {
    background-color: #0b0f19;
}

/* Title */
.title {
    font-size: 40px;
    font-weight: bold;
    color: #00f5ff;
}

/* Glass card */
.card {
    background: rgba(255, 255, 255, 0.05);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    text-align: center;
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-5px) scale(1.03);
    box-shadow: 0 0 15px #00f5ff;
}

/* Section title */
.section {
    font-size: 24px;
    margin-top: 30px;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="title">🎬 CineScope</div>', unsafe_allow_html=True)
st.write("Discover movies with style ✨")

# ================= SEARCH =================
movie_name = st.text_input("🔍 Search any movie")

# ================= FUNCTIONS =================
def get_movie(movie):
    url = f"http://www.omdbapi.com/?t={movie}&apikey={API_KEY}"
    return requests.get(url).json()

def search_movies(movie):
    url = f"http://www.omdbapi.com/?s={movie}&apikey={API_KEY}"
    return requests.get(url).json()

# ================= MAIN SEARCH =================
if st.button("Search"):
    if movie_name:
        data = get_movie(movie_name)

        if data["Response"] == "True":
            st.markdown("---")

            col1, col2 = st.columns([1,2])

            with col1:
                if data["Poster"] != "N/A":
                    st.image(data["Poster"])

            with col2:
                st.markdown(f"## {data['Title']} ({data['Year']})")
                st.write(f"⭐ IMDB: {data['imdbRating']}")
                st.write(f"🎭 Genre: {data['Genre']}")
                st.write(f"🎬 Director: {data['Director']}")
                st.write(f"👨‍🎤 Actors: {data['Actors']}")
                st.write(f"📝 Plot: {data['Plot']}")

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

        if data["Poster"] != "N/A":
            st.image(data["Poster"])

        st.write(data["Title"])
        st.caption(data["Year"])

        st.markdown('</div>', unsafe_allow_html=True)

# ================= DISCOVER =================
if movie_name:
    st.markdown('<div class="section">🎯 Discover Similar</div>', unsafe_allow_html=True)

    results = search_movies(movie_name)

    if results["Response"] == "True":
        cols = st.columns(5)

        for i, movie in enumerate(results["Search"][:10]):
            with cols[i % 5]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if movie["Poster"] != "N/A":
                    st.image(movie["Poster"])

                st.write(movie["Title"])
                st.caption(movie["Year"])

                st.markdown('</div>', unsafe_allow_html=True)
