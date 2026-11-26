"""Tests for the writable application-data root and legacy migration."""

import os
import sys

import pytest

import app_paths


@pytest.fixture(autouse=True)
def _fresh_migration_state():
    app_paths._reset_cache()
    yield
    app_paths._reset_cache()


def _norm(path) -> str:
    return os.path.normcase(os.path.abspath(str(path)))


def test_dev_mode_uses_source_folder(monkeypatch):
    monkeypatch.delenv(app_paths.DATA_DIR_ENV, raising=False)
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert _norm(app_paths.get_data_dir()) == _norm(app_paths.SRC_DIR)


def test_env_override_wins(monkeypatch, tmp_path):
    target = tmp_path / "portable-data"
    monkeypatch.setenv(app_paths.DATA_DIR_ENV, str(target))
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    assert _norm(app_paths.get_data_dir()) == _norm(target)


def test_frozen_uses_platform_data_root(monkeypatch, tmp_path):
    monkeypatch.delenv(app_paths.DATA_DIR_ENV, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    root = tmp_path / "platform-root"
    if os.name == "nt":
        monkeypatch.setenv("LOCALAPPDATA", str(root))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(root))

    assert _norm(app_paths.get_data_dir()) == _norm(root / app_paths.APP_FOLDER_NAME)


def test_ensure_data_dir_creates_folder(monkeypatch, tmp_path):
    target = tmp_path / "created" / "data"
    monkeypatch.setenv(app_paths.DATA_DIR_ENV, str(target))

    assert _norm(app_paths.ensure_data_dir()) == _norm(target)
    assert target.is_dir()


def test_is_packaged_false_in_development(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert app_paths.is_packaged() is False


def test_special_events_db_uses_data_dir(monkeypatch, tmp_path):
    import special_events_manager as sem

    monkeypatch.setattr(app_paths, "ensure_data_dir", lambda: tmp_path)

    assert sem.SpecialEventsManager._get_db_path(object()) == str(tmp_path / "special_events.db")


def _fake_frozen_app(monkeypatch, tmp_path):
    """Point the app at a fake install dir and a fake per-user data root."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    root = tmp_path / "local"
    monkeypatch.delenv(app_paths.DATA_DIR_ENV, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(app_dir / "FCP.exe"))
    if os.name == "nt":
        monkeypatch.setenv("LOCALAPPDATA", str(root))
    else:
        monkeypatch.setenv("XDG_DATA_HOME", str(root))
    return app_dir, root / app_paths.APP_FOLDER_NAME


def test_migrate_copies_legacy_files(monkeypatch, tmp_path):
    app_dir, data_dir = _fake_frozen_app(monkeypatch, tmp_path)
    (app_dir / "file_converter_config.dat").write_bytes(b"encrypted")
    (app_dir / "special_events.db").write_bytes(b"events")
    (app_dir / "automation").mkdir()
    (app_dir / "automation" / "watch.toml").write_text("[watch_folders]\n", encoding="utf-8")
    (app_dir / "styles" / "custom_themes" / "MyTheme").mkdir(parents=True)
    (app_dir / "styles" / "custom_themes" / "MyTheme" / "style.qss").write_text("QWidget {}\n", encoding="utf-8")

    internal = app_dir / "_internal"
    internal.mkdir()
    (internal / "file_converter_stats.db").write_bytes(b"sqlite")

    monkeypatch.setattr(sys, "_MEIPASS", str(internal), raising=False)

    migrated = app_paths.migrate_legacy_data()

    assert set(migrated) == {
        "file_converter_config.dat",
        "file_converter_stats.db",
        "special_events.db",
        "automation/watch.toml",
        "styles/custom_themes/MyTheme/style.qss",
    }
    assert (data_dir / "file_converter_config.dat").read_bytes() == b"encrypted"
    assert (data_dir / "file_converter_stats.db").read_bytes() == b"sqlite"
    assert (data_dir / "automation" / "watch.toml").is_file()
    assert (data_dir / "styles" / "custom_themes" / "MyTheme" / "style.qss").is_file()
    # Originals are never deleted.
    assert (app_dir / "file_converter_config.dat").is_file()
    assert (app_dir / "automation" / "watch.toml").is_file()


def test_migrate_never_overwrites_existing_data(monkeypatch, tmp_path):
    app_dir, data_dir = _fake_frozen_app(monkeypatch, tmp_path)
    data_dir.mkdir(parents=True)
    (data_dir / "file_converter_config.dat").write_bytes(b"current")
    (app_dir / "file_converter_config.dat").write_bytes(b"old")

    assert app_paths.migrate_legacy_data() == []
    assert (data_dir / "file_converter_config.dat").read_bytes() == b"current"


def test_migrate_runs_once(monkeypatch, tmp_path):
    app_dir, _ = _fake_frozen_app(monkeypatch, tmp_path)
    (app_dir / "file_converter_config.dat").write_bytes(b"old")

    assert app_paths.migrate_legacy_data() == ["file_converter_config.dat"]
    assert app_paths.migrate_legacy_data() == []


def test_migrate_skipped_for_explicit_data_dir(monkeypatch, tmp_path):
    app_dir, _ = _fake_frozen_app(monkeypatch, tmp_path)
    (app_dir / "file_converter_config.dat").write_bytes(b"old")
    explicit = tmp_path / "portable"
    monkeypatch.setenv(app_paths.DATA_DIR_ENV, str(explicit))

    assert app_paths.migrate_legacy_data() == []
    assert not (explicit / "file_converter_config.dat").exists()


def test_migrate_skipped_in_development(monkeypatch, tmp_path):
    monkeypatch.delenv(app_paths.DATA_DIR_ENV, raising=False)
    monkeypatch.delattr(sys, "frozen", raising=False)

    assert app_paths.migrate_legacy_data() == []
    assert app_paths.get_legacy_dirs() == []
