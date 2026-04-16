import streamlit as st
import random
import json
import base64
import requests

# ================= CONFIG =================

REPO = "tasoszaf/mr.white"
FILE_PATH = "game.json"

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]

# ================= WORDS =================

WORDS = [
    ("σκύλος", "γάτα"),
    ("θάλασσα", "λίμνη"),
    ("αυτοκίνητο", "μηχανή"),
    ("πόλη", "χωριό"),
]

# ================= GITHUB SAVE =================

def save_to_github(data):

    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

    content = json.dumps(data, ensure_ascii=False, indent=2)
    encoded = base64.b64encode(content.encode()).decode()

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.get(url, headers=headers)
    sha = r.json().get("sha") if r.status_code == 200 else None

    payload = {
        "message": "update game",
        "content": encoded
    }

    if sha:
        payload["sha"] = sha

    requests.put(url, headers=headers, json=payload)

# ================= GAME CORE =================

def assign_roles(players):
    roles = ["mr_white", "undercover"]

    while len(roles) < len(players):
        roles.append("πολίτης")

    random.shuffle(players)
    random.shuffle(roles)

    return [{"name": players[i], "role": roles[i]} for i in range(len(players))]


def count_roles(players):
    spies = sum(1 for p in players if p["role"] == "undercover")
    citizens = sum(1 for p in players if p["role"] == "πολίτης")
    mr_white = any(p["role"] == "mr_white" for p in players)

    return spies, citizens, mr_white


def check_winner(players, mr_white_alive, guessed):

    spies, citizens, _ = count_roles(players)

    # ⚪ MR WHITE WIN
    if guessed:
        return "MR_WHITE_WINS"

    if mr_white_alive and spies == 0:
        return "MR_WHITE_WINS"

    # 🟡 SPIES WIN (ισοφαρία ή υπεροχή)
    if spies >= citizens:
        return "SPIES_WIN"

    # 🟢 CITIZENS WIN
    if spies == 0 and mr_white_alive:
        return "CITIZENS_WIN"

    return None

# ================= INIT =================

if "players" not in st.session_state:
    st.session_state.players = []

if "game" not in st.session_state:
    st.session_state.game = None

if "phase" not in st.session_state:
    st.session_state.phase = "setup"

if "index" not in st.session_state:
    st.session_state.index = 0

if "eliminated" not in st.session_state:
    st.session_state.eliminated = None

if "guess_result" not in st.session_state:
    st.session_state.guess_result = False

# ================= UI =================

st.title("🎭 Mr White (RULE CORRECT VERSION)")

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
            st.session_state.index = 0

            save_to_github(st.session_state.game)
            st.rerun()

    st.write("👥 Players:", st.session_state.players)

# ================= GAME =================

else:

    game = st.session_state.game
    players = game["players"]
    word = game["word"]

    # ---------------- REVEAL LOOP ----------------

    if st.session_state.index < len(players):

        p = players[st.session_state.index]

        st.write("👉", p["name"])

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

    # ---------------- ELIMINATION ----------------

    else:

        st.subheader("❌ Elimination")

        names = [p["name"] for p in players]

        idx = st.selectbox("Pick player", range(len(names)), format_func=lambda i: names[i])

        if st.button("🔥 Confirm"):

            eliminated = names[idx]
            st.session_state.eliminated = eliminated

            players = [p for p in players if p["name"] != eliminated]
            game["players"] = players

            st.session_state.index = 0

            save_to_github(game)
            st.rerun()

    # ---------------- RESOLUTION ----------------

    if st.session_state.eliminated:

        st.error(f"❌ Out: {st.session_state.eliminated}")

        roles = [p["role"] for p in game["players"]]
        mr_white_alive = any(p["role"] == "mr_white" for p in game["players"])

        # MR WHITE GUESS PHASE
        if any(p["role"] == "mr_white" and p["name"] == st.session_state.eliminated for p in players) == False:

            pass

        # guess UI only if mr white is eliminated
        eliminated_player = st.session_state.eliminated
        eliminated_role = None

        for p in players:
            if p["name"] == eliminated_player:
                eliminated_role = p["role"]

        if eliminated_role == "mr_white":

            guess = st.text_input("🎯 Mr White μάντεψε λέξη:")

            if st.button("✔ Check Guess"):

                if guess.lower() in [word[0].lower(), word[1].lower()]:
                    st.success("🏆 MR WHITE WINS")
                    save_to_github(game)
                    st.stop()

                else:
                    st.error("❌ Wrong guess")

        result = check_winner(players, mr_white_alive, st.session_state.guess_result)

        if result == "MR_WHITE_WINS":
            st.success("🏆 MR WHITE WINS")
            st.stop()

        elif result == "SPIES_WIN":
            st.success("🟡 SPIES WIN")
            st.stop()

        elif result == "CITIZENS_WIN":
            st.success("🟢 CITIZENS WIN")
            st.stop()

        if st.button("➡ Next Round"):
            st.session_state.eliminated = None
            st.rerun()
