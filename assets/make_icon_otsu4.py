from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"

# Brand colors — same teal-family background as kikenbutsu (series cohesion),
# but a crimson/red accent (Class-4 flammable-liquid hazard convention) instead
# of kikenbutsu's yellow/orange, so the two icons are clearly distinguishable
# side by side while still reading as the same app family.
BG_DARK = (14, 79, 82)      # 0E4F52 (same as kikenbutsu)
BG_LIGHT = (62, 115, 112)   # 3E7370 (same as kikenbutsu)
ACCENT = (231, 76, 60)      # crimson red (E74C3C)
ACCENT2 = (192, 57, 43)     # deeper red (C0392B)
WHITE = (255, 255, 255)

OUT_DIR = "/home/claude/otsu4-capacitor/assets"
ANDROID_RES = "/home/claude/otsu4-capacitor/android/app/src/main/res"
IOS_ICON_PATH = "/home/claude/otsu4-capacitor/ios/App/App/Assets.xcassets/AppIcon.appiconset/AppIcon-512@2x.png"


def draw_base(size, draw, img, cx_ratio=0.5, cy_ratio=0.40, diamond_ratio=0.30, glow=True):
    """Draws background gradient + glow + diamond + kanji onto img/draw of given size. Returns (img, draw)."""
    # diagonal gradient background
    for y in range(size):
        t = y / size
        r = int(BG_DARK[0] + (BG_LIGHT[0] - BG_DARK[0]) * t)
        g = int(BG_DARK[1] + (BG_LIGHT[1] - BG_DARK[1]) * t)
        b = int(BG_DARK[2] + (BG_LIGHT[2] - BG_DARK[2]) * t)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    if glow:
        glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow_layer)
        gdraw.ellipse([size * 0.14, size * 0.10, size * 0.86, size * 0.82], fill=(231, 110, 90, 60))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(int(size * 0.078)))
        img2 = Image.alpha_composite(img.convert("RGBA"), glow_layer)
        img.paste(img2.convert("RGB"), (0, 0))
        draw = ImageDraw.Draw(img)

    cx, cy = size * cx_ratio, size * cy_ratio
    r = size * diamond_ratio
    diamond = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(diamond, fill=ACCENT, outline=WHITE)
    inset = size * (diamond_ratio * 0.783)
    diamond2 = [(cx, cy - inset), (cx + inset, cy), (cx, cy + inset), (cx - inset, cy)]
    draw.polygon(diamond2, fill=WHITE)

    f_kanji = ImageFont.truetype(FONT_BLACK, int(size * 0.30))
    txt = "危"
    bbox = draw.textbbox((0, 0), txt, font=f_kanji)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), txt, font=f_kanji, fill=ACCENT2)

    return cx, cy, draw


def make_master_icon():
    """Full square icon with badge, for iOS + legacy Android launcher icon. 1024x1024."""
    SIZE = 1024
    img = Image.new("RGB", (SIZE, SIZE), BG_DARK)
    draw = ImageDraw.Draw(img)
    cx, cy, draw = draw_base(SIZE, draw, img)

    # Bottom badge "乙4類"
    f_badge = ImageFont.truetype(FONT_BOLD, int(SIZE * 0.115))
    badge_txt = "乙4類"
    bbox2 = draw.textbbox((0, 0), badge_txt, font=f_badge)
    bw, bh = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
    by = SIZE * 0.80
    pad_x, pad_y = SIZE * 0.065, SIZE * 0.035
    rect = [cx - bw / 2 - pad_x - bbox2[0], by - pad_y - bbox2[1], cx + bw / 2 + pad_x - bbox2[0], by + bh + pad_y - bbox2[1]]
    draw.rounded_rectangle(rect, radius=int(SIZE * 0.05), fill=WHITE)
    draw.text((cx - bw / 2 - bbox2[0], by - bbox2[1]), badge_txt, font=f_badge, fill=BG_DARK)

    img = img.convert("RGB")
    os.makedirs(OUT_DIR, exist_ok=True)
    master_path = os.path.join(OUT_DIR, "icon_1024_master.png")
    img.save(master_path)
    print("master icon saved:", master_path, img.size, img.mode)
    return img


def make_foreground_master():
    """Transparent-background foreground layer for Android adaptive icon.
    Content (diamond+kanji, no badge, no background fill) kept within the
    108dp safe-zone circle (66dp radius) so it survives circular masking.
    Rendered at 1024x1024 (scaled to 108dp canvas) then downsampled per density.
    """
    SIZE = 1024
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Diamond scaled down + centered so it sits inside the safe zone
    # (safe zone radius = 33/54 of half-canvas ~ 0.611 of half-width)
    cx, cy = SIZE * 0.5, SIZE * 0.5
    r = SIZE * 0.225
    diamond = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(diamond, fill=ACCENT, outline=WHITE)
    inset = r * 0.783
    diamond2 = [(cx, cy - inset), (cx + inset, cy), (cx, cy + inset), (cx - inset, cy)]
    draw.polygon(diamond2, fill=WHITE)

    f_kanji = ImageFont.truetype(FONT_BLACK, int(SIZE * 0.225))
    txt = "危"
    bbox = draw.textbbox((0, 0), txt, font=f_kanji)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), txt, font=f_kanji, fill=ACCENT2)

    fg_path = os.path.join(OUT_DIR, "icon_foreground_master.png")
    img.save(fg_path)
    print("foreground master saved:", fg_path, img.size, img.mode)
    return img


def export_ios(master_img):
    os.makedirs(os.path.dirname(IOS_ICON_PATH), exist_ok=True)
    master_img.convert("RGB").save(IOS_ICON_PATH)
    print("iOS AppIcon written:", IOS_ICON_PATH)


def export_android(master_img, fg_img):
    densities = {
        "mdpi": (48, 108),
        "hdpi": (72, 162),
        "xhdpi": (96, 216),
        "xxhdpi": (144, 324),
        "xxxhdpi": (192, 432),
    }
    for name, (legacy_size, fg_size) in densities.items():
        d = os.path.join(ANDROID_RES, f"mipmap-{name}")
        os.makedirs(d, exist_ok=True)

        legacy = master_img.convert("RGB").resize((legacy_size, legacy_size), Image.LANCZOS)
        legacy.save(os.path.join(d, "ic_launcher.png"))
        legacy.save(os.path.join(d, "ic_launcher_round.png"))

        fg = fg_img.convert("RGBA").resize((fg_size, fg_size), Image.LANCZOS)
        fg.save(os.path.join(d, "ic_launcher_foreground.png"))

        print(f"android {name}: legacy {legacy_size}x{legacy_size}, foreground {fg_size}x{fg_size}")

    # Adaptive icon background color -> match brand dark teal instead of default white
    bg_xml_path = os.path.join(ANDROID_RES, "values", "ic_launcher_background.xml")
    hexcolor = "#{:02X}{:02X}{:02X}".format(*BG_DARK)
    with open(bg_xml_path, "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            "<resources>\n"
            f'    <color name="ic_launcher_background">{hexcolor}</color>\n'
            "</resources>\n"
        )
    print("android adaptive background color set to", hexcolor)


if __name__ == "__main__":
    master = make_master_icon()
    fg = make_foreground_master()
    export_ios(master)
    export_android(master, fg)
    print("done")
