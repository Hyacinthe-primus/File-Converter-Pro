"""
Writable application-data locations.

Resolution order for get_data_dir():
1. FCP_DATA_DIR environment variable (portable installs and tests)
2. frozen: %LOCALAPPDATA%\\FileConverterPro
   (POSIX: $XDG_DATA_HOME/FileConverterPro or ~/.local/share/...)
3. development: the src/ folder
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from utils import SRC_DIR

APP_FOLDER_NAME = "FileConverterPro"
DATA_DIR_ENV = "FCP_DATA_DIR"

# SQLite sidecar files travel with their database so WAL contents are not lost.
_LEGACY_FILES: tuple[str, ...] = (
    "file_converter_config.dat",
    "file_converter_key.key",
    "file_converter_stats.db",
    "file_converter_stats.db-wal",
    "file_converter_stats.db-shm",
    "file_converter_advanced.db",
    "file_converter_advanced.db-wal",
    "file_converter_advanced.db-shm",
    "achievements.db",
    "achievements.db-wal",
    "achievements.db-shm",
)

_LEGACY_DIRS: tuple[str, ...] = ("automation",)

_migrated = False


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def is_packaged() -> bool:
    """True inside an MSIX/AppX package (registry writes are virtualized there)."""
    if os.name != "nt" or not is_frozen():
        return False
    try:
        import ctypes
        from ctypes import wintypes

        length = wintypes.UINT(0)
        # 122 (ERROR_INSUFFICIENT_BUFFER) = package identity exists;
        # 15700 (APPMODEL_ERROR_NO_PACKAGE) = unpackaged.
        result = ctypes.windll.kernel32.GetCurrentPackageFullName(ctypes.byref(length), None)
        return result == 122
    except Exception:
        return False


def get_data_dir() -> Path:
    """Return the per-user writable data folder (never creates it)."""
    override = os.environ.get(DATA_DIR_ENV)
    if override:
        return Path(override).expanduser().resolve()

    if not is_frozen():
        return SRC_DIR

    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return Path(base) / APP_FOLDER_NAME

    base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return Path(base) / APP_FOLDER_NAME


def ensure_data_dir() -> Path:
    path = get_data_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_legacy_dirs() -> list[Path]:
    """Folders older builds wrote user data to (frozen only)."""
    if not is_frozen():
        return []

    exe_dir = Path(sys.executable).resolve().parent
    # onedir builds: _MEIPASS is <app>\_internal
    bundle_dir = getattr(sys, "_MEIPASS", None)
    candidates = [exe_dir, Path(bundle_dir) if bundle_dir else exe_dir / "_internal"]
    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = os.path.normcase(os.path.abspath(candidate))
        if key not in seen:
            seen.add(key)
            unique.append(Path(candidate))
    return unique


def _copy_missing(src: Path, dst: Path) -> bool:
    if not src.is_file() or dst.exists():
        return False
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    except OSError as exc:
        print(f"[app_paths] Could not migrate {src} -> {dst}: {exc}")
        return False


def migrate_legacy_data() -> list[str]:
    """Copy legacy user data into get_data_dir() once.

    Never overwrites existing files and leaves the originals in place.
    Skipped in development and when FCP_DATA_DIR is set.
    Returns the names that were copied.
    """
    global _migrated
    if _migrated:
        return []
    _migrated = True

    if not is_frozen() or os.environ.get(DATA_DIR_ENV):
        return []

    target = ensure_data_dir()
    target_key = os.path.normcase(os.path.abspath(target))
    migrated: list[str] = []

    for legacy in get_legacy_dirs():
        if os.path.normcase(os.path.abspath(legacy)) == target_key or not legacy.is_dir():
            continue

        for name in _LEGACY_FILES:
            if _copy_missing(legacy / name, target / name):
                migrated.append(name)

        for name in _LEGACY_DIRS:
            legacy_dir = legacy / name
            if not legacy_dir.is_dir():
                continue
            for item in sorted(legacy_dir.iterdir()):
                if item.is_file() and _copy_missing(item, target / name / item.name):
                    migrated.append(f"{name}/{item.name}")

    return migrated


def _reset_cache() -> None:
    """Test hook: allow migration to run again."""
    global _migrated
    _migrated = False


__all__ = [
    "APP_FOLDER_NAME",
    "DATA_DIR_ENV",
    "ensure_data_dir",
    "get_data_dir",
    "get_legacy_dirs",
    "is_frozen",
    "is_packaged",
    "migrate_legacy_data",
]