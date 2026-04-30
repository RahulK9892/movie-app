import streamlit as st
import requests

# ================= CONFIG =================
API_KEY = "f04c0df7"
BASE_URL = "http://www.omdbapi.com/"

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

# ================= SAFE API =================
def safe_api(params):
    try:
        params["apikey"] = API_KEY
        res = requests.get(BASE_URL, params=params, timeout=5)
        data = res.json()

        if data.get("Response") == "True":
            return data
        return None
    except:
        return None

def get_movie(name):
    return safe_api({"t": name})

def search_movie(name):
    return safe_api({"s": name})

# ================= SEARCH =================
movie_name = st.text_input("🔍 Search any movie")

if st.button("Search"):
    if movie_name.strip() == "":
        st.warning("Enter a movie name")
    else:
        with st.spinner("Fetching movie..."):
            data = get_movie(movie_name.strip())

        if data:
            st.markdown("---")
            col1, col2 = st.columns([1,2])

            with col1:
                if data.get("Poster") and data["Poster"] != "N/A":
                    st.image(data["Poster"])

            with col2:
                st.markdown(f"## {data.get('Title')} ({data.get('Year')})")
                st.write(f"⭐ IMDB: {data.get('imdbRating')}")
                st.write(f"🎭 Genre: {data.get('Genre')}")
                st.write(f"🎬 Director: {data.get('Director')}")
                st.write(f"👨‍🎤 Actors: {data.get('Actors')}")
                st.write(f"📝 {data.get('Plot')}")
        else:
            st.warning("⚠️ Couldn't fetch movie. Try again.")

# ================= TRENDING (100% SAFE) =================
st.markdown('<div class="section">🔥 Trending</div>', unsafe_allow_html=True)

trending = ["Avengers", "Batman", "Avatar", "Titanic", "Inception"]
cols = st.columns(5)

for i, m in enumerate(trending):
    data = get_movie(m)

    with cols[i]:
        if data:  # ONLY SHOW VALID
            st.markdown('<div class="card">', unsafe_allow_html=True)

            if data.get("Poster") != "N/A":
                st.image(data["Poster"])

            st.write(data.get("Title"))
            st.caption(data.get("Year"))

            st.markdown('</div>', unsafe_allow_html=True)

# ================= DISCOVER =================
if movie_name:
    st.markdown('<div class="section">🎯 Discover Similar</div>', unsafe_allow_html=True)

    results = search_movie(movie_name)

    if results:
        cols = st.columns(5)

        for i, m in enumerate(results["Search"][:10]):
            with cols[i % 5]:
                st.markdown('<div class="card">', unsafe_allow_html=True)

                if m.get("Poster") != "N/A":
                    st.image(m["Poster"])

                st.write(m.get("Title"))
                st.caption(m.get("Year"))

                st.markdown('</div>', unsafe_allow_html=True)
