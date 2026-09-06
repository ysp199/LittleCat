import time
import logging

logger = logging.getLogger("DesktopCat.Productivity")


class ProductivityManager:
    """Manages Stretch Break Reminders, Pomodoro Focus/Break Cycles, and Drink Water Reminders."""

    def __init__(self, settings_manager):
        self.settings = settings_manager

        # Stretch Reminder Setup
        self.last_stretch_time = time.time()

        # Drink Water Reminder Setup
        self.last_water_time = time.time()

        # Pomodoro Setup
        self.pomodoro_enabled = self.settings.get("pomodoro_enabled", False)
        self.pomodoro_mode = "focus"  # 'focus' or 'break'
        self.pomodoro_start_time = time.time()
        self.focus_duration = 25 * 60  # 25 minutes
        self.break_duration = 5 * 60   # 5 minutes

    def get_stretch_interval(self):
        return self.settings.get("stretch_interval_minutes", 20) * 60

    def check_stretch_reminder(self):
        """Returns True if it's time for a stretch break."""
        interval = self.get_stretch_interval()
        now = time.time()
        if now - self.last_stretch_time >= interval:
            self.last_stretch_time = now
            return True
        return False

    def get_water_interval(self):
        return self.settings.get("drink_water_interval_minutes", 30) * 60

    def check_water_reminder(self):
        """Returns True if it's time to drink water."""
        if not self.settings.get("drink_water_enabled", True):
            return False
        interval = self.get_water_interval()
        now = time.time()
        if now - self.last_water_time >= interval:
            self.last_water_time = now
            return True
        return False

    def update_pomodoro(self):
        """Updates Pomodoro state machine."""
        if not self.pomodoro_enabled:
            return "disabled"

        now = time.time()
        elapsed = now - self.pomodoro_start_time

        if self.pomodoro_mode == "focus" and elapsed >= self.focus_duration:
            self.pomodoro_mode = "break"
            self.pomodoro_start_time = now
            logger.info("Pomodoro: Focus complete -> Entering Break (5 min)")

        elif self.pomodoro_mode == "break" and elapsed >= self.break_duration:
            self.pomodoro_mode = "focus"
            self.pomodoro_start_time = now
            logger.info("Pomodoro: Break complete -> Entering Focus (25 min)")

        return self.pomodoro_mode

    def get_pomodoro_status(self):
        if not self.pomodoro_enabled:
            return "Pomodoro Off"

        now = time.time()
        elapsed = now - self.pomodoro_start_time
        total = self.focus_duration if self.pomodoro_mode == "focus" else self.break_duration
        remaining = max(0, int(total - elapsed))

        mins = remaining // 60
        secs = remaining % 60
        mode_title = "Focus" if self.pomodoro_mode == "focus" else "Break ☕"
        return f"{mode_title}: {mins:02d}:{secs:02d}"
