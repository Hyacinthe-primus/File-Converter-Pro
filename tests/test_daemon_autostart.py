"""Autostart must stay inert in packaged (MSIX) builds and unchanged elsewhere."""

import sys
import types

import daemon


def test_packaged_build_never_touches_the_run_key(monkeypatch):
    class ForbiddenWinreg(types.ModuleType):
        def __getattr__(self, name):
            raise AssertionError(f"winreg.{name} must not be used in a packaged build")

    monkeypatch.setattr(daemon, "is_packaged", lambda: True)
    monkeypatch.setitem(sys.modules, "winreg", ForbiddenWinreg("winreg"))

    daemon.set_autostart(True)
    assert daemon.is_autostart_enabled() is False


def test_unpackaged_build_still_reads_the_run_key(monkeypatch):
    calls = []

    fake = types.ModuleType("winreg")
    fake.HKEY_CURRENT_USER = object()
    fake.KEY_SET_VALUE = 1
    fake.REG_SZ = 1
    fake.OpenKey = lambda *a, **k: calls.append("open") or object()
    fake.QueryValueEx = lambda *a, **k: ('"FCP.exe" --daemon', 1)
    fake.CloseKey = lambda *a, **k: calls.append("close")

    monkeypatch.setattr(daemon, "is_packaged", lambda: False)
    monkeypatch.setitem(sys.modules, "winreg", fake)

    assert daemon.is_autostart_enabled() is True
    assert calls == ["open", "close"]
