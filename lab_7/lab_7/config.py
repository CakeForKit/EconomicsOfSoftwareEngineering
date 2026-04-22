import json
import os

DEFAULT_CONFIG = {
    "quantity": [
        [0, 0, 0],  # EI: simple, medium, complex
        [0, 0, 0],  # EO
        [0, 0, 0],  # EQ
        [0, 0, 0],  # ILF
        [0, 0, 0],  # EIF
    ],
    "system_params": [0] * 14,
    "lang_percentages": [100, 0, 0],
    "lang_selections": [10, 0, 0],
}


def get_config_path():
    home = os.path.expanduser("~")
    config_dir = os.path.join(home, ".cocomo2")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")


def load_config():
    path = get_config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    path = get_config_path()
    try:
        # Normalize language percentages to sum to 100
        languages = cfg.get("languages", [])
        total_perc = sum(l.get('perc', 0) for l in languages)
        if total_perc > 0:
            for l in languages:
                l['perc'] = int(round(l['perc'] * 100 / total_perc))

        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Failed to save config: {e}")
