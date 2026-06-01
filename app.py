"""Entry point for the climate risk intelligence dashboard."""

from __future__ import annotations

import streamlit as st

from state.initializer import initialize_session_state
from ui.layout.shell import render_app_shell
from ui.theme.styles import apply_global_styles
from utils.config import get_settings
from utils.logger import get_logger


def main() -> None:
	"""Run the Streamlit application."""
	settings = get_settings()

	st.set_page_config(
		page_title=settings.app_title,
		page_icon=settings.page_icon,
		layout="wide",
		initial_sidebar_state="expanded",
	)

	initialize_session_state()
	apply_global_styles()

	logger = get_logger(__name__)
	logger.info("Application initialized")

	render_app_shell()


if __name__ == "__main__":
	main()
