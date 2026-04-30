import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  [50, 180, 255],
    "difficulty": "normal",
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def load_leaderboard() -> list[dict]:
    
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return []

def save_score(name: str, score: int, distance: int, coins: int):
    
    board = load_leaderboard()
    board.append({"name": name, "score": score,
                  "distance": distance, "coins": coins})
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2)
    return board
