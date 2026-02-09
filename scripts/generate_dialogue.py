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
            # map the character (e.g. '"') to the file, and also keep a token
            # entry so we can distinguish left/right variants later
            mapping[named[stem]] = fname
            mapping[f'__token__{stem}'] = fname
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


def _load_glyph_widths(mapping, font_dir, space_width=6):
    """Return dict char -> width (in pixels). Unknown chars are treated as space_width."""
    widths = {}
    for ch, fname in mapping.items():
        if ch == ' ':
            widths[ch] = space_width
            continue
        img_path = os.path.join(font_dir, fname)
        try:
            with Image.open(img_path) as im:
                widths[ch] = im.width
        except Exception:
            widths[ch] = space_width
    return widths


def wrap_text_to_lines(text, mapping, font_dir, max_width, space_width=12):
    """Wrap the given text into lines such that each line's pixel width <= max_width.

    Prefers to break at spaces (words); if a single word exceeds max_width it is
    broken at the character where it overflows.
    """
    # Precompute glyph widths
    glyph_widths = _load_glyph_widths(mapping, font_dir, space_width)

    paragraphs = text.split('\n')
    out_lines = []
    for para in paragraphs:
        if not para:
            out_lines.append('')
            continue
        words = para.split(' ')
        cur_line = ''
        cur_width = 0
        first_word = True
        quote_open = False
        for word in words:
            # compute word width (characters)
            w = 0
            for ch in word:
                # handle double-quote opening/closing selection if tokens exist
                if ch == '"' and ('__token__Left_quote' in mapping or '__token__Right_quote' in mapping):
                    token_key = '__token__Left_quote' if not quote_open else '__token__Right_quote'
                    ch_w = glyph_widths.get(token_key, glyph_widths.get('"', space_width))
                    quote_open = not quote_open
                else:
                    ch_w = glyph_widths.get(ch, glyph_widths.get(ch.lower(), space_width))
                w += ch_w
            # include a space before word if not first
            space_w = 0 if first_word else space_width
            if first_word:
                # place word (may need to break if too long)
                if w <= max_width:
                    cur_line = word
                    cur_width = w
                    first_word = False
                    continue
                # word longer than line - fall back to char-breaking
            # normal handling
            if cur_width + space_w + w <= max_width:
                if not first_word:
                    cur_line += ' '
                cur_line += word
                cur_width += space_w + w
                first_word = False
            else:
                # can't fit whole word; if word itself longer than max_width, break it
                if w > max_width:
                    # flush current line if any
                    if cur_line:
                        out_lines.append(cur_line)
                        cur_line = ''
                        cur_width = 0
                        first_word = True
                    # break word by chars
                    chunk = ''
                    chunk_w = 0
                    for ch in word:
                        if ch == '"' and ('__token__Left_quote' in mapping or '__token__Right_quote' in mapping):
                            token_key = '__token__Left_quote' if not quote_open else '__token__Right_quote'
                            ch_w = glyph_widths.get(token_key, glyph_widths.get('"', space_width))
                            quote_open = not quote_open
                        else:
                            ch_w = glyph_widths.get(ch, glyph_widths.get(ch.lower(), space_width))
                        if chunk_w + ch_w <= max_width:
                            chunk += ch
                            chunk_w += ch_w
                        else:
                            if chunk:
                                out_lines.append(chunk)
                            chunk = ch
                            chunk_w = ch_w
                    if chunk:
                        cur_line = chunk
                        cur_width = chunk_w
                        first_word = False
                else:
                    # flush current line and start with this word
                    if cur_line:
                        out_lines.append(cur_line)
                    cur_line = word
                    cur_width = w
                    first_word = False
        if cur_line:
            out_lines.append(cur_line)
    return out_lines


def compose_string_to_image(s, mapping, font_dir, space_width=12):
    """Compose a single string (no newline) into an Image using glyph files."""
    imgs = []
    quote_open = False
    for ch in s:
        # If double-quote, prefer left/right token variants when available
        fname = None
        if ch == '"' and ('__token__Left_quote' in mapping or '__token__Right_quote' in mapping):
            token_key = '__token__Left_quote' if not quote_open else '__token__Right_quote'
            fname = mapping.get(token_key)
            quote_open = not quote_open
        if fname is None:
            fname = mapping.get(ch)
        if fname is None:
            fname = mapping.get(ch.lower())
        if fname is None:
            if ch == ' ':
                imgs.append(Image.new('RGBA', (space_width, 1), (0,0,0,0)))
                continue
            fname = mapping.get('.') if ch == '.' else None
        if fname is None:
            continue
        img_path = os.path.join(font_dir, fname)
        try:
            img = Image.open(img_path).convert('RGBA')
        except Exception:
            continue
        imgs.append(img)
    if not imgs:
        return Image.new('RGBA', (space_width, 1), (0,0,0,0))
    return compose_line(imgs, space_width)


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


