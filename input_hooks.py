import time
import math
import queue
import logging
from pynput import mouse, keyboard

logger = logging.getLogger("DesktopCat.InputHooks")


class GlobalInputListener:
    """Manages global pynput mouse and keyboard listeners with KPS tracking, mouse velocity, and scroll events."""

    def __init__(self):
        self.mouse_click_queue = queue.Queue()
        self.scroll_queue = queue.Queue()
        self.last_keystroke_time = 0.0
        self.last_scroll_time = 0.0
        self.last_mouse_move_time = 0.0
        self.keypress_count = 0
        self.keystroke_timestamps = []
        self.mouse_listener = None
        self.keyboard_listener = None
        self.running = False

        # Mouse velocity tracking
        self._mouse_positions = []  # [(x, y, time), ...]
        self._mouse_velocity = 0.0

    def start(self):
        self.running = True

        try:
            self.mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
                on_move=self._on_mouse_move,
                on_scroll=self._on_mouse_scroll
            )
            self.mouse_listener.daemon = True
            self.mouse_listener.start()
            logger.info("Global mouse listener started.")
        except Exception as e:
            logger.error("Failed to start global mouse listener: %s", e)

        try:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
            logger.info("Global keyboard listener started.")
        except Exception as e:
            logger.error("Failed to start global keyboard listener: %s", e)

    def stop(self):
        self.running = False
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception:
                pass
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception:
                pass
        logger.info("Global input listeners stopped.")

    def _on_mouse_click(self, x, y, button, pressed):
        if not self.running:
            return

        if pressed:
            button_name = "left" if button == mouse.Button.left else ("right" if button == mouse.Button.right else None)
            if button_name:
                self.mouse_click_queue.put({"button": button_name, "x": x, "y": y, "time": time.time()})

    def _on_mouse_move(self, x, y):
        """Track mouse position for velocity calculation and cursor movement detection."""
        if not self.running:
            return
        now = time.time()
        self.last_mouse_move_time = now
        self._mouse_positions.append((x, y, now))
        # Keep only last 500ms of positions
        cutoff = now - 0.5
        self._mouse_positions = [(px, py, pt) for px, py, pt in self._mouse_positions if pt >= cutoff]

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Capture scroll events and track last scroll time."""
        if not self.running:
            return
        now = time.time()
        self.last_scroll_time = now
        self.scroll_queue.put({"x": x, "y": y, "dx": dx, "dy": dy, "time": now})

    def _on_key_press(self, key):
        if not self.running:
            return
        now = time.time()
        self.last_keystroke_time = now
        self.keypress_count += 1
        self.keystroke_timestamps.append(now)

    def pop_mouse_click(self):
        try:
            return self.mouse_click_queue.get_nowait()
        except queue.Empty:
            return None

    def pop_scroll_event(self):
        """Pop a scroll event from the queue, or None."""
        try:
            return self.scroll_queue.get_nowait()
        except queue.Empty:
            return None

    def is_scrolling(self, threshold_seconds=0.7):
        """Returns True if the user is actively scrolling."""
        if self.last_scroll_time == 0.0:
            return False
        return (time.time() - self.last_scroll_time) < threshold_seconds

    def is_mouse_moving(self, threshold_seconds=0.5):
        """Returns True if the mouse cursor was moved recently."""
        if self.last_mouse_move_time == 0.0:
            return False
        return (time.time() - self.last_mouse_move_time) < threshold_seconds

    def get_mouse_velocity(self):
        """Calculate mouse cursor velocity in pixels/second over rolling 500ms window."""
        now = time.time()
        cutoff = now - 0.5
        self._mouse_positions = [(px, py, pt) for px, py, pt in self._mouse_positions if pt >= cutoff]

        if len(self._mouse_positions) < 2:
            return 0.0

        first = self._mouse_positions[0]
        last = self._mouse_positions[-1]
        dt = last[2] - first[2]
        if dt < 0.01:
            return 0.0

        dx = last[0] - first[0]
        dy = last[1] - first[1]
        dist = math.hypot(dx, dy)
        return dist / dt

    def is_typing(self, threshold_seconds=1.5):
        if self.last_keystroke_time == 0.0:
            return False
        return (time.time() - self.last_keystroke_time) < threshold_seconds

    def get_kps(self):
        """Calculates Keystrokes Per Second over rolling 1.5-second window."""
        now = time.time()
        self.keystroke_timestamps = [t for t in self.keystroke_timestamps if now - t <= 1.5]
        return len(self.keystroke_timestamps) / 1.5

    def get_typing_tier(self):
        """Returns typing speed classification: 'normal', 'fast', or 'very_fast'."""
        kps = self.get_kps()
        if kps > 8.0:
            return "very_fast"
        elif kps >= 4.0:
            return "fast"
        return "normal"
