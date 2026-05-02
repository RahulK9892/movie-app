/**
 * LUMORA — lumora.js
 * Single-page app logic: routing, TMDB API calls, rendering.
 */

/* ══════════════════════════════════════════════════════════════════
   CONFIG
   ══════════════════════════════════════════════════════════════════ */
const IMG      = "https://image.tmdb.org/t/p/w342";
const IMG_LG   = "https://image.tmdb.org/t/p/w500";
const BACKDROP = "https://image.tmdb.org/t/p/w1280";

/* ══════════════════════════════════════════════════════════════════
   STATE
   ══════════════════════════════════════════════════════════════════ */
const state = {
  page:          "home",
  prevPage:      "home",
  detailId:      null,
  detailType:    "movie",   // "movie" | "tv"
  watchlist:     JSON.parse(localStorage.getItem("lm_watchlist") || "[]"),
  trendPage:     1,
  searchPage:    1,
  recPage:       1,
  moviesFilter:  "popular",
  moviesPage:    1,
  seriesFilter:  "popular",
  seriesPage:    1,
  searchQuery:   "",
  recTotal:      1,
};

/* ══════════════════════════════════════════════════════════════════
   API
   ══════════════════════════════════════════════════════════════════ */
async function api(path) {
  try {
    const r = await fetch(path);
    if (!r.ok) throw new Error(r.statusText);
    return await r.json();
  } catch (e) {
    console.error("API error:", path, e);
    return {};
  }
}

const tmdb = {
  trending:         (p=1)  => api(`/api/trending?page=${p}`),
  popular:          (p=1)  => api(`/api/movies/popular?page=${p}`),
  topRated:         (p=1)  => api(`/api/movies/top_rated?page=${p}`),
  nowPlaying:       (p=1)  => api(`/api/movies/now_playing?page=${p}`),
  upcoming:         (p=1)  => api(`/api/movies/upcoming?page=${p}`),
  movieDetail:      (id)   => api(`/api/movie/${id}`),
  movieCredits:     (id)   => api(`/api/movie/${id}/credits`),
  movieVideos:      (id)   => api(`/api/movie/${id}/videos`),
  movieImages:      (id)   => api(`/api/movie/${id}/images`),
  movieRec:         (id,p) => api(`/api/movie/${id}/recommendations?page=${p}`),
  tvPopular:        (p=1)  => api(`/api/tv/popular?page=${p}`),
  tvTopRated:       (p=1)  => api(`/api/tv/top_rated?page=${p}`),
  tvOnAir:          (p=1)  => api(`/api/tv/on_the_air?page=${p}`),
  tvTrending:       (p=1)  => api(`/api/tv/trending?page=${p}`),
  tvDetail:         (id)   => api(`/api/tv/${id}`),
  tvCredits:        (id)   => api(`/api/tv/${id}/credits`),
  tvVideos:         (id)   => api(`/api/tv/${id}/videos`),
  tvImages:         (id)   => api(`/api/tv/${id}/images`),
  tvRec:            (id,p) => api(`/api/tv/${id}/recommendations?page=${p}`),
  search:           (q,p)  => api(`/api/search/movie?query=${encodeURIComponent(q)}&page=${p}`),
};

/* ══════════════════════════════════════════════════════════════════
   DOM HELPERS
   ══════════════════════════════════════════════════════════════════ */
const $  = (id) => document.getElementById(id);
const qs = (sel) => document.querySelector(sel);

function show(id) { $(id).classList.remove("hidden"); }
function hide(id) { $(id).classList.add("hidden"); }
function showEl(el)  { el.style.display = ""; }
function hideEl(el)  { el.style.display = "none"; }

function showLoader()  { $("globalLoader").classList.remove("hide"); }
function hideLoader()  { $("globalLoader").classList.add("hide"); }

function toast(msg, dur=2800) {
  const t = $("toast");
  t.textContent = msg;
  t.classList.add("show");
  setTimeout(() => t.classList.remove("show"), dur);
}

