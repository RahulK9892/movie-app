import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# ================= CONFIG =================
TMDB_API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="LUMORA PRO", layout="wide")

# ================= DARK MODE =================
theme = st.sidebar.toggle("🌙 Dark Mode")

if theme:
    st.markdown("""
    <style>
    body {background-color: #0e1117; color: white;}
    </style>
    """, unsafe_allow_html=True)

# ================= CSS =================
st.markdown("""
<style>
.scroll-container {
    display: flex;
    overflow-x: auto;
    gap: 15px;
}
.movie-card {
    min-width: 150px;
}
.movie-card img {
    border-radius: 10px;
    transition: 0.3s;
}
.movie-card img:hover {
    transform: scale(1.1);
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "page" not in st.session_state:
    st.session_state.page = "home"
if "movie_id" not in st.session_state:
    st.session_state.movie_id = None

# ================= API =================
def fetch(url):
    try:
        return requests.get(url).json()
    except:
        return {}

@st.cache_data
def get_movies(category):
    return fetch(f"https://api.themoviedb.org/3/movie/{category}?api_key={TMDB_API_KEY}")

@st.cache_data
def search_movie(q):
    return fetch(f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={q}")

@st.cache_data
def get_movie(id):
    return fetch(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}")

@st.cache_data
def get_images(id):
    return fetch(f"https://api.themoviedb.org/3/movie/{id}/images?api_key={TMDB_API_KEY}")

@st.cache_data
def get_trailer(id):
    data = fetch(f"https://api.themoviedb.org/3/movie/{id}/videos?api_key={TMDB_API_KEY}")
    for v in data.get("results", []):
        if v["site"] == "YouTube":
            return f"https://youtube.com/watch?v={v['key']}"
    return None

# ================= AI MODEL =================
def build_ai_model(movies):
    df = pd.DataFrame(movies)
    df = df[['title', 'overview']].fillna("")

    cv = CountVectorizer(stop_words='english')
    vectors = cv.fit_transform(df['overview']).toarray()

    similarity = cosine_similarity(vectors)

    return df, similarity

def recommend(title, df, sim):
    idx = df[df['title'] == title].index[0]
    scores = list(enumerate(sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:6]
    return [df.iloc[i[0]].title for i in scores]

# ================= UI =================
def horizontal_row(title, movies):
    st.markdown(f"## {title}")
    cols = st.columns(len(movies[:10]))

    for i, m in enumerate(movies[:10]):
        with cols[i]:
            if m.get("poster_path"):
                st.image(BASE_IMG + m["poster_path"])
            if st.button(m["title"], key=m["id"]):
                st.session_state.movie_id = m["id"]
                st.session_state.page = "movie"
                st.rerun()

# ================= HOME =================
if st.session_state.page == "home":

    st.title("🎬 LUMORA PRO")

    query = st.text_input("🔍 Search")

    if query:
        res = search_movie(query)
        horizontal_row("Results", res.get("results", []))

    trending = get_movies("popular")
    top = get_movies("top_rated")

    horizontal_row("🔥 Trending", trending.get("results", []))
    horizontal_row("⭐ Top Rated", top.get("results", []))

# ================= MOVIE PAGE =================
if st.session_state.page == "movie":

    data = get_movie(st.session_state.movie_id)

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()

    st.title(data.get("title"))

    col1, col2 = st.columns([1,2])

    with col1:
        if data.get("poster_path"):
            st.image(BASE_IMG + data["poster_path"])

    with col2:
        rating = data.get("vote_average", 0)
        st.progress(rating/10)
        st.write(data.get("overview"))

        if st.button("❤️ Add to Watchlist"):
            st.session_state.watchlist.append(data["id"])

    # ===== GRAPH =====
    st.markdown("## 📊 Rating Graph")
    ratings = [rating, rating-1, rating+0.5, rating-0.3]

    plt.figure()
    plt.plot(ratings)
    st.pyplot(plt)

    # ===== TRAILER =====
    trailer = get_trailer(data["id"])
    if trailer:
        st.video(trailer)

    # ===== SCENES =====
    st.markdown("## 🎞️ Scenes")
    imgs = get_images(data["id"])

    cols = st.columns(3)
    for i, img in enumerate(imgs.get("backdrops", [])[:6]):
        with cols[i%3]:
            st.image(BASE_IMG + img["file_path"])

    # ===== AI RECOMMEND =====
    st.markdown("## 🧠 AI Recommendations")

    popular = get_movies("popular").get("results", [])
    df, sim = build_ai_model(popular)

    try:
        recs = recommend(data["title"], df, sim)
        for r in recs:
            st.write("👉", r)
    except:
        st.write("No AI recommendations available")

# ================= WATCHLIST =================
st.sidebar.markdown("## ❤️ Watchlist")

for m in st.session_state.watchlist:
    d = get_movie(m)
    if st.sidebar.button(d["title"], key=m):
        st.session_state.movie_id = m
        st.session_state.page = "movie"
        st.rerun()
