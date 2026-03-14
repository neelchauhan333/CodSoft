# ================================================================
#  SmartBot  —  Beautiful Tkinter GUI Chatbot
#  No extra libraries needed — pure Python + tkinter
#
#  Features:
#    ✅ Modern dark chat UI (WhatsApp / iMessage style)
#    ✅ Animated typing indicator (...)
#    ✅ Sentiment detection (built-in, no libraries)
#    ✅ Intent matching with keyword scoring
#    ✅ Conversation memory (remembers your name)
#    ✅ Smooth message bubbles (user=blue, bot=dark)
#    ✅ Scrollable chat history
#    ✅ Send with Enter key or click Send button
#    ✅ Quick-reply suggestion buttons
#    ✅ Clear chat button
#    ✅ Timestamp on each message
# ================================================================

import tkinter as tk
from tkinter import scrolledtext
import random
import re
import threading
import time
from datetime import datetime

# ================================================================
# COLOURS  — dark chat theme
# ================================================================
BG_DARK       = "#0f172a"   # main background
BG_SIDEBAR    = "#1e293b"   # top bar
BG_USER_MSG   = "#2563eb"   # user bubble (blue)
BG_BOT_MSG    = "#1e293b"   # bot bubble (dark card)
BG_INPUT      = "#1e293b"   # input box background
BG_SEND       = "#2563eb"   # send button
BG_SEND_HOVER = "#1d4ed8"
BG_CLEAR      = "#334155"
BG_QUICK      = "#1e293b"   # quick reply buttons
BG_TYPING     = "#1e293b"

TEXT_WHITE    = "#f1f5f9"
TEXT_DIM      = "#94a3b8"
TEXT_USER     = "#ffffff"
TEXT_BOT      = "#e2e8f0"
TEXT_TIME     = "#64748b"
TEXT_GREEN    = "#4ade80"
TEXT_YELLOW   = "#fbbf24"
TEXT_RED      = "#f87171"
BORDER        = "#334155"
ACCENT        = "#3b82f6"

# ================================================================
# NLP ENGINE  — intent matching + sentiment (no libraries)
# ================================================================
import math

POSITIVE_WORDS = {"good","great","awesome","fantastic","amazing","happy",
    "excellent","wonderful","love","best","nice","cool","brilliant",
    "superb","glad","joy","pleased","perfect","fun","enjoy","excited",
    "thank","yes","yep","sure","beautiful","lovely","incredible"}

NEGATIVE_WORDS = {"bad","terrible","awful","horrible","hate","sad","angry",
    "worst","poor","wrong","no","not","never","boring","useless",
    "annoying","upset","frustrated","sorry","problem","issue","error",
    "broken","fail","disappointed","awful","dreadful","pathetic"}

def detect_sentiment(text):
    words = set(re.findall(r"\b\w+\b", text.lower()))
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    if pos > neg:   return "positive"
    if neg > pos:   return "negative"
    return "neutral"

# Pre-stemming helper (simple suffix stripping)
def simple_stem(word):
    for suffix in ("ing","tion","ed","er","ly","es","s"):
        if word.endswith(suffix) and len(word) - len(suffix) > 2:
            return word[:-len(suffix)]
    return word

