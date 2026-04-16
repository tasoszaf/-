import streamlit as st
import random

# -----------------------
# 🎯 ΕΔΩ ΒΑΖΕΙΣ ΕΣΥ ΤΙΣ ΛΕΞΕΙΣ
# -----------------------

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
    ("ψωμί", "τυρί")
]

# -----------------------
# 🎭 ΡΟΛΟΙ
# -----------------------

def assign_roles(players):
    roles = ["mr_white", "undercover"]

    while len(roles) < len(players):
        roles.append("πολίτης")

    random.shuffle(players)
    random.shuffle(roles)

    return [
        {"name": players[i], "role": roles[i]}
        for i in range(len(players))
    ]

# -----------------------
# 🎲 WORD PICK
# -----------------------

def get_word_pair():
    return random.choice(WORDS)

# -----------------------
# STATE INIT
# -----------------------

if "players" not in st.session_state:
    st.session_state.players = []

if "started" not in st.session_state:
    st.session_state.started = False

# -----------------------
# UI - SETUP
# -----------------------

st.title("🎭 Mr White Game")

if not st.session_state.started:

    name = st.text_input("👤 Όνομα παίκτη")

    if st.button("➕ Προσθήκη παίκτη"):
        if name:
            st.session_state.players.append(name)

    st.write("👥 Παίκτες:", st.session_state.players)

    if st.button("▶ Έναρξη παιχνιδιού"):

        if len(st.session_state.players) >= 3:

            st.session_state.started = True
            st.session_state.game_data = assign_roles(st.session_state.players)
            st.session_state.word_pair = get_word_pair()
            st.session_state.index = 0
            st.session_state.revealed = False

        else:
            st.warning("Χρειάζονται τουλάχιστον 3 παίκτες")

# -----------------------
# GAME SCREEN
# -----------------------

else:

    game = st.session_state.game_data
    words = st.session_state.word_pair
    i = st.session_state.index

    st.subheader("🎮 Το παιχνίδι ξεκίνησε")

    if i < len(game):

        player = game[i]

        st.write(f"👉 Δώσε το κινητό στον/στην: **{player['name']}**")

        if st.button("👁 Δες ρόλο"):
            st.session_state.revealed = True

        if st.session_state.revealed:

            role = player["role"]

            if role == "mr_white":
                st.error("❌ Είσαι MR WHITE (δεν έχεις λέξη)")
            elif role == "undercover":
                st.warning(f"🧠 Η λέξη σου: {words[1]}")
            else:
                st.success(f"🧠 Η λέξη σου: {words[0]}")

            if st.button("🙈 Απόκρυψη & επόμενος παίκτης"):
                st.session_state.index += 1
                st.session_state.revealed = False

    else:
        st.success("🎉 Όλοι είδαν τον ρόλο τους!")
        st.write("Τώρα συζήτηση και ψηφοφορία 🗳️ (χειροκίνητα)")

        if st.button("🔄 Νέο παιχνίδι"):
            st.session_state.clear()
