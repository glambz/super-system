#!/usr/bin/env python3
"""WCAG 2.x contrast checker.

Usage:
    python3 contrast-check.py "#FFFFFF" "#777777"
    python3 contrast-check.py FFFFFF 777777
    python3 contrast-check.py --selftest

Prints the contrast ratio and a PASS/FAIL verdict for normal text (4.5:1)
and large text (3:1). Exit code 0 only when both verdicts pass, so scripts
can chain on it.
"""

import re
import sys

# (foreground, background, expected ratio, passes 4.5, passes 3.0)
KNOWN = [
    ("#FFFFFF", "#000000", 21.00, True, True),
    ("#777777", "#FFFFFF", 4.48, False, True),
    ("#767676", "#FFFFFF", 4.54, True, True),
    ("#999999", "#FFFFFF", 2.85, False, False),
]


def parse_hex(value):
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", value):
        raise ValueError(f"expected a hex color like #FFFFFF, got {value!r}")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def linearize(channel):
    c = channel / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (linearize(ch) for ch in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a, color_b):
    lum_a, lum_b = luminance(color_a), luminance(color_b)
    lighter, darker = sorted((lum_a, lum_b), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def selftest():
    failures = 0
    for fg, bg, ratio, normal, large in KNOWN:
        # Verdicts read the unrounded ratio: 4.498 must not pass 4.5 by rounding.
        raw = contrast_ratio(parse_hex(fg), parse_hex(bg))
        if f"{raw:.2f}" != f"{ratio:.2f}":
            failures += 1
            print(f"selftest: {fg} on {bg}: expected {ratio:.2f}, got {raw:.2f}")
        if (raw >= 4.5) != normal or (raw >= 3.0) != large:
            failures += 1
            print(f"selftest: {fg} on {bg}: verdicts disagree with expected")
    if failures:
        return 1
    print(f"selftest: {len(KNOWN)} pairs OK")
    return 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) != 2:
        print("usage: python3 contrast-check.py <hex1> <hex2> | --selftest")
        return 2
    try:
        ratio = contrast_ratio(parse_hex(argv[0]), parse_hex(argv[1]))
    except ValueError as exc:
        print(f"error: {exc}")
        return 2

    normal = ratio >= 4.5
    large = ratio >= 3.0
    print(f"ratio: {ratio:.2f}:1")
    print(f"normal text (4.5:1): {'PASS' if normal else 'FAIL'}")
    print(f"large text  (3.0:1): {'PASS' if large else 'FAIL'}")
    return 0 if normal and large else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
