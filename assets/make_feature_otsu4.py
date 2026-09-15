from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_MED = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"

BG_DARK = (14, 79, 82)
BG_LIGHT = (28, 100, 100)
ACCENT = (231, 76, 60)     # crimson red, matches app icon
ACCENT_GLOW = (231, 110, 90)
WHITE = (255, 255, 255)
SUBT = (200, 230, 227)

W, H = 1024, 500


def make_feature():
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    for x in range(W):
        t = x / W
        r = int(BG_DARK[0] + (BG_LIGHT[0] - BG_DARK[0]) * t)
        g = int(BG_DARK[1] + (BG_LIGHT[1] - BG_DARK[1]) * t)
        b = int(BG_DARK[2] + (BG_LIGHT[2] - BG_DARK[2]) * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([W * 0.68, -80, W * 1.05, H * 0.9], fill=(*ACCENT_GLOW, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # diamond hazard icon on the right
    cx, cy = W * 0.87, H * 0.5
    r = H * 0.26
    diamond = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(diamond, fill=ACCENT, outline=WHITE)
    inset = r * 0.78
    diamond2 = [(cx, cy - inset), (cx + inset, cy), (cx, cy + inset), (cx - inset, cy)]
    draw.polygon(diamond2, fill=WHITE)
    f_kanji = ImageFont.truetype(FONT_BLACK, int(r * 0.95))
    txt = "危"
    bbox = draw.textbbox((0, 0), txt, font=f_kanji)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), txt, font=f_kanji, fill=BG_DARK)

    # Title text on the left
    margin = 56
    f_title = ImageFont.truetype(FONT_BLACK, 52)
    f_sub = ImageFont.truetype(FONT_BOLD, 28)
    f_tag = ImageFont.truetype(FONT_MED, 22)

    draw.text((margin, 108), "危険物取扱者【乙種4類】", font=f_title, fill=WHITE)
    draw.text((margin, 178), "予想問題演習帳", font=f_title, fill=ACCENT)

    draw.text((margin, 290), "法令・物理学化学・性質火災予防", font=f_sub, fill=SUBT)
    draw.text((margin, 334), "5択形式のオリジナル予想問題で毎日コツコツ演習", font=f_tag, fill=SUBT)

    out = "/home/claude/otsu4-capacitor/assets/feature_graphic_1024x500.png"
    img.save(out)
    print("feature graphic saved:", out, img.size, img.mode)


make_feature()