/* ══════════════════════════════════════════════════════════════════
   WATCHLIST
   ══════════════════════════════════════════════════════════════════ */
function saveWatchlist() {
  localStorage.setItem("lm_watchlist", JSON.stringify(state.watchlist));
}
function inWatchlist(id) {
  return state.watchlist.some(w => w.id === id);
}
function toggleWatchlist(item) {
  if (inWatchlist(item.id)) {
    state.watchlist = state.watchlist.filter(w => w.id !== item.id);
    toast("Removed from My List");
  } else {
    state.watchlist.push(item);
    toast("Added to My List ✓");
  }
  saveWatchlist();
  updateWlBadges();
}
function removeFromWatchlist(id) {
  state.watchlist = state.watchlist.filter(w => w.id !== id);
  saveWatchlist();
  updateWlBadges();
  renderMyList();
}
function updateWlBadges() {
  const cnt = state.watchlist.length;
  const badge = $("navWlCount");
  if (cnt > 0) { badge.textContent = cnt; showEl(badge); }
  else { hideEl(badge); }

  // Also update my list section on home
  const mlSection = $("myListSection");
  if (cnt > 0 && state.page === "home") {
    showEl(mlSection);
    $("myListCount").textContent = `${cnt} saved`;
    renderCardRow($("rowMyList"), state.watchlist.map(w => ({
      id: w.id, poster_path: w.poster, title: w.title, vote_average: 0
    })), false);
  } else {
    hideEl(mlSection);
  }
}

/* ══════════════════════════════════════════════════════════════════
   MONEY FORMATTER
   ══════════════════════════════════════════════════════════════════ */
