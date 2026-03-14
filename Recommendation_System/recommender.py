# ================================================================
#  CineMatch  —  Hybrid Movie Recommendation System (Tkinter GUI)
#  No extra libraries needed — pure Python + tkinter
#
#  Techniques:
#    1. Content-Based Filtering  — TF-IDF cosine similarity
#    2. Collaborative Filtering  — Pearson Correlation
#    3. Hybrid Engine            — blends both scores
#
#  Features:
#    ✅ Beautiful dark modern UI
#    ✅ Browse & search 30 movies
#    ✅ Click stars to rate movies
#    ✅ Get hybrid recommendations with score bars
#    ✅ Filter recommendations by genre
#    ✅ Animated loading bar while computing
#    ✅ Save report to .txt file
#    ✅ Tabbed layout: Browse / Rate / Recommend
# ================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
import threading
import time
from datetime import datetime
from collections import defaultdict

# ================================================================
# COLOURS — dark navy theme (matches chatbot + tictactoe)
# ================================================================
BG_DARK      = "#0f172a"
BG_CARD      = "#1e293b"
BG_HOVER     = "#2d3f55"
BG_INPUT     = "#1e293b"
BG_SIDEBAR   = "#1e293b"
ACCENT_BLUE  = "#3b82f6"
ACCENT_GREEN = "#22c55e"
ACCENT_RED   = "#ef4444"
ACCENT_GOLD  = "#f59e0b"
ACCENT_PURP  = "#8b5cf6"
TEXT_WHITE   = "#f1f5f9"
TEXT_DIM     = "#94a3b8"
TEXT_GREEN   = "#4ade80"
TEXT_YELLOW  = "#fbbf24"
TEXT_RED     = "#f87171"
BORDER       = "#334155"

# Genre → colour map
GENRE_COLORS = {
    "Action": "#ef4444", "Adventure": "#f59e0b", "Sci-Fi": "#3b82f6",
    "Drama": "#8b5cf6",  "Comedy": "#22c55e",    "Thriller": "#ec4899",
    "Crime": "#f97316",  "Horror": "#dc2626",     "Romance": "#f472b6",
    "Animation": "#06b6d4","Fantasy": "#a78bfa",  "History": "#84cc16",
    "Musical": "#e879f9","Music": "#e879f9",
}

