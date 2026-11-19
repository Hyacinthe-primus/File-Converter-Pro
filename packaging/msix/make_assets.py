"""Generate the MSIX image assets from the application icon.

Usage:
    python packaging/msix/make_assets.py <icon.ico> <output-dir>

The Microsoft Store requires a handful of PNG logos; this script renders them
from the existing multi-resolution .ico instead of keeping duplicate binaries
in the repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

TARGETS: dict[str, tuple[int, int]] = {
    "StoreLogo.png": (50, 50),
    "Square44x44Logo.png": (44, 44),
    "Square150x150Logo.png": (150, 150),
    "Wide310x150Logo.png": (310, 150),
    "SplashScreen.png": (620, 300),
}


def load_largest_frame(path: Path) -> Image.Image:
    """Return the highest-resolution frame of an .ico file as RGBA."""
    image = Image.open(path)
    frames = []
    for index in range(getattr(image, "n_frames", 1)):
        image.seek(index)
        frames.append(image.copy())
    frame = max(frames, key=lambda item: item.size[0] * item.size[1])
    return frame.convert("RGBA")


def centered(logo: Image.Image, size: tuple[int, int], fill: float = 0.82) -> Image.Image:
    """Fit *logo* inside *size*, centered on a transparent canvas."""
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    scale = min(size[0] * fill / logo.width, size[1] * fill / logo.height)
    width = max(1, round(logo.width * scale))
    height = max(1, round(logo.height * scale))
    resized = logo.resize((width, height), Image.LANCZOS)
    canvas.alpha_composite(resized, ((size[0] - width) // 2, (size[1] - height) // 2))
    return canvas


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1])
        return 2

    icon_path = Path(argv[1])
    output_dir = Path(argv[2])
    if not icon_path.is_file():
        print(f"Icon not found: {icon_path}")
        return 1

    logo = load_largest_frame(icon_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, size in TARGETS.items():
        centered(logo, size).save(output_dir / name, format="PNG")
        print(f"  {name}: {size[0]}x{size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
