# ================================================================
#  Tic-Tac-Toe AI  —  Beautiful Tkinter GUI  (Upgraded)
#  No extra libraries needed — pure Python + tkinter
#
#  Upgrades vs original:
#    ✅ Modern dark UI with gradient-style colors
#    ✅ Animated X and O placement (fade-in effect)
#    ✅ Win-line cells highlighted in green
#    ✅ Lose-line cells highlighted in red
#    ✅ Score tracker (You / Draws / AI)
#    ✅ Status bar ("Your turn", "AI thinking...", etc.)
#    ✅ Difficulty selector (Easy / Medium / Hard)
#    ✅ Hover effects on buttons
#    ✅ Smooth restart — no messagebox popup
#    ✅ Same minimax logic as original, 100% intact
# ================================================================

import tkinter as tk
import math
import random
import time
import threading

# ================================================================
# COLOURS  — dark navy theme
# ================================================================
BG_DARK     = "#0f172a"   # main background
BG_CARD     = "#1e293b"   # cell background
BG_HOVER    = "#2d3f55"   # cell hover
BG_WIN      = "#166534"   # winning cell (green)
BG_LOSE     = "#7f1d1d"   # losing cell (red)
BG_DRAW     = "#374151"   # draw cell
ACCENT_BLUE = "#3b82f6"   # X colour
ACCENT_RED  = "#ef4444"   # O colour
TEXT_WHITE  = "#f1f5f9"
TEXT_DIM    = "#64748b"
TEXT_GREEN  = "#4ade80"
TEXT_YELLOW = "#fbbf24"
BTN_GREEN   = "#22c55e"
BTN_HOVER   = "#16a34a"
BORDER      = "#334155"

# ================================================================
# GAME LOGIC  (your original logic — unchanged)
# ================================================================
human = "X"
ai    = "O"

WIN_CONDITIONS = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
]

def check_winner(b):
    for condition in WIN_CONDITIONS:
        a, b1, c = condition
        if b[a] == b[b1] == b[c] and b[a] != "":
            return b[a], condition
    if "" not in b:
        return "Draw", []
    return None, None

# ================================================================
# MINIMAX  (your original logic — unchanged)
# ================================================================
def minimax(new_board, is_maximizing):
    result, _ = check_winner(new_board)
    if result == ai:    return 1
    if result == human: return -1
    if result == "Draw": return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if new_board[i] == "":
                new_board[i] = ai
                score = minimax(new_board, False)
                new_board[i] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if new_board[i] == "":
                new_board[i] = human
                score = minimax(new_board, True)
                new_board[i] = ""
                best_score = min(score, best_score)
        return best_score

def best_move(board):
    best_score = -math.inf
    move = None
    for i in range(9):
        if board[i] == "":
            board[i] = ai
            score = minimax(board, False)
            board[i] = ""
            if score > best_score:
                best_score = score
                move = i
    return move

def get_ai_move(board, difficulty):
    empty = [i for i in range(9) if board[i] == ""]
    if difficulty == "Easy":
        return random.choice(empty)
    if difficulty == "Medium" and random.random() < 0.5:
        return random.choice(empty)
    return best_move(board)

