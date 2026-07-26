#!/usr/bin/env python3
"""Deterministic Chinese typography for Kaixin technology covers."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


SIZES = {
    "xhs": (1242, 1656),
    "douyin": (1242, 1656),
    "channels": (1242, 1656),
    "landscape": (1920, 1080),
}

ROOT = Path(__file__).resolve().parent.parent
FONT_STYLES = {
    # Keep one expressive display face across the cover family.
    "variety": ROOT / "assets/fonts/YouSheBiaoTiHei.ttf",
    "comic": ROOT / "assets/fonts/YouSheBiaoTiHei.ttf",
    "tech": ROOT / "assets/fonts/YouSheBiaoTiHei.ttf",
    "round": ROOT / "assets/fonts/YouSheBiaoTiHei.ttf",
    "editorial": ROOT / "assets/fonts/YouSheBiaoTiHei.ttf",
}

AUX_FONT = ROOT / "assets/fonts/SmileySans-Oblique.ttf"
INFO_FONT = ROOT / "assets/fonts/SourceHanSansSC-Heavy.otf"


def cover_crop(image, size):
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def font_path(style, custom=None):
    candidate = Path(custom).expanduser() if custom else FONT_STYLES[style]
    if not candidate.is_file():
        raise SystemExit(f"Font not found: {candidate}")
    return str(candidate)


def hex_rgb(value):
    value = value.lstrip("#")
    if len(value) != 6:
        raise SystemExit("Colours must be #RRGGBB.")
    return tuple(int(value[i:i + 2], 16) for i in range(0, 6, 2))


def wrap_text(draw, text, font, max_width, max_lines=2):
    if not text:
        return []
    if "\n" in text:
        manual = [line.strip() for line in text.splitlines() if line.strip()]
        if len(manual) <= max_lines and all(draw.textbbox((0, 0), line, font=font)[2] <= max_width for line in manual):
            return manual
        return None
    if " " not in text and max_lines >= 2 and len(text) >= 4:
        balanced = []
        for index in range(1, len(text)):
            first, second = text[:index], text[index:]
            if min(len(first), len(second)) < 2:
                continue
            if draw.textbbox((0, 0), first, font=font)[2] <= max_width and draw.textbbox((0, 0), second, font=font)[2] <= max_width:
                score = abs(len(first) - len(second))
                balanced.append((score, -min(len(first), len(second)), first, second))
        if balanced:
            _, _, first, second = sorted(balanced)[0]
            return [first, second]
    chunks = text.split() if " " in text else list(text)
    separator = " " if " " in text else ""
    lines, current = [], ""
    for chunk in chunks:
        trial = chunk if not current else current + separator + chunk
        if draw.textbbox((0, 0), trial, font=font)[2] <= max_width:
            current = trial
        else:
            if not current:
                return None
            lines.append(current)
            current = chunk
    if current:
        lines.append(current)
    return lines if len(lines) <= max_lines else None


def fit_lines(draw, text, path, max_width, max_height, max_lines=2, scale=0.56):
    for size in range(round(max_height * scale), 38, -4):
        font = ImageFont.truetype(path, size=size)
        lines = wrap_text(draw, text, font, max_width, max_lines)
        if not lines:
            continue
        heights = [draw.textbbox((0, 0), line, font=font, stroke_width=max(3, size // 18))[3] for line in lines]
        if sum(heights) + max(0, len(lines) - 1) * round(size * 0.08) <= max_height:
            return font, lines
    raise SystemExit("Headline is too long. Use two compact lines.")


def darken_top(image, platform, layout, treatment="outline"):
    width, height = image.size
    depth = 0.43 if layout in {"top", "split", "ribbon"} else 0.34
    if platform == "landscape":
        depth = 0.44
    if treatment == "blast":
        depth = 0.30 if platform != "landscape" else 0.36
    panel_h = round(height * depth)
    alpha = Image.new("L", (1, panel_h))
    opacity = 120 if treatment == "blast" else 214
    alpha.putdata([round(opacity * (1 - y / max(1, panel_h - 1)) ** 0.72) for y in range(panel_h)])
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shade_colour = (4, 8, 19, 176) if treatment == "blast" else (4, 8, 19, 222)
    shade.paste(shade_colour, (0, 0, width, panel_h), alpha.resize((width, panel_h)))
    return Image.alpha_composite(image.convert("RGBA"), shade)


def text_mask(size, xy, text, font):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255)
    return mask


def draw_gradient_text(canvas, xy, text, font, stroke, top, bottom, stroke_color, treatment):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if treatment == "sticker":
        draw.text(xy, text, font=font, fill=(255, 255, 255, 0), stroke_width=stroke + max(7, stroke // 2), stroke_fill=(255, 255, 255, 235))
    draw.text(xy, text, font=font, fill=(0, 0, 0, 0), stroke_width=stroke, stroke_fill=stroke_color)
    mask = text_mask(canvas.size, xy, text, font)
    gradient = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(gradient)
    bbox = draw.textbbox(xy, text, font=font)
    start, end = bbox[1], max(bbox[1] + 1, bbox[3])
    for y in range(max(0, start), min(canvas.height, end + 1)):
        ratio = (y - start) / max(1, end - start)
        colour = tuple(round(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        gdraw.line((0, y, canvas.width, y), fill=(*colour, 255))
    gradient.putalpha(mask)
    return Image.alpha_composite(Image.alpha_composite(canvas, layer), gradient)


def draw_plain_text(canvas, xy, text, font, colour, stroke, treatment):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    if treatment == "blast":
        stroke = max(stroke, font.size // 10)
        glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        glow_stroke = stroke + max(5, font.size // 26)
        gdraw.text(xy, text, font=font, fill=(255, 255, 255, 0), stroke_width=glow_stroke, stroke_fill=(255, 245, 0, 220))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=max(2, font.size // 55)))
        layer = Image.alpha_composite(layer, glow)
        draw = ImageDraw.Draw(layer)
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow)
        offset = max(5, font.size // 34)
        sdraw.text((xy[0] + offset, xy[1] + offset), text, font=font, fill=(0, 0, 0, 235), stroke_width=stroke + max(2, font.size // 55), stroke_fill=(0, 0, 0, 255))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(1, font.size // 95)))
        layer = Image.alpha_composite(layer, shadow)
        draw = ImageDraw.Draw(layer)
        draw.text(xy, text, font=font, fill=(*colour[:3], 255), stroke_width=stroke, stroke_fill=(3, 5, 10, 255))
        shine_y = xy[1] + max(3, font.size // 30)
        draw.text((xy[0] + max(1, font.size // 90), shine_y), text, font=font, fill=(255, 255, 255, 52))
        draw.text(xy, text, font=font, fill=(*colour[:3], 255))
        return Image.alpha_composite(canvas, layer)
    if treatment == "sticker":
        draw.text(xy, text, font=font, fill=(255, 255, 255, 0), stroke_width=stroke + max(7, stroke // 2), stroke_fill=(255, 255, 255, 235))
    draw.text(xy, text, font=font, fill=colour, stroke_width=stroke, stroke_fill=(13, 16, 22, 255))
    return Image.alpha_composite(canvas, layer)


def tracked_width(draw, text, font, tracking):
    """Measure text with explicit tracking for compact information lines."""
    if not text:
        return 0
    widths = [draw.textbbox((0, 0), char, font=font)[2] for char in text]
    return sum(widths) + max(0, len(text) - 1) * tracking


def draw_tracked_plain_text(canvas, xy, text, font, colour, stroke, treatment, tracking):
    """Draw a support line with deliberate letter spacing, not fake spaces."""
    if tracking <= 0 or treatment == "blast":
        return draw_plain_text(canvas, xy, text, font, colour, stroke, treatment)
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    x, y = xy
    for char in text:
        if treatment == "sticker":
            draw.text((x, y), char, font=font, fill=(255, 255, 255, 0), stroke_width=stroke + max(7, stroke // 2), stroke_fill=(255, 255, 255, 235))
        draw.text((x, y), char, font=font, fill=colour, stroke_width=stroke, stroke_fill=(13, 16, 22, 255))
        x += draw.textbbox((0, 0), char, font=font)[2] + tracking
    return Image.alpha_composite(canvas, layer)


def layout_positions(draw, lines, font, width, height, layout, margin):
    boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
    dimensions = [(box[2] - box[0], box[3] - box[1]) for box in boxes]
    spacing = round(font.size * 0.06)
    total_h = sum(item[1] for item in dimensions) + spacing * (len(lines) - 1)
    if layout == "side":
        x = margin
        y = round(height * 0.085)
    elif layout == "poster":
        x = margin
        y = round(height * 0.18)
    else:
        x = None
        y = round(height * 0.042)
    positions = []
    for index, (tw, th) in enumerate(dimensions):
        current_x = x if x is not None else (width - tw) // 2
        if layout == "split" and len(lines) > 1:
            current_x = margin if index == 0 else width - margin - tw
        positions.append((current_x, y))
        y += th + spacing
    return positions, total_h


def draw_kicker(canvas, text, x, y, width, colour):
    if not text:
        return canvas
    font = ImageFont.truetype(str(AUX_FONT), max(28, round(width * 0.028)))
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bbox = draw.textbbox((0, 0), text, font=font)
    pad_x, pad_y = round(width * 0.02), round(width * 0.008)
    card = (x, y, x + bbox[2] + pad_x * 2, y + bbox[3] + pad_y * 2)
    draw.rounded_rectangle(card, radius=pad_y * 2, fill=(*hex_rgb(colour), 242))
    draw.text((x + pad_x, y + pad_y - bbox[1]), text, font=font, fill=(11, 16, 25, 255))
    return Image.alpha_composite(canvas, layer)


def draw_metric(canvas, metric, label, position, colour, style):
    """Add a large proof-point badge without turning it into another headline."""
    if not metric:
        return canvas
    width, height = canvas.size
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    fill = hex_rgb(colour)
    if position == "left":
        cx, cy = round(width * 0.20), round(height * 0.38)
    elif position == "bottom":
        cx, cy = round(width * 0.50), round(height * 0.73)
    else:
        cx, cy = round(width * 0.80), round(height * 0.38)
    radius = round(width * (0.105 if len(metric) <= 3 else 0.13))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(0, 0, 0, 170))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=round(width * 0.014)))
    canvas = Image.alpha_composite(canvas, shadow)
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(*fill, 255), outline=(13, 16, 22, 255), width=max(6, round(width * 0.01)))
    draw.arc((cx - radius - 8, cy - radius - 8, cx + radius + 8, cy + radius + 8), start=205, end=340, fill=(255, 255, 255, 230), width=max(5, round(width * 0.007)))
    metric_font = ImageFont.truetype(str(FONT_STYLES["comic" if style in {"comic", "variety"} else "tech"]), round(radius * (0.90 if len(metric) <= 3 else 0.62)))
    bbox = draw.textbbox((0, 0), metric, font=metric_font, stroke_width=max(3, metric_font.size // 18))
    mx = cx - (bbox[2] - bbox[0]) // 2
    my = cy - (bbox[3] - bbox[1]) // 2 - bbox[1]
    draw.text((mx, my), metric, font=metric_font, fill=(255, 255, 255, 255), stroke_width=max(4, metric_font.size // 15), stroke_fill=(13, 16, 22, 255))
    if label:
        label_font = ImageFont.truetype(str(INFO_FONT), max(24, round(width * 0.026)))
        label_box = draw.textbbox((0, 0), label, font=label_font)
        ly = cy + round(radius * 0.60)
        lx = cx - (label_box[2] - label_box[0]) // 2
        draw.text((lx, ly), label, font=label_font, fill=(13, 16, 22, 255))
    return Image.alpha_composite(canvas, layer)


def add_foreground(image, foreground_path, anchor, scale):
    """Place a transparent portrait after text for a real foreground occlusion layer."""
    foreground = Image.open(foreground_path).convert("RGBA")
    width, height = image.size
    target_w = round(width * scale)
    ratio = target_w / foreground.width
    foreground = foreground.resize((target_w, round(foreground.height * ratio)), Image.Resampling.LANCZOS)
    if foreground.height > height * 0.88:
        ratio = (height * 0.88) / foreground.height
        foreground = foreground.resize((round(foreground.width * ratio), round(foreground.height * ratio)), Image.Resampling.LANCZOS)
    if anchor == "left":
        x = -round(width * 0.025)
    elif anchor == "center":
        x = (width - foreground.width) // 2
    else:
        x = width - foreground.width + round(width * 0.025)
    y = height - foreground.height
    shadow_mask = foreground.getchannel("A").filter(ImageFilter.GaussianBlur(radius=round(width * 0.014)))
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_colour = Image.new("RGBA", foreground.size, (0, 0, 0, 125))
    shadow.paste(shadow_colour, (x + round(width * 0.012), y + round(width * 0.012)), shadow_mask)
    image = Image.alpha_composite(image, shadow)
    image.alpha_composite(foreground, (x, y))
    return image


def draw_title_panel(canvas, positions, lines, font, layout, treatment, headline_colour, accent_colour):
    width, height = canvas.size
    draw = ImageDraw.Draw(canvas)
    # Let the letterform carry the personality; use a quiet separation edge.
    stroke = max(3, font.size // 24)
    if treatment == "blast":
        stroke = max(9, font.size // 11)
    if layout == "ribbon":
        top = positions[0][1] - round(font.size * 0.10)
        bottom = positions[-1][1] + round(font.size * 1.08)
        panel = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        pdraw = ImageDraw.Draw(panel)
        pdraw.rounded_rectangle((round(width * 0.06), top, round(width * 0.94), bottom), radius=round(width * 0.035), fill=(14, 21, 33, 222), outline=(*hex_rgb(accent_colour), 235), width=max(4, round(width * 0.006)))
        panel = panel.filter(ImageFilter.GaussianBlur(radius=0.3))
        canvas = Image.alpha_composite(canvas, panel)
    for index, (line, xy) in enumerate(zip(lines, positions)):
        if treatment == "blast":
            colour = headline_colour if index == 0 else accent_colour
            canvas = draw_plain_text(canvas, xy, line, font, hex_rgb(colour), stroke, treatment)
        elif layout == "poster" and index == 0:
            canvas = draw_gradient_text(canvas, xy, line, font, stroke, hex_rgb(headline_colour), hex_rgb(accent_colour), (13, 16, 22, 255), treatment)
        else:
            colour = headline_colour if index == 0 else accent_colour
            canvas = draw_plain_text(canvas, xy, line, font, hex_rgb(colour), stroke, treatment)
    return canvas


def add_logo(image, logo_path, margin, platform):
    logo = Image.open(logo_path).convert("RGBA")
    pixels = logo.load()
    for py in range(logo.height):
        for px in range(logo.width):
            red, green, blue, alpha = pixels[px, py]
            brightness = min(red, green, blue)
            if brightness >= 245:
                pixels[px, py] = (red, green, blue, 0)
            elif brightness >= 215:
                pixels[px, py] = (red, green, blue, round((245 - brightness) / 30 * alpha))
    width, height = image.size
    max_w = round(width * (0.25 if platform != "landscape" else 0.18))
    max_h = round(height * 0.055)
    ratio = min(max_w / logo.width, max_h / logo.height)
    logo = logo.resize((round(logo.width * ratio), round(logo.height * ratio)), Image.Resampling.LANCZOS)
    pad = max(10, round(width * 0.012))
    card = Image.new("RGBA", (logo.width + pad * 2, logo.height + pad * 2), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad, fill=(13, 26, 39, 205), outline=(82, 225, 255, 180), width=max(2, pad // 4))
    card.alpha_composite(logo, (pad, pad))
    y = round(height * (0.32 if platform != "landscape" else 0.30))
    image.alpha_composite(card, (margin, y))
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--subhead", default="")
    parser.add_argument("--subhead-tracking", type=int, default=0, help="Extra pixels between subhead characters.")
    parser.add_argument("--platform", choices=SIZES, default="xhs")
    parser.add_argument("--font", help="A verified licensed local font path; otherwise use --style.")
    parser.add_argument("--style", choices=FONT_STYLES, default="variety")
    parser.add_argument("--layout", choices=("top", "split", "side", "ribbon", "poster"), default="top")
    parser.add_argument("--treatment", choices=("outline", "sticker", "blast"), default="outline")
    parser.add_argument("--kicker", default="")
    parser.add_argument("--metric", default="", help="A 1–4 character proof point, for example 18倍 or 5款.")
    parser.add_argument("--metric-label", default="", help="Short label beneath --metric.")
    parser.add_argument("--metric-position", choices=("left", "right", "bottom"), default="right")
    parser.add_argument("--metric-color", default="#FF6B6B")
    parser.add_argument("--foreground", help="Optional transparent PNG portrait placed above title for true depth.")
    parser.add_argument("--foreground-anchor", choices=("left", "right", "center"), default="right")
    parser.add_argument("--foreground-scale", type=float, default=0.54)
    parser.add_argument("--logo", help="Optional logo composited without generative redrawing.")
    parser.add_argument("--headline-color", default="#FDFFA7")
    parser.add_argument("--subhead-color", default="#FFFFFF")
    parser.add_argument("--accent-color", default="#40E0D0")
    args = parser.parse_args()

    path = font_path(args.style, args.font)
    image = darken_top(cover_crop(Image.open(args.input).convert("RGB"), SIZES[args.platform]), args.platform, args.layout, args.treatment)
    width, height = image.size
    margin = round(width * 0.055)
    title_height = round(height * (0.28 if args.platform != "landscape" else 0.34))
    font, lines = fit_lines(ImageDraw.Draw(image), args.headline, path, width - 2 * margin, title_height, 2, 0.58 if args.layout != "side" else 0.48)
    positions, _ = layout_positions(ImageDraw.Draw(image), lines, font, width, height, args.layout, margin)
    if args.kicker:
        image = draw_kicker(image, args.kicker, positions[0][0], max(round(height * 0.018), positions[0][1] - round(font.size * 0.36)), width, args.accent_color)
    image = draw_title_panel(image, positions, lines, font, args.layout, args.treatment, args.headline_color, args.subhead_color)

    if args.subhead:
        sub_font = ImageFont.truetype(str(INFO_FONT), max(38, round(width * 0.046)))
        draw = ImageDraw.Draw(image)
        sub_w = tracked_width(draw, args.subhead, sub_font, args.subhead_tracking)
        sub_x = positions[-1][0] if args.layout == "side" else (width - sub_w) // 2
        sub_y = min(positions[-1][1] + round(font.size * 1.12), round(height * 0.37))
        image = draw_tracked_plain_text(image, (sub_x, sub_y), args.subhead, sub_font, hex_rgb(args.accent_color), max(2, sub_font.size // 28), "outline", args.subhead_tracking)
    image = draw_metric(image, args.metric, args.metric_label, args.metric_position, args.metric_color, args.style)
    if args.foreground:
        image = add_foreground(image, args.foreground, args.foreground_anchor, args.foreground_scale)
    if args.logo:
        image = add_logo(image, args.logo, margin, args.platform)
    output = Path(args.output).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output, quality=95)
    print(output.resolve())


if __name__ == "__main__":
    main()
