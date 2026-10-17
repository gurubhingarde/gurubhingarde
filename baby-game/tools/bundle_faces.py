#!/usr/bin/env python3
"""Make a personal copy of the game with your child's face photos baked in.

The photos never need to go into git. Give it three face pictures (already
cropped around the face works best) and it writes a single HTML file you can
open on any phone, and/or copies them into the app's assets for an APK build.

  python3 tools/bundle_faces.py --calm calm.jpg --oh surprised.jpg --yell shouting.jpg \
      -o ~/baby-bubble-party.html --assets
"""
import argparse, base64, io, os
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(HERE, '..', 'app', 'src', 'main', 'assets', 'index.html')
FACES_DIR = os.path.join(HERE, '..', 'app', 'src', 'main', 'assets', 'faces')


def oval(path, height=512):
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    w, h = im.size
    im = im.resize((max(1, round(w * height / h)), height), Image.LANCZOS)
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).ellipse((4, 4, im.size[0] - 4, im.size[1] - 4), fill=255)
    im.putalpha(mask.filter(ImageFilter.GaussianBlur(3)))
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ('calm', 'oh', 'yell'):
        ap.add_argument('--' + k, required=True, help=f'face photo for the "{k}" expression')
    ap.add_argument('-o', '--out', help='write a standalone HTML game here')
    ap.add_argument('--assets', action='store_true', help='also copy faces into app assets for the APK (git-ignored)')
    a = ap.parse_args()

    faces = {k: oval(getattr(a, k)) for k in ('calm', 'oh', 'yell')}
    if a.out:
        parts = []
        for k, im in faces.items():
            buf = io.BytesIO()
            im.save(buf, 'WEBP', quality=85)
            parts.append(f"{k}:'data:image/webp;base64,{base64.b64encode(buf.getvalue()).decode()}'")
        html = open(GAME, encoding='utf-8').read()
        tag = '<script>window.BUNDLED_FACES={' + ','.join(parts) + '};</script>'
        open(a.out, 'w', encoding='utf-8').write(html.replace('<!--BUNDLED_FACES-->', tag, 1))
        print('wrote', a.out)
    if a.assets:
        os.makedirs(FACES_DIR, exist_ok=True)
        for k, im in faces.items():
            p = os.path.join(FACES_DIR, f'face_{k}.png')
            im.save(p, optimize=True)
            print('wrote', p)


if __name__ == '__main__':
    main()
