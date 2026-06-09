"""Feedback center page for human-in-the-loop interactions."""

from __future__ import annotations

import streamlit as st

from features.human_feedback.use_cases import execute_human_feedback
from state.actions import record_alert_moderation
from state.selectors import (
	get_approved_alerts,
	get_dismissed_alerts,
	get_feedback_history,
	get_feedback_revision,
	get_loading_flags,
	get_reviewed_alerts,
	get_sent_alerts,
)
from state.view_model import build_dashboard_filter_view_model
from ui.charts import (
	render_alert_spatial_distribution,
	render_operational_bars,
	render_operational_indicators,
)
from ui.components.alert_card import render_alert_card
from ui.components.empty_state import render_empty_state
from ui.components.loading_block import render_loading_placeholder
from ui.components.notification_banner import render_notification_banner
from ui.components.status_badge import render_status_badge
from ui.pages.context_loader import load_visible_operational_context


def _submit_moderation(alert_row: dict[str, object], decision: str, observations: str, *, confirm_send: bool = False) -> None:
	"""Persist a moderation action and refresh the page."""
	with st.spinner("Registrando decisão humana..."):
		record_alert_moderation(alert_row, decision=decision, observations=observations, confirm_send=confirm_send)
		st.rerun()


def _apply_feedback_button_styles() -> None:
	"""Apply page-local hover styles for the moderation buttons."""
	st.markdown(
		"""
		<style>
			div[data-testid='stExpander'] div[data-testid='column']:nth-of-type(1) button:hover {
				background: rgba(34, 197, 94, 0.14) !important;
				border-color: rgba(34, 197, 94, 0.65) !important;
				color: #166534 !important;
			}
			div[data-testid='stExpander'] div[data-testid='column']:nth-of-type(2) button:hover {
				background: rgba(239, 68, 68, 0.14) !important;
				border-color: rgba(239, 68, 68, 0.65) !important;
				color: #991b1b !important;
			}
			div[data-testid='stExpander'] div[data-testid='column']:nth-of-type(1) button {
				transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease;
			}
			div[data-testid='stExpander'] div[data-testid='column']:nth-of-type(2) button {
				transition: background-color 120ms ease, border-color 120ms ease, color 120ms ease;
			}
		</style>
		""",
		unsafe_allow_html=True,
	)


def render_feedback_page() -> None:
	vm = build_dashboard_filter_view_model()
	_apply_feedback_button_styles()
	visible_context = load_visible_operational_context(
		vm.region,
		vm.period_days,
		tuple(vm.event_types),
		vm.date_start,
		vm.date_end,
		vm.risk_level,
		vm.threshold,
	)
	feature_vm = execute_human_feedback(visible_context, feedback_revision=get_feedback_revision())

	st.markdown("## Central de Feedback Humano")
	st.markdown(f"**Recorte atual:** {vm.region} — ultimos {vm.period_days} dias")
	render_notification_banner(
		"Fluxo de moderação ativo",
		"Alerta automático, observações, aprovação, rejeição e confirmação de envio ficam persistidos na sessão e atualizam a tela em tempo real.",
		kind="info",
	)

	loading_flags = get_loading_flags()
	if loading_flags.get("feedback_workbench"):
		render_loading_placeholder("Processando decisão do alerta", lines=2)

	metrics = feature_vm.moderation_stats
	metric_columns = st.columns(5)
	metric_items = [
		("Pendentes", int(len(feature_vm.queue)), "warning"),
		("Aprovados", int(metrics.get("approved", 0)), "success"),
		("Em revisão", int(metrics.get("reviewed", 0)), "info"),
		("Rejeitados", int(metrics.get("dismissed", 0)), "error"),
		("Enviados", int(metrics.get("sent", 0)), "success"),
	]
	for column, (label, value, kind) in zip(metric_columns, metric_items, strict=True):
		with column:
			st.metric(label, value)
			render_status_badge(label, kind)

	st.markdown("### Alertas automáticos para revisão")
	if feature_vm.queue.empty:
		render_empty_state("Nenhum alerta pendente", "Os alertas já aprovados ou enviados desaparecem da fila. Ajuste os filtros para gerar novos itens.")
	else:
		for _, row in feature_vm.queue.head(6).iterrows():
			alert = row.to_dict()
			status = str(alert.get("decision_status", "pending"))
			alert_id = str(alert.get("alert_id", alert.get("event_id", "")))
			confirm_key = f"feedback_confirm_{alert_id}"
			if confirm_key not in st.session_state:
				st.session_state[confirm_key] = False
			with st.expander(f"{alert.get('event_type', 'Alerta')} | {alert.get('region', 'N/A')} | risco {float(alert.get('risk_score', 0.0)):.2f}"):
				left, right = st.columns([1.4, 1])
				with left:
					render_alert_card(
						title=str(alert.get("alert_title", alert.get("event_type", "Alerta"))),
						message=str(alert.get("alert_message", alert.get("recommended_action", ""))),
						level=str(alert.get("alert_level", "info")),
						source=f"{alert.get('region', '')}/{alert.get('state', '')}".strip("/"),
						action_text=str(alert.get("recommended_action", "")),
					)
					st.caption(f"Status atual: {status} | confianca {float(alert.get('confidence', 0.0)):.2f} | criticidade geografica {float(alert.get('geographic_criticality_score', 0.0)):.2f}")
				with right:
					observations = st.text_area(
						"Observações",
						value=str(alert.get("observations", "")),
						key=f"feedback_obs_{alert_id}",
						placeholder="Registre contexto operacional, justificativa ou follow-up.",
					)
					confirm_action = st.checkbox(
						"Confirmar ação do usuário",
						key=confirm_key,
						value=bool(st.session_state[confirm_key]),
					)
					button_columns = st.columns(2)
					with button_columns[0]:
						if st.button("Aprovar alerta", key=f"approve_{alert_id}", use_container_width=True, disabled=not confirm_action):
							_submit_moderation(alert, "approve", observations, confirm_send=True)
					with button_columns[1]:
						if st.button("Rejeitar alerta", key=f"reject_{alert_id}", use_container_width=True, disabled=not confirm_action):
							_submit_moderation(alert, "dismiss", observations, confirm_send=False)

	st.markdown("### Visão operacional do fluxo")
	render_operational_indicators(visible_context.enriched_events, visible_context.alert_feed, key="feedback-indicators")
	render_alert_spatial_distribution(visible_context.alert_feed, visible_context.enriched_events, key="feedback-alert-spatial-distribution")
	render_operational_bars(visible_context.risk_summary, key="feedback-risk-distribution")

	st.markdown("### Histórico humano")
	history = feature_vm.history
	if history.empty:
		render_empty_state("Sem histórico ainda", "As decisões e observações aparecerão aqui após a primeira moderação.")
	else:
		visible_columns = [column for column in ["created_at", "alert_id", "decision", "status", "confirm_send", "title", "region", "state", "event_type", "alert_level", "risk_score", "observations"] if column in history.columns]
		st.dataframe(history[visible_columns], use_container_width=True, hide_index=True)

	st.markdown("### Estado persistido")
	state_summary = {
		"approved": get_approved_alerts(),
		"reviewed": get_reviewed_alerts(),
		"dismissed": get_dismissed_alerts(),
		"sent": get_sent_alerts(),
		"history_count": len(get_feedback_history()),
	}
	st.json(state_summary)
