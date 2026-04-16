import streamlit as st
import random

# ---------------- WORDS ----------------

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
]

# ---------------- INIT SAFE STATE ----------------

def init():
    if "state" not in st.session_state:
        st.session_state.state = {
            "stage": "setup",
            "players": [],
            "game": [],
            "word": None,
            "i": 0,
            "revealed": False,
            "eliminated": None,
            "lock": False
        }

init()
S = st.session_state.state

# ---------------- GAME LOGIC ----------------

def assign(players):
    roles = ["mr_white", "undercover"]
    while len(roles) < len(players):
        roles.append("πολίτης")

    random.shuffle(players)
    random.shuffle(roles)

    return [{"name": players[i], "role": roles[i]} for i in range(len(players))]


def reset():
    st.session_state.state = {
        "stage": "setup",
        "players": [],
        "game": [],
        "word": None,
        "i": 0,
        "revealed": False,
        "eliminated": None,
        "lock": False
    }

# ---------------- UI ----------------

st.title("🎭 Mr White (LOCKED VERSION)")

# ---------------- SETUP ----------------

if S["stage"] == "setup":

    name = st.text_input("Όνομα")

    if st.button("➕ Προσθήκη"):
        if name and name not in S["players"]:
            S["players"].append(name)

    if st.button("▶ Start"):
        if len(S["players"]) >= 3:
            S["game"] = assign(S["players"])
            S["word"] = random.choice(WORDS)
            S["stage"] = "game"
            S["i"] = 0
            S["lock"] = False

    st.write(S["players"])

# ---------------- GAME ----------------

elif S["stage"] == "game":

    game = S["game"]

    if S["i"] < len(game):

        p = game[S["i"]]

        st.write("👉", p["name"])

        if st.button("👁 Reveal", disabled=S["lock"]):
            S["revealed"] = True

        if S["revealed"]:

            if p["role"] == "mr_white":
                st.error("MR WHITE")
            elif p["role"] == "undercover":
                st.warning(S["word"][1])
            else:
                st.success(S["word"][0])

            if st.button("➡ Next"):
                S["i"] += 1
                S["revealed"] = False

    else:

        st.subheader("❌ Επιλογή αποβολής")

        options = [p["name"] for p in game]

        idx = st.selectbox("Παίκτης", range(len(options)), format_func=lambda i: options[i])

        if st.button("🔥 Confirm") and not S["lock"]:
            S["lock"] = True
            S["eliminated"] = options[idx]
            S["stage"] = "reveal"
            st.rerun()

# ---------------- REVEAL ----------------

elif S["stage"] == "reveal":

    game = S["game"]
    name = S["eliminated"]

    player = next((p for p in game if p["name"] == name), None)

    if not player:
        st.error("STATE ERROR → RESET")
        reset()
        st.stop()

    st.error(f"Βγήκε: {player['name']}")
    st.write("Ρόλος:", player["role"])

    S["game"] = [p for p in game if p["name"] != name]

    # MR WHITE WIN
    if player["role"] == "mr_white":

        guess = st.text_input("Guess")

        if st.button("Check"):

            if guess.lower() in [S["word"][0].lower(), S["word"][1].lower()]:
                st.success("MR WHITE WINS")
                reset()
                st.stop()

    # WIN CHECK
    roles = [p["role"] for p in S["game"]]
    u = roles.count("undercover")
    c = roles.count("πολίτης")

    if u == 1 and c == 1:
        st.success("UNDERCOVER WINS")
        reset()
        st.stop()

    if u == 0:
        st.success("CIVILIANS WIN")
        reset()
        st.stop()

    if st.button("Next Round"):
        S["stage"] = "game"
        S["i"] = 0
        S["revealed"] = False
        S["lock"] = False
