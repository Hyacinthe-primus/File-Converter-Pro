"""Focused tests for ImageMagick argv path hardening."""

import os
from types import SimpleNamespace

import pytest

from converter.mixins.image_converters import ImageConverters

MAGICK = r"C:\Tools\ImageMagick\magick.exe"


def _install_magick(monkeypatch, returncode=0, error=None):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        if error is not None:
            raise error
        return SimpleNamespace(returncode=returncode)

    monkeypatch.setattr(ImageConverters, "_find_imagemagick", staticmethod(lambda: MAGICK))
    monkeypatch.setattr("converter.mixins.image_converters.subprocess.run", fake_run)
    return calls


@pytest.mark.parametrize("source", ["-source.png", "@source.png"])
def test_relative_special_source_is_passed_as_absolute(monkeypatch, tmp_path, source):
    monkeypatch.chdir(tmp_path)
    calls = _install_magick(monkeypatch)

    assert ImageConverters()._magick_convert(source, "out.psd") is True

    cmd = calls[0][0]
    assert cmd[0] == MAGICK
    assert cmd[1] == os.path.abspath(source)
    assert os.path.isabs(cmd[1])


def test_relative_destination_is_passed_as_absolute(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    calls = _install_magick(monkeypatch)

    assert ImageConverters()._magick_convert("source.png", "out.psd") is True

    cmd = calls[0][0]
    assert cmd[2] == os.path.abspath("out.psd")
    assert os.path.isabs(cmd[2])


def test_absolute_paths_are_unchanged(monkeypatch, tmp_path):
    source = str(tmp_path / "source.png")
    destination = str(tmp_path / "out.psd")
    calls = _install_magick(monkeypatch)

    assert ImageConverters()._magick_convert(source, destination) is True

    assert calls[0][0] == [MAGICK, source, destination]


def test_success_behavior_and_subprocess_options(monkeypatch):
    calls = _install_magick(monkeypatch, returncode=0)

    assert ImageConverters()._magick_convert("source.png", "out.psd") is True

    kwargs = calls[0][1]
    assert kwargs["capture_output"] is True
    assert kwargs["timeout"] == 60
    assert "shell" not in kwargs


def test_nonzero_returncode_returns_false(monkeypatch):
    _install_magick(monkeypatch, returncode=1)

    assert ImageConverters()._magick_convert("source.png", "out.psd") is False


def test_missing_imagemagick_returns_false_without_running(monkeypatch):
    called = []

    monkeypatch.setattr(ImageConverters, "_find_imagemagick", staticmethod(lambda: None))
    monkeypatch.setattr(
        "converter.mixins.image_converters.subprocess.run",
        lambda *args, **kwargs: called.append((args, kwargs)),
    )

    assert ImageConverters()._magick_convert("source.png", "out.psd") is False
    assert called == []


def test_subprocess_exception_returns_false(monkeypatch):
    _install_magick(monkeypatch, error=OSError("magick failed"))

    assert ImageConverters()._magick_convert("source.png", "out.psd") is False
