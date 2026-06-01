"""Modern Plotly visualizations for the operational dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.charts.base import render_plotly_panel


SEMANTIC_COLORS = {
	"critical": "#b91c1c",
	"high": "#ea580c",
	"moderate": "#d97706",
	"low": "#0284c7",
	"info": "#0f766e",
}


DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _empty_figure(title: str, message: str) -> go.Figure:
	"""Create a chart placeholder when a dataset is empty."""
	fig = go.Figure()
	fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="#475569"))
	fig.update_xaxes(visible=False)
	fig.update_yaxes(visible=False)
	fig.update_layout(title=title)
	return fig


def _numeric(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
	"""Return a numeric series or a safe default."""
	if column not in frame.columns:
		return pd.Series([default] * len(frame), index=frame.index, dtype=float)
	return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def _source_mask(frame: pd.DataFrame, source: str) -> pd.Series:
	"""Return a safe boolean source filter."""
	if "source" not in frame.columns:
		return pd.Series(False, index=frame.index)
	return frame["source"].eq(source)


def _geo_frame(frame: pd.DataFrame) -> pd.DataFrame:
	"""Return only rows with usable geographic coordinates."""
	if frame.empty:
		return frame.copy()
	columns = [column for column in ["latitude", "longitude"] if column in frame.columns]
	if not columns:
		return frame.head(0).copy()
	return frame.dropna(subset=columns).copy()


def _date_series(frame: pd.DataFrame) -> pd.Series:
	"""Return a normalized timestamp series for plotting."""
	if "timestamp" in frame.columns:
		return pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
	if "date" in frame.columns:
		return pd.to_datetime(frame["date"], utc=True, errors="coerce")
	return pd.Series(pd.NaT, index=frame.index)


def render_climate_time_series(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render a dual-line climate time series with hover and zoom."""
	if enriched_events.empty:
		render_plotly_panel(title="Serie temporal climatica", fig=_empty_figure("Serie temporal climatica", "Sem dados para o recorte atual."), key=key, help_text="Ajuste os filtros para carregar a evolucao temporal.", height=360)
		return
	frame = enriched_events.copy()
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	frame.loc[:, "risk_score"] = _numeric(frame, "risk_score")
	frame.loc[:, "severity"] = _numeric(frame, "severity")
	trend = (
		frame.groupby("date_bucket", as_index=False)
		.agg(avg_risk_score=("risk_score", "mean"), avg_severity=("severity", "mean"))
		.sort_values("date_bucket")
	)
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=trend["date_bucket"], y=trend["avg_risk_score"], mode="lines+markers", name="Risco medio", line=dict(color=SEMANTIC_COLORS["high"], width=3), hovertemplate="Data %{x|%d/%m/%Y}<br>Risco %{y:.2f}<extra></extra>"))
	fig.add_trace(go.Scatter(x=trend["date_bucket"], y=trend["avg_severity"], mode="lines+markers", name="Severidade media", line=dict(color=SEMANTIC_COLORS["info"], width=2, dash="dot"), hovertemplate="Data %{x|%d/%m/%Y}<br>Severidade %{y:.2f}<extra></extra>"))
	fig.update_layout(title="Evolucao temporal climatica", xaxis_title="Data", yaxis_title="Escala normalizada", hovermode="x unified", legend_title_text="")
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Serie temporal climatica", fig=fig, key=key, help_text="Comparacao entre risco medio e severidade ao longo do periodo selecionado.", height=360)


