import streamlit as st
import random
import json
import requests
import base64
import os

# ================= GITHUB CONFIG =================

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO = st.secrets["GITHUB_REPO"]
FILE_PATH = st.secrets["GITHUB_FILE"]
BRANCH = st.secrets["GITHUB_BRANCH"]

# ================= WORDS =================

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
    ("ψωμί", "τυρί"),
]

# ================= GITHUB STORAGE =================

def load_players():
    url = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{FILE_PATH}"
    try:
        r = requests.get(url)
        return r.json()
    except:
        return []

def save_players(players):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    r = requests.get(url, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })

    sha = None
    if r.status_code == 200:
        sha = r.json()["sha"]

    content = base64.b64encode(
        json.dumps(players, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": "Update players list",
        "content": content,
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, json=payload, headers={
        "Authorization": f"token {GITHUB_TOKEN}"
    })

# ================= GAME LOGIC =================

def assign_roles(players):
    roles = ["mr_white", "undercover"]

    while len(roles) < len(players):
        roles.append("πολίτης")

    shuffled_players = players[:]
    random.shuffle(shuffled_players)
    random.shuffle(roles)

    return [
        {"name": shuffled_players[i], "role": roles[i]}
        for i in range(len(players))
    ]

def check_winner(players, mr_white_won):
    roles = [p["role"] for p in players]

    civilians = roles.count("πολίτης")
    undercovers = roles.count("undercover")
    mr_whites = roles.count("mr_white")

    infiltrators = undercovers + mr_whites

    if mr_white_won:
        return "MR_WHITE"

    if infiltrators == 0:
        return "CIVILIANS"

    if infiltrators >= civilians:
        return "INFILTRATORS"

    return None

# ================= INIT STATE =================

if "players" not in st.session_state:
    st.session_state.players = load_players()

if "game" not in st.session_state:
    st.session_state.game = None

if "revealed" not in st.session_state:
    st.session_state.revealed = {}

if "last_out" not in st.session_state:
    st.session_state.last_out = None

if "mr_white_guess" not in st.session_state:
    st.session_state.mr_white_guess = False

if "mr_white_won" not in st.session_state:
    st.session_state.mr_white_won = False

if "finished" not in st.session_state:
    st.session_state.finished = False

if "winner" not in st.session_state:
    st.session_state.winner = None

# ================= UI =================

st.title("🎭 Mr White Game")

# ================= SETUP =================

if st.session_state.game is None:

    name = st.text_input("👤 Player name")

    if st.button("➕ Add Player"):
        if name and name not in st.session_state.players:
            st.session_state.players.append(name)
            save_players(st.session_state.players)

    if st.button("🗑 Clear Players"):
        st.session_state.players = []
        save_players([])

    if st.button("▶ Start Game"):
        if len(st.session_state.players) >= 3:

            st.session_state.game = {
                "players": assign_roles(st.session_state.players),
                "word": random.choice(WORDS),
            }

            for p in st.session_state.game["players"]:
                st.session_state.revealed[p["name"]] = False

            st.rerun()

    st.write("👥 Players:", st.session_state.players)

# ================= GAME =================

else:

    game = st.session_state.game
    players = game["players"]
    word = game["word"]

    st.subheader("🎴 Cards")

    cols = st.columns(3)

    for i, p in enumerate(players):

        with cols[i % 3]:

            st.markdown("### 🎴 CARD")
            st.write(f"👤 {p['name']}")

            if st.session_state.revealed.get(p["name"], False):

                if p["role"] == "mr_white":
                    st.error("⚪ MR WHITE")
                    st.write("❓ no word")

                elif p["role"] == "undercover":
                    st.warning("🟡 UNDERCOVER")
                    st.write(f"🧠 {word[1]}")

                else:
                    st.success("🟢 CIVILIAN")
                    st.write(f"🧠 {word[0]}")

                if st.button("🔒 Hide", key=f"hide{i}"):
                    st.session_state.revealed[p["name"]] = False
                    st.rerun()

            else:

                st.info("🔒 Hidden")

                if st.button("👁 Reveal", key=f"reveal{i}"):
                    st.session_state.revealed[p["name"]] = True
                    st.rerun()

    # ================= VOTE =================

    st.divider()
    st.subheader("❌ Vote Out")

    names = [p["name"] for p in players]

    idx = st.selectbox("Choose player", range(len(names)),
                        format_func=lambda i: names[i])

    if st.button("🔥 Eliminate"):

        removed = players[idx]
        st.session_state.last_out = removed

        game["players"] = [p for p in players if p["name"] != removed["name"]]

        if removed["role"] == "mr_white":
            st.session_state.mr_white_guess = True

        st.rerun()

    # ================= MR WHITE GUESS =================

    if st.session_state.mr_white_guess:

        st.subheader("⚪ Mr White Guess")

        guess = st.text_input("Guess the word:")

        if st.button("✔ Check"):

            if guess.lower() in [word[0].lower(), word[1].lower()]:
                st.success("🏆 MR WHITE WINS")
                st.session_state.mr_white_won = True
            else:
                st.error("❌ Wrong guess")

            st.session_state.mr_white_guess = False

    # ================= RESULT =================

    if st.session_state.last_out:

        removed = st.session_state.last_out

        st.error(f"❌ Out: {removed['name']}")
        st.write(f"Role: {removed['role']}")

        winner = check_winner(game["players"], st.session_state.mr_white_won)

        if winner:
            st.session_state.finished = True

            if winner == "MR_WHITE":
                st.session_state.winner = "⚪ MR WHITE"
            elif winner == "INFILTRATORS":
                st.session_state.winner = "🟡 INFILTRATORS"
            else:
                st.session_state.winner = "🟢 CIVILIANS"

        if st.session_state.finished:

            st.success(f"🏁 WINNER: {st.session_state.winner}")

            if st.button("🔁 New Game"):
                for key in ["game", "revealed", "last_out",
                            "mr_white_guess", "mr_white_won",
                            "finished", "winner"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        else:

            st.info("🎮 Game continues")

            if st.button("➡ Next Round"):
                st.session_state.last_out = None
                st.rerun()
