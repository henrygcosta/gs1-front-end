"""Application header components."""

from __future__ import annotations

import streamlit as st

from ui.copy.labels import APP_SUBTITLE, APP_TITLE


def render_header(*, title: str = APP_TITLE, subtitle: str = APP_SUBTITLE, eyebrow: str = "Centro de Operacoes") -> None:
	"""Render a compact branded page header.

	Parameters
	----------
	title:
		Primary page title.
	subtitle:
		Secondary line used to frame the current operational context.
	eyebrow:
		Small overline used to anchor the brand.
	"""
	st.markdown(
		f"""
		<div class="gs-hero" style="display:flex;gap:1rem;align-items:center;">
			<div style="width:64px;height:64px;flex:0 0 64px;border-radius:16px;background:linear-gradient(145deg,#0F4C5C,#2E7D32);display:flex;align-items:center;justify-content:center;box-shadow:0 10px 24px rgba(15,76,92,.22);">
				<span style="color:#fff;font-weight:800;font-size:1.05rem;letter-spacing:0.08em;">GS</span>
			</div>
			<div>
				<div class="gs-eyebrow">{eyebrow}</div>
				<div class="gs-title">{title}</div>
				<div class="gs-subtitle">{subtitle}</div>
			</div>
		</div>
		""",
		unsafe_allow_html=True,
	)