INTENTS = [
    {"name":"greeting",
     "keywords":["hello","hi","hey","howdy","sup","morning","afternoon","evening","whats up","what's up"],
     "responses":["Hey there! 👋 Great to see you. How can I help?",
                  "Hello! I'm SmartBot. Ask me anything! 😊",
                  "Hi! How's it going? What's on your mind?",
                  "Hey! Good to hear from you. What can I do for you?"]},
    {"name":"farewell",
     "keywords":["bye","goodbye","see you","later","take care","cya","farewell","gotta go","quit","exit"],
     "responses":["Goodbye! 👋 Come back anytime!",
                  "See you later! Take care 😊",
                  "Bye! It was great chatting with you!",
                  "Farewell! Have a wonderful day! ✨"]},
    {"name":"thanks",
     "keywords":["thank","thanks","thank you","thx","appreciate","grateful","cheers","ty"],
     "responses":["You're very welcome! 😊",
                  "Happy to help! Anything else?",
                  "Anytime — that's what I'm here for! 🤖",
                  "My pleasure! Let me know if you need anything else."]},
    {"name":"identity",
     "keywords":["who are you","what are you","your name","are you a bot","are you human","what is your name","name"],
     "responses":["I'm SmartBot 🤖 — a Python-powered AI chatbot!",
                  "My name is SmartBot! I'm built with Python and Tkinter.",
                  "I'm SmartBot, your friendly AI assistant. 😊"]},
    {"name":"wellbeing",
     "keywords":["how are you","how do you do","how you doing","you okay","are you fine","feeling","doing"],
     "responses":["I'm running at 100% efficiency! 💚 How about you?",
                  "All systems green! I'm doing great. 😄 What about you?",
                  "Feeling fantastic — powered by Python! 🐍 How are you?"]},
    {"name":"datetime",
     "keywords":["time","date","today","day","month","year","current time","what time","what date"],
     "responses":["__DATETIME__"]},
    {"name":"joke",
     "keywords":["joke","funny","laugh","humor","humour","make me laugh","tell me something funny","comedy"],
     "responses":["Why do Python programmers wear glasses?\nBecause they can't C! 😂",
                  "Why do programmers prefer dark mode?\nBecause light attracts bugs! 🐛",
                  "How many programmers to change a lightbulb?\nNone — that's a hardware problem! 💡",
                  "Why did the developer go broke?\nThey used up all their cache! 💸",
                  "What do you call a bear with no teeth?\nA gummy bear! 🐻"]},
    {"name":"help",
     "keywords":["help","what can you do","commands","options","features","menu","capabilities"],
     "responses":["__HELP__"]},
    {"name":"weather",
     "keywords":["weather","rain","sunny","temperature","forecast","hot","cold","snow","wind","climate"],
     "responses":["I can't check live weather ☁️ but try weather.com!\nI could be upgraded with the OpenWeatherMap API. 🌍"]},
    {"name":"about_python",
     "keywords":["python","programming","code","coding","software","developer","program"],
     "responses":["Python is amazing! 🐍 Clean, powerful, and perfect for AI.\nFun fact: Python was named after Monty Python, not the snake!",
                  "Python powers me! It's one of the world's most popular languages. 💪"]},
    {"name":"about_ai",
     "keywords":["artificial intelligence","machine learning","ai","ml","deep learning","neural network","chatgpt"],
     "responses":["AI is transforming every industry! 🤖\nI use rule-based NLP — a core foundation of AI chatbots.",
                  "Machine Learning is fascinating! I'm rule-based, but my next version could use a trained ML model. 🧠"]},
    {"name":"age",
     "keywords":["how old","your age","when were you born","birthday","old"],
     "responses":["I was just created! In bot years, I'm brand new. 🎉",
                  "Age is just a number — I'm freshly compiled! 🤖"]},
    {"name":"favorite",
     "keywords":["favorite","favourite","prefer","like","love","best","enjoy","recommend"],
     "responses":["My favourite thing? Python, obviously! 🐍",
                  "I love having conversations — especially with curious people like you! 😄"]},
    {"name":"creator",
     "keywords":["who made you","who created you","who built you","creator","made by","built by"],
     "responses":["I was built as an AI internship project using Python + Tkinter! 🐍",
                  "My creator coded every line of my logic from scratch. Impressive, right? 😄"]},
]

HELP_TEXT = (
    "Here's what I can talk about:\n\n"
    "👋  Greetings & small talk\n"
    "🤖  Who / what I am\n"
    "😄  Jokes & fun facts\n"
    "🕐  Current time & date\n"
    "🐍  Python & AI topics\n"
    "🌦️  Weather (info only)\n"
    "💬  General conversation\n\n"
    "Type anything to get started!"
)

QUICK_REPLIES = [
    "Tell me a joke 😄",
    "What time is it? 🕐",
    "How are you? 💚",
    "What can you do? 🤖",
]

IGNORE_NAMES = {"a","an","the","not","here","fine","ok","okay","good",
                "well","bot","sorry","just","only","doing","great","called"}

