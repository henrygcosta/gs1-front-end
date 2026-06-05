"""Main application shell composition."""

from __future__ import annotations

from ui.components.footer import render_footer
from ui.components.header import render_header
from ui.copy.labels import APP_SUBTITLE, APP_TITLE
from ui.layout.sidebar import render_sidebar
from ui.layout.tabs import render_main_tabs
from ui.pages.anomalies_page import render_anomalies_page
from ui.pages.dashboard_page import render_dashboard_page
from ui.pages.feedback_page import render_feedback_page
from ui.pages.hotspots_page import render_hotspots_page


def render_app_shell() -> None:
	"""Render the top-level dashboard shell and route tab content."""
	render_header(title=APP_TITLE, subtitle=APP_SUBTITLE)

	render_sidebar()

	overview_tab, hotspots_tab, anomalies_tab, feedback_tab = render_main_tabs()

	with overview_tab:
		render_dashboard_page()
	with hotspots_tab:
		render_hotspots_page()
	with anomalies_tab:
		render_anomalies_page()
	with feedback_tab:
		render_feedback_page()

	render_footer(left_text="Centro de Operacoes Ambientais", right_text="Streamlit | Clean Architecture | State-driven UI")
