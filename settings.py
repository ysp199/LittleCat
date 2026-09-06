import os
import json
import logging

logger = logging.getLogger("DesktopCat.Settings")

DEFAULT_SETTINGS = {
    "movement_mode": "freeroam",
    "follow_cursor": False,
    "follow_distance": 120,
    "cat_color": "orange",
    "active_skin": "default",
    "active_accessory": "none",
    "pause_reactions": False,
    "scale": 3,
    "move_speed": 7,
    "affection": 50.0,
    "pomodoro_enabled": False,
    "stretch_interval_minutes": 20,
    "window_watch_enabled": False,
    "startup_enabled": False,
    "laser_mode": False,
    # v8.0 New Settings
    "user_name": "",
    "drink_water_enabled": True,
    "drink_water_interval_minutes": 30,
    "peek_mode_enabled": False,
    "mouse_hunt_enabled": True,
    "cat_pattern": "orange",  # orange, siamese, mackerel
}

COLOR_PRESETS = {
    "orange": (0, 0, 0),
    "black": (-120, -50, -50),
    "gray": (-180, -60, 20),
    "white": (0, -100, 80),
    "calico": (30, 20, 10),
    "pink": (140, 30, 20),
}

# Cat Pattern Color Definitions
CAT_PATTERNS = {
    "orange": {
        "body": (245, 130, 30, 255),
        "dark": (200, 90, 10, 255),
        "light": (255, 170, 70, 255),
        "markings": None,
    },
    "siamese": {
        "body": (235, 220, 200, 255),     # Cream body
        "dark": (90, 60, 40, 255),         # Dark brown points
        "light": (245, 235, 225, 255),     # Light cream
        "markings": "points",              # Dark ears, face, paws, tail
    },
    "mackerel": {
        "body": (140, 140, 150, 255),      # Gray body
        "dark": (80, 80, 90, 255),         # Dark gray stripes
        "light": (170, 170, 180, 255),     # Light gray
        "markings": "stripes",             # Tabby stripes
    },
    "midnight": {
        "body": (45, 45, 60, 255),
        "dark": (25, 25, 35, 255),
        "light": (75, 75, 100, 255),
        "markings": None,
    },
}


class SettingsManager:
    """Handles loading and saving app settings to JSON in %APPDATA%/DesktopCat/."""

    def __init__(self):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        self.config_dir = os.path.join(appdata, "DesktopCat")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings.update(data)
                logger.info("Settings loaded from %s", self.config_file)
            else:
                self.save()
        except Exception as e:
            logger.warning("Failed to load settings, using defaults: %s", e)

    def save(self):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Settings saved to %s", self.config_file)
        except Exception as e:
            logger.error("Failed to save settings: %s", e)

    def get(self, key, default=None):
        return self.settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()