def render_climate_heatmap(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render a weekday/hour heatmap for climate intensity."""
	if enriched_events.empty:
		render_plotly_panel(title="Heatmap climatico", fig=_empty_figure("Heatmap climatico", "Sem dados para o recorte atual."), key=key, help_text="Ajuste os filtros para carregar o mapa de calor.", height=360)
		return
	frame = enriched_events.copy()
	frame = frame.drop(columns=["timestamp", "hour", "day_of_week"], errors="ignore")
	frame.loc[:, "timestamp"] = _date_series(frame)
	frame.loc[:, "hour"] = frame["timestamp"].dt.hour.fillna(0).astype("int64")
	frame.loc[:, "day_of_week"] = frame["timestamp"].dt.day_name()
	frame.loc[:, "risk_score"] = _numeric(frame, "risk_score")
	pivot = frame.pivot_table(index="day_of_week", columns="hour", values="risk_score", aggfunc="mean").reindex(DAY_ORDER).sort_index(axis=1)
	fig = go.Figure(data=go.Heatmap(z=pivot.values, x=[str(hour).zfill(2) for hour in pivot.columns], y=pivot.index.tolist(), colorscale=[[0.0, "#ecfeff"], [0.35, "#67e8f9"], [0.6, "#fbbf24"], [1.0, "#b91c1c"]], zmin=0, zmax=1, hovertemplate="Dia %{y}<br>Hora %{x}:00<br>Risco %{z:.2f}<extra></extra>"))
	fig.update_layout(title="Mapa de calor climatico", xaxis_title="Hora do dia", yaxis_title="Dia da semana")
	render_plotly_panel(title="Heatmap climatico", fig=fig, key=key, help_text="Leitura de intensidade por horario e dia da semana.", height=360)


def render_operational_bars(risk_summary: pd.DataFrame, *, key: str) -> None:
	"""Render a semantically colored bar chart by event type."""
	if risk_summary.empty:
		render_plotly_panel(title="Distribuicao de risco", fig=_empty_figure("Distribuicao de risco", "Sem eventos agregados no recorte atual."), key=key, help_text="Ajuste os filtros para carregar a distribuicao.", height=360)
		return
	fig = px.bar(risk_summary, x="event_type", y="avg_risk_score", color="alert_level" if "alert_level" in risk_summary.columns else None, color_discrete_map=SEMANTIC_COLORS, text=risk_summary["avg_risk_score"].map(lambda value: f"{float(value):.2f}"), labels={"event_type": "Tipo de evento", "avg_risk_score": "Risco medio"})
	fig.update_traces(textposition="outside", marker_line_color="rgba(15, 23, 42, 0.15)", marker_line_width=1)
	fig.update_layout(title="Distribuicao de risco por tipo de evento", xaxis_title="Tipo de evento", yaxis_title="Risco medio")
	render_plotly_panel(title="Distribuicao de risco", fig=fig, key=key, help_text="Comparativo operacional entre os principais tipos de evento.", height=360)


def render_operational_indicators(enriched_events: pd.DataFrame, alert_feed: pd.DataFrame, *, key: str) -> None:
	"""Render compact executive indicators with gauges and hover metadata."""
	if enriched_events.empty:
		render_plotly_panel(title="Indicadores", fig=_empty_figure("Indicadores", "Sem dados para indicadores."), key=key, help_text="Os indicadores aparecem quando ha dados suficientes.", height=260)
		return
	avg_risk = float(_numeric(enriched_events, "risk_score").mean()) if not enriched_events.empty else 0.0
	avg_confidence = float(_numeric(enriched_events, "confidence").mean()) if not enriched_events.empty else 0.0
	if "is_critical" in enriched_events.columns:
		critical_count = int(pd.to_numeric(enriched_events["is_critical"], errors="coerce").fillna(False).astype(int).sum())
	else:
		critical_count = int((_numeric(enriched_events, "risk_score") >= 0.85).sum())
	total_events = max(len(enriched_events), 1)
	fig = make_subplots(rows=1, cols=3, specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]], horizontal_spacing=0.08)
	fig.add_trace(go.Indicator(mode="gauge+number+delta", value=avg_risk, delta={"reference": 0.5}, title={"text": "Risco medio"}, gauge={"axis": {"range": [0, 1]}, "bar": {"color": SEMANTIC_COLORS["high"]}, "steps": [{"range": [0, 0.35], "color": "#eff6ff"}, {"range": [0.35, 0.75], "color": "#fef3c7"}, {"range": [0.75, 1.0], "color": "#fee2e2"}]}), row=1, col=1)
	fig.add_trace(go.Indicator(mode="gauge+number+delta", value=critical_count, delta={"reference": max(total_events * 0.1, 1)}, title={"text": "Eventos criticos"}, gauge={"axis": {"range": [0, total_events]}, "bar": {"color": SEMANTIC_COLORS["critical"]}, "steps": [{"range": [0, total_events * 0.5], "color": "#f8fafc"}, {"range": [total_events * 0.5, total_events], "color": "#fee2e2"}]}), row=1, col=2)
	fig.add_trace(go.Indicator(mode="gauge+number+delta", value=avg_confidence, delta={"reference": 0.7}, title={"text": "Confianca media"}, gauge={"axis": {"range": [0, 1]}, "bar": {"color": SEMANTIC_COLORS["info"]}, "steps": [{"range": [0, 0.5], "color": "#eff6ff"}, {"range": [0.5, 1.0], "color": "#dbeafe"}]}), row=1, col=3)
	fig.update_layout(title="Indicadores executivos", height=260, margin=dict(l=8, r=8, t=40, b=8))
	render_plotly_panel(title="Indicadores", fig=fig, key=key, help_text=f"{len(alert_feed)} alertas no feed atual.", height=260)


def render_geographic_risk_map(enriched_events: pd.DataFrame, *, key: str, title: str = "Mapa geográfico de risco", help_text: str = "Zoom, hover e densidade de eventos sensiveis no recorte atual.") -> None:
	"""Render an interactive geographic map of operational risk."""
	frame = _geo_frame(enriched_events)
	if frame.empty:
		render_plotly_panel(title=title, fig=_empty_figure(title, "Sem coordenadas geograficas no recorte atual."), key=key, help_text=help_text, height=360)
		return
	fig = px.scatter_map(frame, lat="latitude", lon="longitude", color="risk_score", size="risk_score", size_max=18, zoom=2, color_continuous_scale=[[0.0, "#0f766e"], [0.5, "#f59e0b"], [1.0, "#b91c1c"]], hover_name="event_type", hover_data={"region": True, "state": True, "risk_score": ":.2f", "confidence": ":.2f", "severity": ":.2f"})
	fig.update_layout(title=title, margin=dict(l=0, r=0, t=10, b=40), coloraxis_colorbar=dict(title="Risco"))
	render_plotly_panel(title=title, fig=fig, key=key, help_text=help_text, height=360, footer_gap_px=44)


def render_geospatial_heatmap(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render a density-based geographic heatmap."""
	frame = _geo_frame(enriched_events)
	if frame.empty:
		render_plotly_panel(title="Heatmap geografico", fig=_empty_figure("Heatmap geografico", "Sem coordenadas geograficas no recorte atual."), key=key, help_text="Ajuste o filtro de regiao ou periodo para obter pontos georreferenciados.", height=360)
		return
	fig = px.density_mapbox(frame, lat="latitude", lon="longitude", z=_numeric(frame, "risk_score"), radius=28, center=dict(lat=float(frame["latitude"].mean()), lon=float(frame["longitude"].mean())), zoom=2, mapbox_style="open-street-map", color_continuous_scale=[[0.0, "#ecfeff"], [0.4, "#67e8f9"], [0.7, "#f59e0b"], [1.0, "#b91c1c"]], hover_name="event_type", hover_data={"risk_score": ":.2f", "severity": ":.2f", "confidence": ":.2f"})
	fig.update_layout(title="Heatmap geografico de risco", margin=dict(l=0, r=0, t=10, b=40))
	render_plotly_panel(title="Heatmap geografico", fig=fig, key=key, help_text="Mapa de densidade geoespacial para identificar concentracoes de severidade.", height=360, footer_gap_px=44)


def render_scatter_geo(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render a world-map scatter plot with hover and zoom."""
	frame = _geo_frame(enriched_events)
	if frame.empty:
		render_plotly_panel(title="Scatter Geo", fig=_empty_figure("Scatter Geo", "Sem coordenadas geograficas no recorte atual."), key=key, help_text="Sem pontos geograficos suficientes para o scatter geo.", height=340)
		return
	fig = px.scatter_geo(frame, lat="latitude", lon="longitude", color="alert_level" if "alert_level" in frame.columns else None, size="risk_score", projection="natural earth", color_discrete_map=SEMANTIC_COLORS, hover_name="event_type", hover_data={"region": True, "state": True, "risk_score": ":.2f", "confidence": ":.2f"})
	fig.update_layout(title="Scatter Geo operacional", geo=dict(showland=True, landcolor="#f8fafc"))
	render_plotly_panel(title="Scatter Geo", fig=fig, key=key, help_text="Dispersao espacial com semantica de alerta e risco.", height=340, footer_gap_px=44)


def render_alert_spatial_distribution(alert_feed: pd.DataFrame, enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render the spatial distribution of alerts by joining coordinates from the event stream."""
	if alert_feed.empty:
		render_plotly_panel(title="Distribuicao espacial de alertas", fig=_empty_figure("Distribuicao espacial de alertas", "Sem alertas no recorte atual."), key=key, help_text="O feed atual nao possui alertas para distribuir no mapa.", height=340)
		return
	coords_columns = [column for column in ["event_id", "latitude", "longitude", "risk_score", "alert_level", "region", "state", "event_type"] if column in enriched_events.columns]
	coords = enriched_events[coords_columns].drop_duplicates(subset=["event_id"]) if coords_columns and not enriched_events.empty else enriched_events.head(0).copy()
	merged = alert_feed.merge(coords, on="event_id", how="left", suffixes=("_alert", "_event"))
	merged = _geo_frame(merged)
	if merged.empty:
		render_plotly_panel(title="Distribuicao espacial de alertas", fig=_empty_figure("Distribuicao espacial de alertas", "Os alertas nao possuem coordenadas suficientes."), key=key, help_text="As coordenadas vem do dataset consolidado de eventos.", height=340)
		return
	display_event_type = "event_type_alert" if "event_type_alert" in merged.columns else "event_type_event" if "event_type_event" in merged.columns else None
	display_alert_level = "alert_level_alert" if "alert_level_alert" in merged.columns else "alert_level_event" if "alert_level_event" in merged.columns else None
	display_risk_score = "risk_score_alert" if "risk_score_alert" in merged.columns else "risk_score_event" if "risk_score_event" in merged.columns else None
	display_region = "region_alert" if "region_alert" in merged.columns else "region_event" if "region_event" in merged.columns else None
	display_state = "state_alert" if "state_alert" in merged.columns else "state_event" if "state_event" in merged.columns else None
	hover_data: dict[str, object] = {}
	if display_region:
		hover_data[display_region] = True
	if display_state:
		hover_data[display_state] = True
	if display_risk_score:
		hover_data[display_risk_score] = ":.2f"
	fig = px.scatter_map(
		merged,
		lat="latitude",
		lon="longitude",
		color=display_alert_level,
		size=display_risk_score,
		size_max=18,
		zoom=2,
		color_discrete_map=SEMANTIC_COLORS,
		hover_name=display_event_type,
		hover_data=hover_data,
	)
	fig.update_layout(title="Distribuicao espacial de alertas", margin=dict(l=0, r=0, t=10, b=40))
	render_plotly_panel(title="Distribuicao espacial de alertas", fig=fig, key=key, help_text="Cada ponto mostra a localizacao do alerta e seu nivel semantico.", height=340, footer_gap_px=44)


def render_temporal_disaster_evolution(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render stacked temporal evolution of disasters by type."""
	if enriched_events.empty:
		render_plotly_panel(title="Evolucao temporal de desastres", fig=_empty_figure("Evolucao temporal de desastres", "Sem dados para a evolucao temporal."), key=key, help_text="Ajuste o recorte temporal para visualizar a evolucao.", height=360)
		return
	frame = enriched_events.copy()
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	counts = frame.groupby(["date_bucket", "event_type"], as_index=False).agg(total_events=("event_id", "count"))
	fig = px.area(counts, x="date_bucket", y="total_events", color="event_type", labels={"date_bucket": "Data", "total_events": "Eventos"}, color_discrete_sequence=["#0f766e", "#0284c7", "#f59e0b", "#ea580c", "#b91c1c"])
	fig.update_layout(title="Evolucao temporal de desastres", hovermode="x unified", legend_title_text="Tipo de evento")
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Evolucao temporal de desastres", fig=fig, key=key, help_text="Comparacao da frequencia de eventos por classe ao longo do tempo.", height=360)


def render_risk_distribution(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render the distribution of risk scores."""
	if enriched_events.empty:
		render_plotly_panel(title="Distribuicao de risco", fig=_empty_figure("Distribuicao de risco", "Sem dados para a distribuicao."), key=key, help_text="Ajuste os filtros para carregar a distribuicao de risco.", height=340)
		return
	frame = enriched_events.copy()
	frame.loc[:, "risk_score"] = _numeric(frame, "risk_score")
	fig = px.histogram(frame, x="risk_score", color="alert_level" if "alert_level" in frame.columns else None, nbins=24, color_discrete_map=SEMANTIC_COLORS, labels={"risk_score": "Risco"})
	fig.update_layout(title="Distribuicao de risco", hovermode="x")
	render_plotly_panel(title="Distribuicao de risco", fig=fig, key=key, help_text="Histograma semantico dos escores de risco do recorte atual.", height=340)


def render_rainfall_accumulation(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render rainfall accumulation with cumulative and daily components."""
	if enriched_events.empty:
		render_plotly_panel(title="Acumulado de chuva", fig=_empty_figure("Acumulado de chuva", "Sem registros de precipitacao no recorte atual."), key=key, help_text="A serie acumulada depende de eventos com precipitacao.", height=360)
		return
	frame = enriched_events.copy()
	frame = frame.loc[_numeric(frame, "precipitation_mm") > 0].copy()
	if frame.empty:
		render_plotly_panel(title="Acumulado de chuva", fig=_empty_figure("Acumulado de chuva", "Sem registros de precipitacao no recorte atual."), key=key, help_text="A serie acumulada depende de eventos com precipitacao.", height=360)
		return
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	daily = frame.groupby("date_bucket", as_index=False).agg(daily_rainfall=("precipitation_mm", "sum"), avg_temperature=("temperature_c", "mean")).sort_values("date_bucket")
	daily.loc[:, "cumulative_rainfall"] = daily["daily_rainfall"].cumsum()
	fig = make_subplots(specs=[[{"secondary_y": True}]])
	fig.add_trace(go.Bar(x=daily["date_bucket"], y=daily["daily_rainfall"], name="Chuva diaria", marker_color="#0ea5e9", hovertemplate="Data %{x|%d/%m/%Y}<br>Chuva diaria %{y:.1f} mm<extra></extra>"), secondary_y=False)
	fig.add_trace(go.Scatter(x=daily["date_bucket"], y=daily["cumulative_rainfall"], name="Acumulado", mode="lines+markers", line=dict(color="#0f766e", width=3), hovertemplate="Data %{x|%d/%m/%Y}<br>Acumulado %{y:.1f} mm<extra></extra>"), secondary_y=True)
	fig.update_layout(title="Acumulado de chuva", hovermode="x unified", legend_title_text="")
	fig.update_yaxes(title_text="Chuva diaria (mm)", secondary_y=False)
	fig.update_yaxes(title_text="Acumulado (mm)", secondary_y=True)
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Acumulado de chuva", fig=fig, key=key, help_text="Barras mostram a chuva diaria e a linha mostra o acumulado do periodo.", height=360)


def render_fire_intensity(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render wildfire intensity across time and brightness."""
	if enriched_events.empty:
		render_plotly_panel(title="Intensidade de queimadas", fig=_empty_figure("Intensidade de queimadas", "Sem registros de queimadas no recorte atual."), key=key, help_text="Os dados de fogo aparecem quando o recorte inclui a origem fire.", height=360)
		return
	frame = enriched_events.loc[_source_mask(enriched_events, "fire")].copy()
	if frame.empty:
		render_plotly_panel(title="Intensidade de queimadas", fig=_empty_figure("Intensidade de queimadas", "Sem registros de queimadas no recorte atual."), key=key, help_text="Os dados de fogo aparecem quando o recorte inclui a origem fire.", height=360)
		return
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	fire_trend = frame.groupby("date_bucket", as_index=False).agg(avg_brightness=("brightness", "mean"), avg_risk=("risk_score", "mean"), total_fires=("event_id", "count")).sort_values("date_bucket")
	fig = make_subplots(specs=[[{"secondary_y": True}]])
	fig.add_trace(go.Bar(x=fire_trend["date_bucket"], y=fire_trend["total_fires"], name="Focos", marker_color="#ea580c", hovertemplate="Data %{x|%d/%m/%Y}<br>Focos %{y}<extra></extra>"), secondary_y=False)
	fig.add_trace(go.Scatter(x=fire_trend["date_bucket"], y=fire_trend["avg_brightness"], name="Brightness media", mode="lines+markers", line=dict(color="#b91c1c", width=3), hovertemplate="Data %{x|%d/%m/%Y}<br>Brightness %{y:.1f}<extra></extra>"), secondary_y=True)
	fig.update_layout(title="Intensidade de queimadas", hovermode="x unified", legend_title_text="")
	fig.update_yaxes(title_text="Focos", secondary_y=False)
	fig.update_yaxes(title_text="Brightness media", secondary_y=True)
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Intensidade de queimadas", fig=fig, key=key, help_text="Barras e linha mostram a pressao operacional de queimadas ao longo do tempo.", height=360)


def render_air_quality_index(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render the AQI evolution with semantic thresholds."""
	if enriched_events.empty:
		render_plotly_panel(title="Indice de qualidade do ar", fig=_empty_figure("Indice de qualidade do ar", "Sem medições de AQI no recorte atual."), key=key, help_text="A serie de qualidade do ar depende do dataset air_quality.", height=360)
		return
	frame = enriched_events.loc[_source_mask(enriched_events, "air_quality")].copy()
	if frame.empty:
		render_plotly_panel(title="Indice de qualidade do ar", fig=_empty_figure("Indice de qualidade do ar", "Sem medições de AQI no recorte atual."), key=key, help_text="A serie de qualidade do ar depende do dataset air_quality.", height=360)
		return
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	aqi = frame.groupby("date_bucket", as_index=False).agg(avg_aqi=("aqi", "mean"), avg_risk=("risk_score", "mean"), total_samples=("event_id", "count")).sort_values("date_bucket")
	fig = px.line(aqi, x="date_bucket", y=["avg_aqi", "avg_risk"], markers=True, labels={"value": "Indice", "date_bucket": "Data", "variable": "Serie"}, color_discrete_sequence=["#b91c1c", "#0284c7"])
	fig.update_layout(title="Indice de qualidade do ar", hovermode="x unified", legend_title_text="")
	for threshold, color in [(50, "#22c55e"), (100, "#f59e0b"), (150, "#f97316"), (200, "#dc2626")]:
		fig.add_hline(y=threshold, line_width=1, line_dash="dot", line_color=color)
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Indice de qualidade do ar", fig=fig, key=key, help_text="A linha do AQI mostra a progressao da qualidade do ar com faixas semanticas de referencia.", height=360)


def render_flood_forecast(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render a flood forecast style trend based on predicted flood probability."""
	if enriched_events.empty or "flood_risk_probability" not in enriched_events.columns:
		render_plotly_panel(title="Previsao de enchentes", fig=_empty_figure("Previsao de enchentes", "Sem sinais suficientes para a previsao de enchentes."), key=key, help_text="A previsao depende do indicador flood_risk_probability.", height=360)
		return
	frame = enriched_events.copy()
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	trend = frame.groupby("date_bucket", as_index=False).agg(avg_flood_risk=("flood_risk_probability", "mean"), avg_risk=("risk_score", "mean"), total_events=("event_id", "count")).sort_values("date_bucket")
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=trend["date_bucket"], y=trend["avg_flood_risk"], name="Risco de enchente", mode="lines+markers", fill="tozeroy", line=dict(color="#0284c7", width=3), hovertemplate="Data %{x|%d/%m/%Y}<br>Risco %{y:.2f}<extra></extra>"))
	fig.add_trace(go.Scatter(x=trend["date_bucket"], y=trend["avg_risk"], name="Risco operacional", mode="lines", line=dict(color="#b91c1c", width=2, dash="dot"), hovertemplate="Data %{x|%d/%m/%Y}<br>Risco operacional %{y:.2f}<extra></extra>"))
	fig.update_layout(title="Previsao de enchentes", hovermode="x unified", legend_title_text="")
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Previsao de enchentes", fig=fig, key=key, help_text="Serie de previsao com leitura operacional e risco hidrologico estimado.", height=360)


def render_landslide_forecast(enriched_events: pd.DataFrame, *, key: str) -> None:
	"""Render a landslide forecast style trend based on predicted landslide probability."""
	if enriched_events.empty or "landslide_risk_probability" not in enriched_events.columns:
		render_plotly_panel(title="Previsao de deslizamentos", fig=_empty_figure("Previsao de deslizamentos", "Sem sinais suficientes para a previsao de deslizamentos."), key=key, help_text="A previsao depende do indicador landslide_risk_probability.", height=360)
		return
	frame = enriched_events.copy()
	frame.loc[:, "date_bucket"] = _date_series(frame).dt.floor("D")
	trend = frame.groupby("date_bucket", as_index=False).agg(avg_landslide_risk=("landslide_risk_probability", "mean"), avg_precipitation=("precipitation_mm", "mean"), avg_risk=("risk_score", "mean")).sort_values("date_bucket")
	fig = make_subplots(specs=[[{"secondary_y": True}]])
	fig.add_trace(go.Scatter(x=trend["date_bucket"], y=trend["avg_landslide_risk"], name="Risco de deslizamento", mode="lines+markers", fill="tozeroy", line=dict(color="#7c3aed", width=3), hovertemplate="Data %{x|%d/%m/%Y}<br>Risco %{y:.2f}<extra></extra>"), secondary_y=False)
	fig.add_trace(go.Bar(x=trend["date_bucket"], y=trend["avg_precipitation"], name="Chuva media", marker_color="#0ea5e9", opacity=0.45, hovertemplate="Data %{x|%d/%m/%Y}<br>Chuva %{y:.1f} mm<extra></extra>"), secondary_y=True)
	fig.update_layout(title="Previsao de deslizamentos", hovermode="x unified", legend_title_text="")
	fig.update_yaxes(title_text="Risco de deslizamento", secondary_y=False)
	fig.update_yaxes(title_text="Precipitacao media (mm)", secondary_y=True)
	fig.update_xaxes(rangeslider_visible=True)
	render_plotly_panel(title="Previsao de deslizamentos", fig=fig, key=key, help_text="Acompanhe o aumento do risco junto do acumulado de chuva.", height=360)
