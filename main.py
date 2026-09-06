import os
import sys
import time
import math
import random
import datetime
import logging
import tkinter as tk
from tkinter import Menu, simpledialog

from screeninfo import get_monitors

from settings import SettingsManager, COLOR_PRESETS
from sprite_manager import SpriteManager, resource_path, TRANSPARENT_COLOR_HEX
from input_hooks import GlobalInputListener
from tray import TrayIconManager
from mood import MoodManager
from productivity import ProductivityManager
from window_watch import WindowWatcher
from startup import StartupManager
from taskbar_dock import TaskbarDockManager

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("DesktopCat.Main")


class HeartParticle:
    """Floating heart particle effect when petting the cat."""

    def __init__(self, canvas, start_x, start_y):
        self.canvas = canvas
        self.x = start_x + random.uniform(-10, 10)
        self.y = start_y
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-2.0, -1.0)
        self.life = 1.0
        self.decay = random.uniform(0.04, 0.07)
        self.color = random.choice(["#FF4B72", "#FF69B4", "#FF1493", "#FF85A2"])
        self.size = random.choice([10, 12, 14])

        self.item_id = self.canvas.create_text(
            self.x, self.y,
            text="♥",
            fill=self.color,
            font=("Segoe UI Symbol", self.size, "bold")
        )

    def update(self):
        self.life -= self.decay
        if self.life <= 0:
            self.canvas.delete(self.item_id)
            return False

        self.x += self.vx
        self.y += self.vy
        self.canvas.coords(self.item_id, self.x, self.y)

        if self.life < 0.5:
            self.canvas.itemconfig(self.item_id, fill="#FFA0B4")

        return True


class HeatParticle:
    """Red vertical heat line particle rising above ears during fast typing."""

    def __init__(self, canvas, start_x, start_y):
        self.canvas = canvas
        self.x = start_x + random.uniform(-12, 12)
        self.y = start_y
        self.vy = random.uniform(-2.5, -1.0)
        self.life = 1.0
        self.decay = random.uniform(0.08, 0.12)
        self.color = random.choice(["#FF3232", "#FF5050", "#FF1414", "#FF7832"])

        self.item_id = self.canvas.create_text(
            self.x, self.y,
            text="|",
            fill=self.color,
            font=("Segoe UI", 12, "bold")
        )

    def update(self):
        self.life -= self.decay
        if self.life <= 0:
            self.canvas.delete(self.item_id)
            return False

        self.y += self.vy
        self.canvas.coords(self.item_id, self.x, self.y)
        return True


class PaperParticle:
    """Falling paper strip particle for scroll unroll effect."""

    def __init__(self, canvas, start_x, start_y):
        self.canvas = canvas
        self.x = start_x + random.uniform(-8, 8)
        self.y = start_y
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(1.2, 2.5)
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.06)

        self.item_id = self.canvas.create_text(
            self.x, self.y,
            text=random.choice(["📜", "📄", "≡"]),
            fill="#D4C9A8",
            font=("Segoe UI Symbol", 9)
        )

    def update(self):
        self.life -= self.decay
        if self.life <= 0:
            self.canvas.delete(self.item_id)
            return False

        self.x += self.vx
        self.y += self.vy
        self.canvas.coords(self.item_id, self.x, self.y)
        return True


class WaterDropParticle:
    """Water drop particle for drink water reminder."""

    def __init__(self, canvas, start_x, start_y):
        self.canvas = canvas
        self.x = start_x + random.uniform(-10, 10)
        self.y = start_y
        self.vy = random.uniform(-1.8, -0.6)
        self.life = 1.0
        self.decay = random.uniform(0.04, 0.07)

        self.item_id = self.canvas.create_text(
            self.x, self.y,
            text="💧",
            fill="#4FC3F7",
            font=("Segoe UI Symbol", random.choice([9, 11, 13]))
        )

    def update(self):
        self.life -= self.decay
        if self.life <= 0:
            self.canvas.delete(self.item_id)
            return False

        self.y += self.vy
        self.canvas.coords(self.item_id, self.x, self.y)
        return True


