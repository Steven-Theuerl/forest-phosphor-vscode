#!/usr/bin/env python3
"""
Convert iTerm2 float RGB values to sRGB hex.
P3 colors are converted to sRGB via the Display P3 → XYZ D65 → sRGB matrix.
"""

import json
import math

# Display P3 linear → XYZ D65 matrix
P3_TO_XYZ = [
    [0.4865709, 0.2656677, 0.1982173],
    [0.2289746, 0.6917385, 0.0792869],
    [0.0000000, 0.0451134, 1.0439444],
]

# XYZ D65 → linear sRGB matrix
XYZ_TO_SRGB = [
    [ 3.2404542, -1.5371385, -0.4985314],
    [-0.9692660,  1.8760108,  0.0415560],
    [ 0.0556434, -0.2040259,  1.0572252],
]

def srgb_linearize(v: float) -> float:
    """sRGB/P3 encoded → linear light."""
    if v <= 0.04045:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4

def srgb_encode(v: float) -> float:
    """Linear light → sRGB encoded."""
    v = max(0.0, min(1.0, v))
    if v <= 0.0031308:
        return 12.92 * v
    return 1.055 * (v ** (1.0 / 2.4)) - 0.055

def matmul3(m, v):
    return [
        m[0][0]*v[0] + m[0][1]*v[1] + m[0][2]*v[2],
        m[1][0]*v[0] + m[1][1]*v[1] + m[1][2]*v[2],
        m[2][0]*v[0] + m[2][1]*v[1] + m[2][2]*v[2],
    ]

def p3_to_hex(r: float, g: float, b: float) -> str:
    # Convert Display P3 encoded float RGB to sRGB hex string.
    lin = [srgb_linearize(r), srgb_linearize(g), srgb_linearize(b)]
    xyz = matmul3(P3_TO_XYZ, lin)
    srgb_lin = matmul3(XYZ_TO_SRGB, xyz)
    encoded = [srgb_encode(c) for c in srgb_lin]
    return "#{:02X}{:02X}{:02X}".format(
        round(encoded[0] * 255),
        round(encoded[1] * 255),
        round(encoded[2] * 255),
    )

def srgb_to_hex(r: float, g: float, b: float) -> str:
    # Convert sRGB encoded float RGB to hex string.
    return "#{:02X}{:02X}{:02X}".format(
        round(r * 255),
        round(g * 255),
        round(b * 255),
    )

def color_to_hex(entry: dict) -> str:
    r = entry["Red Component"]
    g = entry["Green Component"]
    b = entry["Blue Component"]
    space = entry.get("Color Space", "sRGB")
    if space == "P3":
        return p3_to_hex(r, g, b)
    else:
        return srgb_to_hex(r, g, b)

with open("example.json") as f:
    data = json.load(f)

# Extract only the keys we care about (Dark variants + fallbacks)
keys = [
    "Background Color (Dark)",
    "Foreground Color (Dark)",
    "Selection Color (Dark)",
    "Ansi 0 Color (Dark)",
    "Ansi 1 Color (Dark)",
    "Ansi 2 Color (Dark)",
    "Ansi 3 Color (Dark)",
    "Ansi 4 Color (Dark)",
    "Ansi 5 Color (Dark)",
    "Ansi 6 Color (Dark)",
    "Ansi 7 Color (Dark)",
    "Ansi 8 Color (Dark)",
    "Ansi 9 Color (Dark)",
    "Ansi 10 Color (Dark)",
    "Ansi 11 Color (Dark)",
    "Ansi 12 Color (Dark)",
    "Ansi 13 Color (Dark)",
    "Ansi 14 Color (Dark)",
    "Ansi 15 Color (Dark)",
    "Cursor Color (Dark)",
    "Bold Color (Dark)",
    "Link Color (Dark)",
]

results = {}
for key in keys:
    if key in data:
        hex_val = color_to_hex(data[key])
        results[key] = hex_val
        print(f"{key:<35} {hex_val}  ({data[key].get('Color Space','sRGB')})")

# Save for use by theme builder
with open("colors.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved to colors.json")
