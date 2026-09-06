import os
import logging
import threading
from PIL import Image
import pystray
from pystray import MenuItem as item, Menu

logger = logging.getLogger("DesktopCat.Tray")


class TrayIconManager:
    """Manages system tray icon using pystray in a separate thread."""

    def __init__(self, app_callbacks, icon_path):
        self.callbacks = app_callbacks
        self.icon_path = icon_path
        self.icon = None
        self.thread = None

    def create_menu(self):
        def is_follow_enabled(item):
            return self.callbacks.get_setting("follow_cursor", False)

        def toggle_follow(icon, item):
            current = self.callbacks.get_setting("follow_cursor", False)
            self.callbacks.set_setting("follow_cursor", not current)

        def is_pause_enabled(item):
            return self.callbacks.get_setting("pause_reactions", False)

        def toggle_pause(icon, item):
            current = self.callbacks.get_setting("pause_reactions", False)
            self.callbacks.set_setting("pause_reactions", not current)

        def is_laser_enabled(item):
            return self.callbacks.get_setting("laser_mode", False)

        def toggle_laser(icon, item):
            current = self.callbacks.get_setting("laser_mode", False)
            self.callbacks.set_setting("laser_mode", not current)

        def is_pomodoro_enabled(item):
            return self.callbacks.get_setting("pomodoro_enabled", False)

        def toggle_pomodoro(icon, item):
            current = self.callbacks.get_setting("pomodoro_enabled", False)
            self.callbacks.set_setting("pomodoro_enabled", not current)
            self.callbacks.toggle_pomodoro()

        def is_winwatch_enabled(item):
            return self.callbacks.get_setting("window_watch_enabled", False)

        def toggle_winwatch(icon, item):
            current = self.callbacks.get_setting("window_watch_enabled", False)
            self.callbacks.set_setting("window_watch_enabled", not current)

        def is_startup_enabled(item):
            return self.callbacks.is_startup_enabled()

        def toggle_startup(icon, item):
            self.callbacks.toggle_startup()

        def is_hunt_enabled(item):
            return self.callbacks.get_setting("mouse_hunt_enabled", True)

        def toggle_hunt(icon, item):
            current = self.callbacks.get_setting("mouse_hunt_enabled", True)
            self.callbacks.set_setting("mouse_hunt_enabled", not current)

        def is_peek_enabled(item):
            return self.callbacks.get_setting("peek_mode_enabled", False)

        def toggle_peek(icon, item):
            self.callbacks.toggle_peek_mode()

        def is_water_enabled(item):
            return self.callbacks.get_setting("drink_water_enabled", True)

        def toggle_water(icon, item):
            current = self.callbacks.get_setting("drink_water_enabled", True)
            self.callbacks.set_setting("drink_water_enabled", not current)

        # Movement Mode Submenu
        def make_move_radio(mode_val):
            def is_mode_selected(item):
                return self.callbacks.get_setting("movement_mode", "freeroam") == mode_val

            def set_mode(icon, item):
                self.callbacks.set_setting("movement_mode", mode_val)

            return is_mode_selected, set_mode

        move_menu = Menu(
            item("Free Roam", make_move_radio("freeroam")[1], checked=make_move_radio("freeroam")[0], radio=True),
            item("Taskbar Mode 📌", make_move_radio("taskbar")[1], checked=make_move_radio("taskbar")[0], radio=True)
        )

        # Cat Pattern Submenu (Siamese, Orange, Mackerel, Midnight)
        def make_pattern_radio(skin_name):
            def is_selected(item):
                return self.callbacks.get_setting("active_skin", "default") == skin_name

            def set_skin(icon, item):
                self.callbacks.set_setting("active_skin", skin_name)

            return is_selected, set_skin

        patterns = [
            ("Orange 🟠", "default"),
            ("Siamese 🐱", "siamese"),
            ("Mackerel 🐈", "mackerel"),
            ("Midnight 🌙", "midnight"),
        ]
        pattern_items = [
            item(label, make_pattern_radio(skin)[1], checked=make_pattern_radio(skin)[0], radio=True)
            for label, skin in patterns
        ]
        pattern_menu = Menu(*pattern_items)

        # Accessories Submenu
        def make_acc_radio(acc_name):
            def is_acc_selected(item):
                return self.callbacks.get_setting("active_accessory", "none") == acc_name

            def set_acc(icon, item):
                self.callbacks.set_setting("active_accessory", acc_name)

            return is_acc_selected, set_acc

        accs = ["none", "bow", "collar"]
        acc_items = [item(a.capitalize(), make_acc_radio(a)[1], checked=make_acc_radio(a)[0], radio=True) for a in accs]
        acc_menu = Menu(*acc_items)

        # Speed Submenu
        def make_speed_radio(label, speed_val):
            def is_speed_selected(item):
                return self.callbacks.get_setting("move_speed", 7) == speed_val

            def set_speed(icon, item):
                self.callbacks.set_setting("move_speed", speed_val)

            return is_speed_selected, set_speed

        speed_presets = [("Slow", 4), ("Normal", 7), ("Fast", 12), ("Zoomies", 18)]
        speed_items = [item(lbl, make_speed_radio(lbl, val)[1], checked=make_speed_radio(lbl, val)[0], radio=True) for lbl, val in speed_presets]
        speed_menu = Menu(*speed_items)

        def feed_fish(icon, item):
            self.callbacks.feed_fish()

        def reset_pos(icon, item):
            self.callbacks.reset_position()

        def tell_name(icon, item):
            self.callbacks.ask_user_name()

        def quit_app(icon, item):
            self.callbacks.quit_app()

        menu = Menu(
            item("Cat Pattern 🎨", pattern_menu),
            item("Movement Mode", move_menu),
            item("Feed Fish Treat 🐟", feed_fish),
            item("Mouse Hunt Mode 🐭", toggle_hunt, checked=is_hunt_enabled),
            item("Peek Mode 👀", toggle_peek, checked=is_peek_enabled),
            item("Drink Water Reminder 💧", toggle_water, checked=is_water_enabled),
            item("Laser Pointer Mode 🔴", toggle_laser, checked=is_laser_enabled),
            item("Follow Cursor", toggle_follow, checked=is_follow_enabled),
            item("Accessories", acc_menu),
            item("Movement Speed", speed_menu),
            item("Pomodoro Mode (25/5m)", toggle_pomodoro, checked=is_pomodoro_enabled),
            item("App Awareness (Opt-In)", toggle_winwatch, checked=is_winwatch_enabled),
            item("Launch on Windows Startup", toggle_startup, checked=is_startup_enabled),
            item("Pause Reactions", toggle_pause, checked=is_pause_enabled),
            item("Tell Your Name 📛", tell_name),
            item("Reset Position", reset_pos),
            item("Quit", quit_app)
        )
        return menu

    def start(self):
        try:
            if os.path.exists(self.icon_path):
                img = Image.open(self.icon_path)
            else:
                img = Image.new("RGBA", (32, 32), (245, 140, 45, 255))

            self.icon = pystray.Icon("DesktopCat", img, "Desktop Cat Pet v8.0", self.create_menu())
            self.thread = threading.Thread(target=self.icon.run, daemon=True)
            self.thread.start()
            logger.info("System tray icon started.")
        except Exception as e:
            logger.error("Failed to start system tray icon: %s", e)

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        logger.info("System tray icon stopped.")
