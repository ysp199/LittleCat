import os
import sys
import logging

logger = logging.getLogger("DesktopCat.Startup")


class StartupManager:
    """Manages Windows Startup shortcut for auto-launch on boot."""

    def __init__(self):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        self.startup_folder = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        self.shortcut_path = os.path.join(self.startup_folder, "DesktopCat.bat")

    def is_startup_enabled(self):
        return os.path.exists(self.shortcut_path)

    def set_startup(self, enable=True):
        try:
            if enable:
                target_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
                cmd = f'@start "" "{target_exe}"'
                with open(self.shortcut_path, "w", encoding="utf-8") as f:
                    f.write(cmd)
                logger.info("Created Windows Startup launcher at %s", self.shortcut_path)
            else:
                if os.path.exists(self.shortcut_path):
                    os.remove(self.shortcut_path)
                    logger.info("Removed Windows Startup launcher from %s", self.shortcut_path)
        except Exception as e:
            logger.error("Failed to update Windows Startup setting: %s", e)
