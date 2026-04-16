import streamlit as st
import random

# -----------------------
# WORD PAIRS (εσύ τα αλλάζεις)
# -----------------------

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
    ("ψωμί", "τυρί")
]

# -----------------------
# ENGINE
# -----------------------

def assign_roles(players):
    roles = ["mr_white", "undercover"]

    while len(roles) < len(players):
        roles.append("πολίτης")

    random.shuffle(players)
    random.shuffle(roles)

    return [{"name": players[i], "role": roles[i]} for i in range(len(players))]


def reset_game():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def get_player(game, name):
    return next((p for p in game if p["name"] == name), None)


def check_end(players):
    roles = [p["role"] for p in players]

    u = roles.count("undercover")
    c = roles.count("πολίτης")

    if u == 1 and c == 1:
        return "undercover_win"
    if u == 0:
        return "civilians_win"

    return "continue"

# -----------------------
# SAFE INIT
# -----------------------

defaults = {
    "stage": "setup",
    "players": [],
    "game": [],
    "word": None,
    "index": 0,
    "revealed": False,
    "eliminated_index": None
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------
# UI
# -----------------------

st.title("🎭 Mr White (FINAL STABLE VERSION)")

# -----------------------
# SETUP
# -----------------------

if st.session_state.stage == "setup":

    name = st.text_input("👤 Όνομα παίκτη")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Προσθήκη"):
            if name and name not in st.session_state.players:
                st.session_state.players.append(name)

    with col2:
        if st.button("▶ Start Game"):
            if len(st.session_state.players) >= 3:
                st.session_state.game = assign_roles(st.session_state.players)
                st.session_state.word = random.choice(WORDS)

                st.session_state.stage = "game"
                st.session_state.index = 0
                st.session_state.revealed = False
            else:
                st.warning("Χρειάζονται 3+ παίκτες")

    st.write("👥 Παίκτες:", st.session_state.players)

# -----------------------
# GAME PHASE
# -----------------------

elif st.session_state.stage == "game":

    game = st.session_state.game
    word = st.session_state.word
    i = st.session_state.index

    st.subheader("🎮 Game Phase")

    if i < len(game):

        player = game[i]

        st.write(f"👉 Παίκτης: **{player['name']}**")

        if st.button("👁 Reveal"):
            st.session_state.revealed = True

        if st.session_state.revealed:

            if player["role"] == "mr_white":
                st.error("❌ MR WHITE (χωρίς λέξη)")
            elif player["role"] == "undercover":
                st.warning(f"🧠 Λέξη: {word[1]}")
            else:
                st.success(f"🧠 Λέξη: {word[0]}")

            if st.button("➡ Next Player"):
                st.session_state.index += 1
                st.session_state.revealed = False

    else:

        st.success("🎉 Τέλος γύρου")

        # INDEX-BASED SAFE SELECT
        options = st.session_state.players

        st.session_state.eliminated_index = st.selectbox(
            "❌ Ποιος φεύγει;",
            range(len(options)),
            format_func=lambda i: options[i]
        )

        if st.button("🔥 Επιβεβαίωση"):
            st.session_state.eliminated = options[st.session_state.eliminated_index]
            st.stage = "reveal"
            st.session_state.stage = "reveal"

# -----------------------
# REVEAL + ENGINE
# -----------------------

elif st.session_state.stage == "reveal":

    game = st.session_state.game
    word = st.session_state.word

    eliminated_name = st.session_state.eliminated

    player = get_player(game, eliminated_name)

    if not player:
        st.error("❌ State error - resetting round")
        st.session_state.stage = "game"
        st.stop()

    st.error(f"❌ Βγήκε: {player['name']}")
    st.write(f"🎭 Ρόλος: **{player['role']}**")

    # remove player safely
    remaining = [p for p in game if p["name"] != eliminated_name]
    st.session_state.game = remaining

    # -----------------------
    # MR WHITE
    # -----------------------

    if player["role"] == "mr_white":

        guess = st.text_input("🎯 Mr White μάντεψε:")

        if st.button("✔ Check"):

            if guess.lower() in [word[0].lower(), word[1].lower()]:
                st.success("🏆 MR WHITE WINS!")
                reset_game()
                st.stop()
            else:
                st.error("❌ Λάθος")

    # -----------------------
    # END CHECK
    # -----------------------

    result = check_end(remaining)

    if result == "undercover_win":
        st.success("🔵 UNDERCOVER WINS")
        reset_game()
        st.stop()

    if result == "civilians_win":
        st.success("🟢 CIVILIANS WINS")
        reset_game()
        st.stop()

    # CONTINUE
    if st.button("➡ Next Round"):
        st.session_state.stage = "game"
        st.session_state.index = 0
        st.session_state.revealed = False