class SpeechBubble:
    """Dynamic multi-line speech bubble popup above cat's head."""

    def __init__(self, canvas, x, y, text, duration=3.0):
        self.canvas = canvas
        self.text = text
        self.end_time = time.time() + duration

        self.text_id = self.canvas.create_text(
            x, y,
            text=text,
            fill="#1A1A1A",
            font=("Segoe UI", 8, "bold"),
            justify="center"
        )
        bbox = self.canvas.bbox(self.text_id)
        if bbox:
            pad_x, pad_y = 6, 3
            self.bg_id = self.canvas.create_rectangle(
                bbox[0] - pad_x, bbox[1] - pad_y, bbox[2] + pad_x, bbox[3] + pad_y,
                fill="#FFFFFF", outline="#333333", width=1
            )
            self.canvas.tag_raise(self.text_id, self.bg_id)
        else:
            self.bg_id = None

    def update(self):
        if time.time() >= self.end_time:
            self.canvas.delete(self.text_id)
            if self.bg_id:
                self.canvas.delete(self.bg_id)
            return False
        return True


class DesktopCatApp:
    """Main Desktop Cat Pet Application (Full-Body Compact Cat)."""

    SPECIAL_IDLE_STATES = ("idle_play", "idle_roll", "idle_jump", "idle_groom", "idle_look_around")

    def __init__(self):
        self.settings = SettingsManager()
        self.input_listener = GlobalInputListener()
        self.mood = MoodManager(self.settings)
        self.productivity = ProductivityManager(self.settings)
        self.window_watcher = WindowWatcher(self.settings)
        self.startup = StartupManager()
        self.taskbar_dock = TaskbarDockManager()

        # Compact 32x32 Base Resolution scaled up (Default Scale = 3 -> 96x96 px)
        self.scale = self.settings.get("scale", 3)
        self.sprite_manager = SpriteManager(
            scale=self.scale,
            color_name=self.settings.get("cat_color", "orange"),
            skin_name=self.settings.get("active_skin", "default"),
            accessory_name=self.settings.get("active_accessory", "none")
        )

        self.update_virtual_desktop_bounds()

        self.root = tk.Tk()
        self.root.title("Desktop Cat Pet")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR_HEX)
        self.root.config(bg=TRANSPARENT_COLOR_HEX)

        self.cat_size = 32 * self.scale
        self.base_cat_size = self.cat_size
        self.x = float(self.v_width - self.cat_size - 100)
        self.y = float(self.v_height - self.cat_size - 80)
        self.root.geometry(f"{self.cat_size}x{self.cat_size}+{int(self.x)}+{int(self.y)}")

        self.canvas = tk.Canvas(
            self.root,
            width=self.cat_size,
            height=self.cat_size,
            bg=TRANSPARENT_COLOR_HEX,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.cat_image_id = None
        self.current_photo = None
        self.particles = []
        self.speech_bubbles = []

        # State Machine
        self.state = "sit"
        self.frame_index = 0
        self.flip = False
        self.state_start_time = time.time()
        self.idle_pause_duration = random.uniform(4.0, 8.0)
        self.last_input_time = time.time()

        # Hover Greeting Tracker
        self.last_hover_greeting_time = 0.0

        # Peek Mode
        self.peek_active = False
        self.peek_timer = 0.0
        self.original_x_before_peek = 0.0

        # Mouse Hunt
        self.mouse_hunt_cooldown = 0.0

        # Scroll Tracking
        self.last_scroll_particle_time = 0.0

        # Click Tracking
        self.last_left_click_time = 0.0

        # Movement Variables
        self.target_x = self.x
        self.target_y = self.y
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.last_heart_spawn = 0

        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        icon_path = os.path.join(self.sprite_manager.root_assets_dir, "cat.ico")
        self.tray = TrayIconManager(self, icon_path)

        self.context_menu = Menu(self.root, tearoff=0)
        self.build_context_menu()

    def update_virtual_desktop_bounds(self):
        try:
            monitors = get_monitors()
            min_x = min(m.x for m in monitors)
            min_y = min(m.y for m in monitors)
            max_x = max(m.x + m.width for m in monitors)
            max_y = max(m.y + m.height for m in monitors)
            self.v_min_x, self.v_min_y = min_x, min_y
            self.v_width, self.v_height = max_x - min_x, max_y - min_y
        except Exception:
            self.v_min_x, self.v_min_y = 0, 0
            self.v_width = self.root.winfo_screenwidth() if hasattr(self, 'root') else 1920
            self.v_height = self.root.winfo_screenheight() if hasattr(self, 'root') else 1080

    def get_personalized_text(self, base_text):
        name = self.settings.get("user_name", "")
        if name:
            return f"{name}, {base_text}"
        return base_text

    def select_next_idle_substate(self):
        mood_state = self.mood.get_mood_state()

        if mood_state == "playful":
            options = ["idle_play", "idle_jump", "idle_roll", "idle_groom", "idle_look_around", "sit"]
            weights = [0.30, 0.25, 0.20, 0.10, 0.10, 0.05]
        elif mood_state == "grumpy":
            options = ["sit", "idle_groom", "idle_look_around", "idle_breathe"]
            weights = [0.40, 0.30, 0.20, 0.10]
        else:
            options = ["sit", "idle_groom", "idle_play", "idle_look_around", "idle_roll", "idle_jump", "idle_breathe"]
            weights = [0.25, 0.20, 0.18, 0.15, 0.10, 0.07, 0.05]

        chosen = random.choices(options, weights=weights)[0]

        # Occasional cute thought bubble during idle
        if random.random() < 0.18 and not self.speech_bubbles:
            thoughts = ["🧶", "🐟", "🐾", "✨", "💤", "mew~", "🐱"]
            self.show_speech_bubble(random.choice(thoughts), duration=2.0)

        return chosen

    def build_context_menu(self):
        self.context_menu.delete(0, "end")
        self.context_menu.add_command(label="Feed Fish Treat 🐟", command=self.feed_fish)
        self.context_menu.add_command(label="Reset Position", command=self.reset_position)

        # Cat Pattern Submenu
        pattern_menu = Menu(self.context_menu, tearoff=0)
        patterns = [("Orange 🟠", "default"), ("Siamese 🐱", "siamese"), ("Mackerel 🐈", "mackerel"), ("Midnight 🌙", "midnight")]
        for label, skin in patterns:
            pattern_menu.add_radiobutton(
                label=label,
                value=skin,
                variable=tk.StringVar(value=self.settings.get("active_skin", "default")),
                command=lambda s=skin: self.set_setting("active_skin", s)
            )
        self.context_menu.add_cascade(label="Cat Pattern 🎨", menu=pattern_menu)

        # Accessories Submenu
        acc_menu = Menu(self.context_menu, tearoff=0)
        accs = ["none", "bow", "collar"]
        for a in accs:
            acc_menu.add_radiobutton(
                label=a.capitalize(),
                value=a,
                variable=tk.StringVar(value=self.settings.get("active_accessory", "none")),
                command=lambda acc=a: self.set_setting("active_accessory", acc)
            )
        self.context_menu.add_cascade(label="Accessories", menu=acc_menu)

        # Color Submenu
        color_menu = Menu(self.context_menu, tearoff=0)
        colors = ["orange", "black", "calico", "gray", "white", "pink"]
        for c in colors:
            color_menu.add_radiobutton(
                label=c.capitalize(),
                value=c,
                variable=tk.StringVar(value=self.settings.get("cat_color", "orange")),
                command=lambda color=c: self.set_setting("cat_color", color)
            )
        self.context_menu.add_cascade(label="Cat Color", menu=color_menu)

        # Speed Submenu
        speed_menu = Menu(self.context_menu, tearoff=0)
        speed_presets = [("Slow (4px)", 4), ("Normal (7px)", 7), ("Fast (12px)", 12), ("Zoomies (18px)", 18)]
        for lbl, val in speed_presets:
            speed_menu.add_radiobutton(
                label=lbl,
                value=val,
                variable=tk.IntVar(value=self.settings.get("move_speed", 7)),
                command=lambda speed=val: self.set_setting("move_speed", speed)
            )
        self.context_menu.add_cascade(label="Movement Speed", menu=speed_menu)

        self.context_menu.add_separator()

        # Feature Toggles
        follow_val = tk.BooleanVar(value=self.settings.get("follow_cursor", False))
        self.context_menu.add_checkbutton(
            label="Follow Cursor Mode",
            variable=follow_val,
            command=lambda: self.set_setting("follow_cursor", not self.settings.get("follow_cursor", False))
        )

        hunt_val = tk.BooleanVar(value=self.settings.get("mouse_hunt_enabled", True))
        self.context_menu.add_checkbutton(
            label="Mouse Hunt Mode 🐭",
            variable=hunt_val,
            command=lambda: self.set_setting("mouse_hunt_enabled", not self.settings.get("mouse_hunt_enabled", True))
        )

        peek_val = tk.BooleanVar(value=self.settings.get("peek_mode_enabled", False))
        self.context_menu.add_checkbutton(
            label="Peek Mode 👀",
            variable=peek_val,
            command=lambda: self.toggle_peek_mode()
        )

        water_val = tk.BooleanVar(value=self.settings.get("drink_water_enabled", True))
        self.context_menu.add_checkbutton(
            label="Drink Water Reminder 💧",
            variable=water_val,
            command=lambda: self.set_setting("drink_water_enabled", not self.settings.get("drink_water_enabled", True))
        )

        laser_val = tk.BooleanVar(value=self.settings.get("laser_mode", False))
        self.context_menu.add_checkbutton(
            label="Laser Pointer Mode 🔴",
            variable=laser_val,
            command=lambda: self.set_setting("laser_mode", not self.settings.get("laser_mode", False))
        )

        pause_val = tk.BooleanVar(value=self.settings.get("pause_reactions", False))
        self.context_menu.add_checkbutton(
            label="Pause Reactions",
            variable=pause_val,
            command=lambda: self.set_setting("pause_reactions", not self.settings.get("pause_reactions", False))
        )

        self.context_menu.add_separator()

        # Tell Your Name
        self.context_menu.add_command(label="Tell Your Name 📛", command=self.ask_user_name)

        self.context_menu.add_separator()
        self.context_menu.add_command(label="Quit", command=self.quit_app)

    def ask_user_name(self):
        current = self.settings.get("user_name", "")
        name = simpledialog.askstring(
            "Tell Your Name",
            "What's your name? (Leave empty to clear)",
            initialvalue=current,
            parent=self.root
        )
        if name is not None:
            self.set_setting("user_name", name.strip())
            if name.strip():
                self.show_speech_bubble(f"Hi {name.strip()}! 😸", duration=3.0)
            else:
                self.show_speech_bubble("Name cleared!", duration=2.0)

    def toggle_peek_mode(self):
        current = self.settings.get("peek_mode_enabled", False)
        new_val = not current
        self.set_setting("peek_mode_enabled", new_val)
        if new_val:
            self.enter_peek_mode()
        else:
            self.exit_peek_mode()

    def enter_peek_mode(self):
        self.peek_active = True
        self.original_x_before_peek = self.x
        self.x = float(self.v_width - self.cat_size // 2)
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.set_state("peek")
        self.peek_timer = time.time()

    def exit_peek_mode(self):
        self.peek_active = False
        self.x = self.original_x_before_peek
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.set_state("sit")

    def spawn_petting_hearts(self, count=2):
        now = time.time()
        if now - self.last_heart_spawn > 0.15:
            self.last_heart_spawn = now
            for _ in range(count):
                cx = self.cat_size / 2.0
                cy = self.cat_size / 3.0
                self.particles.append(HeartParticle(self.canvas, cx, cy))

    def spawn_heat_particles(self):
        cx = self.cat_size / 2.0
        cy = self.cat_size / 4.0
        self.particles.append(HeatParticle(self.canvas, cx, cy))

    def spawn_paper_particles(self):
        cx = self.cat_size / 2.0
        cy = self.cat_size * 0.7
        for _ in range(2):
            self.particles.append(PaperParticle(self.canvas, cx, cy))

    def spawn_water_particles(self):
        cx = self.cat_size / 2.0
        cy = self.cat_size / 3.0
        for _ in range(3):
            self.particles.append(WaterDropParticle(self.canvas, cx, cy))

    def show_speech_bubble(self, text, duration=3.0):
        # Clear existing bubbles to avoid overlapping text
        for b in self.speech_bubbles:
            self.canvas.delete(b.text_id)
            if b.bg_id:
                self.canvas.delete(b.bg_id)
        self.speech_bubbles.clear()

        self.speech_bubbles.append(SpeechBubble(self.canvas, self.cat_size / 2.0, 16, text, duration))

    def feed_fish(self):
        self.mood.add_affection(15.0)
        self.set_state("eating")
        self.spawn_petting_hearts(count=4)
        self.show_speech_bubble("Yum! 🐟", duration=2.5)

    def is_startup_enabled(self):
        return self.startup.is_startup_enabled()

    def toggle_startup(self):
        current = self.is_startup_enabled()
        self.startup.set_startup(not current)

    def toggle_pomodoro(self):
        self.productivity.pomodoro_enabled = self.settings.get("pomodoro_enabled", False)
        self.productivity.pomodoro_start_time = time.time()

    def update_particles(self):
        self.particles = [p for p in self.particles if p.update()]
        self.speech_bubbles = [b for b in self.speech_bubbles if b.update()]

    def show_context_menu(self, event):
        if not self.settings.get("pause_reactions", False):
            self.set_state("right_click_react")
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # --- Mouse Dragging (Clean drag without stretch/wobble) ---
    def on_drag_start(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.set_state("dragging")
        self.spawn_petting_hearts(count=3)
        self.mood.add_affection(2.0)

        if self.peek_active:
            self.peek_active = False
            self.settings.set("peek_mode_enabled", False)

    def on_drag_motion(self, event):
        if self.is_dragging:
            deltax = event.x - self.drag_start_x
            deltay = event.y - self.drag_start_y
            self.x += deltax
            self.y += deltay
            self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
            self.spawn_petting_hearts(count=1)

    def on_drag_stop(self, event):
        self.is_dragging = False
        self.set_state("left_click_react")

    def on_double_click(self, event):
        """Slightly bigger jump on double left click."""
        self.is_dragging = False
        self.set_state("left_click_alt_react")
        self.spawn_petting_hearts(count=5)
        self.show_speech_bubble("Hop! 🐾", duration=1.5)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings.set(key, value)
        logger.info("Setting updated: %s = %s", key, value)

        if key == "cat_color":
            self.sprite_manager.set_color(value)
        elif key == "active_skin":
            self.sprite_manager.set_skin(value)
        elif key == "active_accessory":
            self.sprite_manager.set_accessory(value)
        elif key == "scale":
            self.scale = value
            self.cat_size = 32 * value
            self.base_cat_size = self.cat_size
            self.sprite_manager.set_scale(value)
            self.root.geometry(f"{self.cat_size}x{self.cat_size}+{int(self.x)}+{int(self.y)}")
            self.canvas.config(width=self.cat_size, height=self.cat_size)

        self.build_context_menu()

    def reset_position(self):
        self.x = float(self.v_width - self.cat_size - 100)
        self.y = float(self.v_height - self.cat_size - 80)
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.set_state("sit")
        if self.peek_active:
            self.peek_active = False
            self.settings.set("peek_mode_enabled", False)
        logger.info("Position reset to default.")

    def set_state(self, new_state):
        if self.state != new_state:
            logger.debug("State transition: %s -> %s", self.state, new_state)
            self.state = new_state
            self.frame_index = 0
            self.state_start_time = time.time()

            if new_state in ("sit", "idle_breathe"):
                self.idle_pause_duration = random.uniform(4.0, 8.0)

            if new_state == "walk" and not self.settings.get("follow_cursor", False):
                self.target_x = float(random.randint(20, max(20, self.v_width - self.cat_size - 20)))
                self.target_y = float(self.v_height - self.cat_size - 40)
                self.flip = (self.target_x < self.x)

    def check_hover_greeting(self):
        """Shows Hello + User Name + Meow~ on hover."""
        mx, my = self.root.winfo_pointerxy()
        cat_center_x = self.x + self.cat_size / 2.0
        cat_center_y = self.y + self.cat_size / 2.0
        dist = math.hypot(mx - cat_center_x, my - cat_center_y)

        now = time.time()
        if dist <= 45:
            # Trigger greeting bubble once every 3.5 seconds on hover
            if now - self.last_hover_greeting_time >= 3.5:
                self.last_hover_greeting_time = now

                name = self.settings.get("user_name", "").strip()
                greeting = f"Hello {name}! Meow~" if name else "Hello! Meow~"

                self.show_speech_bubble(greeting, duration=2.5)
                self.spawn_petting_hearts(count=3)
                self.mood.add_affection(3.0)

                if self.state not in ("petting", "dragging"):
                    self.set_state("petting")

    def process_inputs(self):
        if self.settings.get("pause_reactions", False):
            return

        # --- Continuous Scroll Event (Paper Unroll persists while scrolling) ---
        if self.input_listener.is_scrolling(threshold_seconds=0.7) and self.state not in ("sleep", "dragging"):
            self.last_input_time = time.time()
            if self.state != "scroll_react":
                self.set_state("scroll_react")

            now = time.time()
            if now - self.last_scroll_particle_time > 0.25:
                self.last_scroll_particle_time = now
                self.spawn_paper_particles()
            return

        # --- Mouse Hunt: detect fast cursor movement ---
        if self.settings.get("mouse_hunt_enabled", True):
            velocity = self.input_listener.get_mouse_velocity()
            now = time.time()
            if velocity > 800 and now - self.mouse_hunt_cooldown > 5.0:
                self.mouse_hunt_cooldown = now
                if self.state not in ("pounce", "dragging", "typing_left_react", "typing_right_react"):
                    self.set_state("pounce")
                    self.show_speech_bubble("🐭!", duration=1.5)
                    mx, my = self.root.winfo_pointerxy()
                    self.target_x = float(max(self.v_min_x, min(self.v_width - self.cat_size, mx - self.cat_size / 2.0)))
                    self.target_y = float(max(self.v_min_y, min(self.v_height - self.cat_size, my - self.cat_size / 2.0)))
                    self.flip = (self.target_x < self.x)
                    return

        # --- Click Events & Double Left Click Big Jump ---
        click_evt = self.input_listener.pop_mouse_click()
        if click_evt:
            now = time.time()
            self.last_input_time = now
            if self.state == "sleep":
                self.set_state("sit")

            if self.peek_active:
                self.exit_peek_mode()

            if click_evt["button"] == "left":
                # Double left-click detection (< 380ms) -> Bigger Jump!
                is_double_click = (now - self.last_left_click_time < 0.38)
                self.last_left_click_time = now

                if is_double_click:
                    self.set_state("left_click_alt_react")
                    self.spawn_petting_hearts(count=4)
                    self.show_speech_bubble("Hop! 🐾", duration=1.5)
                else:
                    self.set_state("left_click_react")
                    self.spawn_petting_hearts(count=2)

            elif click_evt["button"] == "right":
                if self.state not in ("right_click_react", "right_click_alt_react"):
                    self.set_state("right_click_react")
            return

        # --- Typing Events ---
        if self.input_listener.is_typing(threshold_seconds=1.5):
            self.last_input_time = time.time()
            if self.state == "sleep":
                self.set_state("sit")

            if self.state not in ("left_click_react", "right_click_react"):
                current_kp = self.input_listener.keypress_count
                state_choice = "typing_left_react" if current_kp % 2 == 0 else "typing_right_react"
                self.set_state(state_choice)

    def update_state_machine(self):
        now = time.time()
        time_in_state = now - self.state_start_time
        time_since_input = now - self.last_input_time

        self.mood.update()
        pomo_state = self.productivity.update_pomodoro()

        # Stretch Reminder
        if self.productivity.check_stretch_reminder():
            self.set_state("stretch")
            text = self.get_personalized_text("time to stretch! 🤸")
            self.show_speech_bubble(text, duration=4.0)

        # Drink Water Reminder
        if self.productivity.check_water_reminder():
            text = self.get_personalized_text("drink water! 💧")
            self.show_speech_bubble(text, duration=4.0)
            self.spawn_water_particles()
            self.set_state("drink_water")
            if self.peek_active:
                self.exit_peek_mode()

        if pomo_state == "break" and self.state != "resting":
            self.set_state("resting")

        # Sleep after inactivity
        if time_since_input > 150 and self.state not in ("sleep", "resting", "peek",
                                                           "left_click_react", "right_click_react"):
            self.set_state("sleep")
            self.show_speech_bubble("Zzz...", duration=3.0)

        # State transitions
        if self.state in ("left_click_react", "left_click_alt_react", "right_click_react",
                          "right_click_alt_react", "eating", "stretch", "drink_water"):
            max_frames = self.sprite_manager.get_frame_count(self.state)
            if self.frame_index >= max_frames - 1:
                self.set_state("sit")

        elif self.state == "scroll_react":
            # Scroll animation persists while scrolling; when scrolling stops, return to sitting
            if not self.input_listener.is_scrolling(threshold_seconds=0.7):
                self.set_state("sit")

        elif self.state == "pounce":
            # Dash toward target
            speed = 18
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.hypot(dx, dy)

            # When cat reaches target, stop moving immediately and sit down!
            if dist > 8:
                step_x = math.copysign(min(abs(dx), speed), dx)
                step_y = math.copysign(min(abs(dy), speed), dy)
                self.x += step_x
                self.y += step_y
                self.flip = (dx < 0)
                self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
            else:
                self.set_state("sit")

        elif self.state in ("typing_left_react", "typing_right_react"):
            if not self.input_listener.is_typing(threshold_seconds=1.5):
                self.set_state("sit")
            else:
                typing_tier = self.input_listener.get_typing_tier()
                if typing_tier in ("fast", "very_fast"):
                    self.spawn_heat_particles()

        elif self.state == "petting":
            if time_in_state > 2.5:
                self.set_state("sit")

        elif self.state == "peek":
            pass

        elif self.state in ("sit", "idle_breathe"):
            if time_in_state >= self.idle_pause_duration:
                if self.settings.get("peek_mode_enabled", False) and not self.peek_active:
                    self.enter_peek_mode()
                else:
                    self.set_state(self.select_next_idle_substate())

        elif self.state in self.SPECIAL_IDLE_STATES:
            max_frames = self.sprite_manager.get_frame_count(self.state)
            if self.frame_index >= max_frames - 1:
                self.set_state("sit")

        # Movement: Follow Cursor Mode
        can_move = self.state not in ("left_click_react", "left_click_alt_react", "right_click_react",
                                       "right_click_alt_react", "typing_left_react", "typing_right_react",
                                       "sleep", "resting", "eating", "petting", "dragging",
                                       "pounce", "peek", "scroll_react", "drink_water")

        if can_move and self.settings.get("follow_cursor", False):
            mx, my = self.root.winfo_pointerxy()
            cat_center_x = self.x + self.cat_size / 2.0
            cat_center_y = self.y + self.cat_size / 2.0

            dist = math.hypot(mx - cat_center_x, my - cat_center_y)
            follow_threshold = self.settings.get("follow_distance", 80)
            is_mouse_active = self.input_listener.is_mouse_moving(threshold_seconds=0.6)

            # When cursor is moving and far, walk towards it
            if is_mouse_active and dist > follow_threshold:
                if self.state != "walk":
                    self.set_state("walk")

                offset_x = -35 if mx < cat_center_x else 35
                self.target_x = max(self.v_min_x, min(self.v_width - self.cat_size, mx - self.cat_size / 2.0 + offset_x))
                self.target_y = max(self.v_min_y, min(self.v_height - self.cat_size, my - self.cat_size / 2.0 + 20))

                speed = self.settings.get("move_speed", 7)
                dx = self.target_x - self.x
                dy = self.target_y - self.y

                step_x = math.copysign(min(abs(dx), speed), dx) if abs(dx) > 0.5 else 0
                step_y = math.copysign(min(abs(dy), speed), dy) if abs(dy) > 0.5 else 0

                self.x += step_x
                self.y += step_y
                self.flip = (dx < 0)
                self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
            else:
                # When cursor isn't moving or cat reaches cursor -> cat sits down!
                if self.state == "walk":
                    self.set_state("sit")

    def render_frame(self):
        """Draws current sprite frame with all visual effects."""
        mx, my = self.root.winfo_pointerxy()
        cat_center_x = self.x + self.cat_size / 2.0
        cat_center_y = self.y + self.cat_size / 2.0

        pupil_x = int(max(-2, min(2, (mx - cat_center_x) / 60.0)))
        pupil_y = int(max(-2, min(2, (my - cat_center_y) / 60.0)))

        typing_tier = self.input_listener.get_typing_tier()

        frame_photo = self.sprite_manager.get_frame(
            self.state,
            self.frame_index,
            flip=self.flip,
            master=self.root,
            pupil_offset=(pupil_x, pupil_y),
            typing_tier=typing_tier
        )
        self.current_photo = frame_photo

        if self.cat_image_id is None:
            self.cat_image_id = self.canvas.create_image(0, 0, anchor="nw", image=self.current_photo)
        else:
            self.canvas.itemconfig(self.cat_image_id, image=self.current_photo)

        total_frames = self.sprite_manager.get_frame_count(self.state)
        self.frame_index = (self.frame_index + 1) % total_frames

        self.update_particles()

    def main_loop(self):
        try:
            if not self.is_dragging:
                self.process_inputs()
                self.check_hover_greeting()
                self.update_state_machine()
            else:
                self.update_state_machine()
            self.render_frame()
        except Exception as e:
            logger.error("Error in main loop tick: %s", e)

        fps = self.sprite_manager.get_fps(self.state)

        # Dynamic Typing Speed: As typing speed increases, paw tapping speed increases proportionally!
        if "typing" in self.state:
            kps = self.input_listener.get_kps()
            # Scales smoothly: 1 KPS -> 11 FPS, 4 KPS -> 22 FPS, 7+ KPS -> 30-32 FPS
            fps = min(32, max(8, int(8 + kps * 3.5)))

        delay_ms = max(30, int(1000 / fps))
        self.root.after(delay_ms, self.main_loop)

    def run(self):
        logger.info("Starting Desktop Cat Pet v9.0...")
        self.input_listener.start()
        self.tray.start()

        self.main_loop()

        try:
            self.root.mainloop()
        finally:
            self.clean_exit()

    def quit_app(self):
        logger.info("Quit command received.")
        self.root.after(0, self.root.destroy)

    def clean_exit(self):
        logger.info("Cleaning up resources...")
        self.input_listener.stop()
        self.tray.stop()
        logger.info("Desktop Cat Pet exited cleanly.")


if __name__ == "__main__":
    app = DesktopCatApp()
    app.run()
