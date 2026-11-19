"""Tests for document conversions - using mixin methods directly."""

import json

from converter.mixins.document_converters import DocumentConverters


def _engine():
    return DocumentConverters()


def test_txt_to_pdf(tmp_path):
    src = tmp_path / "test.txt"
    src.write_text("Hello World\nLine 2\nLine 3", encoding="utf-8")
    dst = tmp_path / "test.pdf"
    engine = _engine()
    result = engine._txt_to_pdf(str(src), str(dst))
    assert result is True
    assert dst.exists()
    assert dst.stat().st_size > 0


def test_txt_to_pdf_empty(tmp_path):
    src = tmp_path / "empty.txt"
    src.write_text("", encoding="utf-8")
    dst = tmp_path / "empty.pdf"
    engine = _engine()
    result = engine._txt_to_pdf(str(src), str(dst))
    assert result is True
    assert dst.exists()


def test_markdown_to_html(tmp_path):
    src = tmp_path / "readme.md"
    src.write_text(
        "# Heading\n\nA **bold** paragraph.\n\n| A | B |\n|---|---|\n| 1 | 2 |",
        encoding="utf-8",
    )
    dst = tmp_path / "readme.html"
    result = _engine()._markdown_to_html(str(src), str(dst))
    html = dst.read_text(encoding="utf-8")

    assert result is True
    assert html.startswith("<!DOCTYPE html>")
    assert "<title>readme</title>" in html
    assert "<h1>Heading</h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<table>" in html


def test_csv_to_json(tmp_path):
    src = tmp_path / "test.csv"
    src.write_text("name,age\nAlice,30\nBob,25", encoding="utf-8")
    dst = tmp_path / "test.json"
    engine = _engine()
    result = engine._csv_to_json(str(src), str(dst))
    assert result is True
    data = json.loads(dst.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert data[0]["name"] == "Alice"
    assert data[1]["age"] == "25"


def test_csv_to_json_excel_encodings(tmp_path):
    for name, raw in [
        ("utf8_bom.csv", "\ufeffName,City\r\nJosé,München\r\n".encode("utf-8")),
        ("ansi.csv", "Name,City\r\nJosé,München\r\n".encode("cp1252")),
    ]:
        src = tmp_path / name
        src.write_bytes(raw)
        dst = tmp_path / f"{name}.json"
        assert _engine()._csv_to_json(str(src), str(dst)) is True
        assert json.loads(dst.read_text(encoding="utf-8")) == [{"Name": "José", "City": "München"}]


def test_csv_to_json_semicolon_delimiter(tmp_path):
    src = tmp_path / "semi.csv"
    src.write_text("name;price;qty\r\nApple;1,50;3\r\n", encoding="utf-8")
    dst = tmp_path / "semi.json"
    assert _engine()._csv_to_json(str(src), str(dst)) is True
    assert json.loads(dst.read_text(encoding="utf-8")) == [{"name": "Apple", "price": "1,50", "qty": "3"}]


def test_json_to_csv(tmp_path):
    src = tmp_path / "test.json"
    src.write_text(json.dumps([{"a": 1, "b": 2}, {"a": 3, "b": 4}]), encoding="utf-8")
    dst = tmp_path / "test.csv"
    engine = _engine()
    result = engine._json_to_csv(str(src), str(dst))
    assert result is True
    lines = dst.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3  # header + 2 rows
    assert "a,b" in lines[0]


def test_json_to_csv_records_with_different_fields(tmp_path):
    src = tmp_path / "test.json"
    src.write_text(json.dumps([{"id": 1, "name": "Ann"}, {"id": 2, "email": "bob@x.com"}]), encoding="utf-8")
    dst = tmp_path / "test.csv"
    result = _engine()._json_to_csv(str(src), str(dst))
    assert result is True
    assert dst.read_text(encoding="utf-8").splitlines() == ["id,name,email", "1,Ann,", "2,,bob@x.com"]


def test_txt_to_docx(tmp_path):
    src = tmp_path / "test.txt"
    src.write_text("Hello\nWorld", encoding="utf-8")
    dst = tmp_path / "test.docx"
    engine = _engine()
    result = engine._txt_to_docx(str(src), str(dst))
    assert result is True
    assert dst.exists()
    assert dst.stat().st_size > 0


def test_json_to_csv_empty(tmp_path):
    src = tmp_path / "empty.json"
    src.write_text("[]", encoding="utf-8")
    dst = tmp_path / "empty.csv"
    engine = _engine()
    result = engine._json_to_csv(str(src), str(dst))
    assert result is False


def test_csv_to_json_special_chars(tmp_path):
    src = tmp_path / "special.csv"
    src.write_text('text,value\n"hello, world",42\n"line1\nline2",99', encoding="utf-8")
    dst = tmp_path / "special.json"
    engine = _engine()
    result = engine._csv_to_json(str(src), str(dst))
    assert result is True
    data = json.loads(dst.read_text(encoding="utf-8"))
    assert data[0]["text"] == "hello, world"


def test_rtf_to_spans():
    engine = _engine()
    raw = r"{\rtf1\ansi {\b Bold} and normal}"
    spans = engine._rtf_to_spans(raw)
    assert len(spans) > 0
    texts = [s["text"] for s in spans if s.get("text")]
    full = "".join(texts)
    assert "Bold" in full
