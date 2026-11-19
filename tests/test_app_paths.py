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


def test_frozen_uses_localappdata(monkeypatch, tmp_path):
    monkeypatch.delenv(app_paths.DATA_DIR_ENV, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))

    assert _norm(app_paths.get_data_dir()) == _norm(tmp_path / "local" / app_paths.APP_FOLDER_NAME)


def test_ensure_data_dir_creates_folder(monkeypatch, tmp_path):
    target = tmp_path / "created" / "data"
    monkeypatch.setenv(app_paths.DATA_DIR_ENV, str(target))

    assert _norm(app_paths.ensure_data_dir()) == _norm(target)
    assert target.is_dir()


def _fake_frozen_app(monkeypatch, tmp_path):
    """Point the app at a fake install dir and a fake LOCALAPPDATA."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    monkeypatch.delenv(app_paths.DATA_DIR_ENV, raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(app_dir / "FCP.exe"))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    return app_dir, tmp_path / "local" / app_paths.APP_FOLDER_NAME


def test_migrate_copies_legacy_files(monkeypatch, tmp_path):
    app_dir, data_dir = _fake_frozen_app(monkeypatch, tmp_path)
    (app_dir / "file_converter_config.dat").write_bytes(b"encrypted")
    (app_dir / "automation").mkdir()
    (app_dir / "automation" / "watch.toml").write_text("[watch_folders]\n", encoding="utf-8")

    internal = app_dir / "_internal"
    internal.mkdir()
    (internal / "file_converter_stats.db").write_bytes(b"sqlite")

    monkeypatch.setattr(sys, "_MEIPASS", str(internal), raising=False)

    migrated = app_paths.migrate_legacy_data()

    assert set(migrated) == {
        "file_converter_config.dat",
        "file_converter_stats.db",
        "automation/watch.toml",
    }
    assert (data_dir / "file_converter_config.dat").read_bytes() == b"encrypted"
    assert (data_dir / "file_converter_stats.db").read_bytes() == b"sqlite"
    assert (data_dir / "automation" / "watch.toml").is_file()
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
