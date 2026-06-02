#!/usr/bin/env python3
"""Generate a simple icon.ico for IT Support Toolkit."""

import os
import struct
import zlib


def create_png(size=32):
    """Create a minimal valid PNG image data for an icon."""
    width, height = size, size
    raw_data = bytearray()

    for y in range(height):
        raw_data.append(0)  # filter byte
        for x in range(width):
            cx, cy = width // 2, height // 2

            # Shield shape
            in_shield = False
            if y < height * 0.75:
                edge = int((y / (height * 0.75)) * (width // 2 - 4)) + 2
                in_shield = x >= edge and x < width - edge
            else:
                progress = (y - height * 0.75) / (height * 0.25)
                edge = int((1 - progress) * (width // 2 - 4)) + 2
                in_shield = x >= edge and x < width - edge

            if in_shield:
                dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
                intensity = int(80 + 100 * (1 - dist / cx))
                r = max(0, min(255, intensity // 2))
                g = max(0, min(255, intensity))
                b = 180
                a = 255
                # White wrench/gear in center
                if 10 < y < 22 and 10 < x < 22:
                    if abs(x - 16) <= 1 and abs(y - 16) <= 1:
                        r, g, b = 255, 255, 255
                    elif abs(x - 12) <= 1 and 14 < y < 18:
                        r, g, b = 220, 220, 220
                    elif abs(x - 20) <= 1 and 14 < y < 18:
                        r, g, b = 220, 220, 220
            else:
                r, g, b, a = 0, 0, 0, 0

            raw_data.extend([r, g, b, a])

    # Build PNG
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    png = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(bytes(raw_data)))
    png += chunk(b'IEND', b'')
    return png


def create_ico():
    """Create a .ico file with multiple sizes."""
    sizes = [16, 32, 48]
    icons = []
    offset = 6 + 16 * len(sizes)

    header = struct.pack('<HHH', 0, 1, len(sizes))
    dir_entries = b''

    for s in sizes:
        png_data = create_png(s)
        icons.append(png_data)
        bpp = 32
        dir_entries += struct.pack('<BBBBHHII',
                                  s if s < 256 else 0,
                                  s if s < 256 else 0,
                                  0, 0, 1, bpp,
                                  len(png_data), offset)
        offset += len(png_data)

    ico = header + dir_entries
    for png_data in icons:
        ico += png_data
    return ico


def main():
    assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    icon_path = os.path.join(assets_dir, "icon.ico")

    ico_data = create_ico()
    with open(icon_path, 'wb') as f:
        f.write(ico_data)

    print(f"[OK] Icon created: {icon_path} ({len(ico_data)} bytes)")
    return True


if __name__ == "__main__":
    main()
