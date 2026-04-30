import streamlit as st
import requests

# ================= CONFIG =================
API_KEY = "56bb6403529bf7858db4fb63d2d8ca55"
BASE = "https://api.themoviedb.org/3"
IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="LUMORA", layout="wide")

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

# ================= STYLE =================
st.markdown("""
<style>
body {background:#0a0f1c;}

.title {
    font-size:45px;
    font-weight:bold;
    color:#00f5ff;
}

.card img {
    border-radius:12px;
    transition:0.3s;
}
.card img:hover {
    transform:scale(1.08);
    box-shadow:0 0 15px #00f5ff;
}

button {
    border-radius:10px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= API =================
def fetch(url):
    try:
        return requests.get(url).json()
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
            if v["type"] == "Trailer":
                return v["key"]
    return None

# ================= LOGIN =================
def login_ui():
    st.markdown("## 🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user and pwd:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Enter details")

# ================= HEADER =================
st.markdown('<div class="title">🎬 LUMORA</div>', unsafe_allow_html=True)

# ================= LOGIN CHECK =================
if not st.session_state.logged_in:
    login_ui()
    st.stop()

# ================= NAV =================
menu = st.sidebar.radio("Menu", ["Home", "Watchlist", "Logout"])

if menu == "Logout":
    st.session_state.logged_in = False
    st.rerun()

# ================= MOVIE DETAILS =================
def show_details(mid):
    d = details(mid)
    c = credits(mid)

    st.markdown("---")

    col1, col2 = st.columns([1,2])

    with col1:
        if d.get("poster_path"):
            st.image(IMG + d["poster_path"])

    with col2:
        st.markdown(f"## {d['title']}")
        st.write(f"⭐ {d.get('vote_average')}")
        st.write(d.get("overview"))

        if d.get("revenue"):
            st.write(f"💰 ${d['revenue']:,}")

        # WATCHLIST BUTTON
        if mid not in st.session_state.watchlist:
            if st.button("❤️ Add to Watchlist"):
                st.session_state.watchlist.append(mid)
        else:
            if st.button("❌ Remove from Watchlist"):
                st.session_state.watchlist.remove(mid)

    # TRAILER
    key = trailer(mid)
    if key:
        st.video(f"https://youtube.com/watch?v={key}")

    # CAST
    st.markdown("### 👨‍🎤 Cast")
    cols = st.columns(5)

    for i, actor in enumerate(c["cast"][:10]):
        with cols[i % 5]:
            if actor.get("profile_path"):
                st.image(IMG + actor["profile_path"])
            st.caption(actor["name"])

# ================= HOME =================
if menu == "Home":

    query = st.text_input("🔍 Search movie")

    # SELECTED MOVIE
    if st.session_state.selected_movie:
        if st.button("⬅ Back"):
            st.session_state.selected_movie = None
            st.rerun()
        else:
            show_details(st.session_state.selected_movie)
            st.stop()

    # SEARCH
    if query:
        data = search(query)

        if data and data.get("results"):
            cols = st.columns(5)

            for i, m in enumerate(data["results"][:10]):
                with cols[i % 5]:
                    if m.get("poster_path"):
                        st.image(IMG + m["poster_path"])

                    if st.button(m["title"], key=f"s{i}"):
                        st.session_state.selected_movie = m["id"]
                        st.rerun()

    # TRENDING
    else:
        st.markdown("### 🔥 Trending")

        data = trending()

        if data and data.get("results"):
            cols = st.columns(5)

            for i, m in enumerate(data["results"][:10]):
                with cols[i % 5]:
                    if m.get("poster_path"):
                        st.image(IMG + m["poster_path"])

                    if st.button(m["title"], key=f"t{i}"):
                        st.session_state.selected_movie = m["id"]
                        st.rerun()

# ================= WATCHLIST =================
if menu == "Watchlist":
    st.markdown("### ❤️ Your Watchlist")

    if not st.session_state.watchlist:
        st.write("Empty")

    cols = st.columns(5)

    for i, mid in enumerate(st.session_state.watchlist):
        d = details(mid)

        with cols[i % 5]:
            if d.get("poster_path"):
                st.image(IMG + d["poster_path"])

            if st.button(d["title"], key=f"w{i}"):
                st.session_state.selected_movie = mid
                st.rerun()
