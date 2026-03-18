# ================================================================
#  CineMatch  —  Movie Recommendation System (Tkinter GUI)
#  pip install pandas scikit-learn
#
#  Techniques:
#    1. Content-Based  — TF-IDF + Cosine Similarity (sklearn)
#    2. Collaborative  — Pearson Correlation (pandas)
#    3. Hybrid         — blends both scores 50/50
# ================================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, time
from datetime import datetime
from collections import defaultdict

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Colours ──────────────────────────────────────────────────────
BG       = "#0f172a"
CARD     = "#1e293b"
HOVER    = "#2d3f55"
BLUE     = "#3b82f6"
GREEN    = "#22c55e"
GOLD     = "#f59e0b"
PURP     = "#8b5cf6"
WHITE    = "#f1f5f9"
DIM      = "#94a3b8"
BORDER   = "#334155"

GENRE_CLR = {
    "Action":"#ef4444","Adventure":"#f59e0b","Sci-Fi":"#3b82f6",
    "Drama":"#8b5cf6","Comedy":"#22c55e","Thriller":"#ec4899",
    "Crime":"#f97316","Horror":"#dc2626","Romance":"#f472b6",
    "Animation":"#06b6d4","Fantasy":"#a78bfa","History":"#84cc16",
    "Musical":"#e879f9","Music":"#e879f9",
}

# ── Dataset ───────────────────────────────────────────────────────
RAW = [
    (1,"The Shawshank Redemption",1994,["Drama"],        "hope prison friendship redemption morgan-freeman"),
    (2,"The Godfather",           1972,["Crime","Drama"], "mafia family power al-pacino marlon-brando classic"),
    (3,"The Dark Knight",         2008,["Action","Thriller"],"batman joker nolan christian-bale superhero"),
    (4,"Pulp Fiction",            1994,["Crime","Thriller"],"nonlinear crime tarantino samuel-jackson"),
    (5,"Forrest Gump",            1994,["Drama","Romance"],"life journey love tom-hanks emotional"),
    (6,"Inception",               2010,["Action","Sci-Fi","Thriller"],"dream heist nolan dicaprio mind-bending"),
    (7,"The Matrix",              1999,["Action","Sci-Fi"],"simulation hacker keanu-reeves sci-fi"),
    (8,"Interstellar",            2014,["Sci-Fi","Drama"],"space time nolan mcconaughey emotional"),
    (9,"Goodfellas",              1990,["Crime","Drama"],"gangster mafia scorsese de-niro classic"),
    (10,"Fight Club",             1999,["Drama","Thriller"],"identity brad-pitt norton psychological twist"),
    (11,"Silence of the Lambs",   1991,["Crime","Thriller","Horror"],"serial-killer fbi jodie-foster anthony-hopkins"),
    (12,"Schindler's List",       1993,["Drama","History"],"holocaust war liam-neeson spielberg emotional"),
    (13,"The Lord of the Rings",  2001,["Adventure","Fantasy"],"fantasy quest fellowship peter-jackson"),
    (14,"Star Wars: A New Hope",  1977,["Action","Sci-Fi"],"space opera george-lucas lightsaber classic"),
    (15,"Jurassic Park",          1993,["Adventure","Sci-Fi"],"dinosaurs spielberg adventure science"),
    (16,"Titanic",                1997,["Drama","Romance"],"love ship tragedy james-cameron dicaprio"),
    (17,"Avatar",                 2009,["Action","Sci-Fi"],"alien planet james-cameron visuals action"),
    (18,"The Avengers",           2012,["Action","Adventure"],"superhero marvel team action ensemble"),
    (19,"Toy Story",              1995,["Animation","Comedy"],"toys pixar tom-hanks family friendship"),
    (20,"The Lion King",          1994,["Animation","Drama"],"lion disney family emotional classic"),
    (21,"Spirited Away",          2002,["Animation","Fantasy"],"anime miyazaki spirit magical japanese"),
    (22,"Parasite",               2019,["Drama","Thriller"],"class inequality korean bong-joon-ho twist"),
    (23,"Get Out",                2017,["Horror","Thriller"],"race jordan-peele psychological horror twist"),
    (24,"Mad Max: Fury Road",     2015,["Action","Adventure"],"post-apocalyptic cars george-miller action"),
    (25,"La La Land",             2016,["Drama","Romance","Musical"],"music love ryan-gosling emma-stone"),
    (26,"Whiplash",               2014,["Drama","Music"],"drumming ambition miles-teller obsession"),
    (27,"Grand Budapest Hotel",   2014,["Comedy","Drama"],"wes-anderson quirky ralph-fiennes stylish"),
    (28,"Blade Runner 2049",      2017,["Sci-Fi","Drama"],"future ai replicant ryan-gosling sci-fi"),
    (29,"Dune",                   2021,["Sci-Fi","Adventure"],"desert planet epic villeneuve chalamet"),
    (30,"Everything Everywhere",  2022,["Action","Comedy","Sci-Fi"],"multiverse michelle-yeoh absurd family"),
]

