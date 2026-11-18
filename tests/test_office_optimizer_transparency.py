"""Optimize with image compression must not turn transparent images into JPEG."""

import io

import pytest
from docx import Document
from PIL import Image
from pptx import Presentation

from app.mixins.office_optimizer import OfficeDocOptimizerMixin, _has_transparency


def _transparent_png() -> bytes:
    png = io.BytesIO()
    # Noise so a JPEG would come out smaller than the PNG
    Image.effect_noise((200, 200), 64).convert("RGBA").save(png, format="PNG")
    return png.getvalue()


def test_transparent_png_survives_word_optimize(tmp_path):
    png = _transparent_png()
    src, out = tmp_path / "in.docx", tmp_path / "out.docx"
    doc = Document()
    doc.add_picture(io.BytesIO(png))
    doc.save(src)

    assert OfficeDocOptimizerMixin().optimize_word_file(str(src), str(out), "normal", False, True)

    blob = next(r.target_part.blob for r in Document(out).part.rels.values() if "image" in r.reltype)
    with Image.open(io.BytesIO(blob)) as img:
        assert (img.format, img.mode) == ("PNG", "RGBA")


def test_transparent_png_survives_powerpoint_optimize(tmp_path):
    png = _transparent_png()
    src, out = tmp_path / "in.pptx", tmp_path / "out.pptx"
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_picture(io.BytesIO(png), 0, 0)
    prs.save(src)

    assert OfficeDocOptimizerMixin().optimize_powerpoint_file(str(src), str(out), "normal", False, True)

    result = Presentation(out)
    picture = next(shape for shape in result.slides[0].shapes if shape.shape_type == 13)
    with Image.open(io.BytesIO(picture.image.blob)) as img:
        assert (img.format, img.mode) == ("PNG", "RGBA")


@pytest.mark.parametrize("mode", ["RGBA", "LA", "PA", "RGBa", "La"])
def test_has_transparency_detects_alpha_band_modes(mode):
    with Image.new(mode, (2, 2)) as img:
        assert _has_transparency(img)
