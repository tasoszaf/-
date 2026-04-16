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

if "phase" not in st.session_state:
    st.session_state.phase = "setup"

if "index" not in st.session_state:
    st.session_state.index = 0

if "last_out" not in st.session_state:
    st.session_state.last_out = None

if "finished" not in st.session_state:
    st.session_state.finished = False

if "winner" not in st.session_state:
    st.session_state.winner = None

if "mr_white_guess_mode" not in st.session_state:
    st.session_state.mr_white_guess_mode = False

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

    # 🟡 SPIES WIN
    if spies >= citizens:
        return "SPIES"

    # 🟢 CITIZENS WIN
    if spies == 0:
        return "CITIZENS"

    return None


# ================= UI =================

st.title("🎭 Mr White (CORRECT RULE VERSION)")

# ================= SETUP =================

if st.session_state.phase == "setup":

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

            st.session_state.phase = "game"
            st.rerun()

    st.write("👥 Players:", st.session_state.players)

# ================= GAME =================

else:

    game = st.session_state.game
    players = game["players"]
    word = game["word"]

    # ---------------- REVEAL ----------------

    if st.session_state.index < len(players):

        p = players[st.session_state.index]

        st.write(f"👉 **{p['name']}**")

        if st.button("👁 Reveal"):

            if p["role"] == "mr_white":
                st.error("⚪ MR WHITE (χωρίς λέξη)")
            elif p["role"] == "undercover":
                st.warning(word[1])
            else:
                st.success(word[0])

        if st.button("➡ Next"):
            st.session_state.index += 1
            st.rerun()

    # ---------------- VOTE ----------------

    else:

        st.subheader("❌ Vote Phase")

        names = [p["name"] for p in players]

        idx = st.selectbox("Ποιος φεύγει;", range(len(names)), format_func=lambda i: names[i])

        if st.button("🔥 Vote Out"):

            removed = players[idx]
            st.session_state.last_out = removed

            players = [p for p in players if p["name"] != removed["name"]]
            game["players"] = players

            st.session_state.index = 0

            # 🧠 MR WHITE CHECK
            if removed["role"] == "mr_white":
                st.session_state.mr_white_guess_mode = True

            st.rerun()

    # ---------------- MR WHITE GUESS ----------------

    if st.session_state.mr_white_guess_mode:

        st.subheader("⚪ MR WHITE GUESS PHASE")

        guess = st.text_input("Μάντεψε τη λέξη:")

        if st.button("✔ Check Guess"):

            if guess.lower() in [word[0].lower(), word[1].lower()]:

                st.success("🏆 MR WHITE WINS")
                st.session_state.finished = True
                st.session_state.winner = "⚪ MR WHITE"

            else:
                st.error("❌ Wrong guess → game συνεχίζεται")

            st.session_state.mr_white_guess_mode = False

    # ---------------- RESULT ----------------

    if st.session_state.last_out:

        removed = st.session_state.last_out

        st.error(f"❌ Out: {removed['name']}")
        st.write(f"🎭 Ρόλος: **{removed['role']}**")

        winner = check_winner(game["players"])

        if winner == "SPIES":
            st.session_state.finished = True
            st.session_state.winner = "🟡 ΚΑΤΑΣΚΟΠΟΙ"

        elif winner == "CITIZENS":
            st.session_state.finished = True
            st.session_state.winner = "🟢 ΠΟΛΙΤΕΣ"

        # ---------------- END ----------------

        if st.session_state.finished:

            st.success(f"🏁 ΤΕΛΟΣ ΠΑΙΧΝΙΔΙΟΥ → ΝΙΚΗΤΕΣ: {st.session_state.winner}")

            if st.button("🔁 Play Again"):
                st.session_state.clear()
                st.rerun()

        else:

            st.info("🎮 Το παιχνίδι συνεχίζεται")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔁 Vote Again"):
                    st.session_state.last_out = None
                    st.rerun()

            with col2:
                if st.button("🏁 End Game"):

                    winner = check_winner(game["players"])

                    st.session_state.finished = True

                    if winner == "SPIES":
                        st.session_state.winner = "🟡 ΚΑΤΑΣΚΟΠΟΙ"
                    else:
                        st.session_state.winner = "🟢 ΠΟΛΙΤΕΣ"

                    st.rerun()
