"""Smoke tests for the top-level application entrypoint."""

from __future__ import annotations

import app


def test_app_main_invokes_shell_and_configuration(monkeypatch) -> None:
	called = {"set_page_config": False, "shell": False, "styles": False, "init": False}

	def fake_set_page_config(**kwargs) -> None:
		called["set_page_config"] = True
		assert kwargs["layout"] == "wide"

	monkeypatch.setattr(app.st, "set_page_config", fake_set_page_config)
	monkeypatch.setattr(app, "apply_global_styles", lambda: called.__setitem__("styles", True))
	monkeypatch.setattr(app, "initialize_session_state", lambda: called.__setitem__("init", True))
	monkeypatch.setattr(app, "render_app_shell", lambda: called.__setitem__("shell", True))

	app.main()

	assert all(called.values())
