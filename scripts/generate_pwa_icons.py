#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'assets' / 'icons'
out.mkdir(parents=True, exist_ok=True)

def icon(size):
    img = Image.new('RGB', (size, size), '#00c853')
    draw = ImageDraw.Draw(img)
    pad = int(size * 0.12)
    draw.rounded_rectangle([pad, pad, size-pad, size-pad], radius=int(size*0.18), fill='#ffffff')
    chart = [
        (int(size*.28), int(size*.64)),
        (int(size*.42), int(size*.50)),
        (int(size*.56), int(size*.56)),
        (int(size*.72), int(size*.34)),
    ]
    draw.line(chart, fill='#1976d2', width=max(8, size//22), joint='curve')
    r = max(8, size//28)
    for x, y in chart:
        draw.ellipse([x-r, y-r, x+r, y+r], fill='#00c853')
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(size*.18))
    except Exception:
        font = ImageFont.load_default()
    text = 'R$'
    bbox = draw.textbbox((0,0), text, font=font)
    draw.text(((size-(bbox[2]-bbox[0]))/2, int(size*.72)), text, fill='#111827', font=font)
    return img

for size in (192, 512):
    icon(size).save(out / f'icon-{size}.png')
print('Ícones PWA gerados.')
