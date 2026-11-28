"""Build-channel identity for File Converter Pro.

Stable is the default. ``packaging/build.ps1`` writes ``_build_channel.py``
with the selected channel for packaged builds; ``FCP_CHANNEL=dev`` does the
same for source runs.

Everything channel-specific (window icon, data folder, single-instance pipe,
autostart value, toast id, donor marker, staging prefix) is derived from here
so a merge between ``dev`` and ``main`` never flips the stable identity.
"""

from __future__ import annotations

import os

try:
    from _build_channel import CHANNEL as _BUILT_CHANNEL
except ImportError:
    _BUILT_CHANNEL = "stable"

CHANNEL = os.environ.get("FCP_CHANNEL", _BUILT_CHANNEL).strip().lower()
if CHANNEL not in {"stable", "dev"}:
    CHANNEL = "stable"

IS_DEV = CHANNEL == "dev"
SUFFIX = "Dev" if IS_DEV else ""
ICON_SUFFIX = "_DEV" if IS_DEV else ""

APP_FOLDER_NAME = f"FileConverterPro{SUFFIX}"
ICON_ICO = f"icon{ICON_SUFFIX}.ico"
ICON_PNG = f"icon{ICON_SUFFIX}.png"
SOCKET_NAME = f"FileConverterPro{SUFFIX}_SingleInstance"
DAEMON_RUN_VALUE = f"FileConverterProDaemon{SUFFIX}"
DONOR_FOLDER_NAME = f"FileConverterPro{SUFFIX}"
STAGING_PREFIX = f"fcp{SUFFIX.lower()}_"
TOAST_APP_ID = f"FileConverterPro{SUFFIX}.SystemNotifier"
