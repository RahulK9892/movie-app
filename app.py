import streamlit as st
import requests

# ================= CONFIG =================
API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"
BACKDROP = "https://image.tmdb.org/t/p/original"

st.set_page_config(page_title="LUMORA", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
body {background:#0a0f1c;}
.title {
    font-size:45px;
    font-weight:bold;
    color:#00f5ff;
}
.section {
    font-size:26px;
    color:white;
    margin-top:20px;
}
.card img {
    border-radius:12px;
    transition:0.3s;
}
.card img:hover {
    transform:scale(1.07);
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
    return fetch(f"{BASE}/trending/movie/week?api_key={API_KEY}")

def search(q):
    return fetch(f"{BASE}/search/movie?api_key={API_KEY}&query={q}")

def details(mid):
    return fetch(f"{BASE}/movie/{mid}?api_key={API_KEY}")

def credits(mid):
    return fetch(f"{BASE}/movie/{mid}/credits?api_key={API_KEY}")

def trailer(mid):
    data = fetch(f"{BASE}/movie/{mid}/videos?api_key={API_KEY}")
    if data:
        for v in data["results"]:
            if v["type"] == "Trailer" and v["site"] == "YouTube":
                return v["key"]
    return None

# ================= HEADER =================
st.markdown('<div class="title">🎬 LUMORA</div>', unsafe_allow_html=True)
st.write("A cinematic discovery platform")

# ================= HERO =================
trend = trending()

if trend and trend.get("results"):
    hero = trend["results"][0]

    if hero.get("backdrop_path"):
        st.image(BACKDROP + hero["backdrop_path"], use_container_width=True)

    st.markdown(f"## {hero['title']}")
    st.write(hero["overview"][:200] + "...")

    if st.button("▶ Play Trailer (Hero)"):
        key = trailer(hero["id"])
        if key:
            st.video(f"https://www.youtube.com/watch?v={key}")

# ================= SEARCH =================
st.markdown("---")
query = st.text_input("🔍 Search movie")

if query:
    data = search(query)

    if data and data.get("results"):
        st.markdown('<div class="section">Search Results</div>', unsafe_allow_html=True)

        cols = st.columns(5)

        for i, m in enumerate(data["results"][:10]):
            with cols[i % 5]:
                if m.get("poster_path"):
                    st.image(IMG + m["poster_path"])

                if st.button(m["title"], key=i):
                    mid = m["id"]
                    d = details(mid)
                    c = credits(mid)

                    st.markdown("---")
                    col1, col2 = st.columns([1,2])

                    with col1:
                        if m.get("poster_path"):
                            st.image(IMG + m["poster_path"])

                    with col2:
                        st.markdown(f"## {m['title']}")
                        st.write(f"⭐ {d.get('vote_average')}")
                        st.write(f"📅 {d.get('release_date')}")
                        st.write(d.get("overview"))

                        if d.get("revenue"):
                            st.write(f"💰 Box Office: ${d['revenue']:,}")

                    # TRAILER
                    t = trailer(mid)
                    if t:
                        st.video(f"https://www.youtube.com/watch?v={t}")

                    # DIRECTOR
                    director = next((x for x in c["crew"] if x["job"]=="Director"), None)
                    if director:
                        st.markdown("### 🎬 Director")
                        if director.get("profile_path"):
                            st.image(IMG + director["profile_path"], width=120)
                        st.write(director["name"])

                    # CAST
                    st.markdown("### 👨‍🎤 Cast")
                    cols2 = st.columns(5)
                    for j, actor in enumerate(c["cast"][:10]):
                        with cols2[j % 5]:
                            if actor.get("profile_path"):
                                st.image(IMG + actor["profile_path"])
                            st.caption(actor["name"])

# ================= TRENDING =================
st.markdown('<div class="section">🔥 Trending Now</div>', unsafe_allow_html=True)

if trend and trend.get("results"):
    cols = st.columns(5)

    for i, m in enumerate(trend["results"][:10]):
        with cols[i % 5]:
            if m.get("poster_path"):
                st.image(IMG + m["poster_path"])
            st.caption(m["title"])
