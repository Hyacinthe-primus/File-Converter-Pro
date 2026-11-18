"""Optimize with image compression must not turn transparent images into JPEG."""

import io

from docx import Document
from PIL import Image

from app.mixins.office_optimizer import OfficeDocOptimizerMixin


def test_transparent_png_survives_word_optimize(tmp_path):
    png = io.BytesIO()
    # Noise so a JPEG would come out smaller than the PNG
    Image.effect_noise((200, 200), 64).convert("RGBA").save(png, format="PNG")
    src, out = tmp_path / "in.docx", tmp_path / "out.docx"
    doc = Document()
    doc.add_picture(io.BytesIO(png.getvalue()))
    doc.save(src)

    assert OfficeDocOptimizerMixin().optimize_word_file(str(src), str(out), "normal", False, True)

    blob = next(r.target_part.blob for r in Document(out).part.rels.values() if "image" in r.reltype)
    with Image.open(io.BytesIO(blob)) as img:
        assert (img.format, img.mode) == ("PNG", "RGBA")
