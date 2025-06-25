import json
import os

LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    return []

def save_score(name, score):
    leaderboard = load_leaderboard()

    # Update score only if it's higher
    updated = False
    for entry in leaderboard:
        if entry["name"] == name:
            if score > entry["score"]:
                entry["score"] = score
            updated = True
            break

    if not updated:
        leaderboard.append({"name": name, "score": score})

    # Optional: sort descending by score
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=2)

def get_high_score():
    leaderboard = load_leaderboard()
    if leaderboard:
        top = max(leaderboard, key=lambda x: x["score"])
        return top["name"], top["score"]
    return "None", 0

def format_leaderboard():
    leaderboard = load_leaderboard()
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return [f"{entry['name']}: {entry['score']}" for entry in leaderboard]