"""Generate pixel-art Jimny frames for drive and water_crossing animations."""
from PIL import Image, ImageDraw
import math, os

W, H = 80, 56  # sprite canvas size

# Color palette
BODY    = (220, 60,  40)   # red body
DARK    = (30,  30,  30)   # outline / tires
GLASS   = (140, 200, 230)  # windscreen
LIGHT   = (255, 240, 160)  # headlights
SILVER  = (180, 180, 180)  # bumper/trim
WHEEL_H = (60,  60,  60)   # wheel hub
GROUND  = (0,   0,   0,  0)  # transparent

def new():
    return Image.new("RGBA", (W, H), (0,0,0,0))

def draw_jimny(img, wheel_rot=0, facing_right=True):
    d = ImageDraw.Draw(img)
    ox = 0  # x origin

    # --- body ---
    # main cabin box
    d.rectangle([ox+12, 16, ox+66, 40], fill=BODY, outline=DARK)
    # roof
    d.rectangle([ox+18, 8,  ox+60, 16], fill=BODY, outline=DARK)

    # windscreen
    d.rectangle([ox+20, 9, ox+38, 15], fill=GLASS)
    # rear window
    d.rectangle([ox+42, 9, ox+58, 15], fill=GLASS)

    # headlights (front = right if facing_right)
    if facing_right:
        d.rectangle([ox+60, 20, ox+66, 26], fill=LIGHT, outline=DARK)
        d.rectangle([ox+12, 20, ox+16, 26], fill=SILVER)   # rear
    else:
        d.rectangle([ox+12, 20, ox+18, 26], fill=LIGHT, outline=DARK)
        d.rectangle([ox+62, 20, ox+66, 26], fill=SILVER)

    # bumper
    if facing_right:
        d.rectangle([ox+63, 30, ox+70, 40], fill=SILVER, outline=DARK)
    else:
        d.rectangle([ox+8,  30, ox+15, 40], fill=SILVER, outline=DARK)

    # door line
    d.line([ox+38, 17, ox+38, 40], fill=DARK, width=1)
    # door handle
    d.rectangle([ox+28, 28, ox+34, 30], fill=SILVER)
    d.rectangle([ox+44, 28, ox+50, 30], fill=SILVER)

    # --- wheels ---
    for cx, cy in [(ox+22, 42), (ox+56, 42)]:
        # tire
        d.ellipse([cx-10, cy-10, cx+10, cy+10], fill=DARK)
        # hub
        d.ellipse([cx-5, cy-5, cx+5, cy+5], fill=WHEEL_H)
        # spoke
        angle = math.radians(wheel_rot)
        sx = cx + int(4*math.cos(angle))
        sy = cy + int(4*math.sin(angle))
        d.line([cx, cy, sx, sy], fill=SILVER, width=2)

    # mudflaps
    d.rectangle([ox+10, 36, ox+14, 44], fill=DARK)
    d.rectangle([ox+64, 36, ox+68, 44], fill=DARK)

    return img

def draw_water_drop(img, frame, total):
    """Add water splash effect."""
    d = ImageDraw.Draw(img)
    progress = frame / total
    # water ripple on ground
    for i in range(3):
        r = int(10 + i*8 + progress*20)
        alpha = max(0, int(200 - progress*200 - i*50))
        color = (80, 140, 220, alpha)
        overlay = Image.new("RGBA", (W, H), (0,0,0,0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([W//2-r, 44-4, W//2+r, 44+4], outline=(80,140,220,alpha), width=2)
        img = Image.alpha_composite(img, overlay)

    # splash droplets
    num_drops = 8
    for i in range(num_drops):
        angle = (i / num_drops) * math.pi  # semicircle upward
        dist = progress * 28
        dx = int(math.cos(angle) * dist)
        dy = -int(abs(math.sin(angle)) * dist)
        cx = W//2 + dx
        cy = 44 + dy
        size = max(1, int(4 * (1 - progress)))
        drop_alpha = max(0, int(255 * (1 - progress)))
        overlay2 = Image.new("RGBA", (W, H), (0,0,0,0))
        od2 = ImageDraw.Draw(overlay2)
        od2.ellipse([cx-size, cy-size, cx+size, cy+size],
                    fill=(80, 160, 240, drop_alpha))
        img = Image.alpha_composite(img, overlay2)
    return img

# ── Generate drive frames (12 frames, wheel turning) ──────────────────────
DRIVE_DIR = "frames/drive"
os.makedirs(DRIVE_DIR, exist_ok=True)
for i in range(12):
    img = new()
    draw_jimny(img, wheel_rot=i*(360/12), facing_right=True)
    img.save(f"{DRIVE_DIR}/frame_{i:02d}.png")

# ── Generate water_crossing frames (21 frames) ────────────────────────────
WATER_DIR = "frames/water_crossing"
os.makedirs(WATER_DIR, exist_ok=True)
for i in range(21):
    img = new()
    # car bobs up-down during water crossing
    bob = int(math.sin(i / 21 * math.pi * 2) * 3)
    # draw on temporary then paste with offset
    tmp = new()
    draw_jimny(tmp, wheel_rot=i*(360/21)*0.3, facing_right=True)
    # water splash composited on top
    img.paste(tmp, (0, bob), tmp)
    img = draw_water_drop(img, i, 21)
    img.save(f"{WATER_DIR}/frame_{i:02d}.png")

print("✅ All frames generated.")
