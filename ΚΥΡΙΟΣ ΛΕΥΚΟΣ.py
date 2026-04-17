import streamlit as st
import random
import json
import os

# ================= FILE =================

PLAYERS_FILE = "players.json"c

def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_players(players):
    with open(PLAYERS_FILE, "w") as f:
        json.dump(players, f)

# ================= WORDS =================

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
    ("ψωμί", "τυρί"),
]

# ================= INIT =================

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

# ================= ROLE ASSIGN =================

def assign_roles(players):
    roles = ["mr_white", "undercover"]

    while len(roles) < len(players):
        roles.append("πολίτης")

    random.shuffle(players)
    random.shuffle(roles)

    return [{"name": players[i], "role": roles[i]} for i in range(len(players))]

# ================= WIN LOGIC =================

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

    if civilians == 1 and infiltrators > 0:
        return "INFILTRATORS"

    return None

# ================= UI =================

st.title("🎭 Mr White")

# ================= SETUP =================

if st.session_state.game is None:

    name = st.text_input("👤 Παίκτης")

    if st.button("➕ Add"):
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

                st.markdown("### 🎭 Ο ΡΟΛΟΣ ΣΟΥ")

                if p["role"] == "mr_white":
                    st.error("⚪ MR WHITE")
                    st.markdown("### ❓ Δεν έχεις λέξη")

                elif p["role"] == "undercover":
                    st.warning("🟡 UNDERCOVER")
                    st.markdown(f"### 🧠 {word[1]}")

                else:
                    st.success("🟢 ΠΟΛΙΤΗΣ")
                    st.markdown(f"### 🧠 {word[0]}")

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
    st.subheader("❌ Vote")

    names = [p["name"] for p in players]

    idx = st.selectbox("Ποιος φεύγει;", range(len(names)), format_func=lambda i: names[i])

    if st.button("🔥 Remove Player"):

        removed = players[idx]
        st.session_state.last_out = removed

        game["players"] = [p for p in players if p["name"] != removed["name"]]

        if removed["role"] == "mr_white":
            st.session_state.mr_white_guess = True

        st.rerun()

    # ================= MR WHITE GUESS =================

    if st.session_state.mr_white_guess:

        st.subheader("⚪ Mr White Guess")

        guess = st.text_input("Μάντεψε τη λέξη:")

        if st.button("✔ Check Guess"):

            if guess.lower() in [word[0].lower(), word[1].lower()]:
                st.success("🏆 MR WHITE WINS")
                st.session_state.mr_white_won = True
            else:
                st.error("❌ Λάθος λέξη")

            st.session_state.mr_white_guess = False

    # ================= RESULT =================

    if st.session_state.last_out:

        removed = st.session_state.last_out

        st.error(f"❌ Out: {removed['name']}")
        st.write(f"🎭 Role: **{removed['role']}**")

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

            st.success(f"🏁 GAME OVER → WINNER: {st.session_state.winner}")

            if st.button("🔁 New Game"):
                st.session_state.clear()
                st.rerun()

        else:

            st.info("🎮 Συνεχίζεται")

            if st.button("🔁 Next Round"):
                st.session_state.last_out = None
                st.rerun()
