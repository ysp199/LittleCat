import time
import logging

logger = logging.getLogger("DesktopCat.Mood")


class MoodManager:
    """Manages cat affection and mood decay (0.0 to 100.0)."""

    def __init__(self, settings_manager):
        self.settings = settings_manager
        self.affection = float(self.settings.get("affection", 50.0))
        self.last_decay_time = time.time()

    def update(self):
        """Decays affection over time (-1.0 point per minute)."""
        now = time.time()
        elapsed_minutes = (now - self.last_decay_time) / 60.0

        if elapsed_minutes >= 1.0:
            decay_amount = elapsed_minutes * 1.0
            self.affection = max(0.0, self.affection - decay_amount)
            self.last_decay_time = now
            self.settings.set("affection", self.affection)

    def add_affection(self, amount):
        """Increases affection level."""
        self.affection = min(100.0, self.affection + amount)
        self.settings.set("affection", self.affection)
        logger.info("Affection increased by %.1f -> Current: %.1f", amount, self.affection)

    def get_mood_state(self):
        """Returns 'playful' if high mood (>75), 'grumpy' if low mood (<25), else 'neutral'."""
        if self.affection > 75.0:
            return "playful"
        elif self.affection < 25.0:
            return "grumpy"
        return "neutral"
