#!/usr/bin/env python3
"""
Generate dialogue PNGs by composing character PNGs from the `custom_font` folder.
Usage:
  python3 scripts/generate_dialogue.py "Hello, World!" --output dialogue/hello.png

Requires: Pillow (pip install pillow)
"""
import os
import sys
import argparse
from PIL import Image
from datetime import datetime


def build_mapping(font_dir):
    mapping = {}
    if not os.path.isdir(font_dir):
        return mapping
    for fname in os.listdir(font_dir):
        if not fname.lower().endswith('.png'):
            continue
        stem = os.path.splitext(fname)[0]
        # Upper_/Lower_ tokens
        if stem.startswith('Upper_') and len(stem) > len('Upper_'):
            ch = stem[len('Upper_'):]
            mapping[ch] = fname
            continue
        if stem.startswith('Lower_') and len(stem) > len('Lower_'):
            ch = stem[len('Lower_'):]
            mapping[ch] = fname
            continue
        # single-character filenames (e.g. "a.png" or ".png" or "[.png")
        if len(stem) == 1:
            mapping[stem] = fname
            continue
        # some named tokens -> characters
        named = {
            'Period': '.',
            'Comma': ',',
            'Left_quote': '"',
            'Right_quote': '"',
            'Left_slash': '/',
            'Right_slash': '/',
            'Underscore': '_',
            'Dash': '-',
            'Space': ' ',
            'Plus': '+',
            'Equals': '=',
        }
        if stem in named:
            mapping[named[stem]] = fname
            continue
        # fallback: map full stem to itself so users can name custom symbols
        mapping[stem] = fname
    return mapping


def compose_line(images, space_width=10, bg=(0,0,0,0)):
    widths = [img.width for img in images]
    heights = [img.height for img in images]
    total_w = sum(widths)
    max_h = max(heights) if heights else 0
    out = Image.new('RGBA', (total_w, max_h), bg)
    x = 0
    for img in images:
        y = max_h - img.height
        out.paste(img, (x, y), img)
        x += img.width
    return out


def parse_color(s):
    if s is None:
        return None
    s = s.strip()
    if s.startswith('#') and len(s) == 7:
        r = int(s[1:3], 16)
        g = int(s[3:5], 16)
        b = int(s[5:7], 16)
        return (r, g, b, 255)
    parts = [p.strip() for p in s.split(',') if p.strip()]
    if len(parts) == 3:
        return (int(parts[0]), int(parts[1]), int(parts[2]), 255)
    return None


def generate_image(text, font_dir, out_path, space_width=12, line_spacing=8, bg_color=None):
    mapping = build_mapping(font_dir)
    lines = text.split('\n')
    line_images = []
    for line in lines:
        imgs = []
        for ch in line:
            # try direct mapping
            fname = mapping.get(ch)
            # try case-insensitive fallback
            if fname is None:
                fname = mapping.get(ch.lower())
            if fname is None:
                # skip unknown chars as space
                if ch == ' ':
                    # create blank image for space
                    imgs.append(Image.new('RGBA', (space_width, 1), (0,0,0,0)))
                    continue
                # attempt to find a visually-similar file by common names
                fname = mapping.get('.') if ch == '.' else None
            if fname is None:
                # unknown -> skip
                continue
            img_path = os.path.join(font_dir, fname)
            try:
                img = Image.open(img_path).convert('RGBA')
            except Exception:
                continue
            imgs.append(img)
        # if no images in line, create a blank one
        if not imgs:
            line_images.append(Image.new('RGBA', (space_width, 1), (0,0,0,0)))
        else:
            line_images.append(compose_line(imgs, space_width))
    # stack lines vertically
    widths = [li.width for li in line_images]
    heights = [li.height for li in line_images]
    total_w = max(widths) if widths else 0
    total_h = sum(heights) + line_spacing * (len(heights)-1 if len(heights)>0 else 0)
    out_img_bg = (0,0,0,0) if bg_color is None else bg_color
    out_img = Image.new('RGBA', (total_w, total_h), out_img_bg)
    y = 0
    for li in line_images:
        x = (total_w - li.width) // 2 if total_w > li.width else 0
        out_img.paste(li, (x, y), li)
        y += li.height + line_spacing
    # ensure output directory exists (handle bare filenames)
    out_dir = os.path.dirname(out_path) or '.'
    os.makedirs(out_dir, exist_ok=True)
    out_img.save(out_path)
    return out_path


def main(argv):
    parser = argparse.ArgumentParser(description='Generate PNG text using images from custom_font')
    parser.add_argument('text', nargs='*', help='Text to render (wrap in quotes). Use "\\n" for newlines. If omitted, you will be prompted.')
    parser.add_argument('--font-dir', default=None, help='Path to custom_font folder (defaults to repo custom_font or game_assets/custom_font)')
    parser.add_argument('--output', default=None, help='Output PNG path (defaults to dialogue/<timestamp>.png)')
    parser.add_argument('--list-fonts', action='store_true', help='List available glyph mappings and exit')
    parser.add_argument('--bg', default=None, help='Background color as R,G,B (e.g. 255,255,255) or hex (#RRGGBB). If set, fills background')
    args = parser.parse_args(argv)
    # Join positional text parts if provided, otherwise prompt the user
    if args.text:
        text_arg = ' '.join(args.text)
    else:
        try:
            text_arg = input('Enter text to render: ')
        except EOFError:
            parser.error('No text provided')

    # compute default dirs relative to repo root (one level up from scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '..'))
    # prefer explicit, then repo/custom_font, then repo/game_assets/custom_font
    if args.font_dir:
        font_dir = args.font_dir
    else:
        candidate1 = os.path.join(repo_root, 'custom_font')
        candidate2 = os.path.join(repo_root, 'game_assets', 'custom_font')
        if os.path.isdir(candidate1):
            font_dir = candidate1
        elif os.path.isdir(candidate2):
            font_dir = candidate2
        else:
            font_dir = candidate1

    # If requested, list the mapping and exit
    if args.list_fonts:
        mapping = build_mapping(font_dir)
        if not mapping:
            print('No glyphs found in', font_dir)
        else:
            print('Glyph mapping (char -> filename):')
            for k in sorted(mapping.keys()):
                print(repr(k), '->', mapping[k])
        return

    out = args.output
    if not out:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out = os.path.join(repo_root, 'dialogue', f'dialogue_{ts}.png')
    bg_color = parse_color(args.bg)
    out_path = generate_image(text_arg, font_dir, out, bg_color=bg_color)
    print('Saved:', out_path)

if __name__ == '__main__':
    main(sys.argv[1:])
