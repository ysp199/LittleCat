import os
import sys
import datetime
import logging
from PIL import Image, ImageDraw, ImageTk, ImageEnhance, ImageOps

logger = logging.getLogger("DesktopCat.SpriteManager")

TRANSPARENT_COLOR_HEX = "#000001"
TRANSPARENT_COLOR_RGB = (0, 0, 1, 255)
TRANSPARENT_BG_RGB = (0, 0, 1)

# Compact 32x32 Frame Size for Complete Full-Body Cat Pet
FRAME_SIZE = (32, 32)

ANIMATION_CONFIG = {
    "idle_breathe": {"frames": 4, "fps": 3},
    "idle_play": {"frames": 6, "fps": 5},
    "idle_roll": {"frames": 6, "fps": 5},
    "idle_jump": {"frames": 5, "fps": 6},
    "idle_groom": {"frames": 6, "fps": 4},
    "idle_look_around": {"frames": 4, "fps": 3},
    "walk": {"frames": 4, "fps": 10},
    "sit": {"frames": 4, "fps": 4},
    "sleep": {"frames": 4, "fps": 3},
    "left_click_react": {"frames": 4, "fps": 12},
    "left_click_alt_react": {"frames": 4, "fps": 12},
    "right_click_react": {"frames": 4, "fps": 12},
    "right_click_alt_react": {"frames": 4, "fps": 12},
    "typing_left_react": {"frames": 4, "fps": 12},
    "typing_right_react": {"frames": 4, "fps": 12},
    "petting": {"frames": 4, "fps": 6},
    "dragging": {"frames": 4, "fps": 8},
    "stretch": {"frames": 4, "fps": 4},
    "resting": {"frames": 4, "fps": 3},
    "eating": {"frames": 4, "fps": 8},
    "pounce": {"frames": 4, "fps": 12},
    "scroll_react": {"frames": 4, "fps": 8},
    "peek": {"frames": 4, "fps": 4},
    "drink_water": {"frames": 4, "fps": 5},
}


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def generate_placeholder_assets(assets_dir, skin_name="default"):
    """Procedurally generates full-body 32x32 cat pet frames based on Version 4."""
    os.makedirs(assets_dir, exist_ok=True)

    from settings import CAT_PATTERNS
    pattern = CAT_PATTERNS.get(skin_name, CAT_PATTERNS["orange"])

    CAT_COLOR = pattern["body"]
    DARK_COLOR = pattern["dark"]
    LIGHT_COLOR = pattern["light"]
    markings_type = pattern.get("markings")

    WHITE = (255, 255, 255, 255)
    PINK = (255, 150, 170, 255)
    DARK_EYE = (25, 25, 30, 255)
    KEY_COLOR = (150, 150, 160, 255)
    KEY_BORDER = (80, 80, 90, 255)
    PAPER_COLOR = (245, 240, 230, 255)

    def create_frame():
        return Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))

    def draw_markings(draw, bx, by, posture="stand"):
        """Draws tabby stripes or siamese points on body/head."""
        if markings_type == "points":
            # Siamese: dark face mask & ear tips
            draw.rectangle([bx + 4, by - 4, bx + 8, by - 1], fill=DARK_COLOR)
            draw.point((bx + 3, by - 6), fill=DARK_COLOR)
            draw.point((bx + 7, by - 6), fill=DARK_COLOR)
        elif markings_type == "stripes":
            # Tabby stripes
            if posture == "stand":
                draw.line([(bx + 3, by + 1), (bx + 3, by + 5)], fill=DARK_COLOR)
                draw.line([(bx + 7, by + 1), (bx + 7, by + 5)], fill=DARK_COLOR)
                draw.line([(bx + 11, by + 1), (bx + 11, by + 5)], fill=DARK_COLOR)
            elif posture == "sit":
                draw.line([(bx + 4, by + 3), (bx + 4, by + 8)], fill=DARK_COLOR)
                draw.line([(bx + 8, by + 3), (bx + 8, by + 8)], fill=DARK_COLOR)

    def draw_cat_full_body(draw, offset_x=0, offset_y=0, posture="stand",
                           eye_state="open", paw_left=0, paw_right=0,
                           tail_angle=0, key_impact=None, look_dir=0):
        """Draws complete full-body cat: ears, head, face, torso, belly, paws, and tail."""
        bx, by = 8 + offset_x, 14 + offset_y

        # 1. SLEEPING / RESTING LOAF
        if posture == "sleep" or posture == "resting":
            draw.ellipse([bx - 1, by + 2, bx + 15, by + 12], fill=CAT_COLOR, outline=DARK_COLOR)
            draw.ellipse([bx + 10, by + 1, bx + 16, by + 8], fill=CAT_COLOR, outline=DARK_COLOR)
            draw.polygon([(bx + 11, by + 1), (bx + 13, by - 2), (bx + 14, by + 1)], fill=PINK)
            draw.line([(bx + 12, by + 4), (bx + 14, by + 4)], fill=DARK_EYE)
            draw.arc([bx - 3, by + 4, bx + 5, by + 12], 90, 270, fill=DARK_COLOR, width=2)
            return

        # 2. PLAYFUL ROLL
        if posture == "roll":
            draw.ellipse([bx - 2, by + 1, bx + 14, by + 11], fill=CAT_COLOR)
            draw.rectangle([bx + 3, by + 3, bx + 9, by + 9], fill=WHITE)
            draw.line([(bx + 2, by + 1), (bx + 2, by - 3)], fill=LIGHT_COLOR, width=2)
            draw.line([(bx + 8, by + 1), (bx + 8, by - 3)], fill=LIGHT_COLOR, width=2)
            return

        # 3. DRAGGING / SURPRISED
        if posture == "dragging":
            draw.rectangle([bx + 3, by - 4, bx + 11, by + 12], fill=CAT_COLOR)
            draw.rectangle([bx + 5, by - 2, bx + 9, by + 10], fill=WHITE)
            hx, hy = bx + 2, by - 8
            draw.rectangle([hx, hy, hx + 10, hy + 6], fill=CAT_COLOR)
            draw.polygon([(hx + 1, hy), (hx + 3, hy - 3), (hx + 4, hy)], fill=PINK)
            draw.polygon([(hx + 6, hy), (hx + 8, hy - 3), (hx + 9, hy)], fill=PINK)
            draw.rectangle([hx + 2, hy + 2, hx + 4, hy + 4], fill=DARK_EYE)
            draw.rectangle([hx + 6, hy + 2, hx + 8, hy + 4], fill=DARK_EYE)
            draw.line([(bx + 4, by + 12), (bx + 4, by + 15)], fill=LIGHT_COLOR, width=2)
            draw.line([(bx + 10, by + 12), (bx + 10, by + 15)], fill=LIGHT_COLOR, width=2)
            return

        # 4. PEEK MODE (Head & Paw Peeking from edge)
        if posture == "peek":
            hx, hy = bx + 6, by - 2
            draw.rectangle([hx, hy, hx + 8, hy + 7], fill=CAT_COLOR)
            draw.polygon([(hx + 1, hy), (hx + 3, hy - 3), (hx + 4, hy)], fill=PINK)
            draw.polygon([(hx + 5, hy), (hx + 7, hy - 3), (hx + 8, hy)], fill=PINK)
            draw.rectangle([hx + 2, hy + 2, hx + 4, hy + 4], fill=DARK_EYE)
            draw.rectangle([hx + 5, hy + 2, hx + 7, hy + 4], fill=DARK_EYE)
            draw.point((hx + 3, hy + 2), fill=WHITE)
            draw.point((hx + 6, hy + 2), fill=WHITE)
            draw.point((hx + 4, hy + 4), fill=PINK)
            draw.rectangle([hx + 1, hy + 7, hx + 4, hy + 10], fill=WHITE)
            return

        # 6. SCROLL REACT (Paper Unrolling)
        if posture == "scroll":
            # Sitting cat holding paper roll
            draw.rectangle([bx + 2, by + 2, bx + 12, by + 12], fill=CAT_COLOR)
            draw.rectangle([bx + 4, by + 4, bx + 10, by + 12], fill=WHITE)
            hx, hy = bx + 2, by - 6
            draw.rectangle([hx, hy, hx + 10, hy + 7], fill=CAT_COLOR)
            draw.polygon([(hx + 1, hy), (hx + 3, hy - 4), (hx + 4, hy)], fill=PINK)
            draw.polygon([(hx + 6, hy), (hx + 7, hy - 4), (hx + 9, hy)], fill=PINK)
            draw.rectangle([hx + 2, hy + 2, hx + 4, hy + 4], fill=DARK_EYE)
            draw.rectangle([hx + 6, hy + 2, hx + 8, hy + 4], fill=DARK_EYE)
            # Paper roll
            draw.rectangle([bx + 4, by + 7, bx + 10, by + 9], fill=PAPER_COLOR, outline=DARK_EYE)
            draw.rectangle([bx + 5, by + 9, bx + 9, by + 15], fill=PAPER_COLOR)
            draw.line([(bx + 6, by + 11), (bx + 8, by + 11)], fill=DARK_EYE)
            draw.line([(bx + 6, by + 13), (bx + 8, by + 13)], fill=DARK_EYE)
            return

        # 7. STRETCH
        if posture == "stretch":
            draw.rectangle([bx, by + 2, bx + 15, by + 9], fill=CAT_COLOR)
            draw.rectangle([bx + 10, by + 8, bx + 17, by + 11], fill=WHITE)
            hx, hy = bx + 11, by - 2
            draw.rectangle([hx, hy, hx + 7, hy + 6], fill=CAT_COLOR)
            draw.polygon([(hx + 1, hy), (hx + 3, hy - 3), (hx + 4, hy)], fill=PINK)
            draw.polygon([(hx + 4, hy), (hx + 6, hy - 3), (hx + 7, hy)], fill=PINK)
            draw.line([(hx + 2, hy + 2), (hx + 5, hy + 2)], fill=DARK_EYE)
            return

        # 8. SITTING POSTURE (Full body sitting with paws and tail)
        if posture == "sit":
            # Torso & white belly
            draw.rectangle([bx + 2, by + 2, bx + 12, by + 12], fill=CAT_COLOR)
            draw.rectangle([bx + 4, by + 4, bx + 10, by + 12], fill=WHITE)
            draw_markings(draw, bx, by, posture="sit")

            # Head
            hx, hy = bx + 2 + look_dir, by - 6
            draw.rectangle([hx, hy, hx + 10, hy + 7], fill=CAT_COLOR)
            draw.polygon([(hx + 1, hy), (hx + 3, hy - 4), (hx + 4, hy)], fill=PINK)
            draw.polygon([(hx + 6, hy), (hx + 7, hy - 4), (hx + 9, hy)], fill=PINK)

            # Eyes
            if eye_state == "purr":
                draw.line([(hx + 2, hy + 2), (hx + 4, hy + 4)], fill=DARK_EYE)
                draw.line([(hx + 4, hy + 4), (hx + 6, hy + 2)], fill=DARK_EYE)
            elif eye_state == "blink":
                draw.line([(hx + 2, hy + 3), (hx + 4, hy + 3)], fill=DARK_EYE)
                draw.line([(hx + 6, hy + 3), (hx + 8, hy + 3)], fill=DARK_EYE)
            else:
                draw.rectangle([hx + 2, hy + 2, hx + 4, hy + 4], fill=DARK_EYE)
                draw.rectangle([hx + 6, hy + 2, hx + 8, hy + 4], fill=DARK_EYE)
                draw.point((hx + 3, hy + 2), fill=WHITE)
                draw.point((hx + 7, hy + 2), fill=WHITE)

            # Pink nose
            draw.point((hx + 5, hy + 4), fill=PINK)

            # Front Paws
            draw.rectangle([bx + 2, by + 8 - paw_left, bx + 5, by + 12 - paw_left], fill=WHITE)
            draw.rectangle([bx + 9, by + 8 - paw_right, bx + 12, by + 12 - paw_right], fill=WHITE)

            # Keycaps ONLY when typing
            if key_impact == "left":
                draw.rectangle([bx + 1, by + 13, bx + 6, by + 15], fill=KEY_COLOR, outline=KEY_BORDER)
            elif key_impact == "right":
                draw.rectangle([bx + 8, by + 13, bx + 13, by + 15], fill=KEY_COLOR, outline=KEY_BORDER)

            # Tail
            tx = bx - 1
            draw.line([(tx, by + 10), (tx - 3, by + 6 + tail_angle), (tx - 1, by + 2 + tail_angle)], fill=DARK_COLOR, width=2)
            return

        # 9. STANDING / WALKING / POUNCING (Full body standing on 4 paws with tail)
        draw.rectangle([bx, by, bx + 14, by + 8], fill=CAT_COLOR)
        draw.rectangle([bx + 2, by + 3, bx + 6, by + 8], fill=WHITE)
        draw_markings(draw, bx, by, posture="stand")

        # Head
        hx, hy = bx + 10 + look_dir, by - 4
        draw.rectangle([hx, hy, hx + 8, hy + 7], fill=CAT_COLOR)
        draw.polygon([(hx + 1, hy), (hx + 3, hy - 3), (hx + 4, hy)], fill=PINK)
        draw.polygon([(hx + 5, hy), (hx + 6, hy - 3), (hx + 7, hy)], fill=PINK)

        # Eyes
        if eye_state == "wide":
            draw.rectangle([hx + 1, hy + 1, hx + 4, hy + 5], fill=WHITE)
            draw.rectangle([hx + 5, hy + 1, hx + 8, hy + 5], fill=WHITE)
            draw.rectangle([hx + 2, hy + 2, hx + 3, hy + 4], fill=DARK_EYE)
            draw.rectangle([hx + 6, hy + 2, hx + 7, hy + 4], fill=DARK_EYE)
        elif eye_state == "blink":
            draw.line([(hx + 2, hy + 3), (hx + 4, hy + 3)], fill=DARK_EYE)
            draw.line([(hx + 5, hy + 3), (hx + 7, hy + 3)], fill=DARK_EYE)
        else:
            draw.rectangle([hx + 2, hy + 2, hx + 4, hy + 4], fill=DARK_EYE)
            draw.rectangle([hx + 5, hy + 2, hx + 7, hy + 4], fill=DARK_EYE)
            draw.point((hx + 3, hy + 2), fill=WHITE)
            draw.point((hx + 6, hy + 2), fill=WHITE)

        # Pink nose
        draw.point((hx + 4, hy + 4), fill=PINK)

        # 4 Legs / Paws
        draw.rectangle([bx + 1, by + 8, bx + 3, by + 11 + paw_left], fill=LIGHT_COLOR)
        draw.rectangle([bx + 4, by + 8, bx + 6, by + 11 - paw_left], fill=CAT_COLOR)
        draw.rectangle([bx + 8, by + 8, bx + 10, by + 11 + paw_right], fill=LIGHT_COLOR)
        draw.rectangle([bx + 11, by + 8, bx + 13, by + 11 - paw_right], fill=CAT_COLOR)

        # Tail
        tx = bx
        draw.line([(tx, by + 2), (tx - 3, by - 2 + tail_angle), (tx - 2, by - 5 + tail_angle)], fill=DARK_COLOR, width=2)

    def save_sheet(filename, num_frames, draw_func):
        sheet = Image.new("RGBA", (32 * num_frames, 32), (0, 0, 0, 0))
        for f in range(num_frames):
            frame = create_frame()
            draw = ImageDraw.Draw(frame)
            draw_func(draw, f)
            sheet.paste(frame, (f * 32, 0))
        sheet.save(os.path.join(assets_dir, filename))

    # --- IDLE & BEHAVIOR SPRITESHEETS ---
    save_sheet("idle_breathe.png", 4, lambda draw, f: draw_cat_full_body(draw, offset_y=-1 if f == 2 else 0, eye_state="blink" if f == 1 else "open", tail_angle=2 if f == 3 else 0))
    save_sheet("idle_play.png", 6, lambda draw, f: draw_cat_full_body(draw, posture="sit", paw_right=4 if f in (1, 2, 4) else 0, tail_angle=f % 3))
    save_sheet("idle_roll.png", 6, lambda draw, f: draw_cat_full_body(draw, posture="roll" if f in (1, 2, 3, 4) else "sit"))
    save_sheet("idle_jump.png", 5, lambda draw, f: draw_cat_full_body(draw, offset_y=-12 if f in (1, 2) else (-6 if f == 3 else 0), eye_state="wide" if f in (1, 2) else "open"))
    save_sheet("idle_groom.png", 6, lambda draw, f: draw_cat_full_body(draw, posture="sit", paw_left=3 if f % 2 == 1 else 1, eye_state="blink" if f in (2, 3) else "open"))
    save_sheet("idle_look_around.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", look_dir=-2 if f == 1 else (2 if f == 3 else 0)))

    save_sheet("walk.png", 4, lambda draw, f: draw_cat_full_body(draw, offset_y=-1 if f % 2 == 1 else 0, paw_left=2 if f in (0, 2) else -1, paw_right=-1 if f in (0, 2) else 2, tail_angle=f))
    save_sheet("sit.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", eye_state="blink" if f == 2 else "open", tail_angle=f % 3))
    save_sheet("sleep.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sleep"))
    save_sheet("resting.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="resting"))
    save_sheet("stretch.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="stretch"))
    save_sheet("dragging.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="dragging"))
    save_sheet("petting.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", eye_state="purr", tail_angle=f % 2))
    save_sheet("left_click.png", 4, lambda draw, f: draw_cat_full_body(draw, offset_y=-6 if f == 1 else (-4 if f == 2 else 0), eye_state="wide", tail_angle=-3))
    save_sheet("left_click_alt.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", offset_y=-14 if f in (1, 2) else 0, eye_state="wide"))
    save_sheet("right_click.png", 4, lambda draw, f: draw_cat_full_body(draw, eye_state="wide"))
    save_sheet("right_click_alt.png", 4, lambda draw, f: draw_cat_full_body(draw, offset_y=-3 if f == 2 else 0, eye_state="wide"))
    save_sheet("typing_left.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", paw_left=4 if f in (0, 1) else -1, paw_right=-1, key_impact="left" if f in (0, 1) else None))
    save_sheet("typing_right.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", paw_left=-1, paw_right=4 if f in (0, 1) else -1, key_impact="right" if f in (0, 1) else None))
    save_sheet("eating.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", eye_state="purr"))
    save_sheet("pounce.png", 4, lambda draw, f: draw_cat_full_body(draw, offset_y=-8 if f == 1 else -4, eye_state="wide", tail_angle=3))
    save_sheet("scroll_react.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="scroll"))
    save_sheet("peek.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="peek"))
    save_sheet("drink_water.png", 4, lambda draw, f: draw_cat_full_body(draw, posture="sit", eye_state="purr" if f in (2, 3) else "open"))

    # Icon
    ico_img = create_frame()
    draw = ImageDraw.Draw(ico_img)
    draw_cat_full_body(draw, posture="sit")
    ico_img.save(os.path.join(assets_dir, "cat.ico"), format="ICO", sizes=[(32, 32), (48, 48), (64, 64)])


def generate_eye_and_typing_effects(assets_dir):
    """Generates pupil overlay (eyes.png) and fast typing red heat lines (typing_effect.png)."""
    os.makedirs(assets_dir, exist_ok=True)

    eyes = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(eyes)
    draw.point((13, 11), fill=(20, 20, 20, 255))
    draw.point((17, 11), fill=(20, 20, 20, 255))
    eyes.save(os.path.join(assets_dir, "eyes.png"))

    sparks = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sparks)
    draw.line([(10, 2), (10, 5)], fill=(255, 40, 40, 255), width=1)
    draw.line([(15, 1), (15, 6)], fill=(255, 20, 20, 255), width=1)
    draw.line([(20, 2), (20, 5)], fill=(255, 40, 40, 255), width=1)
    sparks.save(os.path.join(assets_dir, "typing_effect.png"))


def generate_accessory_assets(acc_dir):
    os.makedirs(acc_dir, exist_ok=True)

    # Pink Bow: positioned on top of the cat's head/ear
    bow = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bow)
    draw.polygon([(10, 4), (13, 6), (10, 8)], fill=(255, 20, 147, 255))
    draw.polygon([(16, 4), (13, 6), (16, 8)], fill=(255, 20, 147, 255))
    draw.rectangle([12, 5, 14, 7], fill=(255, 255, 255, 255))
    bow.save(os.path.join(acc_dir, "bow.png"))

    # Red Collar: positioned neatly around the cat's neck with gold bell
    collar = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(collar)
    draw.rectangle([11, 14, 18, 15], fill=(230, 30, 30, 255))
    draw.rectangle([14, 16, 15, 17], fill=(255, 215, 0, 255))
    collar.save(os.path.join(acc_dir, "collar.png"))


