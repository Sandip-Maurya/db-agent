from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from .api_client import AgentAnswerPayload, HealthPayload, TableProfilePayload, TablesPayload


def render_health_summary(health: HealthPayload) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Status", health.status)
    col2.metric("Dialect", health.dialect)
    col3.metric("Database", health.database_name)
    col4.metric("Environment", health.environment)

    st.caption(
        " | ".join(
            [
                f"App: {health.app_name}",
                f"Default query limit: {health.default_query_limit}",
                f"Max rows per query: {health.max_rows_per_query}",
                f"Max sample rows: {health.max_sample_rows}",
            ]
        )
    )


def render_table_selector(tables_payload: TablesPayload) -> str | None:
    table_names = [table.name for table in tables_payload.tables]
    if not table_names:
        st.info("No tables were returned by the backend.")
        return None

    return st.selectbox("Choose a table", options=table_names, index=0)



def render_table_profile(profile: TableProfilePayload) -> None:
    st.subheader(f"Table: {profile.name}")
    if profile.description:
        st.write(profile.description)

    if profile.foreign_keys:
        st.caption("Foreign keys: " + ", ".join(profile.foreign_keys))

    if profile.columns:
        columns_df = pd.DataFrame(
            [
                {
                    "name": column.name,
                    "data_type": column.data_type,
                    "nullable": column.nullable,
                    "default": column.default,
                    "primary_key": column.is_primary_key,
                    "notes": column.notes,
                }
                for column in profile.columns
            ]
        )
        st.dataframe(columns_df, width="content", hide_index=True)

    if profile.sample_rows:
        st.markdown("**Sample rows**")
        sample_df = pd.DataFrame(profile.sample_rows)
        st.dataframe(sample_df, width="content", hide_index=True)
    else:
        st.info("No sample rows available for this table.")



def render_agent_answer(answer: AgentAnswerPayload) -> None:
    st.subheader("Answer")
    st.write(answer.answer)

    info1, info2 = st.columns(2)
    info1.metric("Confidence", answer.confidence)
    info2.metric("Needs follow-up", "Yes" if answer.needs_followup else "No")

    with st.expander("Assumptions", expanded=bool(answer.assumptions)):
        if answer.assumptions:
            for item in answer.assumptions:
                st.write(f"- {item}")
        else:
            st.write("No explicit assumptions returned.")

    with st.expander("Evidence", expanded=True):
        if answer.evidence:
            evidence_df = pd.DataFrame(
                [{"kind": item.kind, "detail": item.detail} for item in answer.evidence]
            )
            st.dataframe(evidence_df, width="content", hide_index=True)
        else:
            st.write("No evidence items returned.")

    with st.expander("Generated SQL", expanded=answer.db_query_executed):
        if answer.db_query_executed:
            st.code(answer.executed_sql, language="sql")
        else:
            st.write("No SQL was returned for this answer.")



def render_debug_payload(payload: Any) -> None:
    with st.expander("Debug response payload"):
        st.json(payload)