def try_extract_name(text):
    patterns = [r"my name is ([A-Za-z]+)", r"i am ([A-Za-z]+)",
                r"i'm ([A-Za-z]+)",        r"call me ([A-Za-z]+)",
                r"you can call me ([A-Za-z]+)"]
    for pat in patterns:
        m = re.search(pat, text.lower())
        if m:
            name = m.group(1).capitalize()
            if name.lower() not in IGNORE_NAMES:
                return name
    return None

def match_intent(text):
    lower = text.lower()
    words = set(re.findall(r"\b\w+\b", lower))
    stemmed = {simple_stem(w) for w in words}
    best_intent = None
    best_score  = 0
    for intent in INTENTS:
        score = 0
        for kw in intent["keywords"]:
            if " " in kw:
                if kw in lower: score += 3
            else:
                if kw in words or simple_stem(kw) in stemmed:
                    score += 1
        if score > best_score:
            best_score  = score
            best_intent = intent
    return best_intent if best_score > 0 else None

SENTIMENT_REPLIES = {
    "positive": ["That sounds great! 😊 Tell me more.",
                 "Awesome! I love the positivity! ✨",
                 "Glad to hear that! What else is on your mind?"],
    "negative": ["I'm sorry to hear that 😔 Is there anything I can help with?",
                 "That sounds tough. I hope things get better! 💙",
                 "I understand. Would you like to talk about it?"],
    "neutral":  ["Hmm, I didn't quite catch that. Try typing 'help'! 🤔",
                 "Could you rephrase that? Type 'help' for options.",
                 "I'm still learning! Type 'help' to see what I can do. 🤖"],
}

def get_response(text, memory):
    # Name extraction
    name = try_extract_name(text)
    if name:
        memory["name"] = name
        return f"Nice to meet you, {name}! 😊 How can I help you today?"

    # Intent match
    intent = match_intent(text)
    if intent:
        reply = random.choice(intent["responses"])
        if reply == "__DATETIME__":
            now = datetime.now()
            reply = (f"🕐 Current time: {now.strftime('%I:%M %p')}\n"
                     f"📅 Today: {now.strftime('%A, %d %B %Y')}")
        elif reply == "__HELP__":
            reply = HELP_TEXT
        if memory.get("name"):
            reply = reply.replace("{name}", memory["name"])
        return reply

    # Sentiment fallback
    sentiment = detect_sentiment(text)
    return random.choice(SENTIMENT_REPLIES[sentiment])

