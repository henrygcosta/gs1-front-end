"""Human-in-the-loop feedback form component."""

from __future__ import annotations

import streamlit as st

from state.actions import push_feedback


def render_feedback_form() -> None:
	"""Render analyst feedback form and persist entry in session queue."""
	with st.form("feedback_form"):
		event_id = st.text_input("ID do evento")
		decision = st.selectbox("Decisao humana", options=["confirm", "review", "discard"])
		rationale = st.text_area("Justificativa")
		submitted = st.form_submit_button("Registrar feedback")

	if submitted:
		if not event_id.strip() or not rationale.strip():
			st.warning("Preencha ID do evento e justificativa para registrar o feedback.")
			return

		push_feedback(
			{
				"event_id": event_id.strip(),
				"decision": decision,
				"rationale": rationale.strip(),
			}
		)
		st.success("Feedback registrado com sucesso.")
