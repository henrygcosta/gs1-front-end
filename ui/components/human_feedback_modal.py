"""Human feedback modal component."""

from __future__ import annotations

import streamlit as st

from state.actions import record_alert_moderation


@st.dialog("Revisao humana")
def render_human_feedback_modal(alert_id: str, title: str, description: str) -> None:
	"""Render a modal dialog for human review of an alert."""
	st.markdown(f"**{title}**")
	st.write(description)
	decision = st.radio("Decisao", options=["approve", "review", "dismiss"], horizontal=True, format_func=lambda option: {"approve": "Aprovar", "review": "Revisar", "dismiss": "Rejeitar"}[option])
	confirm_send = st.checkbox("Confirmar envio ao centro operacional", value=False)
	comment = st.text_area("Observacao opcional", placeholder="Descreva o motivo da decisao")
	if st.button("Confirmar", type="primary"):
		record_alert_moderation({"alert_id": alert_id, "alert_title": title, "event_type": title}, decision=decision, observations=comment.strip(), confirm_send=confirm_send)
		st.success("Decisao registrada.")
		st.rerun()
