"""Global style injection for Streamlit UI customization."""

from __future__ import annotations

import streamlit as st

from state.selectors import get_preferences_state
from ui.theme.tokens import COLORS


def apply_global_styles() -> None:
	"""Inject a concise CSS layer for visual consistency and hierarchy."""
	preferences = get_preferences_state()
	theme_mode = preferences.theme_mode.lower()
	is_dark = theme_mode == "dark"
	background = "#08111F" if is_dark else COLORS.background
	surface = "#111827" if is_dark else COLORS.surface
	text_primary = "#F4F7FB" if is_dark else COLORS.text_primary
	text_secondary = "#B7C0D1" if is_dark else COLORS.text_secondary
	border = "rgba(148, 163, 184, 0.22)" if is_dark else "#E2E8F0"
	card_bg = "rgba(15, 23, 42, 0.70)" if is_dark else "rgba(255, 255, 255, 0.94)"
	input_bg = "rgba(15, 23, 42, 0.62)" if is_dark else "rgba(255, 255, 255, 0.92)"
	tab_bg = "rgba(15, 23, 42, 0.42)" if is_dark else "rgba(248, 250, 252, 0.92)"
	hover_bg = "rgba(59, 130, 246, 0.12)" if is_dark else "rgba(15, 118, 92, 0.08)"
	header_shadow = "0 18px 44px rgba(0, 0, 0, 0.18)" if is_dark else "0 18px 40px rgba(15, 23, 42, 0.06)"
	card_shadow = "0 14px 28px rgba(0, 0, 0, 0.16)" if is_dark else "0 16px 34px rgba(15, 23, 42, 0.06)"
	app_gradient = (
		"radial-gradient(circle at top right, rgba(14, 165, 233, 0.08) 0%, transparent 24%),"
		"radial-gradient(circle at bottom left, rgba(34, 197, 94, 0.06) 0%, transparent 22%),"
		f"linear-gradient(180deg, {('#0C1526' if is_dark else '#FAFBFC')} 0%, {background} 100%)"
	)
	container_padding = "1.6rem 2.4rem 2.2rem 2.4rem"
	panel_padding = "1rem"
	card_padding = "1rem 1.1rem"
	card_margin = "0.85rem"
	font_scale = "1"
	st.markdown(
		f"""
		<style>
			@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

			:root {{
				--gs-background: {background};
				--gs-surface: {surface};
				--gs-card-bg: {card_bg};
				--gs-input-bg: {input_bg};
				--gs-tab-bg: {tab_bg};
				--gs-hover-bg: {hover_bg};
				--gs-border: {border};
				--gs-text-primary: {text_primary};
				--gs-text-secondary: {text_secondary};
				--gs-placeholder: {('rgba(148, 163, 184, 0.24)' if is_dark else 'rgba(148, 163, 184, 0.18)')};
				--gs-placeholder-strong: {('rgba(148, 163, 184, 0.42)' if is_dark else 'rgba(203, 213, 225, 0.88)')};
			}}

			.stApp {{
				background: {app_gradient};
				font-family: 'Manrope', 'Aptos', 'Segoe UI', sans-serif;
				color: {text_primary};
			}}
			header[data-testid='stHeader'],
			div[data-testid='stToolbar'],
			div[data-testid='stDecoration'] {{
				background: transparent;
				color: {text_primary};
			}}
			header[data-testid='stHeader'] {{
				border: 0;
			}}
			.block-container {{
				padding: {container_padding};
				max-width: 1500px;
			}}
			section[data-testid='stSidebar'] {{
				background: linear-gradient(180deg, {('#0C1526' if is_dark else '#FFFFFF')} 0%, {('#101A2E' if is_dark else '#F4F7FA')} 100%);
				border-right: 1px solid {border};
				color: {text_primary};
			}}
			section[data-testid='stSidebar'] * {{
				color: {text_primary};
			}}
			section[data-testid='stSidebar'] .block-container {{
				padding-top: 1.25rem;
				padding-bottom: 1.5rem;
			}}
			section[data-testid='stSidebar'] .block-container > div:first-child {{
				margin-bottom: 0.75rem;
			}}
			[data-testid='stForm'] {{
				background: {input_bg};
				backdrop-filter: blur(14px);
				border: 1px solid {border};
				border-radius: 16px;
				padding: {panel_padding};
				box-shadow: {header_shadow};
			}}
			.gs-title {{
				color: {text_primary};
				font-size: clamp(1.7rem, 2.4vw, 2.6rem);
				font-weight: 800;
				letter-spacing: -0.04em;
				margin-bottom: 0.35rem;
			}}
			.gs-eyebrow {{
				color: {COLORS.brand_primary};
				text-transform: uppercase;
				letter-spacing: 0.18em;
				font-size: 0.72rem;
				font-weight: 700;
				margin-bottom: 0.45rem;
			}}
			.gs-subtitle {{
				color: {text_secondary};
				max-width: 70ch;
				margin-bottom: 1rem;
				font-size: 0.96rem;
			}}
			.gs-panel {{
				background-color: {surface};
				border: 1px solid {border};
				border-radius: 16px;
				padding: {card_padding};
				box-shadow: {card_shadow};
			}}
			.gs-card {{
				background: var(--gs-card-bg);
				border: 1px solid {border};
				border-radius: 16px;
				padding: {card_padding};
				box-shadow: {card_shadow};
				margin-bottom: {card_margin};
			}}
			.gs-card-title {{
				color: {text_primary};
				font-size: 0.98rem;
				font-weight: 700;
				margin-bottom: 0.35rem;
			}}
			.gs-card-copy {{
				color: {text_secondary};
				font-size: 0.92rem;
				line-height: 1.5;
			}}
			.gs-hero {{
				padding: 0.15rem 0 0.75rem 0;
			}}
			.gs-badge {{
				display: inline-flex;
				align-items: center;
				justify-content: center;
				padding: 0.38rem 0.7rem;
				border-radius: 999px;
				border: 1px solid color-mix(in srgb, var(--gs-badge-color) 30%, var(--gs-surface));
				background: color-mix(in srgb, var(--gs-badge-color) 12%, var(--gs-surface));
				color: var(--gs-badge-color);
				font-size: 0.78rem;
				font-weight: 700;
				text-transform: uppercase;
				letter-spacing: 0.08em;
			}}
			.gs-banner {{
				border-left: 4px solid var(--gs-banner-accent);
				background: linear-gradient(90deg, color-mix(in srgb, var(--gs-banner-accent) 10%, {('#0E1728' if is_dark else '#ffffff')}), {('#0E1728' if is_dark else '#ffffff')});
				border-radius: 16px;
				padding: {panel_padding};
				margin: 0.5rem 0 0.85rem 0;
			}}
			.gs-banner-title {{
				font-weight: 800;
				color: {text_primary};
				margin-bottom: 0.25rem;
			}}
			.gs-banner-message {{
				color: {text_secondary};
				font-size: 0.93rem;
			}}
			.gs-footer {{
				display: flex;
				justify-content: space-between;
				gap: 1rem;
				padding: 1rem 0 0.25rem 0;
				color: {text_secondary};
				font-size: 0.84rem;
				border-top: 1px solid {border};
				margin-top: 1rem;
			}}
			.gs-chart-card {{
				padding-bottom: 0.35rem;
			}}
			.gs-chart-spacer {{
				height: 1rem;
			}}
			body {{
				font-size: {font_scale}rem;
			}}
			button[kind='primary'] {{
				border-radius: 12px;
			}}
			.stButton > button {{
				border-radius: 10px;
			}}
			button[data-testid^='stBaseButton-'],
			.stButton > button,
			button[kind='secondary'],
			button[kind='primary'] {{
				background-color: {('rgba(15, 23, 42, 0.80)' if is_dark else 'rgba(248, 250, 252, 0.98)')} !important;
				color: {text_primary} !important;
				border: 1px solid {border} !important;
				box-shadow: none !important;
			}}
			button[data-testid^='stBaseButton-']:hover,
			.stButton > button:hover,
			button[kind='secondary']:hover,
			button[kind='primary']:hover {{
				background-color: {('rgba(30, 41, 59, 0.94)' if is_dark else 'rgba(241, 245, 249, 1)')} !important;
				border-color: color-mix(in srgb, var(--gs-border) 40%, #60A5FA) !important;
			}}
			button[data-testid^='stBaseButton-'] p,
			.stButton > button p {{
				color: {text_primary} !important;
				margin: 0 !important;
			}}
			button[data-testid^='stBaseButton-'] span,
			.stButton > button span {{
				color: {text_primary} !important;
			}}
			[data-testid='stCheckbox'] label,
			[data-testid='stCheckbox'] p,
			[data-testid='stCheckbox'] span,
			[data-testid='stToggle'] label,
			[data-testid='stToggle'] p,
			[data-testid='stToggle'] span {{
				color: {text_primary} !important;
			}}
			button[data-testid='stBaseButton-header'],
			button[data-testid='stBaseButton-headerNoPadding'] {{
				background-color: {('rgba(15, 23, 42, 0.80)' if is_dark else 'rgba(248, 250, 252, 0.98)')} !important;
				color: {text_primary} !important;
				border: 1px solid {border} !important;
				border-radius: 12px !important;
			}}
			button[data-testid='stBaseButton-header'] p,
			button[data-testid='stBaseButton-headerNoPadding'] p {{
				color: {text_primary} !important;
			}}
			button[data-testid='stBaseButton-header'] svg,
			button[data-testid='stBaseButton-headerNoPadding'] svg {{
				fill: currentColor !important;
			}}
			a, button {{
				transition: transform 120ms ease, background-color 120ms ease, border-color 120ms ease, color 120ms ease;
			}}
			a:hover, button:hover {{
				background-color: {hover_bg};
			}}
			div[data-baseweb='tab-list'] {{
				gap: 0.35rem;
				border-bottom: 1px solid {border};
			}}
			.stTabs [data-baseweb='tab-list'] button[data-baseweb='tab'],
			.stTabs [data-baseweb='tab-list'] button[data-baseweb='tab'] *,
			div[data-baseweb='tab'] {{
				background: {('rgba(15, 23, 42, 0.82)' if is_dark else tab_bg)};
				border: 1px solid transparent;
				border-radius: 999px;
				padding: 0.45rem 0.9rem;
				color: {text_secondary} !important;
				font-weight: 700;
				-webkit-text-fill-color: {text_secondary} !important;
			}}
			.stTabs [data-baseweb='tab-list'] button[data-baseweb='tab']:hover,
			.stTabs [data-baseweb='tab-list'] button[data-baseweb='tab']:hover * {{
				color: {text_primary} !important;
				-webkit-text-fill-color: {text_primary} !important;
				background: transparent;
				border-color: transparent;
			}}
			button[data-baseweb='tab'][aria-selected='true'],
			button[data-baseweb='tab'][aria-selected='true'] *,
			div[data-baseweb='tab'][aria-selected='true'],
			.stTabs [aria-selected='true'] {{
				background: {('rgba(14, 165, 233, 0.18)' if is_dark else 'rgba(15, 118, 92, 0.10)')};
				color: {text_primary} !important;
				-webkit-text-fill-color: {text_primary} !important;
				border-color: {border};
			}}
			.js-plotly-plot .gtitle {{
				display: none !important;
			}}
			.stTabs [aria-selected='true'] * {{
				color: {text_primary} !important;
				-webkit-text-fill-color: {text_primary} !important;
			}}
			section[data-testid='stSidebar'] .stSelectbox,
			section[data-testid='stSidebar'] .stCheckbox,
			section[data-testid='stSidebar'] .stSlider,
			section[data-testid='stSidebar'] .stMultiSelect {{
				margin-bottom: 0.55rem;
			}}
			[data-testid='stSidebar'] [data-baseweb='select'] > div,
			[data-testid='stSidebar'] [data-baseweb='base-input'] {{
				background: var(--gs-input-bg);
				border-color: var(--gs-border);
				color: var(--gs-text-primary);
			}}
			[data-testid='stSidebar'] [data-baseweb='select'] * {{
				color: var(--gs-text-primary);
			}}
			[data-testid='stSidebar'] [data-baseweb='select'] > div:hover,
			[data-testid='stSidebar'] [data-baseweb='base-input']:hover {{
				border-color: color-mix(in srgb, var(--gs-border) 40%, #60A5FA);
				background: color-mix(in srgb, var(--gs-input-bg) 88%, var(--gs-hover-bg));
			}}
			section[data-testid='stSidebar'] input,
			section[data-testid='stSidebar'] textarea {{
				color: var(--gs-text-primary);
			}}
			[data-testid='stMetric'] {{
				background: var(--gs-card-bg);
				border: 1px solid {border};
				border-radius: 16px;
				padding: 0.85rem 1rem;
				box-shadow: {card_shadow};
			}}
			[data-testid='stMetric'] * {{
				color: var(--gs-text-primary);
			}}
			[data-testid='stMetricLabel'] p,
			[data-testid='stMetricDelta'] {{
				color: {text_secondary};
			}}
			[data-testid='stAlert'] {{
				background: var(--gs-card-bg);
				border: 1px solid {border};
				color: {text_primary};
				border-radius: 16px;
				box-shadow: {card_shadow};
			}}
			[data-testid='stAlert'] * {{
				color: {text_primary};
			}}
			[data-testid='stAlert'] p {{
				color: {text_primary};
			}}
			button[data-testid^='stBaseButton-']:not([kind='headerNoPadding']) {{
				background-color: {('rgba(15, 23, 42, 0.80)' if is_dark else 'rgba(248, 250, 252, 0.98)')} !important;
				color: {text_primary} !important;
				border: 1px solid {border} !important;
				border-radius: 12px !important;
				box-shadow: none !important;
			}}
			button[data-testid^='stBaseButton-']:not([kind='headerNoPadding']):hover {{
				background-color: {('rgba(30, 41, 59, 0.94)' if is_dark else 'rgba(241, 245, 249, 1)')} !important;
				border-color: color-mix(in srgb, var(--gs-border) 40%, #60A5FA) !important;
			}}
			button[data-testid^='stBaseButton-']:not([kind='headerNoPadding']) p {{
				color: {text_primary} !important;
				margin: 0 !important;
			}}
			button[data-testid^='stBaseButton-']:not([kind='headerNoPadding']) svg {{
				fill: currentColor !important;
			}}
			[data-testid='stSidebar'] button[data-testid='stBaseButton-secondary'],
			[data-testid='stSidebar'] button[data-testid='stBaseButton-secondaryFormSubmit'] {{
				all: unset !important;
				display: inline-flex !important;
				align-items: center !important;
				justify-content: center !important;
				gap: 0.35rem !important;
				width: 100% !important;
				box-sizing: border-box !important;
				padding: 0.72rem 0.95rem !important;
				border-radius: 12px !important;
				background-color: {('rgba(15, 23, 42, 0.80)' if is_dark else 'rgba(248, 250, 252, 0.98)')} !important;
				color: {text_primary} !important;
				border: 1px solid {border} !important;
				cursor: pointer !important;
				font: inherit !important;
				font-weight: 700 !important;
				line-height: 1.2 !important;
				text-align: center !important;
				text-decoration: none !important;
				box-shadow: none !important;
			}}
			.js-plotly-plot .legendtext,
			.js-plotly-plot .legendtitletext,
			.js-plotly-plot g.legend text {{
				fill: {text_primary} !important;
				color: {text_primary} !important;
			}}
			[data-testid='stPlotlyChart'] {{
				margin-bottom: 0;
			}}
			[data-testid='stPlotlyChart'] .js-plotly-plot {{
				margin-bottom: 0;
			}}
			.js-plotly-plot .mapboxgl-ctrl-attrib,
			.js-plotly-plot .mapboxgl-ctrl-attrib a,
			.js-plotly-plot .mapboxgl-ctrl-attrib-button,
			.js-plotly-plot .mapboxgl-ctrl-logo {{
				font-size: 0.72rem !important;
				line-height: 1.1 !important;
				color: {text_secondary} !important;
			}}
			.js-plotly-plot .mapboxgl-ctrl-attrib {{
				background: {('rgba(15, 23, 42, 0.72)' if is_dark else 'rgba(255, 255, 255, 0.84)')} !important;
				padding: 0.15rem 0.4rem !important;
				border-radius: 8px !important;
			}}
			.js-plotly-plot .mapboxgl-ctrl-bottom-right {{
				margin-bottom: 0.25rem !important;
				margin-right: 0.25rem !important;
			}}
			.js-plotly-plot g.legend rect.bg {{
				fill: {('rgba(15, 23, 42, 0.78)' if is_dark else 'rgba(255, 255, 255, 0.82)')} !important;
				stroke: {border} !important;
			}}
		</style>
		""",
		unsafe_allow_html=True,
	)

	# Load optional custom CSS file from assets/custom.css to allow local tweaks
	try:
		with open("assets/custom.css", encoding="utf-8") as fh:
			custom_css = fh.read()
			if custom_css.strip():
				st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)
	except Exception:
		# ignore missing or unreadable custom CSS
		pass
