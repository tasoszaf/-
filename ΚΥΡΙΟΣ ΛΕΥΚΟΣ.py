import streamlit as st
import random
import json
import os

# ================= FILES =================

PLAYERS_FILE = "players.json"
GAME_FILE = "game.json"

# ================= WORDS =================

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
    ("ψωμί", "τυρί"),
]

# ================= LOAD / SAVE =================

def save_players(players):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False)

def load_players():
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_game(game_state):
    with open(GAME_FILE, "w", encoding="utf-8") as f:
        json.dump(game_state, f, ensure_ascii=False)

def load_game():
    if os.path.exists(GAME_FILE):
        with open(GAME_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ================= INIT STATE =================

if "players" not in st.session_state:
    st.session_state.players = load_players()

if "game" not in st.session_state:
    st.session_state.game = load_game()

if "revealed" not in st.session_state:
    st.session_state.revealed = {}

if "last_out" not in st.session_state:
    st.session_state.last_out = None

if "mr_white_guess_mode" not in st.session_state:
    st.session_state.mr_white_guess_mode = False

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

def check_winner(players):
    roles = [p["role"] for p in players]

    civilians = roles.count("πολίτης")
    undercovers = roles.count("undercover")
    mr_whites = roles.count("mr_white")

    infiltrators = undercovers + mr_whites

    if civilians <= 1 and infiltrators > 0:
        return "INFILTRATORS"

    if undercovers == 0 and mr_whites == 0:
        return "CIVILIANS"

    return None

# ================= UI =================

st.title("🎭 Mr White (Persistent Version)")

# ================= SETUP =================

if st.session_state.game is None:

    st.subheader("➕ Players Setup")

    new_name = st.text_input("👤 Νέος παίκτης")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Add Player"):
            if new_name and new_name not in st.session_state.players:
                st.session_state.players.append(new_name)
                save_players(st.session_state.players)
                st.rerun()

    with col2:
        if st.button("🗑 Clear Players"):
            st.session_state.players = []
            save_players([])
            st.rerun()

    st.write("📋 Saved Players:")
    st.write(st.session_state.players)

    if st.button("▶ Start Game"):

        if len(st.session_state.players) >= 3:

            st.session_state.game = {
                "players": assign_roles(st.session_state.players.copy()),
                "word": random.choice(WORDS),
            }

            for p in st.session_state.game["players"]:
                st.session_state.revealed[p["name"]] = False

            save_game(st.session_state.game)
            st.rerun()

# ================= RESTORE GAME =================

elif st.session_state.game is not None:

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
                elif p["role"] == "undercover":
                    st.warning(word[1])
                else:
                    st.success(word[0])

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
    st.subheader("❌ Vote Phase")

    names = [p["name"] for p in players]

    idx = st.selectbox("Ποιος φεύγει;", range(len(names)), format_func=lambda i: names[i])

    if st.button("🔥 Remove Player"):

        removed = players[idx]
        st.session_state.last_out = removed

        players = [p for p in players if p["name"] != removed["name"]]
        game["players"] = players

        st.session_state.revealed.pop(removed["name"], None)

        save_game(game)

        if removed["role"] == "mr_white":
            st.session_state.mr_white_guess_mode = True

        st.rerun()

    # ================= MR WHITE GUESS =================

    if st.session_state.mr_white_guess_mode:

        st.subheader("⚪ MR WHITE GUESS PHASE")

        guess = st.text_input("Μάντεψε τη λέξη:")

        if st.button("✔ Check Guess"):

            if guess.lower() in [word[0].lower(), word[1].lower()]:
                st.success("🏆 MR WHITE WINS")
                st.session_state.mr_white_won = True
            else:
                st.error("❌ Wrong guess")

            st.session_state.mr_white_guess_mode = False

    # ================= RESULT =================

    if st.session_state.last_out:

        removed = st.session_state.last_out

        st.error(f"❌ Out: {removed['name']}")
        st.write(f"🎭 Role: **{removed['role']}**")

        winner = check_winner(game["players"])

        if st.session_state.mr_white_won:
            st.session_state.finished = True
            st.session_state.winner = "⚪ MR WHITE"

        elif winner == "INFILTRATORS":
            st.session_state.finished = True
            st.session_state.winner = "🟡 INFILTRATORS"

        elif winner == "CIVILIANS":
            st.session_state.finished = True
            st.session_state.winner = "🟢 CIVILIANS"

        # ================= END =================

        if st.session_state.finished:

            st.success(f"🏁 GAME OVER → {st.session_state.winner}")

            if st.button("🔁 Restart Game"):
                st.session_state.clear()
                if os.path.exists(GAME_FILE):
                    os.remove(GAME_FILE)
                st.rerun()

        else:

            st.info("🎮 Game continues")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔁 Next Round"):
                    st.session_state.last_out = None
                    st.rerun()

            with col2:
                if st.button("🏁 End Game"):
                    st.session_state.finished = True
                    st.rerun()
