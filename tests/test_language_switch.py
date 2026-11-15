"""Regression tests for language switching across menu and settings entry points."""

from dialogs.settings_dialog import SettingsDialog


def _menu_titles(window):
    return [action.text() for action in window.menuBar().actions()]


def test_settings_language_switch_updates_menu_bar(app, qapp):
    app.apply_language("fr")
    dialog = SettingsDialog(app.config, app, "fr")
    try:
        dialog._apply_language("en")
        qapp.processEvents()

        assert _menu_titles(app)[:4] == [
            app.translate_text("file"),
            app.translate_text("edit"),
            app.translate_text("view"),
            app.translate_text("help"),
        ]
        assert app.language_action.text() == app._get_language_label("en")
    finally:
        dialog.deleteLater()
        qapp.processEvents()
        app.apply_language("fr")