# ================================================================
# MAIN APPLICATION CLASS
# ================================================================
class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe AI")
        self.root.geometry("420x620")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        # Game state
        self.board      = [""] * 9
        self.game_over  = False
        self.difficulty = tk.StringVar(value="Hard")
        self.scores     = {"X": 0, "Draw": 0, "O": 0}
        self.game_count = 0

        self._build_ui()

    # ────────────────────────────────────────────────────────────
    # UI BUILDER
    # ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Title ─────────────────────────────────────────────
        title_frame = tk.Frame(self.root, bg=BG_DARK)
        title_frame.pack(pady=(18, 4))

        tk.Label(
            title_frame, text="🤖 Tic Tac Toe AI",
            font=("Arial", 22, "bold"),
            bg=BG_DARK, fg=TEXT_WHITE
        ).pack()

        # ── Difficulty selector ────────────────────────────────
        diff_frame = tk.Frame(self.root, bg=BG_DARK)
        diff_frame.pack(pady=(0, 8))

        tk.Label(diff_frame, text="Difficulty:",
                 font=("Arial", 11), bg=BG_DARK,
                 fg=TEXT_DIM).pack(side=tk.LEFT, padx=(0, 6))

        for level in ("Easy", "Medium", "Hard"):
            rb = tk.Radiobutton(
                diff_frame, text=level,
                variable=self.difficulty, value=level,
                font=("Arial", 11, "bold"),
                bg=BG_DARK, fg=TEXT_WHITE,
                selectcolor=BG_CARD,
                activebackground=BG_DARK,
                activeforeground=TEXT_WHITE,
                command=self.reset_game
            )
            rb.pack(side=tk.LEFT, padx=4)

        # ── Scoreboard ─────────────────────────────────────────
        score_frame = tk.Frame(self.root, bg=BG_DARK)
        score_frame.pack(pady=(0, 10))

        self.score_labels = {}
        score_data = [
            ("You (X)", "X", ACCENT_BLUE),
            ("Draws",  "Draw", TEXT_DIM),
            ("AI  (O)", "O",  ACCENT_RED),
        ]
        for label_text, key, color in score_data:
            card = tk.Frame(score_frame, bg=BG_CARD,
                            highlightbackground=BORDER,
                            highlightthickness=1)
            card.pack(side=tk.LEFT, padx=6, ipadx=14, ipady=6)
            tk.Label(card, text=label_text,
                     font=("Arial", 9), bg=BG_CARD,
                     fg=TEXT_DIM).pack()
            lbl = tk.Label(card, text="0",
                           font=("Arial", 20, "bold"),
                           bg=BG_CARD, fg=color)
            lbl.pack()
            self.score_labels[key] = lbl

        # ── Status bar ─────────────────────────────────────────
        self.status_var = tk.StringVar(value="Your turn  —  place X")
        self.status_lbl = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Arial", 13, "bold"),
            bg=BG_DARK, fg=TEXT_YELLOW,
            height=2
        )
        self.status_lbl.pack()

        # ── Game board ─────────────────────────────────────────
        board_outer = tk.Frame(self.root, bg=BORDER, padx=3, pady=3)
        board_outer.pack()

        board_frame = tk.Frame(board_outer, bg=BG_DARK)
        board_frame.pack()

        self.buttons = []
        for i in range(9):
            btn = tk.Button(
                board_frame,
                text="",
                font=("Arial", 30, "bold"),
                width=4, height=2,
                bg=BG_CARD, fg=TEXT_WHITE,
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda idx=i: self.player_move(idx)
            )
            btn.grid(row=i // 3, column=i % 3, padx=3, pady=3)
            btn.bind("<Enter>", lambda e, b=btn: self._on_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_hover(b, False))
            self.buttons.append(btn)

        # ── Restart button ─────────────────────────────────────
        self.restart_btn = tk.Button(
            self.root,
            text="⟳  New Game",
            font=("Arial", 13, "bold"),
            bg=BTN_GREEN, fg="white",
            relief=tk.FLAT, cursor="hand2",
            padx=20, pady=8,
            command=self.reset_game
        )
        self.restart_btn.pack(pady=18)
        self.restart_btn.bind("<Enter>",
            lambda e: self.restart_btn.config(bg=BTN_HOVER))
        self.restart_btn.bind("<Leave>",
            lambda e: self.restart_btn.config(bg=BTN_GREEN))

        # ── Game counter ───────────────────────────────────────
        self.game_lbl = tk.Label(
            self.root, text="Game 1",
            font=("Arial", 10), bg=BG_DARK, fg=TEXT_DIM
        )
        self.game_lbl.pack()

    # ────────────────────────────────────────────────────────────
    # HOVER EFFECT
    # ────────────────────────────────────────────────────────────
    def _on_hover(self, btn, entering):
        if btn["text"] == "" and not self.game_over:
            btn.config(bg=BG_HOVER if entering else BG_CARD)

    # ────────────────────────────────────────────────────────────
    # PLAYER MOVE
    # ────────────────────────────────────────────────────────────
    def player_move(self, i):
        if self.board[i] != "" or self.game_over:
            return

        self.board[i] = human
        self._animate_place(i, human)

        winner, line = check_winner(self.board)
        if winner:
            self._end_game(winner, line)
            return

        self.game_over = True   # lock board while AI thinks
        self.status_var.set("AI is thinking…")
        self.status_lbl.config(fg=TEXT_DIM)
        self.root.after(400, self._ai_turn)

    # ────────────────────────────────────────────────────────────
    # AI TURN
    # ────────────────────────────────────────────────────────────
    def _ai_turn(self):
        move = get_ai_move(self.board, self.difficulty.get())
        if move is not None:
            self.board[move] = ai
            self._animate_place(move, ai)

        winner, line = check_winner(self.board)
        if winner:
            self._end_game(winner, line)
        else:
            self.game_over = False
            self.status_var.set("Your turn  —  place X")
            self.status_lbl.config(fg=TEXT_YELLOW)

    # ────────────────────────────────────────────────────────────
    # PIECE ANIMATION  (quick pop-in via font size growth)
    # ────────────────────────────────────────────────────────────
    def _animate_place(self, idx, mark):
        color = ACCENT_BLUE if mark == human else ACCENT_RED
        btn   = self.buttons[idx]
        btn.config(text=mark, fg=color, state=tk.DISABLED,
                   disabledforeground=color)

        # Grow font size from 10 → 30 over 6 frames
        def grow(size):
            if size <= 30:
                btn.config(font=("Arial", size, "bold"))
                self.root.after(18, grow, size + 4)

        grow(10)

    # ────────────────────────────────────────────────────────────
    # END GAME
    # ────────────────────────────────────────────────────────────
    def _end_game(self, winner, line):
        self.game_over = True

        if winner == "Draw":
            self.scores["Draw"] += 1
            self.status_var.set("It's a draw!")
            self.status_lbl.config(fg=TEXT_DIM)
            for btn in self.buttons:
                btn.config(bg=BG_DRAW)
        elif winner == human:
            self.scores["X"] += 1
            self.status_var.set("🎉  You win!")
            self.status_lbl.config(fg=TEXT_GREEN)
            for idx in line:
                self.buttons[idx].config(bg=BG_WIN)
        else:
            self.scores["O"] += 1
            self.status_var.set("AI wins!  Try again.")
            self.status_lbl.config(fg=ACCENT_RED)
            for idx in line:
                self.buttons[idx].config(bg=BG_LOSE)

        self._update_scores()

    # ────────────────────────────────────────────────────────────
    # UPDATE SCORE DISPLAY
    # ────────────────────────────────────────────────────────────
    def _update_scores(self):
        for key, lbl in self.score_labels.items():
            lbl.config(text=str(self.scores[key]))

    # ────────────────────────────────────────────────────────────
    # RESET
    # ────────────────────────────────────────────────────────────
    def reset_game(self):
        self.board     = [""] * 9
        self.game_over = False
        self.game_count += 1
        self.game_lbl.config(text=f"Game {self.game_count + 1}")
        self.status_var.set("Your turn  —  place X")
        self.status_lbl.config(fg=TEXT_YELLOW)

        for btn in self.buttons:
            btn.config(
                text="", bg=BG_CARD,
                font=("Arial", 30, "bold"),
                state=tk.NORMAL,
                disabledforeground=TEXT_WHITE
            )


# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app  = TicTacToeApp(root)
    root.mainloop()