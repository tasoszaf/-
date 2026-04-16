import streamlit as st
import random

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
    st.session_state.players = []

if "game" not in st.session_state:
    st.session_state.game = None

if "index" not in st.session_state:
    st.session_state.index = 0

if "revealed" not in st.session_state:
    st.session_state.revealed = {}

if "last_out" not in st.session_state:
    st.session_state.last_out = None

if "finished" not in st.session_state:
    st.session_state.finished = False

if "winner" not in st.session_state:
    st.session_state.winner = None

if "mr_white_guess" not in st.session_state:
    st.session_state.mr_white_guess = False

# ================= LOGIC =================

def assign_roles(players):
    roles = ["mr_white", "undercover"]

    while len(roles) < len(players):
        roles.append("πολίτης")

    random.shuffle(players)
    random.shuffle(roles)

    return [{"name": players[i], "role": roles[i]} for i in range(len(players))]


def check_winner(players):

    roles = [p["role"] for p in players]

    spies = roles.count("undercover")
    citizens = roles.count("πολίτης")

    if spies >= citizens:
        return "SPIES"

    if spies == 0:
        return "CITIZENS"

    return None


# ================= UI =================

st.title("🎭 Mr White (CARD VERSION)")

# ================= SETUP =================

if st.session_state.game is None:

    name = st.text_input("👤 Παίκτης")

    if st.button("➕ Add"):
        if name and name not in st.session_state.players:
            st.session_state.players.append(name)

    if st.button("▶ Start Game"):
        if len(st.session_state.players) >= 3:

            st.session_state.game = {
                "players": assign_roles(st.session_state.players),
                "word": random.choice(WORDS),
                "index": 0
            }

            st.rerun()

    st.write("👥 Players:", st.session_state.players)

# ================= GAME =================

else:

    game = st.session_state.game
    players = game["players"]
    word = game["word"]

    st.subheader("🎴 Players Cards")

    # ================= CARDS =================

    cols = st.columns(3)

    for i, p in enumerate(players):

        with cols[i % 3]:

            st.markdown("### 🎴 CARD")

            st.write(f"👤 {p['name']}")

            if st.button(f"Reveal {p['name']}", key=f"r{i}"):

                st.session_state.revealed[p["name"]] = True

                if p["role"] == "mr_white":
                    st.error("⚪ MR WHITE")
                elif p["role"] == "undercover":
                    st.warning(word[1])
                else:
                    st.success(word[0])

    # ================= VOTE =================

    st.divider()
    st.subheader("❌ Vote")

    names = [p["name"] for p in players]

    idx = st.selectbox("Ποιος φεύγει;", range(len(names)), format_func=lambda i: names[i])

    if st.button("🔥 Remove Player"):

        removed = players[idx]
        st.session_state.last_out = removed

        players = [p for p in players if p["name"] != removed["name"]]
        game["players"] = players

        # MR WHITE GUESS MODE
        if removed["role"] == "mr_white":
            st.session_state.mr_white_guess = True

        st.rerun()

    # ================= MR WHITE GUESS =================

    if st.session_state.mr_white_guess:

        st.subheader("⚪ MR WHITE GUESS")

        guess = st.text_input("Μάντεψε τη λέξη:")

        if st.button("✔ Check"):

            if guess.lower() in [word[0].lower(), word[1].lower()]:
                st.success("🏆 MR WHITE WINS")
                st.session_state.finished = True
                st.session_state.winner = "MR WHITE"
            else:
                st.error("❌ Wrong guess")

            st.session_state.mr_white_guess = False

    # ================= RESULT =================

    if st.session_state.last_out:

        removed = st.session_state.last_out

        st.error(f"❌ Out: {removed['name']}")
        st.write(f"🎭 Role: **{removed['role']}**")

        winner = check_winner(game["players"])

        if winner == "SPIES":
            st.session_state.finished = True
            st.session_state.winner = "🟡 SPIES"

        elif winner == "CITIZENS":
            st.session_state.finished = True
            st.session_state.winner = "🟢 CITIZENS"

        if st.session_state.finished:

            st.success(f"🏁 WINNER: {st.session_state.winner}")

            if st.button("🔁 Restart"):
                st.session_state.clear()
                st.rerun()

    # ================= CONTROLS =================

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔁 Next Round"):
            st.session_state.last_out = None
            st.rerun()

    with col2:
        if st.button("🏁 End Game"):

            winner = check_winner(game["players"])

            if winner == "SPIES":
                st.session_state.winner = "🟡 SPIES"
            else:
                st.session_state.winner = "🟢 CITIZENS"

            st.session_state.finished = True
            st.rerun()
