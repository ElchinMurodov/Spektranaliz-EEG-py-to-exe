"""SVG ikonadan Windows .ico faylini yasaydi.

Bu skript `spektranaliz-eeg-icon.svg` faylidan ko'p o'lchamli (16..256 px)
`spektranaliz-eeg-icon.ico` faylini hosil qiladi. Bu .ico fayl .exe va
o'rnatuvchi (setup) uchun ishlatiladi.

Rasterlash tartibi (birinchi ishlagani qo'llaniladi):
  1) svglib + reportlab  (eng ishonchli, qo'shimcha DLL kerak emas)
  2) cairosvg            (agar tizimda o'rnatilgan bo'lsa)
  3) mavjud PNG/JPG fon  (oxirgi zaxira yechim)

Ishga tushirish:
    python make_ico.py
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_ICON = os.path.join(HERE, "spektranaliz-eeg-icon.svg")
OUT_ICO = os.path.join(HERE, "spektranaliz-eeg-icon.ico")
OUT_PNG = os.path.join(HERE, "spektranaliz-eeg-icon.png")

# Zaxira (fallback) rasm fayllari - SVG rasterlanmasa shulardan foydalaniladi.
FALLBACK_IMAGES = [
    os.path.join(HERE, "EEG-spectrum-background-730x730.png"),
    os.path.join(HERE, "EEG spectrum background 685x685.jpg"),
]

ICON_SIZES = [16, 24, 32, 48, 64, 128, 256]
RENDER_SIZE = 256


def render_with_svglib(size):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM

    drawing = svg2rlg(SVG_ICON)
    if drawing is None:
        raise RuntimeError("svglib SVG faylni o'qiy olmadi.")
    scale_x = size / drawing.width
    scale_y = size / drawing.height
    drawing.width = size
    drawing.height = size
    drawing.scale(scale_x, scale_y)
    png_bytes = renderPM.drawToString(drawing, fmt="PNG", bg=0x000000)
    from PIL import Image
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def render_with_cairosvg(size):
    import cairosvg
    from PIL import Image

    png_bytes = cairosvg.svg2png(url=SVG_ICON, output_width=size, output_height=size)
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def render_from_fallback(size):
    from PIL import Image

    for path in FALLBACK_IMAGES:
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            return img.resize((size, size), Image.LANCZOS)
    raise FileNotFoundError("Zaxira rasm fayllari topilmadi.")


def build_base_image():
    """256x256 RGBA asosiy rasmni qaytaradi."""
    errors = []

    if os.path.exists(SVG_ICON):
        for name, renderer in (("svglib", render_with_svglib), ("cairosvg", render_with_cairosvg)):
            try:
                img = renderer(RENDER_SIZE)
                print(f"[OK] SVG ikona '{name}' yordamida rasterlandi.")
                return img
            except Exception as error:  # noqa: BLE001
                errors.append(f"{name}: {error}")
    else:
        errors.append(f"SVG topilmadi: {SVG_ICON}")

    try:
        img = render_from_fallback(RENDER_SIZE)
        print("[OK] Zaxira PNG/JPG rasmidan ikona yasaldi.")
        return img
    except Exception as error:  # noqa: BLE001
        errors.append(f"fallback: {error}")

    raise SystemExit(
        "[XATO] Ikona yasab bo'lmadi. Sabablari:\n  - "
        + "\n  - ".join(errors)
        + "\n\nYechim: pip install svglib reportlab pillow"
    )


def apply_circle_mask(img):
    """Ikona burchaklarini shaffof qiladi (dizayn aylana shaklida)."""
    from PIL import Image, ImageDraw

    size = img.size[0]
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    result = img.copy()
    result.putalpha(mask)
    return result


def main():
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        raise SystemExit("[XATO] Pillow o'rnatilmagan. Bajaring: pip install pillow")

    base = build_base_image()
    base = apply_circle_mask(base)

    # Ko'p o'lchamli .ico faylini saqlaymiz.
    base.save(OUT_ICO, format="ICO", sizes=[(s, s) for s in ICON_SIZES])
    print(f"[OK] .ico fayl yaratildi: {OUT_ICO}")

    # Qo'shimcha: PNG ikona (Tkinter iconphoto zaxirasi uchun).
    base.save(OUT_PNG, format="PNG")
    print(f"[OK] .png ikona yaratildi: {OUT_PNG}")


if __name__ == "__main__":
    sys.exit(main())