# ================================================================
# DATASET — 30 movies
# ================================================================
MOVIES = [
    {"id":1,  "title":"The Shawshank Redemption","year":1994,"genres":["Drama"],
     "tags":"hope prison friendship redemption classic morgan-freeman"},
    {"id":2,  "title":"The Godfather",           "year":1972,"genres":["Crime","Drama"],
     "tags":"mafia family power crime al-pacino marlon-brando classic"},
    {"id":3,  "title":"The Dark Knight",         "year":2008,"genres":["Action","Thriller"],
     "tags":"superhero batman joker action christopher-nolan christian-bale"},
    {"id":4,  "title":"Pulp Fiction",            "year":1994,"genres":["Crime","Drama","Thriller"],
     "tags":"nonlinear crime violence quentin-tarantino samuel-jackson"},
    {"id":5,  "title":"Forrest Gump",            "year":1994,"genres":["Drama","Romance"],
     "tags":"life journey love history tom-hanks emotional classic"},
    {"id":6,  "title":"Inception",               "year":2010,"genres":["Action","Sci-Fi","Thriller"],
     "tags":"dream heist mind-bending christopher-nolan leonardo-dicaprio"},
    {"id":7,  "title":"The Matrix",              "year":1999,"genres":["Action","Sci-Fi"],
     "tags":"simulation reality hacker action keanu-reeves sci-fi"},
    {"id":8,  "title":"Interstellar",            "year":2014,"genres":["Sci-Fi","Drama"],
     "tags":"space time emotion christopher-nolan matthew-mcconaughey"},
    {"id":9,  "title":"Goodfellas",              "year":1990,"genres":["Crime","Drama"],
     "tags":"mafia crime gangster martin-scorsese robert-de-niro classic"},
    {"id":10, "title":"Fight Club",              "year":1999,"genres":["Drama","Thriller"],
     "tags":"identity violence twist brad-pitt edward-norton psychological"},
    {"id":11, "title":"The Silence of the Lambs","year":1991,"genres":["Crime","Thriller","Horror"],
     "tags":"serial-killer psychological fbi jodie-foster anthony-hopkins"},
    {"id":12, "title":"Schindler's List",        "year":1993,"genres":["Drama","History"],
     "tags":"holocaust war history liam-neeson steven-spielberg emotional"},
    {"id":13, "title":"The Lord of the Rings",   "year":2001,"genres":["Adventure","Fantasy"],
     "tags":"fantasy epic quest fellowship peter-jackson elijah-wood"},
    {"id":14, "title":"Star Wars: A New Hope",   "year":1977,"genres":["Action","Adventure","Sci-Fi"],
     "tags":"space opera hero lightsaber george-lucas mark-hamill classic"},
    {"id":15, "title":"Jurassic Park",           "year":1993,"genres":["Adventure","Sci-Fi"],
     "tags":"dinosaurs adventure science steven-spielberg sam-neill"},
    {"id":16, "title":"Titanic",                 "year":1997,"genres":["Drama","Romance"],
     "tags":"love ship tragedy romance james-cameron leonardo-dicaprio"},
    {"id":17, "title":"Avatar",                  "year":2009,"genres":["Action","Adventure","Sci-Fi"],
     "tags":"alien planet visuals action james-cameron sam-worthington"},
    {"id":18, "title":"The Avengers",            "year":2012,"genres":["Action","Adventure"],
     "tags":"superhero team marvel action ensemble joss-whedon"},
    {"id":19, "title":"Toy Story",               "year":1995,"genres":["Animation","Comedy"],
     "tags":"toys friendship animation pixar tom-hanks family"},
    {"id":20, "title":"The Lion King",           "year":1994,"genres":["Animation","Drama"],
     "tags":"lion kingdom family animation disney classic emotional"},
    {"id":21, "title":"Spirited Away",           "year":2002,"genres":["Animation","Fantasy"],
     "tags":"anime spirit world miyazaki magical japanese"},
    {"id":22, "title":"Parasite",                "year":2019,"genres":["Drama","Thriller"],
     "tags":"class inequality twist korean bong-joon-ho social"},
    {"id":23, "title":"Get Out",                 "year":2017,"genres":["Horror","Thriller"],
     "tags":"race social-commentary horror twist jordan-peele psychological"},
    {"id":24, "title":"Mad Max: Fury Road",      "year":2015,"genres":["Action","Adventure"],
     "tags":"post-apocalyptic cars action practical-effects george-miller"},
    {"id":25, "title":"La La Land",              "year":2016,"genres":["Drama","Romance","Musical"],
     "tags":"music love dreams los-angeles ryan-gosling emma-stone"},
    {"id":26, "title":"Whiplash",                "year":2014,"genres":["Drama","Music"],
     "tags":"ambition drumming music obsession miles-teller j-k-simmons"},
    {"id":27, "title":"The Grand Budapest Hotel","year":2014,"genres":["Comedy","Drama"],
     "tags":"quirky wes-anderson colourful comedy ralph-fiennes stylish"},
    {"id":28, "title":"Blade Runner 2049",       "year":2017,"genres":["Sci-Fi","Drama","Thriller"],
     "tags":"future ai replicant visuals sci-fi ryan-gosling harrison-ford"},
    {"id":29, "title":"Dune",                    "year":2021,"genres":["Sci-Fi","Adventure"],
     "tags":"desert planet prophecy epic denis-villeneuve timothee-chalamet"},
    {"id":30, "title":"Everything Everywhere",   "year":2022,"genres":["Action","Comedy","Sci-Fi"],
     "tags":"multiverse absurd family michelle-yeoh emotional action"},
]

RATINGS_DATA = {
    "Alice" : {1:5,5:5,12:4,16:4,20:5,25:4,26:5,27:3},
    "Bob"   : {3:5,6:5,7:5,10:4,18:5,24:4,28:5,29:5},
    "Carol" : {2:5,4:5,9:5,11:4,22:5,23:4,10:4},
    "Dave"  : {8:5,6:4,14:5,15:4,17:4,29:5,7:4,21:3},
    "Eve"   : {19:5,20:5,21:5,13:4,14:4,15:5,27:4,30:4},
    "Frank" : {1:4,9:5,12:5,2:4,4:4,11:5,22:4,26:4},
    "Grace" : {25:5,16:5,5:4,20:4,27:5,19:4,30:5,21:4},
    "Henry" : {3:5,18:5,24:5,7:4,17:4,29:4,6:5,28:4},
}

# ================================================================
# NLP — simple TF-IDF + Cosine Similarity (no sklearn needed)
# ================================================================
def build_tfidf(movies):
    """Build a simple TF-IDF matrix from movie features."""
    docs = []
    for m in movies:
        text = " ".join(m["genres"]).lower() + " " + m["tags"].lower()
        docs.append(text.split())

    # Build vocabulary
    vocab = {}
    for doc in docs:
        for word in set(doc):
            if word not in vocab:
                vocab[word] = len(vocab)

    N = len(docs)
    # Document frequency
    df = defaultdict(int)
    for doc in docs:
        for word in set(doc):
            df[word] += 1

    # TF-IDF vectors (as dicts for sparse representation)
    vectors = []
    for doc in docs:
        tf = defaultdict(float)
        for word in doc:
            tf[word] += 1
        vec = {}
        for word, count in tf.items():
            tfidf = (count / len(doc)) * math.log((N + 1) / (df[word] + 1))
            vec[vocab[word]] = tfidf
        vectors.append(vec)

    return vectors