def generate_image(text, font_dir, out_path, space_width=12, line_spacing=8, bg_color=None, box_width=None, box_height=None):
    mapping = build_mapping(font_dir)
    # Wrap to box_width if provided, otherwise respect explicit newlines
    if box_width:
        lines = wrap_text_to_lines(text, mapping, font_dir, box_width, space_width)
    else:
        lines = text.split('\n')

    # Compose each line into an image and keep strings for trimming
    line_images = []
    line_strings = []
    for line in lines:
        img = compose_string_to_image(line, mapping, font_dir, space_width)
        line_images.append(img)
        line_strings.append(line)

    # If a box_height is specified, trim lines and add ellipsis if needed
    if box_height is not None and line_images:
        widths = [li.width for li in line_images]
        heights = [li.height for li in line_images]
        total_h = sum(heights) + line_spacing * (len(heights)-1 if len(heights)>0 else 0)
        # remove trailing lines until height fits
        while total_h > box_height and len(line_images) > 1:
            line_images.pop()
            line_strings.pop()
            widths = [li.width for li in line_images]
            heights = [li.height for li in line_images]
            total_h = sum(heights) + line_spacing * (len(heights)-1 if len(heights)>0 else 0)

        # If still too tall (single line larger than box), try to trim that line
        if total_h > box_height and line_images:
            # We'll trim characters from the last line until it fits (adding ellipsis)
            last_idx = len(line_strings) - 1
            base = line_strings[last_idx]
            ell = '...'
            # compute ellipsis image width
            ell_img = compose_string_to_image(ell, mapping, font_dir, space_width)
            ell_w = ell_img.width
            # repeatedly remove characters and recompute image width
            cur = base
            while cur:
                cur = cur[:-1]
                cur_img = compose_string_to_image(cur, mapping, font_dir, space_width)
                if cur_img.width + ell_w <= (box_width or cur_img.width + ell_w):
                    # ok, use cur + ell
                    new_img = compose_string_to_image(cur + ell, mapping, font_dir, space_width)
                    line_images[last_idx] = new_img
                    line_strings[last_idx] = cur + ell
                    break
            # if cur became empty and still doesn't fit, replace with ellipsis only
            if not cur:
                line_images[last_idx] = ell_img
                line_strings[last_idx] = ell

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
    parser.add_argument('--name', default=None, help='Output filename (e.g. "hello.png") - saves to dialogue/<name>')
    parser.add_argument('--output', default=None, help='Full output path (overrides --name)')
    parser.add_argument('--list-fonts', action='store_true', help='List available glyph mappings and exit')
    parser.add_argument('--bg', default=None, help='Background color as R,G,B (e.g. 255,255,255) or hex (#RRGGBB). If set, fills background')
    parser.add_argument('--box-width', type=int, default=None, help='Max pixel width of a dialogue box; text will wrap to this width')
    parser.add_argument('--box-height', type=int, default=None, help='Max pixel height of a dialogue box; text will be trimmed to this height')
    parser.add_argument('--space-width', type=int, default=10, help='Pixel width to use for space characters (word spacing)')
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

    # Determine output path: --output > --name > timestamp default
    if args.output:
        out = args.output
    elif args.name:
        out = os.path.join(repo_root, 'dialogue', args.name)
    else:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        out = os.path.join(repo_root, 'dialogue', f'dialogue_{ts}.png')
    bg_color = parse_color(args.bg)
    # Default dialogue box size if not provided
    default_box_w = 143
    default_box_h = 73
    box_w = args.box_width if args.box_width is not None else default_box_w
    box_h = args.box_height if args.box_height is not None else default_box_h
    out_path = generate_image(text_arg, font_dir, out, bg_color=bg_color, box_width=box_w, box_height=box_h, space_width=args.space_width)
    print('Saved:', out_path)

if __name__ == '__main__':
    main(sys.argv[1:])