function fmtMoney(n) {
  if (!n || n === 0) return "N/A";
  if (n >= 1e9)  return `$${(n/1e9).toFixed(2)}B`;
  if (n >= 1e6)  return `$${(n/1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

/* ══════════════════════════════════════════════════════════════════
   CARD RENDERERS
   ══════════════════════════════════════════════════════════════════ */
function makeCard(item, type="movie", showRemove=false) {
  const id     = item.id;
  const title  = item.title || item.name || "Untitled";
  const poster = item.poster_path;
  const rating = (item.vote_average || 0).toFixed(1);
  const year   = (item.release_date || item.first_air_date || "").slice(0,4);

  const div = document.createElement("div");

  if (!poster) {
    div.className = "no-poster";
    div.textContent = title;
    div.onclick = () => goDetail(id, type);
    return div;
  }

  div.className = "poster-card";
  div.innerHTML = `
    <img src="${IMG}${poster}" alt="${escHtml(title)}" loading="lazy" />
    <div class="card-play">▶</div>
    <div class="card-overlay">
      <div class="card-title">${escHtml(title)}</div>
      <div class="card-meta">
        <span class="card-star">★ ${rating}</span>
        <span class="card-year">${year}</span>
      </div>
    </div>
    ${showRemove ? `<button class="card-remove" data-id="${id}" title="Remove">✕ Remove</button>` : ""}
  `;
  div.onclick = (e) => {
    if (e.target.classList.contains("card-remove")) return;
    goDetail(id, type);
  };
  if (showRemove) {
    div.querySelector(".card-remove").onclick = (e) => {
      e.stopPropagation();
      removeFromWatchlist(id);
    };
  }
  return div;
}

function renderCardRow(container, items, isTV=false) {
  container.innerHTML = "";
  items.forEach(item => {
    container.appendChild(makeCard(item, isTV ? "tv" : "movie"));
  });
}

function renderCardGrid(container, items, isTV=false, showRemove=false) {
  container.innerHTML = "";
  items.forEach(item => {
    container.appendChild(makeCard(item, isTV ? "tv" : "movie", showRemove));
  });
}

/* ══════════════════════════════════════════════════════════════════
   PAGINATION
   ══════════════════════════════════════════════════════════════════ */
function renderPagination(container, current, total, onSelect) {
  container.innerHTML = "";
  if (total <= 1) return;

  const maxVisible = 5;
  const pages = new Set([1, total]);
  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) pages.add(i);
  const sorted = [...pages].sort((a,b) => a-b);

  // Prev
  const prev = document.createElement("button");
  prev.className = "pg-btn";
  prev.textContent = "◀";
  prev.disabled = current === 1;
  prev.onclick = () => onSelect(current - 1);
  container.appendChild(prev);

  let last = 0;
  sorted.forEach(p => {
    if (last && p - last > 1) {
      const ell = document.createElement("span");
      ell.className = "pg-ellipsis";
      ell.textContent = "…";
      container.appendChild(ell);
    }
    const btn = document.createElement("button");
    btn.className = "pg-btn" + (p === current ? " active" : "");
    btn.textContent = p;
    btn.onclick = () => onSelect(p);
    container.appendChild(btn);
    last = p;
  });

  // Next
  const next = document.createElement("button");
  next.className = "pg-btn";
  next.textContent = "▶";
  next.disabled = current === total;
  next.onclick = () => onSelect(current + 1);
  container.appendChild(next);
}

/* ══════════════════════════════════════════════════════════════════
   ROUTING / NAVIGATION
   ══════════════════════════════════════════════════════════════════ */
function showPage(pageId) {
  document.querySelectorAll(".page").forEach(p => p.classList.add("hidden"));
  $(`page-${pageId}`).classList.remove("hidden");

  // Update nav active
  document.querySelectorAll(".nav-link").forEach(a => {
    a.classList.toggle("active", a.dataset.nav === navNameFor(pageId));
  });

  // Scroll to top
  window.scrollTo(0, 0);
}

function navNameFor(pageId) {
  return { home: "Browse", movies: "Movies", series: "Series", mylist: "My List", detail: "" }[pageId] || "";
}

async function goHome() {
  state.page = "home"; state.prevPage = "home";
  showPage("home");
  clearSearch();
  await loadHome();
}
async function goMovies() {
  state.page = "movies"; state.prevPage = "movies";
  showPage("movies");
  await loadMovies();
}
async function goSeries() {
  state.page = "series"; state.prevPage = "series";
  showPage("series");
  await loadSeries();
}
function goMyList() {
  state.page = "mylist"; state.prevPage = "mylist";
  showPage("mylist");
  renderMyList();
}
async function goDetail(id, type="movie") {
  state.prevPage = state.page;
  state.page = "detail";
  state.detailId = id;
  state.detailType = type;
  state.recPage = 1;
  showPage("detail");
  await loadDetail(id, type);
}

/* ══════════════════════════════════════════════════════════════════
   BACK BUTTON
   ══════════════════════════════════════════════════════════════════ */
$("backBtn").onclick = () => {
  const prev = state.prevPage || "home";
  if (prev === "movies") goMovies();
  else if (prev === "series") goSeries();
  else if (prev === "mylist") goMyList();
  else goHome();
};

/* ══════════════════════════════════════════════════════════════════
   HOME PAGE
   ══════════════════════════════════════════════════════════════════ */
async function loadHome() {
  showLoader();
  const [trendData, nowData, topData, popData] = await Promise.all([
    tmdb.trending(state.trendPage),
    tmdb.nowPlaying(),
    tmdb.topRated(),
    tmdb.popular(),
  ]);
  hideLoader();

  const trending  = trendData.results  || [];
  const nowPlay   = nowData.results     || [];
  const topRated  = topData.results     || [];
  const popular   = popData.results     || [];

  // Hero
  if (trending.length) renderHero(trending[0]);

  // Rows
  renderCardRow($("rowTrending"),   trending.slice(0, 12));
  renderCardRow($("rowNowPlaying"), nowPlay.slice(0, 12));
  renderCardRow($("rowTopRated"),   topRated.slice(0, 12));
  renderCardRow($("rowPopular"),    popular.slice(0, 12));

  // Trend pagination
  const trendTotal = Math.min(trendData.total_pages || 1, 20);
  renderPagination($("paginationTrending"), state.trendPage, trendTotal, async (p) => {
    state.trendPage = p;
    showLoader();
    const d = await tmdb.trending(p);
    hideLoader();
    renderCardRow($("rowTrending"), (d.results || []).slice(0, 12));
    renderPagination($("paginationTrending"), p, trendTotal, () => {});
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // My List on home
  updateWlBadges();
}

function renderHero(movie) {
  const id       = movie.id;
  const title    = movie.title || movie.name || "";
  const overview = (movie.overview || "").slice(0, 210);
  const rating   = (movie.vote_average || 0).toFixed(1);
  const year     = (movie.release_date || "").slice(0,4);
  const bd       = movie.backdrop_path ? BACKDROP + movie.backdrop_path : "";

  $("heroBg").style.backgroundImage = `url('${bd}')`;
  $("heroTitle").textContent = title;
  $("heroMeta").innerHTML = `
    <span class="hero-rating">★ ${rating}</span>
    <span class="hero-dot">•</span>
    <span class="hero-year">${year}</span>
  `;
  $("heroOverview").textContent = overview + (overview.length >= 210 ? "…" : "");

  const detailBtn = $("heroDetails");
  const wlBtn     = $("heroWatchlist");

  detailBtn.onclick = () => goDetail(id, "movie");

  const refreshWlBtn = () => {
    if (inWatchlist(id)) {
      wlBtn.textContent = "✓ In My List";
      wlBtn.classList.add("in-list");
    } else {
      wlBtn.textContent = "＋ My List";
      wlBtn.classList.remove("in-list");
    }
  };
  refreshWlBtn();
  wlBtn.onclick = () => {
    toggleWatchlist({ id, title, poster: movie.poster_path });
    refreshWlBtn();
  };
}

/* ══════════════════════════════════════════════════════════════════
   MOVIES PAGE
   ══════════════════════════════════════════════════════════════════ */
async function loadMovies() {
  showLoader();
  let data;
  const f = state.moviesFilter;
  const p = state.moviesPage;
  if      (f === "popular")     data = await tmdb.popular(p);
  else if (f === "top_rated")   data = await tmdb.topRated(p);
  else if (f === "now_playing") data = await tmdb.nowPlaying(p);
  else                          data = await tmdb.upcoming(p);
  hideLoader();

  const movies = data.results || [];
  const total  = Math.min(data.total_pages || 1, 20);

  renderCardGrid($("movieGrid"), movies, false, false);
  renderPagination($("paginationMovies"), p, total, (np) => {
    state.moviesPage = np;
    loadMovies();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// Movie filter tabs
$("movieFilters").querySelectorAll(".filter-tab").forEach(btn => {
  btn.onclick = () => {
    $("movieFilters").querySelectorAll(".filter-tab").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    state.moviesFilter = btn.dataset.filter;
    state.moviesPage   = 1;
    loadMovies();
  };
});

/* ══════════════════════════════════════════════════════════════════
   SERIES PAGE
   ══════════════════════════════════════════════════════════════════ */
async function loadSeries() {
  showLoader();
  let data;
  const f = state.seriesFilter;
  const p = state.seriesPage;
  if      (f === "popular")    data = await tmdb.tvPopular(p);
  else if (f === "top_rated")  data = await tmdb.tvTopRated(p);
  else if (f === "on_the_air") data = await tmdb.tvOnAir(p);
  else                         data = await tmdb.tvTrending(p);
  hideLoader();

  const shows = data.results || [];
  const total = Math.min(data.total_pages || 1, 20);

  renderCardGrid($("seriesGrid"), shows, true, false);
  renderPagination($("paginationSeries"), p, total, (np) => {
    state.seriesPage = np;
    loadSeries();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

$("seriesFilters").querySelectorAll(".filter-tab").forEach(btn => {
  btn.onclick = () => {
    $("seriesFilters").querySelectorAll(".filter-tab").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    state.seriesFilter = btn.dataset.filter;
    state.seriesPage   = 1;
    loadSeries();
  };
});

/* ══════════════════════════════════════════════════════════════════
   MY LIST PAGE
   ══════════════════════════════════════════════════════════════════ */
function renderMyList() {
  const grid   = $("mylistGrid");
  const empty  = $("mylistEmpty");
  const sub    = $("mylistSubtitle");

  if (state.watchlist.length === 0) {
    grid.innerHTML = "";
    showEl(empty);
    sub.textContent = "";
  } else {
    hideEl(empty);
    const n = state.watchlist.length;
    sub.textContent = `${n} title${n !== 1 ? "s" : ""} saved`;
    renderCardGrid(grid, state.watchlist.map(w => ({
      id: w.id, poster_path: w.poster, title: w.title, vote_average: 0
    })), false, true);
  }
}

// Empty state buttons
$("mylistEmpty").querySelectorAll("[data-page]").forEach(btn => {
  btn.onclick = () => {
    if (btn.dataset.page === "movies") goMovies();
    else goSeries();
  };
});

/* ══════════════════════════════════════════════════════════════════
   DETAIL PAGE
   ══════════════════════════════════════════════════════════════════ */
async function loadDetail(id, type) {
  showLoader();

  // Clear stale
  $("castGrid").innerHTML = "";
  $("sceneGrid").innerHTML = "";
  $("trailerWrap").innerHTML = "";
  $("rowRec").innerHTML = "";
  $("paginationRec").innerHTML = "";
  $("detailStats").innerHTML = "";
  $("directorWrap").innerHTML = "";
  hide("castHeader"); hide("trailerHeader"); hide("scenesHeader"); hide("recHeader");
  hideEl($("directorWrap")); hideEl($("castGrid").parentElement || $("castHeader"));

  const isTV = type === "tv";

  const [detail, credits, videos, images, recData] = await Promise.all([
    isTV ? tmdb.tvDetail(id)    : tmdb.movieDetail(id),
    isTV ? tmdb.tvCredits(id)   : tmdb.movieCredits(id),
    isTV ? tmdb.tvVideos(id)    : tmdb.movieVideos(id),
    isTV ? tmdb.tvImages(id)    : tmdb.movieImages(id),
    isTV ? tmdb.tvRec(id, 1)    : tmdb.movieRec(id, 1),
  ]);
  hideLoader();

  // ── HERO ──
  const title    = detail.title || detail.name || "Untitled";
  const tagline  = detail.tagline || "";
  const rating   = (detail.vote_average || 0).toFixed(1);
  const votes    = (detail.vote_count || 0).toLocaleString();
  const year     = (detail.release_date || detail.first_air_date || "").slice(0,4);
  const runtime  = detail.runtime || (detail.episode_run_time || [])[0] || 0;
  const genres   = detail.genres || [];
  const overview = detail.overview || "No overview available.";
  const revenue  = detail.revenue || 0;
  const budget   = detail.budget  || 0;
  const bd       = detail.backdrop_path ? BACKDROP + detail.backdrop_path : "";
  const poster   = detail.poster_path  ? IMG_LG   + detail.poster_path  : null;

  $("detailBg").style.backgroundImage = bd ? `url('${bd}')` : "";

  const runtimeStr = runtime ? `${Math.floor(runtime/60)}h ${runtime%60}m` : "";
  const genreTags  = genres.map(g => `<span class="genre-tag">${escHtml(g.name)}</span>`).join("");

  $("detailPosterWrap").innerHTML = poster
    ? `<img src="${poster}" alt="${escHtml(title)}" />`
    : `<div style="height:270px;background:#1c1c1c;border-radius:10px;"></div>`;

  $("detailInfo").innerHTML = `
    ${tagline ? `<div class="detail-tagline">${escHtml(tagline)}</div>` : ""}
    <div class="detail-title">${escHtml(title)}</div>
    <div class="detail-meta-row">
      <span class="d-rating">★ ${rating}</span>
      <span class="d-votes">(${votes} votes)</span>
      <span class="d-sep">·</span>
      <span class="d-year">${year}</span>
      ${runtimeStr ? `<span class="d-sep">·</span><span class="d-runtime">${runtimeStr}</span>` : ""}
    </div>
    <div style="margin-bottom:10px;">${genreTags}</div>
    <div class="detail-overview">${escHtml(overview)}</div>
  `;

  // ── ACTIONS ──
  const trailer = findTrailer(videos.results || []);
  const actionsEl = $("detailActions");

  const renderActions = () => {
    const wl = inWatchlist(id);
    actionsEl.innerHTML = `
      ${trailer
        ? `<a href="https://www.youtube.com/watch?v=${trailer}" target="_blank" rel="noopener">
             <button class="btn-primary">▶ Watch Trailer</button>
           </a>`
        : ""}
      <button class="btn-ghost ${wl ? "in-list" : ""}" id="detailWlBtn">
        ${wl ? "✓ In My List" : "＋ Add to My List"}
      </button>
    `;
    $("detailWlBtn").onclick = () => {
      toggleWatchlist({ id, title, poster: detail.poster_path });
      renderActions();
    };
  };
  renderActions();

  // ── BOX OFFICE ──
  const profit = (revenue && budget) ? fmtMoney(revenue - budget) : "N/A";
  $("detailStats").innerHTML = `
    <div class="stat-card">
      <div class="stat-label">🌍 Worldwide Revenue</div>
      <div class="stat-value">${fmtMoney(revenue)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">🎥 Production Budget</div>
      <div class="stat-value">${fmtMoney(budget)}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">📈 Box Office Profit</div>
      <div class="stat-value">${profit}</div>
    </div>
  `;

  // ── CAST ──
  const cast = (credits.cast || []).slice(0, 12);
  if (cast.length) {
    show("castHeader");
    const castGrid = $("castGrid");
    castGrid.innerHTML = cast.map(c => {
      const ph = c.profile_path
        ? `<img class="cast-img" src="https://image.tmdb.org/t/p/w185${c.profile_path}" alt="${escHtml(c.name)}" loading="lazy" />`
        : `<div class="cast-no-img">👤</div>`;
      return `<div class="cast-card">
        ${ph}
        <div class="cast-name">${escHtml(c.name || "")}</div>
        <div class="cast-role">${escHtml(c.character || c.roles?.[0]?.character || "")}</div>
      </div>`;
    }).join("");
  }

  // ── DIRECTOR ──
  const crew = credits.crew || [];
  const director = crew.find(c => c.job === "Director" || c.known_for_department === "Directing");
  if (director) {
    const dw = $("directorWrap");
    const dImg = director.profile_path
      ? `<img class="dir-img" src="https://image.tmdb.org/t/p/w185${director.profile_path}" alt="${escHtml(director.name)}" loading="lazy" />`
      : "";
    dw.innerHTML = `
      ${dImg}
      <div>
        <div class="dir-label">Director</div>
        <div class="dir-name">${escHtml(director.name || "")}</div>
      </div>
    `;
    showEl(dw);
  }

  // ── TRAILER ──
  if (trailer) {
    show("trailerHeader");
    $("trailerWrap").innerHTML = `
      <iframe
        src="https://www.youtube.com/embed/${trailer}?rel=0&modestbranding=1"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
        loading="lazy"
      ></iframe>
    `;
  }

  // ── SCENES ──
  const backdrops = (images.backdrops || []).slice(0, 6);
  if (backdrops.length) {
    show("scenesHeader");
    $("sceneGrid").innerHTML = backdrops.map(img =>
      `<img class="scene-img" src="${BACKDROP}${img.file_path}" loading="lazy" alt="Scene" />`
    ).join("");
  }

  // ── RECOMMENDATIONS ──
  const recResults = recData.results || [];
  const recTotal   = Math.min(recData.total_pages || 1, 10);
  state.recPage    = 1;
  state.recTotal   = recTotal;

  if (recResults.length) {
    show("recHeader");
    renderCardRow($("rowRec"), recResults.slice(0, 6), isTV);
    renderPagination($("paginationRec"), 1, recTotal, async (p) => {
      state.recPage = p;
      showLoader();
      const d = isTV ? await tmdb.tvRec(id, p) : await tmdb.movieRec(id, p);
      hideLoader();
      renderCardRow($("rowRec"), (d.results || []).slice(0, 6), isTV);
      renderPagination($("paginationRec"), p, recTotal, () => {});
    });
  }
}

function findTrailer(videos) {
  const t = videos.find(v => v.type === "Trailer" && v.site === "YouTube");
  return t ? t.key : null;
}

/* ══════════════════════════════════════════════════════════════════
   SEARCH
   ══════════════════════════════════════════════════════════════════ */
let searchTimer = null;

$("searchInput").addEventListener("input", (e) => {
  const q = e.target.value.trim();
  $("searchClear").style.display = q ? "" : "none";
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => runSearch(q), 380);
});

$("searchClear").onclick = () => {
  $("searchInput").value = "";
  $("searchClear").style.display = "none";
  clearSearch();
};

async function runSearch(q) {
  if (!q) { clearSearch(); return; }

  // If not on home, go home first (search lives on home)
  if (state.page !== "home") {
    state.page = "home";
    state.prevPage = "home";
    showPage("home");
    await loadHome();
  }

  state.searchQuery = q;
  state.searchPage  = 1;

  // Hide normal sections
  $("hero").style.visibility = "hidden";
  document.querySelectorAll(".content-section:not(#searchSection)").forEach(s => hideEl(s));
  show("searchSection");

  await execSearch(q, 1);
}

async function execSearch(q, page) {
  showLoader();
  const data = await tmdb.search(q, page);
  hideLoader();

  const results = data.results || [];
  const total   = Math.min(data.total_pages || 1, 20);
  const found   = data.total_results || 0;

  $("searchLabel").innerHTML = `🔎 Results for "<em>${escHtml(q)}</em>" &nbsp;<span style="font-size:11px;color:rgba(255,255,255,0.3);font-weight:400;">${found.toLocaleString()} found</span>`;
  renderCardRow($("rowSearch"), results.slice(0, 12));
  renderPagination($("paginationSearch"), page, total, (p) => {
    state.searchPage = p;
    execSearch(q, p);
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

function clearSearch() {
  state.searchQuery = "";
  $("hero").style.visibility = "";
  document.querySelectorAll(".content-section").forEach(s => showEl(s));
  hide("searchSection");
  updateWlBadges(); // re-shows mylist section if needed
}

/* ══════════════════════════════════════════════════════════════════
   NAV LINKS
   ══════════════════════════════════════════════════════════════════ */
document.querySelectorAll("[data-page]").forEach(el => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    const pg = el.dataset.page;
    if      (pg === "home")   goHome();
    else if (pg === "movies") goMovies();
    else if (pg === "series") goSeries();
    else if (pg === "mylist") goMyList();
  });
});

/* ══════════════════════════════════════════════════════════════════
   NAVBAR SCROLL EFFECT
   ══════════════════════════════════════════════════════════════════ */
window.addEventListener("scroll", () => {
  $("navbar").classList.toggle("scrolled", window.scrollY > 40);
}, { passive: true });

/* ══════════════════════════════════════════════════════════════════
   UTILS
   ══════════════════════════════════════════════════════════════════ */
function escHtml(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ══════════════════════════════════════════════════════════════════
   INIT
   ══════════════════════════════════════════════════════════════════ */
(async function init() {
  updateWlBadges();
  await loadHome();
})();