def cosine_sim(v1, v2):
    """Cosine similarity between two sparse vectors (dicts)."""
    dot = sum(v1.get(k, 0) * v2.get(k, 0) for k in v1)
    mag1 = math.sqrt(sum(x*x for x in v1.values()))
    mag2 = math.sqrt(sum(x*x for x in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)

def pearson_correlation(ra, rb):
    """Pearson correlation between two rating dicts."""
    common = set(ra) & set(rb)
    if len(common) < 2:
        return 0.0
    a = [ra[m] for m in common]
    b = [rb[m] for m in common]
    ma, mb = sum(a)/len(a), sum(b)/len(b)
    num  = sum((x-ma)*(y-mb) for x,y in zip(a,b))
    dena = math.sqrt(sum((x-ma)**2 for x in a))
    denb = math.sqrt(sum((y-mb)**2 for y in b))
    if dena == 0 or denb == 0:
        return 0.0
    return num / (dena * denb)

class HybridEngine:
    def __init__(self, movies, ratings_data):
        self.movies       = movies
        self.ratings_data = ratings_data
        self.tfidf        = build_tfidf(movies)
        self.id_to_idx    = {m["id"]: i for i, m in enumerate(movies)}

    def content_scores(self, liked_ids, exclude_ids):
        scores = defaultdict(float)
        counts = defaultdict(int)
        for lid in liked_ids:
            row = self.id_to_idx.get(lid)
            if row is None: continue
            for i, movie in enumerate(self.movies):
                if movie["id"] in exclude_ids: continue
                sim = cosine_sim(self.tfidf[row], self.tfidf[i])
                scores[movie["id"]] += sim
                counts[movie["id"]] += 1
        return {mid: scores[mid]/counts[mid] for mid in scores if counts[mid]>0}

    def collab_scores(self, user_ratings, exclude_ids):
        sims = {}
        for uname, uratings in self.ratings_data.items():
            sim = pearson_correlation(user_ratings, uratings)
            if sim > 0:
                sims[uname] = sim
        if not sims: return {}
        weighted = defaultdict(float)
        sim_sum  = defaultdict(float)
        for uname, sim in sims.items():
            for mid, rating in self.ratings_data[uname].items():
                if mid not in exclude_ids:
                    weighted[mid] += sim * rating
                    sim_sum[mid]  += abs(sim)
        predicted = {mid: weighted[mid]/sim_sum[mid]
                     for mid in weighted if sim_sum[mid]>0}
        maxr = max(predicted.values()) if predicted else 1
        return {mid: v/maxr for mid, v in predicted.items()}

    def recommend(self, user_ratings, top_n=8):
        liked_ids   = [mid for mid, r in user_ratings.items() if r >= 4]
        exclude_ids = set(user_ratings.keys())
        cs = self.content_scores(liked_ids, exclude_ids)
        cf = self.collab_scores(user_ratings, exclude_ids)
        all_ids = set(cs) | set(cf)
        blended = {}
        for mid in all_ids:
            c  = cs.get(mid, 0)
            co = cf.get(mid, 0)
            if mid in cs and mid in cf:
                final = 0.5*c + 0.5*co
            elif mid in cs:
                final = c
            else:
                final = co
            blended[mid] = {"final": final,
                            "content": round(c*100,1),
                            "collab": round(co*100,1)}
        return sorted(blended.items(), key=lambda x: x[1]["final"], reverse=True)[:top_n]

    def get_movie(self, mid):
        for m in self.movies:
            if m["id"] == mid:
                return m
        return None

# ================================================================
# HELPER WIDGETS
# ================================================================
def make_genre_tag(parent, genre):
    color = GENRE_COLORS.get(genre, "#64748b")
    lbl = tk.Label(parent, text=genre,
                   font=("Arial", 9, "bold"),
                   bg=color, fg="white",
                   padx=6, pady=2)
    lbl.pack(side=tk.LEFT, padx=2)
    return lbl

def score_bar_canvas(parent, pct, width=120, height=10, color=ACCENT_GREEN):
    c = tk.Canvas(parent, width=width, height=height,
                  bg=BG_CARD, highlightthickness=0)
    filled = int((pct/100) * width)
    c.create_rectangle(0, 0, width, height, fill="#1e3a5f", outline="")
    if filled > 0:
        c.create_rectangle(0, 0, filled, height, fill=color, outline="")
    return c

# ================================================================
# MAIN APPLICATION
# ================================================================
class CineMatchApp:
    def __init__(self, root):
        self.root        = root
        self.root.title("CineMatch — Movie Recommendation System")
        self.root.geometry("860x640")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self.engine       = HybridEngine(MOVIES, RATINGS_DATA)
        self.user_ratings = {}
        self.last_recs    = []
        self.search_var   = tk.StringVar()
        self.genre_filter = tk.StringVar(value="All")

        self._build_ui()

    # ─────────────────────────────────────────────────────────────
    # MAIN UI
    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────
        topbar = tk.Frame(self.root, bg=BG_SIDEBAR, pady=12)
        topbar.pack(fill=tk.X)

        tk.Label(topbar, text="🎬 CineMatch",
                 font=("Arial", 20, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(side=tk.LEFT, padx=18)

        tk.Label(topbar, text="Hybrid Movie Recommendation System",
                 font=("Arial", 11),
                 bg=BG_SIDEBAR, fg=TEXT_DIM).pack(side=tk.LEFT, padx=4)

        # Save report button
        save_btn = tk.Button(topbar, text="💾 Save Report",
                             font=("Arial", 10, "bold"),
                             bg=ACCENT_PURP, fg=TEXT_WHITE,
                             relief=tk.FLAT, cursor="hand2",
                             padx=12, pady=5,
                             command=self._save_report)
        save_btn.pack(side=tk.RIGHT, padx=14)

        # ── Notebook (tabs) ──────────────────────────────────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.TNotebook",
                         background=BG_DARK, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                         background=BG_CARD, foreground=TEXT_DIM,
                         font=("Arial", 11, "bold"),
                         padding=[16, 8])
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", TEXT_WHITE)])

        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tab frames
        self.tab_browse  = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_rate    = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_recs    = tk.Frame(self.notebook, bg=BG_DARK)

        self.notebook.add(self.tab_browse, text="🎬 Browse Movies")
        self.notebook.add(self.tab_rate,   text="⭐ Rate Movies")
        self.notebook.add(self.tab_recs,   text="✨ Recommendations")

        self._build_browse_tab()
        self._build_rate_tab()
        self._build_recs_tab()

    # ─────────────────────────────────────────────────────────────
    # TAB 1 — BROWSE
    # ─────────────────────────────────────────────────────────────
    def _build_browse_tab(self):
        # Search + filter bar
        bar = tk.Frame(self.tab_browse, bg=BG_DARK, pady=10)
        bar.pack(fill=tk.X, padx=14)

        tk.Label(bar, text="Search:", font=("Arial", 11),
                 bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT)

        search_entry = tk.Entry(bar, textvariable=self.search_var,
                                font=("Arial", 11),
                                bg=BG_INPUT, fg=TEXT_WHITE,
                                insertbackground=TEXT_WHITE,
                                relief=tk.FLAT, width=22)
        search_entry.pack(side=tk.LEFT, padx=(6,14), ipady=6)
        self.search_var.trace("w", lambda *a: self._refresh_browse())

        tk.Label(bar, text="Genre:", font=("Arial", 11),
                 bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT)

        genres = ["All","Action","Adventure","Sci-Fi","Drama","Comedy",
                  "Thriller","Crime","Horror","Romance","Animation","Fantasy"]
        genre_menu = ttk.Combobox(bar, textvariable=self.genre_filter,
                                  values=genres, state="readonly",
                                  font=("Arial", 11), width=12)
        genre_menu.pack(side=tk.LEFT, padx=6)
        genre_menu.bind("<<ComboboxSelected>>", lambda e: self._refresh_browse())

        count_frame = tk.Frame(bar, bg=BG_DARK)
        count_frame.pack(side=tk.RIGHT)
        self.browse_count = tk.Label(count_frame, text="30 movies",
                                     font=("Arial", 10), bg=BG_DARK,
                                     fg=TEXT_DIM)
        self.browse_count.pack()

        # Scrollable movie grid
        outer = tk.Frame(self.tab_browse, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0,10))

        self.browse_canvas = tk.Canvas(outer, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL,
                          command=self.browse_canvas.yview)
        self.browse_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.browse_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.browse_inner = tk.Frame(self.browse_canvas, bg=BG_DARK)
        self.browse_win   = self.browse_canvas.create_window(
            (0,0), window=self.browse_inner, anchor=tk.NW)

        self.browse_inner.bind("<Configure>", lambda e: self.browse_canvas.configure(
            scrollregion=self.browse_canvas.bbox("all")))
        self.browse_canvas.bind("<Configure>", lambda e:
            self.browse_canvas.itemconfig(self.browse_win, width=e.width))
        self.browse_canvas.bind_all("<MouseWheel>", lambda e:
            self.browse_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._refresh_browse()

    def _refresh_browse(self):
        for w in self.browse_inner.winfo_children():
            w.destroy()

        query  = self.search_var.get().lower().strip()
        genre  = self.genre_filter.get()
        movies = MOVIES

        if query:
            movies = [m for m in movies if query in m["title"].lower()
                      or query in m["tags"].lower()]
        if genre != "All":
            movies = [m for m in movies if genre in m["genres"]]

        self.browse_count.config(text=f"{len(movies)} movies")

        for i, movie in enumerate(movies):
            self._movie_card(self.browse_inner, movie, i)

    def _movie_card(self, parent, movie, idx):
        bg = BG_CARD
        card = tk.Frame(parent, bg=bg, pady=8, padx=12,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill=tk.X, pady=4)

        # Left: ID badge + title + year
        left = tk.Frame(card, bg=bg)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        top_row = tk.Frame(left, bg=bg)
        top_row.pack(fill=tk.X)

        tk.Label(top_row, text=f"#{movie['id']:02d}",
                 font=("Arial", 10, "bold"),
                 bg=ACCENT_BLUE, fg=TEXT_WHITE,
                 padx=6, pady=1).pack(side=tk.LEFT, padx=(0,8))

        tk.Label(top_row, text=movie["title"],
                 font=("Arial", 13, "bold"),
                 bg=bg, fg=TEXT_WHITE).pack(side=tk.LEFT)

        tk.Label(top_row, text=str(movie["year"]),
                 font=("Arial", 10),
                 bg=bg, fg=TEXT_DIM).pack(side=tk.LEFT, padx=8)

        # Genre tags
        tag_row = tk.Frame(left, bg=bg)
        tag_row.pack(fill=tk.X, pady=(4,0))
        for g in movie["genres"]:
            make_genre_tag(tag_row, g)

        # Right: user rating display
        right = tk.Frame(card, bg=bg)
        right.pack(side=tk.RIGHT, padx=4)

        rating = self.user_ratings.get(movie["id"], 0)
        if rating:
            stars = "★" * rating + "☆" * (5-rating)
            tk.Label(right, text=stars,
                     font=("Arial", 13),
                     bg=bg, fg=ACCENT_GOLD).pack()
        else:
            tk.Label(right, text="not rated",
                     font=("Arial", 9),
                     bg=bg, fg=TEXT_DIM).pack()

    # ─────────────────────────────────────────────────────────────
    # TAB 2 — RATE
    # ─────────────────────────────────────────────────────────────
    def _build_rate_tab(self):
        # Instructions + stats bar
        info = tk.Frame(self.tab_rate, bg=BG_DARK, pady=10)
        info.pack(fill=tk.X, padx=14)

        tk.Label(info, text="Click the stars to rate a movie  (1–5 ★)",
                 font=("Arial", 11), bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT)

        self.rated_count_lbl = tk.Label(info, text="0 rated",
                                        font=("Arial", 11, "bold"),
                                        bg=BG_DARK, fg=ACCENT_GREEN)
        self.rated_count_lbl.pack(side=tk.RIGHT)

        # Quick-rate tip
        tk.Label(self.tab_rate,
                 text="Tip: Rate at least 3 movies for best recommendations",
                 font=("Arial", 10), bg=BG_DARK, fg=TEXT_DIM).pack(anchor=tk.W, padx=14)

        # Scrollable rate list
        outer = tk.Frame(self.tab_rate, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=(8,10))

        self.rate_canvas = tk.Canvas(outer, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL,
                          command=self.rate_canvas.yview)
        self.rate_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.rate_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.rate_inner = tk.Frame(self.rate_canvas, bg=BG_DARK)
        self.rate_win   = self.rate_canvas.create_window(
            (0,0), window=self.rate_inner, anchor=tk.NW)
        self.rate_inner.bind("<Configure>", lambda e: self.rate_canvas.configure(
            scrollregion=self.rate_canvas.bbox("all")))
        self.rate_canvas.bind("<Configure>", lambda e:
            self.rate_canvas.itemconfig(self.rate_win, width=e.width))
        self.rate_canvas.bind_all("<MouseWheel>", lambda e:
            self.rate_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.star_vars = {}
        for movie in MOVIES:
            self._rate_row(self.rate_inner, movie)

    def _rate_row(self, parent, movie):
        bg   = BG_CARD
        row  = tk.Frame(parent, bg=bg, pady=7, padx=12,
                        highlightbackground=BORDER, highlightthickness=1)
        row.pack(fill=tk.X, pady=3)

        # Title
        left = tk.Frame(row, bg=bg)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        title_row = tk.Frame(left, bg=bg)
        title_row.pack(fill=tk.X)
        tk.Label(title_row, text=movie["title"],
                 font=("Arial", 12, "bold"),
                 bg=bg, fg=TEXT_WHITE).pack(side=tk.LEFT)
        tk.Label(title_row, text=f" ({movie['year']})",
                 font=("Arial", 10), bg=bg, fg=TEXT_DIM).pack(side=tk.LEFT)

        # Genre tags (small)
        tag_row = tk.Frame(left, bg=bg)
        tag_row.pack(fill=tk.X, pady=(3,0))
        for g in movie["genres"]:
            make_genre_tag(tag_row, g)

        # Star rating widget
        right = tk.Frame(row, bg=bg)
        right.pack(side=tk.RIGHT)

        var = tk.IntVar(value=self.user_ratings.get(movie["id"], 0))
        self.star_vars[movie["id"]] = var
        star_frame = tk.Frame(right, bg=bg)
        star_frame.pack()

        def make_star_btn(mid, star_frame, var, n):
            lbl = tk.Label(star_frame, text="☆",
                           font=("Arial", 18), bg=bg, fg=ACCENT_GOLD,
                           cursor="hand2")
            lbl.pack(side=tk.LEFT)

            def on_click(rating=n, mid=mid, var=var):
                var.set(rating)
                self.user_ratings[mid] = rating
                self._update_star_display(mid)
                self._update_rated_count()
                self._refresh_browse()

            def on_hover(event, rating=n, mid=mid, var=var):
                self._highlight_stars(mid, rating)

            def on_leave(event, mid=mid, var=var):
                self._highlight_stars(mid, var.get())

            lbl.bind("<Button-1>", lambda e, f=on_click: f())
            lbl.bind("<Enter>",    on_hover)
            lbl.bind("<Leave>",    on_leave)
            return lbl

        self.star_vars[f"labels_{movie['id']}"] = []
        for n in range(1, 6):
            lbl = make_star_btn(movie["id"], star_frame, var, n)
            self.star_vars[f"labels_{movie['id']}"].append(lbl)

        # Clear button
        def clear_rating(mid=movie["id"]):
            self.user_ratings.pop(mid, None)
            self.star_vars[mid].set(0)
            self._update_star_display(mid)
            self._update_rated_count()
            self._refresh_browse()

        tk.Label(right, text="×", font=("Arial", 14),
                 bg=bg, fg=TEXT_DIM, cursor="hand2").pack(
            side=tk.LEFT, padx=(6,0)).bind("<Button-1>", lambda e: clear_rating())

        self._update_star_display(movie["id"])

    def _highlight_stars(self, mid, count):
        labels = self.star_vars.get(f"labels_{mid}", [])
        for i, lbl in enumerate(labels):
            lbl.config(text="★" if i < count else "☆",
                       fg=ACCENT_GOLD if i < count else "#475569")

    def _update_star_display(self, mid):
        self._highlight_stars(mid, self.user_ratings.get(mid, 0))

    def _update_rated_count(self):
        n = len(self.user_ratings)
        self.rated_count_lbl.config(text=f"{n} rated")

    # ─────────────────────────────────────────────────────────────
    # TAB 3 — RECOMMENDATIONS
    # ─────────────────────────────────────────────────────────────
    def _build_recs_tab(self):
        # Control bar
        ctrl = tk.Frame(self.tab_recs, bg=BG_DARK, pady=10)
        ctrl.pack(fill=tk.X, padx=14)

        self.get_recs_btn = tk.Button(
            ctrl, text="✨  Get My Recommendations",
            font=("Arial", 12, "bold"),
            bg=ACCENT_BLUE, fg=TEXT_WHITE,
            relief=tk.FLAT, cursor="hand2",
            padx=20, pady=8,
            command=self._compute_recs
        )
        self.get_recs_btn.pack(side=tk.LEFT)
        self.get_recs_btn.bind("<Enter>", lambda e: self.get_recs_btn.config(bg="#1d4ed8"))
        self.get_recs_btn.bind("<Leave>", lambda e: self.get_recs_btn.config(bg=ACCENT_BLUE))

        # Demo profile button
        demo_btn = tk.Button(
            ctrl, text="⚡ Load Demo Profile",
            font=("Arial", 11),
            bg=BG_CARD, fg=TEXT_DIM,
            relief=tk.FLAT, cursor="hand2",
            padx=14, pady=8,
            command=self._load_demo
        )
        demo_btn.pack(side=tk.LEFT, padx=10)
        demo_btn.bind("<Enter>", lambda e: demo_btn.config(fg=TEXT_WHITE, bg=BG_HOVER))
        demo_btn.bind("<Leave>", lambda e: demo_btn.config(fg=TEXT_DIM, bg=BG_CARD))

        self.rec_status = tk.Label(ctrl, text="",
                                   font=("Arial", 11),
                                   bg=BG_DARK, fg=TEXT_DIM)
        self.rec_status.pack(side=tk.LEFT, padx=10)

        # Progress bar (hidden initially)
        self.prog_frame = tk.Frame(self.tab_recs, bg=BG_DARK)
        self.prog_frame.pack(fill=tk.X, padx=14, pady=(0,6))
        self.prog_canvas = tk.Canvas(self.prog_frame, height=6,
                                     bg="#1e3a5f", highlightthickness=0)

        # Scrollable recs area
        outer = tk.Frame(self.tab_recs, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0,10))

        self.rec_canvas = tk.Canvas(outer, bg=BG_DARK, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL,
                          command=self.rec_canvas.yview)
        self.rec_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.rec_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.rec_inner = tk.Frame(self.rec_canvas, bg=BG_DARK)
        self.rec_win   = self.rec_canvas.create_window(
            (0,0), window=self.rec_inner, anchor=tk.NW)
        self.rec_inner.bind("<Configure>", lambda e: self.rec_canvas.configure(
            scrollregion=self.rec_canvas.bbox("all")))
        self.rec_canvas.bind("<Configure>", lambda e:
            self.rec_canvas.itemconfig(self.rec_win, width=e.width))
        self.rec_canvas.bind_all("<MouseWheel>", lambda e:
            self.rec_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Placeholder
        self.placeholder = tk.Label(self.rec_inner,
            text="Rate some movies ⭐ then click\n'Get My Recommendations'",
            font=("Arial", 13), bg=BG_DARK, fg=TEXT_DIM,
            justify=tk.CENTER)
        self.placeholder.pack(pady=80)

    def _load_demo(self):
        demo = {6:5, 7:5, 8:4, 3:5, 28:4}
        self.user_ratings = demo
        for mid, r in demo.items():
            if mid in self.star_vars:
                self.star_vars[mid].set(r)
            self._update_star_display(mid)
        self._update_rated_count()
        self._refresh_browse()
        self.rec_status.config(text="Demo profile loaded!", fg=ACCENT_GREEN)
        self.notebook.select(self.tab_recs)
        self.root.after(1500, lambda: self.rec_status.config(text=""))

    def _compute_recs(self):
        if not self.user_ratings:
            messagebox.showwarning("No Ratings",
                "Please rate at least 3 movies first!\nGo to the ⭐ Rate Movies tab.")
            return
        if len(self.user_ratings) < 2:
            messagebox.showinfo("More Ratings Needed",
                "Rate at least 2 movies for better recommendations!")

        self.get_recs_btn.config(state=tk.DISABLED)
        self.rec_status.config(text="Computing...", fg=TEXT_YELLOW)

        # Show animated progress bar
        self.prog_canvas.pack(fill=tk.X)
        self._animate_progress(0)

        threading.Thread(target=self._run_engine, daemon=True).start()

    def _animate_progress(self, pct):
        if pct > 100:
            return
        w = self.prog_frame.winfo_width()
        if w < 2: w = 800
        filled = int((pct / 100) * w)
        self.prog_canvas.config(width=w)
        self.prog_canvas.delete("all")
        self.prog_canvas.create_rectangle(0,0,w,6, fill="#1e3a5f", outline="")
        if filled > 0:
            self.prog_canvas.create_rectangle(0,0,filled,6,
                fill=ACCENT_BLUE, outline="")
        if pct <= 100:
            self.root.after(25, self._animate_progress, pct+3)

    def _run_engine(self):
        time.sleep(0.5)
        recs = self.engine.recommend(self.user_ratings, top_n=8)
        self.last_recs = recs
        self.root.after(0, self._show_recs, recs)

    def _show_recs(self, recs):
        for w in self.rec_inner.winfo_children():
            w.destroy()

        self.prog_canvas.pack_forget()
        self.get_recs_btn.config(state=tk.NORMAL)
        self.rec_status.config(text=f"{len(recs)} recommendations ready!",
                               fg=ACCENT_GREEN)

        if not recs:
            tk.Label(self.rec_inner, text="Not enough data to recommend.\nRate more movies!",
                     font=("Arial", 12), bg=BG_DARK, fg=TEXT_DIM).pack(pady=60)
            return

        # Header: based on
        liked = [self.engine.get_movie(mid) for mid, r in self.user_ratings.items() if r >= 4]
        if liked:
            based_frame = tk.Frame(self.rec_inner, bg=BG_DARK)
            based_frame.pack(fill=tk.X, pady=(0,8))
            tk.Label(based_frame, text="Based on: ",
                     font=("Arial", 10), bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT)
            for m in liked[:4]:
                if m:
                    tk.Label(based_frame, text=m["title"],
                             font=("Arial", 10, "bold"),
                             bg=BG_CARD, fg=TEXT_WHITE,
                             padx=8, pady=3).pack(side=tk.LEFT, padx=3)

        medals = {1:"🥇", 2:"🥈", 3:"🥉"}

        for rank, (mid, scores) in enumerate(recs, 1):
            movie = self.engine.get_movie(mid)
            if not movie: continue
            self._rec_card(self.rec_inner, movie, scores, rank, medals.get(rank,""))

        self.root.after(100, lambda: self.rec_canvas.yview_moveto(0))

    def _rec_card(self, parent, movie, scores, rank, medal):
        bg   = BG_CARD
        card = tk.Frame(parent, bg=bg, pady=12, padx=14,
                        highlightbackground=ACCENT_BLUE if rank<=3 else BORDER,
                        highlightthickness=2 if rank<=3 else 1)
        card.pack(fill=tk.X, pady=5)

        # ── Left column ───────────────────────────────────────
        left = tk.Frame(card, bg=bg)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Rank + title
        title_row = tk.Frame(left, bg=bg)
        title_row.pack(fill=tk.X)

        if medal:
            tk.Label(title_row, text=medal,
                     font=("Arial", 18), bg=bg).pack(side=tk.LEFT, padx=(0,6))

        tk.Label(title_row, text=f"#{rank}",
                 font=("Arial", 11, "bold"),
                 bg=ACCENT_BLUE, fg=TEXT_WHITE,
                 padx=6, pady=1).pack(side=tk.LEFT, padx=(0,8))

        tk.Label(title_row, text=movie["title"],
                 font=("Arial", 14, "bold"),
                 bg=bg, fg=TEXT_WHITE).pack(side=tk.LEFT)

        tk.Label(title_row, text=f"({movie['year']})",
                 font=("Arial", 10), bg=bg,
                 fg=TEXT_DIM).pack(side=tk.LEFT, padx=6)

        # Genres
        tag_row = tk.Frame(left, bg=bg)
        tag_row.pack(fill=tk.X, pady=(5,8))
        for g in movie["genres"]:
            make_genre_tag(tag_row, g)

        # Score bars
        final_pct = min(100, scores["final"] * 100)

        bars = [
            ("Overall match",   final_pct,           ACCENT_GREEN),
            ("Content-based",   scores["content"],   ACCENT_BLUE),
            ("Collaborative",   scores["collab"],    ACCENT_PURP),
        ]
        for label, pct, color in bars:
            bar_row = tk.Frame(left, bg=bg)
            bar_row.pack(fill=tk.X, pady=2)
            tk.Label(bar_row, text=f"{label:<16}",
                     font=("Arial", 10), bg=bg,
                     fg=TEXT_DIM, width=16, anchor=tk.W).pack(side=tk.LEFT)
            bar = score_bar_canvas(bar_row, pct, width=160, height=8, color=color)
            bar.pack(side=tk.LEFT, padx=6)
            tk.Label(bar_row, text=f"{pct:.0f}%",
                     font=("Arial", 10, "bold"),
                     bg=bg, fg=TEXT_WHITE).pack(side=tk.LEFT)

    # ─────────────────────────────────────────────────────────────
    # SAVE REPORT
    # ─────────────────────────────────────────────────────────────
    def _save_report(self):
        if not self.last_recs:
            messagebox.showinfo("No Recommendations",
                "Generate recommendations first!")
            return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"recommendations_{ts}.txt",
            filetypes=[("Text files","*.txt"),("All files","*.*")])
        if not path: return

        with open(path, "w", encoding="utf-8") as f:
            f.write("CineMatch — Hybrid Movie Recommendation Report\n")
            f.write(f"Generated: {datetime.now().strftime('%A, %d %B %Y at %I:%M %p')}\n")
            f.write("=" * 55 + "\n\n")
            f.write("YOUR RATINGS\n" + "-"*30 + "\n")
            for mid, r in self.user_ratings.items():
                m = self.engine.get_movie(mid)
                if m:
                    f.write(f"  {m['title']:<35} {'★'*r}{'☆'*(5-r)}\n")
            f.write("\nRECOMMENDATIONS\n" + "-"*30 + "\n")
            for rank, (mid, sc) in enumerate(self.last_recs, 1):
                m = self.engine.get_movie(mid)
                if m:
                    pct = min(100, sc["final"]*100)
                    f.write(f"  #{rank}  {m['title']:<35}  Match: {pct:.0f}%\n")
                    f.write(f"       Genres: {', '.join(m['genres'])}\n\n")
        messagebox.showinfo("Saved", f"Report saved to:\n{path}")

# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app  = CineMatchApp(root)
    root.mainloop()