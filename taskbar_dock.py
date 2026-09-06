import logging

logger = logging.getLogger("DesktopCat.TaskbarDock")

try:
    import win32gui
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class TaskbarDockManager:
    """Detects Windows taskbar geometry, edge position, and auto-hide state."""

    def __init__(self):
        self.taskbar_hwnd = None
        self.update_taskbar_info()

    def update_taskbar_info(self):
        if not WIN32_AVAILABLE:
            return

        try:
            self.taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        except Exception as e:
            logger.debug("Failed to find Taskbar window handle: %s", e)

    def get_taskbar_rect(self):
        """Returns (left, top, right, bottom) rect of Windows Taskbar."""
        if not WIN32_AVAILABLE or not self.taskbar_hwnd:
            self.update_taskbar_info()

        if WIN32_AVAILABLE and self.taskbar_hwnd:
            try:
                rect = win32gui.GetWindowRect(self.taskbar_hwnd)
                return rect
            except Exception as e:
                logger.debug("Failed to get Taskbar window rect: %s", e)

        # Fallback for default bottom taskbar on 1080p
        return (0, 1040, 1920, 1080)

    def get_taskbar_top_y(self, cat_height):
        """Returns exact Y coordinate for sitting on top of the taskbar."""
        left, top, right, bottom = self.get_taskbar_rect()
        return float(top - cat_height)

    def is_taskbar_visible(self):
        """Checks if taskbar is currently visible (not auto-hidden)."""
        if not WIN32_AVAILABLE or not self.taskbar_hwnd:
            return True

        try:
            return win32gui.IsWindowVisible(self.taskbar_hwnd)
        except Exception:
            return True
