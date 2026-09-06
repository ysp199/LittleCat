import logging

logger = logging.getLogger("DesktopCat.WindowWatch")

try:
    import win32gui
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class WindowWatcher:
    """Safely inspects active foreground window title (OPT-IN, OFF BY DEFAULT)."""

    def __init__(self, settings_manager):
        self.settings = settings_manager

    def is_enabled(self):
        return self.settings.get("window_watch_enabled", False) and WIN32_AVAILABLE

    def get_active_window_category(self):
        """Categorizes foreground window into 'code', 'browser', 'video', or 'other'."""
        if not self.is_enabled():
            return "other"

        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd).lower()

            if any(term in title for term in ["code", "pycharm", "visual studio", "sublime", "terminal", "cmd", "powershell"]):
                return "code"
            elif any(term in title for term in ["chrome", "firefox", "edge", "brave", "opera"]):
                return "browser"
            elif any(term in title for term in ["vlc", "youtube", "netflix", "media player", "mpv"]):
                return "video"
        except Exception as e:
            logger.debug("Failed to read foreground window title: %s", e)

        return "other"