MOVIES_DF = pd.DataFrame(RAW, columns=["id","title","year","genres","tags"])
MOVIES_DF["features"] = MOVIES_DF["genres"].apply(
    lambda g: " ".join(g).lower()) + " " + MOVIES_DF["tags"]

RATINGS_DATA = {
    "Alice":{1:5,5:5,12:4,16:4,20:5,25:4,26:5},
    "Bob"  :{3:5,6:5,7:5,10:4,18:5,24:4,28:5,29:5},
    "Carol":{2:5,4:5,9:5,11:4,22:5,23:4},
    "Dave" :{8:5,6:4,14:5,15:4,17:4,29:5,7:4},
    "Eve"  :{19:5,20:5,21:5,13:4,14:4,15:5,30:4},
    "Frank":{1:4,9:5,12:5,2:4,11:5,22:4,26:4},
    "Grace":{25:5,16:5,5:4,20:4,27:5,19:4,30:5},
    "Henry":{3:5,18:5,24:5,7:4,17:4,29:4,6:5,28:4},
}

# ── Hybrid Engine ─────────────────────────────────────────────────
class HybridEngine:
    def __init__(self):
        vec = TfidfVectorizer(stop_words="english")
        self.tfidf   = vec.fit_transform(MOVIES_DF["features"])
        self.cos_sim = cosine_similarity(self.tfidf)
        self.id_idx  = {row.id: i for i, row in MOVIES_DF.iterrows()}

    def content_recs(self, liked_ids, exclude):
        scores = defaultdict(list)
        for lid in liked_ids:
            idx = self.id_idx.get(lid)
            if idx is None: continue
            for i, sim in enumerate(self.cos_sim[idx]):
                mid = int(MOVIES_DF.iloc[i]["id"])
                if mid not in exclude:
                    scores[mid].append(sim)
        return {mid: sum(v)/len(v) for mid, v in scores.items()}

    def collab_recs(self, user_ratings, exclude):
        df = pd.DataFrame(RATINGS_DATA).T
        user_series = pd.Series(user_ratings)
        sims = {}
        for name in df.index:
            common = user_series.index.intersection(
                df.loc[name].dropna().index)
            if len(common) < 2: continue
            try:
                corr = user_series[common].corr(df.loc[name][common])
                if corr > 0: sims[name] = corr
            except Exception:
                pass
        if not sims: return {}
        weighted = defaultdict(float)
        sim_sum  = defaultdict(float)
        for name, sim in sims.items():
            for mid, r in RATINGS_DATA[name].items():
                if mid not in exclude:
                    weighted[mid] += sim * r
                    sim_sum[mid]  += abs(sim)
        predicted = {m: weighted[m]/sim_sum[m] for m in weighted if sim_sum[m]>0}
        mx = max(predicted.values()) if predicted else 1
        return {m: v/mx for m, v in predicted.items()}

    def recommend(self, user_ratings, top_n=8):
        liked   = [m for m, r in user_ratings.items() if r >= 4]
        exclude = set(user_ratings)
        cs = self.content_recs(liked, exclude)
        cf = self.collab_recs(user_ratings, exclude)
        all_ids = set(cs) | set(cf)
        blended = {}
        for mid in all_ids:
            c, co = cs.get(mid, 0), cf.get(mid, 0)
            final = 0.5*c + 0.5*co if (mid in cs and mid in cf) else (c or co)
            blended[mid] = {"final": final,
                            "content": round(c*100,1),
                            "collab":  round(co*100,1)}
        return sorted(blended.items(), key=lambda x: x[1]["final"], reverse=True)[:top_n]

    def get_movie(self, mid):
        row = MOVIES_DF[MOVIES_DF["id"]==mid]
        return row.iloc[0] if len(row) else None

