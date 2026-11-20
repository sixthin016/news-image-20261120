#!/usr/bin/env python3
"""news-image-20261120 entry: copy the pre-rendered front page to /output.

The image is rendered locally by render.py (Pillow) from manifest.json, a
manifest of 42 stories verified against reporting filed 19-20 Nov 2026.
This entrypoint uses only the standard library, needs no network, and is
byte-deterministic: two runs write identical bytes.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    src = os.path.join(HERE, "entry.png")
    if not os.path.isfile(src):
        print("entry.png missing: run python3 render.py first", file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