class SpriteManager:
    """Manages 32x32 Full-Body Desktop Cat Pet with crisp pixel art scaling and animations."""

    def __init__(self, scale=3, color_name="orange", skin_name="default", accessory_name="none"):
        self.scale = scale
        self.color_name = color_name
        self.skin_name = skin_name
        self.accessory_name = accessory_name

        self.root_assets_dir = resource_path("assets")
        self.skins_dir = resource_path("skins")
        self.accessories_dir = resource_path("accessories")

        generate_placeholder_assets(self.root_assets_dir, "default")
        generate_placeholder_assets(os.path.join(self.skins_dir, "default"), "default")
        generate_placeholder_assets(os.path.join(self.skins_dir, "midnight"), "midnight")
        generate_placeholder_assets(os.path.join(self.skins_dir, "siamese"), "siamese")
        generate_placeholder_assets(os.path.join(self.skins_dir, "mackerel"), "mackerel")
        generate_accessory_assets(self.accessories_dir)
        generate_eye_and_typing_effects(self.root_assets_dir)

        self.animations = {}
        self.photo_cache = {}
        self.accessory_img = None
        self.eyes_img = None
        self.typing_effect_img = None

        self.load_all_sprites()

    def set_skin(self, skin_name):
        if self.skin_name != skin_name:
            self.skin_name = skin_name
            self.load_all_sprites()

    def set_accessory(self, acc_name):
        if self.accessory_name != acc_name:
            self.accessory_name = acc_name
            self.load_all_sprites()

    def set_scale(self, scale):
        if self.scale != scale:
            self.scale = scale
            self.load_all_sprites()

    def set_color(self, color_name):
        if self.color_name != color_name:
            self.color_name = color_name
            self.load_all_sprites()

    def apply_day_night_tint(self, image):
        hour = datetime.datetime.now().hour
        if hour >= 19 or hour < 6:
            r, g, b, a = image.split()
            rgb = Image.merge("RGB", (r, g, b))
            enhancer = ImageEnhance.Brightness(rgb)
            rgb = enhancer.enhance(0.85)
            r_n, g_n, b_n = rgb.split()
            return Image.merge("RGBA", (r_n, g_n, b_n, a))
        return image

    def load_accessory(self):
        self.accessory_img = None
        if self.accessory_name != "none":
            path = os.path.join(self.accessories_dir, f"{self.accessory_name}.png")
            if not os.path.exists(path):
                generate_accessory_assets(self.accessories_dir)
            if os.path.exists(path):
                self.accessory_img = Image.open(path).convert("RGBA")

        eyes_path = os.path.join(self.root_assets_dir, "eyes.png")
        if os.path.exists(eyes_path):
            self.eyes_img = Image.open(eyes_path).convert("RGBA")

        effect_path = os.path.join(self.root_assets_dir, "typing_effect.png")
        if os.path.exists(effect_path):
            self.typing_effect_img = Image.open(effect_path).convert("RGBA")

    def recolor_image(self, image):
        if self.color_name == "orange" or image.mode != "RGBA":
            return image

        r, g, b, a = image.split()
        rgb = Image.merge("RGB", (r, g, b))

        if self.color_name == "black":
            enhancer = ImageEnhance.Brightness(rgb)
            rgb = enhancer.enhance(0.3)
        elif self.color_name == "gray":
            rgb = ImageOps.grayscale(rgb).convert("RGB")
            enhancer = ImageEnhance.Brightness(rgb)
            rgb = enhancer.enhance(0.8)
        elif self.color_name == "white":
            rgb = ImageOps.grayscale(rgb).convert("RGB")
            enhancer = ImageEnhance.Brightness(rgb)
            rgb = enhancer.enhance(1.4)
        elif self.color_name == "pink":
            hsv = rgb.convert("HSV")
            h, s, v = hsv.split()
            h = h.point(lambda p: (p + 110) % 256)
            rgb = Image.merge("HSV", (h, s, v)).convert("RGB")
        elif self.color_name == "calico":
            hsv = rgb.convert("HSV")
            h, s, v = hsv.split()
            h = h.point(lambda p: (p + 20) % 256)
            rgb = Image.merge("HSV", (h, s, v)).convert("RGB")

        r_new, g_new, b_new = rgb.split()
        return Image.merge("RGBA", (r_new, g_new, b_new, a))

    def load_spritesheet(self, filename, num_frames):
        skin_folder = os.path.join(self.skins_dir, self.skin_name)
        path = os.path.join(skin_folder, filename)

        if not os.path.exists(path):
            path = os.path.join(self.root_assets_dir, filename)

        if not os.path.exists(path):
            generate_placeholder_assets(self.root_assets_dir, "default")

        sheet = Image.open(path).convert("RGBA")
        frame_width = sheet.width // num_frames
        frame_height = sheet.height

        normal_frames = []
        flipped_frames = []

        for i in range(num_frames):
            crop_box = (i * frame_width, 0, (i + 1) * frame_width, frame_height)
            frame = sheet.crop(crop_box)
            frame = self.recolor_image(frame)

            if self.accessory_img:
                frame = Image.alpha_composite(frame, self.accessory_img)

            scaled_size = (frame_width * self.scale, frame_height * self.scale)
            frame_scaled = frame.resize(scaled_size, Image.Resampling.NEAREST)
            flipped_scaled = frame_scaled.transpose(Image.FLIP_LEFT_RIGHT)

            normal_frames.append(frame_scaled)
            flipped_frames.append(flipped_scaled)

        return {"normal": normal_frames, "flipped": flipped_frames}

    def load_all_sprites(self):
        self.photo_cache.clear()
        self.load_accessory()

        filename_map = {
            "idle_breathe": "idle_breathe.png",
            "idle_play": "idle_play.png",
            "idle_roll": "idle_roll.png",
            "idle_jump": "idle_jump.png",
            "idle_groom": "idle_groom.png",
            "idle_look_around": "idle_look_around.png",
            "walk": "walk.png",
            "sit": "sit.png",
            "sleep": "sleep.png",
            "left_click_react": "left_click.png",
            "left_click_alt_react": "left_click_alt.png",
            "right_click_react": "right_click.png",
            "right_click_alt_react": "right_click_alt.png",
            "typing_left_react": "typing_left.png",
            "typing_right_react": "typing_right.png",
            "petting": "petting.png",
            "dragging": "dragging.png",
            "stretch": "stretch.png",
            "resting": "resting.png",
            "eating": "eating.png",
            "pounce": "pounce.png",
            "scroll_react": "scroll_react.png",
            "peek": "peek.png",
            "drink_water": "drink_water.png",
        }

        for state, cfg in ANIMATION_CONFIG.items():
            fname = filename_map.get(state, "idle_breathe.png")
            self.animations[state] = self.load_spritesheet(fname, cfg["frames"])

        logger.info("All spritesheets loaded (Skin: %s, Accessory: %s, Scale: %dx)", self.skin_name, self.accessory_name, self.scale)

    def get_frame(self, state, frame_idx, flip=False, master=None, pupil_offset=(0, 0), typing_tier="normal"):
        anim = self.animations.get(state)
        if not anim:
            anim = self.animations["idle_breathe"]
        pil_frames = anim["flipped"] if flip else anim["normal"]
        idx = frame_idx % len(pil_frames)

        px, py = pupil_offset
        key = (state, idx, flip, self.scale, self.color_name, self.skin_name, self.accessory_name, px, py, typing_tier)

        if key not in self.photo_cache:
            pil_img = pil_frames[idx].copy()

            # 1. Eye Pupil Dots Overlay Tracking
            if state not in ("sleep", "resting") and self.eyes_img:
                shifted_eyes = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
                shifted_eyes.paste(self.eyes_img, (px, py), self.eyes_img)
                scaled_eyes = shifted_eyes.resize(pil_img.size, Image.Resampling.NEAREST)
                if flip:
                    scaled_eyes = scaled_eyes.transpose(Image.FLIP_LEFT_RIGHT)
                pil_img = Image.alpha_composite(pil_img, scaled_eyes)

            # 2. Fast Typing FIERY RED Escalation
            if "typing" in state:
                if typing_tier in ("fast", "very_fast"):
                    r, g, b, a = pil_img.split()
                    red_tint = Image.new("RGBA", pil_img.size, (255, 30, 30, 255))
                    pil_img = Image.blend(pil_img, red_tint, 0.45)
                    pil_img.putalpha(a)

                    if self.typing_effect_img:
                        scaled_spark = self.typing_effect_img.resize(pil_img.size, Image.Resampling.NEAREST)
                        if flip:
                            scaled_spark = scaled_spark.transpose(Image.FLIP_LEFT_RIGHT)
                        pil_img = Image.alpha_composite(pil_img, scaled_spark)

            pil_img = self.apply_day_night_tint(pil_img)
            bg = Image.new("RGBA", pil_img.size, TRANSPARENT_BG_RGB)
            bg.paste(pil_img, (0, 0), pil_img)
            self.photo_cache[key] = ImageTk.PhotoImage(bg, master=master)

        return self.photo_cache[key]

    def get_frame_count(self, state):
        cfg = ANIMATION_CONFIG.get(state)
        return cfg["frames"] if cfg else 4

    def get_fps(self, state):
        cfg = ANIMATION_CONFIG.get(state)
        return cfg["fps"] if cfg else 8
