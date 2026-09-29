#!/usr/bin/env python3
"""Generate a professional shield icon for IT Support Toolkit."""

import os
import struct
import zlib
import math


def create_png(size=64):
    """Create a professional shield-with-gear PNG for the icon."""
    width, height = size, size
    cx, cy = width / 2.0, height / 2.0
    outer = size * 0.44
    inner = size * 0.24

    raw_data = bytearray()

    for y in range(height):
        raw_data.append(0)  # filter byte (None)
        for x in range(width):
            # Determine if inside shield
            in_shield = False

            # Top triangle section
            if y < height * 0.65:
                edge = int(((y / (height * 0.65)) ** 0.7) * (width // 2 - 4)) + 2
                in_shield = x >= edge and x < width - edge
            else:
                # Bottom point section
                progress = (y - height * 0.65) / (height * 0.35)
                edge = int((1.0 - progress) * (width // 2 - 4)) + 2
                in_shield = x >= edge and x < width - edge

            if in_shield:
                # Gradient from top (purple) to bottom (pink)
                t = y / height
                r_base = int(203 * (1 - t) + 243 * t)
                g_base = int(166 * (1 - t) + 139 * t)
                b_base = int(247 * (1 - t) + 168 * t)

                # Slight highlight toward center
                dist_center = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                highlight = max(0, 1.0 - dist_center / (size * 0.5))
                highlight = highlight ** 0.5

                r = min(255, int(r_base + highlight * 40))
                g = min(255, int(g_base + highlight * 30))
                b = min(255, int(b_base + highlight * 20))
                a = 255

                # Draw gear/mechanism inside
                dx, dy = x - cx, y - cy
                dist = (dx ** 2 + dy ** 2) ** 0.5
                angle = math.atan2(dy, dx)

                # Gear teeth
                teeth = 8
                tooth_angle = (2 * math.pi) / teeth
                tooth_half = tooth_angle / 3.5

                # Normalize angle to [0, 2*pi)
                na = angle + math.pi

                in_tooth = False
                for i in range(teeth):
                    ta = i * tooth_angle
                    if na >= ta - tooth_half and na <= ta + tooth_half:
                        in_tooth = True
                        break

                inner_ring = inner * 0.65
                gear_outer = inner * 1.2
                gear_inner = inner * 0.92

                if inner_ring <= dist <= gear_outer and not in_tooth:
                    r, g, b = 30, 30, 46
                elif gear_inner <= dist <= gear_outer and in_tooth:
                    r, g, b = 30, 30, 46
                elif dist <= inner_ring:
                    r, g, b = 30, 30, 46

                # Center dot
                if dist <= inner * 0.18:
                    r, g, b = 205, 214, 244
            else:
                r, g, b, a = 0, 0, 0, 0

            raw_data.extend([r, g, b, a])

    # Build PNG chunks
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
    """Create a .ico file with multiple sizes for hi-DPI displays."""
    sizes = [16, 24, 32, 48, 64, 256]
    icons = []
    offset = 6 + 16 * len(sizes)

    header = struct.pack('<HHH', 0, 1, len(sizes))
    dir_entries = b''

    for s in sizes:
        png_data = create_png(s)
        icons.append(png_data)
        dir_entries += struct.pack('<BBBBHHII',
                                   s if s < 256 else 0,
                                   s if s < 256 else 0,
                                   0, 0, 1, 32,
                                   len(png_data), offset)
        offset += len(png_data)

    return header + dir_entries + b''.join(icons)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    icon_path = os.path.join(assets_dir, "icon.ico")

    ico_data = create_ico()
    with open(icon_path, 'wb') as f:
        f.write(ico_data)

    print(f"[OK] Icon created: {icon_path} ({len(ico_data)} bytes)")
    return True


if __name__ == "__main__":
    main()