# ================================================================
# MAIN APPLICATION
# ================================================================
class SmartBotApp:
    def __init__(self, root):
        self.root    = root
        self.root.title("SmartBot — AI Chatbot")
        self.root.geometry("480x720")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(False, False)

        self.memory   = {"name": None, "turns": 0}
        self.typing   = False

        self._build_ui()
        self._send_bot_message(
            "👋 Hello! I'm SmartBot, your AI assistant.\n"
            "Type anything to get started, or tap a suggestion below!"
        )

    # ────────────────────────────────────────────────────────────
    # UI BUILDER
    # ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ────────────────────────────────────────────
        topbar = tk.Frame(self.root, bg=BG_SIDEBAR, pady=12)
        topbar.pack(fill=tk.X)

        # Avatar circle
        avatar_canvas = tk.Canvas(topbar, width=40, height=40,
                                  bg=BG_SIDEBAR, highlightthickness=0)
        avatar_canvas.pack(side=tk.LEFT, padx=(14, 8))
        avatar_canvas.create_oval(2, 2, 38, 38, fill=ACCENT, outline="")
        avatar_canvas.create_text(20, 20, text="🤖", font=("Arial", 18))

        info_frame = tk.Frame(topbar, bg=BG_SIDEBAR)
        info_frame.pack(side=tk.LEFT, fill=tk.Y, pady=2)

        tk.Label(info_frame, text="SmartBot",
                 font=("Arial", 14, "bold"),
                 bg=BG_SIDEBAR, fg=TEXT_WHITE).pack(anchor=tk.W)

        self.status_dot = tk.Label(info_frame,
                 text="● Online",
                 font=("Arial", 10),
                 bg=BG_SIDEBAR, fg=TEXT_GREEN)
        self.status_dot.pack(anchor=tk.W)

        # Clear button
        clear_btn = tk.Button(topbar, text="Clear",
                              font=("Arial", 10),
                              bg=BG_CLEAR, fg=TEXT_DIM,
                              relief=tk.FLAT, cursor="hand2",
                              padx=10, pady=4,
                              command=self._clear_chat)
        clear_btn.pack(side=tk.RIGHT, padx=14)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(fg=TEXT_WHITE))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(fg=TEXT_DIM))

        # ── Chat area ──────────────────────────────────────────
        self.chat_frame_outer = tk.Frame(self.root, bg=BG_DARK)
        self.chat_frame_outer.pack(fill=tk.BOTH, expand=True,
                                   padx=0, pady=0)

        self.canvas = tk.Canvas(self.chat_frame_outer,
                                bg=BG_DARK, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_frame_outer,
                                      orient=tk.VERTICAL,
                                      command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.messages_frame = tk.Frame(self.canvas, bg=BG_DARK)
        self.canvas_window  = self.canvas.create_window(
            (0, 0), window=self.messages_frame, anchor=tk.NW
        )

        self.messages_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>",         self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>",    self._on_mousewheel)

        # ── Quick replies ──────────────────────────────────────
        self.quick_frame = tk.Frame(self.root, bg=BG_DARK, pady=6)
        self.quick_frame.pack(fill=tk.X, padx=10)

        for suggestion in QUICK_REPLIES:
            btn = tk.Button(
                self.quick_frame,
                text=suggestion,
                font=("Arial", 10),
                bg=BG_QUICK, fg=TEXT_DIM,
                relief=tk.FLAT, cursor="hand2",
                padx=10, pady=4,
                bd=0,
                highlightbackground=BORDER,
                highlightthickness=1,
                command=lambda s=suggestion: self._quick_reply(s)
            )
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(fg=TEXT_WHITE, bg="#2d3f55"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(fg=TEXT_DIM,   bg=BG_QUICK))

        # ── Input area ─────────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=BG_SIDEBAR, pady=10)
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.input_var = tk.StringVar()
        self.input_box = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Arial", 13),
            bg=BG_INPUT, fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            relief=tk.FLAT,
            bd=0
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True,
                            padx=(14, 8), ipady=10)
        self.input_box.bind("<Return>", lambda e: self._on_send())
        self.input_box.focus_set()

        self.send_btn = tk.Button(
            input_frame,
            text="Send ➤",
            font=("Arial", 11, "bold"),
            bg=BG_SEND, fg=TEXT_WHITE,
            relief=tk.FLAT, cursor="hand2",
            padx=16, pady=8,
            command=self._on_send
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(0, 14))
        self.send_btn.bind("<Enter>",
            lambda e: self.send_btn.config(bg=BG_SEND_HOVER))
        self.send_btn.bind("<Leave>",
            lambda e: self.send_btn.config(bg=BG_SEND))

    # ────────────────────────────────────────────────────────────
    # SCROLL HELPERS
    # ────────────────────────────────────────────────────────────
    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    # ────────────────────────────────────────────────────────────
    # MESSAGE BUBBLE BUILDER
    # ────────────────────────────────────────────────────────────
    def _add_message(self, text, sender="user"):
        is_user   = sender == "user"
        align     = tk.E if is_user else tk.W
        bg        = BG_USER_MSG if is_user else BG_BOT_MSG
        fg        = TEXT_USER   if is_user else TEXT_BOT
        padx_l    = (60, 10) if is_user else (10, 60)
        anchor    = tk.E       if is_user else tk.W

        # Timestamp
        ts = datetime.now().strftime("%I:%M %p")

        # Outer row frame
        row = tk.Frame(self.messages_frame, bg=BG_DARK)
        row.pack(fill=tk.X, padx=10, pady=(4, 0))

        # Bubble frame
        bubble_frame = tk.Frame(row, bg=BG_DARK)
        bubble_frame.pack(anchor=anchor, padx=padx_l)

        # Message label
        msg_lbl = tk.Label(
            bubble_frame,
            text=text,
            font=("Arial", 12),
            bg=bg, fg=fg,
            wraplength=290,
            justify=tk.LEFT,
            padx=12, pady=8,
        )
        msg_lbl.pack(anchor=anchor)

        # Timestamp label
        ts_lbl = tk.Label(
            bubble_frame,
            text=ts,
            font=("Arial", 8),
            bg=BG_DARK, fg=TEXT_TIME
        )
        ts_lbl.pack(anchor=anchor, pady=(0, 2))

        self._scroll_to_bottom()

    # ────────────────────────────────────────────────────────────
    # TYPING INDICATOR
    # ────────────────────────────────────────────────────────────
    def _show_typing(self):
        self.typing_row = tk.Frame(self.messages_frame, bg=BG_DARK)
        self.typing_row.pack(fill=tk.X, padx=10, pady=4, anchor=tk.W)

        self.typing_lbl = tk.Label(
            self.typing_row,
            text="SmartBot is typing...",
            font=("Arial", 11, "italic"),
            bg=BG_DARK, fg=TEXT_DIM
        )
        self.typing_lbl.pack(anchor=tk.W, padx=10)
        self._scroll_to_bottom()

        # Animate dots
        self._dot_count  = 0
        self._typing_anim()

    def _typing_anim(self):
        if not hasattr(self, "typing_lbl") or not self.typing_lbl.winfo_exists():
            return
        dots = "." * ((self._dot_count % 3) + 1)
        self.typing_lbl.config(text=f"SmartBot is typing{dots:<3}")
        self._dot_count += 1
        if self.typing:
            self.root.after(400, self._typing_anim)

    def _hide_typing(self):
        self.typing = False
        if hasattr(self, "typing_row") and self.typing_row.winfo_exists():
            self.typing_row.destroy()

    # ────────────────────────────────────────────────────────────
    # SEND LOGIC
    # ────────────────────────────────────────────────────────────
    def _on_send(self):
        text = self.input_var.get().strip()
        if not text or self.typing:
            return

        self.input_var.set("")
        self.memory["turns"] += 1
        self._add_message(text, sender="user")

        # Disable input while bot responds
        self.input_box.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.status_dot.config(text="● Typing...", fg=TEXT_YELLOW)
        self.typing = True
        self._show_typing()

        # Run bot response in thread so UI stays responsive
        threading.Thread(
            target=self._bot_respond, args=(text,), daemon=True
        ).start()

    def _bot_respond(self, text):
        # Simulate thinking delay (0.8–1.5s)
        delay = random.uniform(0.8, 1.5)
        time.sleep(delay)
        reply = get_response(text, self.memory)
        self.root.after(0, self._deliver_response, reply)

    def _deliver_response(self, reply):
        self._hide_typing()
        self._send_bot_message(reply)
        self.input_box.config(state=tk.NORMAL)
        self.send_btn.config(state=tk.NORMAL)
        self.status_dot.config(text="● Online", fg=TEXT_GREEN)
        self.input_box.focus_set()

        # Milestone every 5 turns
        if self.memory["turns"] % 5 == 0:
            self.root.after(600, lambda: self._send_bot_message(
                f"🎉 We've exchanged {self.memory['turns']} messages!"
            ))

    def _send_bot_message(self, text):
        self._add_message(text, sender="bot")

    # ────────────────────────────────────────────────────────────
    # QUICK REPLIES
    # ────────────────────────────────────────────────────────────
    def _quick_reply(self, text):
        if self.typing:
            return
        self.input_var.set(text)
        self._on_send()

    # ────────────────────────────────────────────────────────────
    # CLEAR CHAT
    # ────────────────────────────────────────────────────────────
    def _clear_chat(self):
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.memory = {"name": None, "turns": 0}
        self.typing  = False
        self._send_bot_message(
            "Chat cleared! 🧹 I'm SmartBot — ready to chat again. 😊"
        )

# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app  = SmartBotApp(root)
    root.mainloop()