# ── Helpers ───────────────────────────────────────────────────────
def genre_tag(parent, genre):
    color = GENRE_CLR.get(genre, "#64748b")
    tk.Label(parent, text=genre, font=("Arial",9,"bold"),
             bg=color, fg="white", padx=6, pady=2).pack(side=tk.LEFT, padx=2)

def bar_widget(parent, pct, color, width=150):
    c = tk.Canvas(parent, width=width, height=8,
                  bg=CARD, highlightthickness=0)
    filled = int((pct/100)*width)
    c.create_rectangle(0,0,width,8, fill="#1e3a5f", outline="")
    if filled > 0:
        c.create_rectangle(0,0,filled,8, fill=color, outline="")
    return c

# ================================================================
# APP
# ================================================================
class CineMatchApp:
    def __init__(self, root):
        self.root         = root
        self.root.title("🎬 CineMatch — Recommendation System")
        self.root.geometry("820x620")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.engine       = HybridEngine()
        self.user_ratings = {}
        self.last_recs    = []
        self.star_labels  = {}   # mid → list of star Label widgets
        self.search_var   = tk.StringVar()
        self.genre_var    = tk.StringVar(value="All")

        self._ui()

    # ── TOP BAR ──────────────────────────────────────────────────
    def _ui(self):
        top = tk.Frame(self.root, bg=CARD, pady=10)
        top.pack(fill=tk.X)
        tk.Label(top, text="🎬  CineMatch",
                 font=("Arial",18,"bold"), bg=CARD, fg=WHITE).pack(side=tk.LEFT, padx=16)
        tk.Label(top, text="Hybrid Recommendation  •  Content-Based + Collaborative",
                 font=("Arial",10), bg=CARD, fg=DIM).pack(side=tk.LEFT, padx=4)

        save = tk.Button(top, text="💾 Save Report", font=("Arial",10,"bold"),
                         bg=PURP, fg=WHITE, relief=tk.FLAT, cursor="hand2",
                         padx=10, pady=4, command=self._save)
        save.pack(side=tk.RIGHT, padx=14)

        # Tabs
        style = ttk.Style()
        style.theme_use("default")
        style.configure("T.TNotebook", background=BG, borderwidth=0)
        style.configure("T.TNotebook.Tab", background=CARD, foreground=DIM,
                        font=("Arial",11,"bold"), padding=[14,7])
        style.map("T.TNotebook.Tab",
                  background=[("selected", BLUE)],
                  foreground=[("selected", WHITE)])

        nb = ttk.Notebook(self.root, style="T.TNotebook")
        nb.pack(fill=tk.BOTH, expand=True)

        t1 = tk.Frame(nb, bg=BG)
        t2 = tk.Frame(nb, bg=BG)
        t3 = tk.Frame(nb, bg=BG)
        nb.add(t1, text="🎬  Browse")
        nb.add(t2, text="⭐  Rate")
        nb.add(t3, text="✨  Recommend")

        self._browse_tab(t1)
        self._rate_tab(t2)
        self._rec_tab(t3)

    # ── SCROLL FRAME HELPER ───────────────────────────────────────
    def _scroll_frame(self, parent):
        outer = tk.Frame(parent, bg=BG)
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,8))
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = tk.Frame(canvas, bg=BG)
        win   = canvas.create_window((0,0), window=inner, anchor=tk.NW)
        inner.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e:
            canvas.itemconfig(win, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e:
            canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return inner

    # ── TAB 1: BROWSE ─────────────────────────────────────────────
    def _browse_tab(self, parent):
        bar = tk.Frame(parent, bg=BG, pady=8)
        bar.pack(fill=tk.X, padx=12)
        tk.Label(bar, text="Search:", font=("Arial",11), bg=BG, fg=DIM).pack(side=tk.LEFT)
        tk.Entry(bar, textvariable=self.search_var, font=("Arial",11),
                 bg=CARD, fg=WHITE, insertbackground=WHITE, relief=tk.FLAT,
                 width=20).pack(side=tk.LEFT, padx=(6,14), ipady=5)
        self.search_var.trace("w", lambda *_: self._refresh_browse())

        tk.Label(bar, text="Genre:", font=("Arial",11), bg=BG, fg=DIM).pack(side=tk.LEFT)
        genres = ["All","Action","Adventure","Sci-Fi","Drama","Comedy",
                  "Thriller","Crime","Horror","Romance","Animation","Fantasy"]
        combo = ttk.Combobox(bar, textvariable=self.genre_var,
                             values=genres, state="readonly", width=12)
        combo.pack(side=tk.LEFT, padx=6)
        combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_browse())

        self.browse_count = tk.Label(bar, text="30 movies",
                                     font=("Arial",10), bg=BG, fg=DIM)
        self.browse_count.pack(side=tk.RIGHT)

        self.browse_inner = self._scroll_frame(parent)
        self._refresh_browse()

    def _refresh_browse(self):
        for w in self.browse_inner.winfo_children():
            w.destroy()
        q = self.search_var.get().lower()
        g = self.genre_var.get()
        movies = MOVIES_DF
        if q:
            movies = movies[movies["title"].str.lower().str.contains(q) |
                            movies["tags"].str.lower().str.contains(q)]
        if g != "All":
            movies = movies[movies["genres"].apply(lambda gs: g in gs)]
        self.browse_count.config(text=f"{len(movies)} movies")
        for _, row in movies.iterrows():
            self._browse_card(self.browse_inner, row)

    def _browse_card(self, parent, row):
        card = tk.Frame(parent, bg=CARD, pady=7, padx=12,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill=tk.X, pady=3)
        top = tk.Frame(card, bg=CARD)
        top.pack(fill=tk.X)
        tk.Label(top, text=f"#{int(row.id):02d}", font=("Arial",9,"bold"),
                 bg=BLUE, fg=WHITE, padx=5, pady=1).pack(side=tk.LEFT, padx=(0,8))
        tk.Label(top, text=row.title, font=("Arial",12,"bold"),
                 bg=CARD, fg=WHITE).pack(side=tk.LEFT)
        tk.Label(top, text=str(int(row.year)), font=("Arial",9),
                 bg=CARD, fg=DIM).pack(side=tk.LEFT, padx=6)
        r = self.user_ratings.get(int(row.id), 0)
        tk.Label(top, text=("★"*r + "☆"*(5-r)) if r else "not rated",
                 font=("Arial",12), bg=CARD,
                 fg=GOLD if r else DIM).pack(side=tk.RIGHT)
        gr = tk.Frame(card, bg=CARD)
        gr.pack(fill=tk.X, pady=(4,0))
        for g in row.genres:
            genre_tag(gr, g)

    # ── TAB 2: RATE ───────────────────────────────────────────────
    def _rate_tab(self, parent):
        info = tk.Frame(parent, bg=BG, pady=8)
        info.pack(fill=tk.X, padx=12)
        tk.Label(info, text="Hover & click stars to rate (1–5)",
                 font=("Arial",11), bg=BG, fg=DIM).pack(side=tk.LEFT)
        self.rated_lbl = tk.Label(info, text="0 rated",
                                  font=("Arial",11,"bold"), bg=BG, fg=GREEN)
        self.rated_lbl.pack(side=tk.RIGHT)

        self.rate_inner = self._scroll_frame(parent)
        for _, row in MOVIES_DF.iterrows():
            self._rate_card(self.rate_inner, row)

    def _rate_card(self, parent, row):
        mid  = int(row.id)
        card = tk.Frame(parent, bg=CARD, pady=7, padx=12,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill=tk.X, pady=3)

        left = tk.Frame(card, bg=CARD)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(left, text=f"{row.title}  ({int(row.year)})",
                 font=("Arial",12,"bold"), bg=CARD, fg=WHITE).pack(anchor=tk.W)
        gr = tk.Frame(left, bg=CARD)
        gr.pack(anchor=tk.W, pady=(3,0))
        for g in row.genres:
            genre_tag(gr, g)

        # Stars
        right = tk.Frame(card, bg=CARD)
        right.pack(side=tk.RIGHT)
        stars = []
        for n in range(1, 6):
            lbl = tk.Label(right, text="☆", font=("Arial",18),
                           bg=CARD, fg=GOLD, cursor="hand2")
            lbl.pack(side=tk.LEFT)
            stars.append(lbl)

        def refresh_stars(count):
            for i, s in enumerate(stars):
                s.config(text="★" if i < count else "☆",
                         fg=GOLD if i < count else "#475569")

        def on_enter(n):
            refresh_stars(n)

        def on_leave(_):
            refresh_stars(self.user_ratings.get(mid, 0))

        def on_click(n):
            self.user_ratings[mid] = n
            refresh_stars(n)
            self.rated_lbl.config(text=f"{len(self.user_ratings)} rated")
            self._refresh_browse()

        for i, lbl in enumerate(stars):
            n = i + 1
            lbl.bind("<Enter>",    lambda e, n=n: on_enter(n))
            lbl.bind("<Leave>",    on_leave)
            lbl.bind("<Button-1>", lambda e, n=n: on_click(n))

        # × clear button — use a separate Label, bind separately
        clr = tk.Label(right, text=" ×", font=("Arial",14),
                       bg=CARD, fg=DIM, cursor="hand2")
        clr.pack(side=tk.LEFT, padx=(4,0))

        def do_clear(e, mid=mid, rf=refresh_stars):
            self.user_ratings.pop(mid, None)
            rf(0)
            self.rated_lbl.config(text=f"{len(self.user_ratings)} rated")
            self._refresh_browse()

        clr.bind("<Button-1>", do_clear)
        self.star_labels[mid] = (stars, refresh_stars)

        refresh_stars(self.user_ratings.get(mid, 0))

    # ── TAB 3: RECOMMEND ─────────────────────────────────────────
    def _rec_tab(self, parent):
        ctrl = tk.Frame(parent, bg=BG, pady=10)
        ctrl.pack(fill=tk.X, padx=12)

        self.go_btn = tk.Button(ctrl, text="✨  Get Recommendations",
                                font=("Arial",12,"bold"),
                                bg=BLUE, fg=WHITE, relief=tk.FLAT,
                                cursor="hand2", padx=18, pady=7,
                                command=self._run_recs)
        self.go_btn.pack(side=tk.LEFT)
        self.go_btn.bind("<Enter>", lambda e: self.go_btn.config(bg="#1d4ed8"))
        self.go_btn.bind("<Leave>", lambda e: self.go_btn.config(bg=BLUE))

        demo = tk.Button(ctrl, text="⚡ Demo Profile",
                         font=("Arial",11), bg=CARD, fg=DIM,
                         relief=tk.FLAT, cursor="hand2",
                         padx=12, pady=7, command=self._demo)
        demo.pack(side=tk.LEFT, padx=10)
        demo.bind("<Enter>", lambda e: demo.config(fg=WHITE, bg=HOVER))
        demo.bind("<Leave>", lambda e: demo.config(fg=DIM,   bg=CARD))

        self.rec_status = tk.Label(ctrl, text="",
                                   font=("Arial",11), bg=BG, fg=DIM)
        self.rec_status.pack(side=tk.LEFT, padx=8)

        # Progress bar
        self.prog_outer = tk.Frame(parent, bg=BG)
        self.prog_outer.pack(fill=tk.X, padx=12, pady=(0,4))
        self.prog_canvas = tk.Canvas(self.prog_outer, height=6,
                                     bg="#1e3a5f", highlightthickness=0)

        self.rec_inner = self._scroll_frame(parent)

        # Placeholder
        self.placeholder = tk.Label(self.rec_inner,
            text="Rate some movies ⭐  then click  ✨ Get Recommendations",
            font=("Arial",13), bg=BG, fg=DIM)
        self.placeholder.pack(pady=80)

    def _demo(self):
        demo_ratings = {6:5, 7:5, 8:4, 3:5, 28:4}
        for mid, r in demo_ratings.items():
            self.user_ratings[mid] = r
            if mid in self.star_labels:
                _, rf = self.star_labels[mid]
                rf(r)
        self.rated_lbl.config(text=f"{len(self.user_ratings)} rated")
        self._refresh_browse()
        self.rec_status.config(text="Demo profile loaded!", fg=GREEN)
        self.root.after(2000, lambda: self.rec_status.config(text=""))

    def _run_recs(self):
        if not self.user_ratings:
            messagebox.showwarning("No Ratings",
                "Rate at least 3 movies first!\nGo to the ⭐ Rate tab.")
            return
        self.go_btn.config(state=tk.DISABLED)
        self.rec_status.config(text="Computing...", fg="#fbbf24")
        self.prog_canvas.pack(fill=tk.X)
        self._progress(0)
        threading.Thread(target=self._engine_thread, daemon=True).start()

    def _progress(self, pct):
        if pct > 100: return
        w = max(self.prog_outer.winfo_width(), 400)
        self.prog_canvas.config(width=w)
        self.prog_canvas.delete("all")
        self.prog_canvas.create_rectangle(0,0,w,6, fill="#1e3a5f", outline="")
        filled = int((pct/100)*w)
        if filled > 0:
            self.prog_canvas.create_rectangle(0,0,filled,6, fill=BLUE, outline="")
        if pct <= 100:
            self.root.after(20, self._progress, pct+4)

    def _engine_thread(self):
        time.sleep(0.6)
        recs = self.engine.recommend(self.user_ratings, top_n=8)
        self.last_recs = recs
        self.root.after(0, self._show_recs, recs)

    def _show_recs(self, recs):
        for w in self.rec_inner.winfo_children():
            w.destroy()
        self.prog_canvas.pack_forget()
        self.go_btn.config(state=tk.NORMAL)
        self.rec_status.config(text=f"{len(recs)} recommendations ready!", fg=GREEN)

        if not recs:
            tk.Label(self.rec_inner, text="Not enough data. Rate more movies!",
                     font=("Arial",12), bg=BG, fg=DIM).pack(pady=60)
            return

        medals = {1:"🥇", 2:"🥈", 3:"🥉"}
        for rank, (mid, sc) in enumerate(recs, 1):
            movie = self.engine.get_movie(mid)
            if movie is None: continue
            self._rec_card(self.rec_inner, movie, sc, rank, medals.get(rank,""))

        self.root.after(80, lambda: self.rec_inner.winfo_toplevel())

    def _rec_card(self, parent, movie, sc, rank, medal):
        border = BLUE if rank <= 3 else BORDER
        bw     = 2    if rank <= 3 else 1
        card   = tk.Frame(parent, bg=CARD, pady=10, padx=14,
                          highlightbackground=border, highlightthickness=bw)
        card.pack(fill=tk.X, pady=5)

        # Title row
        top = tk.Frame(card, bg=CARD)
        top.pack(fill=tk.X)
        if medal:
            tk.Label(top, text=medal, font=("Arial",16), bg=CARD).pack(side=tk.LEFT, padx=(0,4))
        tk.Label(top, text=f"#{rank}", font=("Arial",9,"bold"),
                 bg=BLUE, fg=WHITE, padx=5, pady=1).pack(side=tk.LEFT, padx=(0,8))
        tk.Label(top, text=movie.title, font=("Arial",13,"bold"),
                 bg=CARD, fg=WHITE).pack(side=tk.LEFT)
        tk.Label(top, text=f"({int(movie.year)})", font=("Arial",10),
                 bg=CARD, fg=DIM).pack(side=tk.LEFT, padx=5)

        # Genres
        gr = tk.Frame(card, bg=CARD)
        gr.pack(fill=tk.X, pady=(5,8))
        for g in movie.genres:
            genre_tag(gr, g)

        # Score bars
        final_pct = min(100, sc["final"]*100)
        for label, pct, color in [
            ("Overall match", final_pct,       GREEN),
            ("Content-based", sc["content"],   BLUE),
            ("Collaborative", sc["collab"],    PURP),
        ]:
            row = tk.Frame(card, bg=CARD)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=("Arial",10),
                     bg=CARD, fg=DIM, width=14, anchor=tk.W).pack(side=tk.LEFT)
            bar = bar_widget(row, pct, color, width=160)
            bar.pack(side=tk.LEFT, padx=6)
            tk.Label(row, text=f"{pct:.0f}%", font=("Arial",10,"bold"),
                     bg=CARD, fg=WHITE).pack(side=tk.LEFT)

    # ── SAVE REPORT ───────────────────────────────────────────────
    def _save(self):
        if not self.last_recs:
            messagebox.showinfo("No Data", "Generate recommendations first!")
            return
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"recommendations_{ts}.txt",
            filetypes=[("Text","*.txt"),("All","*.*")])
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write("CineMatch — Recommendation Report\n")
            f.write(f"Generated: {datetime.now().strftime('%d %B %Y  %I:%M %p')}\n")
            f.write("="*50+"\n\nYOUR RATINGS\n"+"-"*30+"\n")
            for mid, r in self.user_ratings.items():
                m = self.engine.get_movie(mid)
                if m is not None:
                    f.write(f"  {m.title:<35} {'★'*r}{'☆'*(5-r)}\n")
            f.write("\nRECOMMENDATIONS\n"+"-"*30+"\n")
            for rank, (mid, sc) in enumerate(self.last_recs, 1):
                m = self.engine.get_movie(mid)
                if m is not None:
                    pct = min(100, sc["final"]*100)
                    f.write(f"  #{rank}  {m.title:<35} Match: {pct:.0f}%\n")
        messagebox.showinfo("Saved!", f"Report saved:\n{path}")

# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app  = CineMatchApp(root)
    root.mainloop()