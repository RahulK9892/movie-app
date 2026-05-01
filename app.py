import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# ================= CONFIG =================
TMDB_API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="LUMORA FINAL", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
.movie-card {
    text-align: center;
    cursor: pointer;
}
.movie-card img {
    border-radius: 12px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.movie-card img:hover {
    transform: scale(1.08);
    box-shadow: 0px 12px 25px rgba(0,0,0,0.6);
}
.movie-title {
    font-size: 14px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
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
def get_movies(cat):
    return fetch(f"https://api.themoviedb.org/3/movie/{cat}?api_key={TMDB_API_KEY}")

@st.cache_data
def get_movie(mid):
    return fetch(f"https://api.themoviedb.org/3/movie/{mid}?api_key={TMDB_API_KEY}")

@st.cache_data
def get_trailer(mid):
    data = fetch(f"https://api.themoviedb.org/3/movie/{mid}/videos?api_key={TMDB_API_KEY}")
    for v in data.get("results", []):
        if v["site"] == "YouTube":
            return f"https://youtube.com/watch?v={v['key']}"
    return None

@st.cache_data
def get_images(mid):
    return fetch(f"https://api.themoviedb.org/3/movie/{mid}/images?api_key={TMDB_API_KEY}")

# ================= AI =================
def build_ai(movies):
    df = pd.DataFrame(movies)[['title','overview']].fillna("")
    cv = CountVectorizer(stop_words='english')
    vec = cv.fit_transform(df['overview']).toarray()
    sim = cosine_similarity(vec)
    return df, sim

def recommend(title, df, sim):
    if title not in df['title'].values:
        return []
    idx = df[df['title']==title].index[0]
    scores = sorted(list(enumerate(sim[idx])), key=lambda x:x[1], reverse=True)[1:6]
    return [df.iloc[i[0]].title for i in scores]

# ================= CARD =================
def movie_card(movie, key):
    if movie.get("poster_path"):
        st.markdown(f"""
        <div class="movie-card">
            <img src="{BASE_IMG + movie['poster_path']}">
            <div class="movie-title">{movie['title']}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("▶ View", key=key):
        st.session_state.movie_id = movie["id"]
        st.session_state.page = "movie"
        st.rerun()

# ================= HOME =================
if st.session_state.page == "home":

    st.title("🎬 LUMORA")

    trending = get_movies("popular")
    top = get_movies("top_rated")

    st.markdown("## 🔥 Trending")
    cols = st.columns(5)
    for i, m in enumerate(trending.get("results", [])[:10]):
        with cols[i % 5]:
            movie_card(m, f"t{i}")

    st.markdown("## ⭐ Top Rated")
    cols = st.columns(5)
    for i, m in enumerate(top.get("results", [])[:10]):
        with cols[i % 5]:
            movie_card(m, f"tr{i}")

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

    # GRAPH
    st.markdown("## 📊 Rating Graph")
    fig, ax = plt.subplots()
    ax.plot([rating, rating-1, rating+0.5])
    st.pyplot(fig)

    # TRAILER
    trailer = get_trailer(data["id"])
    if trailer:
        st.video(trailer)

    # SCENES
    st.markdown("## 🎞️ Movie Scenes")
    imgs = get_images(data["id"])

    cols = st.columns(3)
    for i, img in enumerate(imgs.get("backdrops", [])[:6]):
        with cols[i % 3]:
            st.image(BASE_IMG + img["file_path"])

    # AI
    st.markdown("## 🧠 AI Recommendations")
    popular = get_movies("popular").get("results", [])
    df, sim = build_ai(popular)

    recs = recommend(data["title"], df, sim)
    for r in recs:
        st.write("👉", r)
