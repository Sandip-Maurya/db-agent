from __future__ import annotations

import streamlit as st

from db_agent.streamlit_settings import StreamlitSettings

from streamlit_app.api_client import BackendRequestError, BackendUnavailableError, DbAgentApiClient
from streamlit_app.state import initialize_state
from streamlit_app.ui_components import (
    render_agent_answer,
    render_debug_payload,
    render_health_summary,
    render_table_profile,
    render_table_selector,
)


settings = StreamlitSettings()
st.set_page_config(page_title=settings.page_title, page_icon=settings.page_icon, layout="wide")


@st.cache_resource
def get_client() -> DbAgentApiClient:
    return DbAgentApiClient(
        base_url=settings.normalized_backend_base_url,
        timeout_seconds=settings.request_timeout_seconds,
    )


initialize_state()
client = get_client()

st.title("db-agent")
st.caption("Streamlit UI for schema exploration and natural-language querying")

with st.sidebar:
    st.header("Backend")
    st.write(f"Base URL: `{settings.normalized_backend_base_url}`")
    st.write(f"Timeout: `{settings.request_timeout_seconds}` seconds")
    use_test_model = st.toggle("Use test model", value=False)
    refresh = st.button("Refresh metadata")


if refresh or st.session_state.backend_status is None:
    try:
        st.session_state.backend_status = client.get_health()
        st.session_state.tables_payload = client.get_tables()
        st.session_state.last_error = None
    except BackendUnavailableError as exc:
        st.session_state.last_error = str(exc)
    except BackendRequestError as exc:
        st.session_state.last_error = str(exc)


if st.session_state.last_error:
    st.error(st.session_state.last_error)
    st.stop()


render_health_summary(st.session_state.backend_status)

left, right = st.columns([1, 2])

with left:
    st.subheader("Schema explorer")
    tables_payload = st.session_state.tables_payload
    selected_table = render_table_selector(tables_payload)
    st.session_state.selected_table = selected_table

    if selected_table:
        try:
            st.session_state.table_profile = client.get_table(selected_table)
        except BackendRequestError as exc:
            st.error(str(exc))
        except BackendUnavailableError as exc:
            st.error(str(exc))

        if st.session_state.table_profile is not None:
            render_table_profile(st.session_state.table_profile)

with right:
    st.subheader("Ask the agent")
    question = st.text_area(
        "Question",
        value=st.session_state.last_question,
        height=120,
        placeholder="Example: What currencies appear in orders?",
    )

    submit = st.button("Run question", type="primary")

    if submit and question:
        st.session_state.last_question = question
        try:
            response = client.ask(question, use_test_model=use_test_model)
            st.session_state.last_answer = response
            st.session_state.last_error = None
        except BackendUnavailableError as exc:
            st.session_state.last_error = str(exc)
        except BackendRequestError as exc:
            st.session_state.last_error = str(exc)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.last_answer is not None:
        render_agent_answer(st.session_state.last_answer.answer)
        if settings.debug:
            render_debug_payload(st.session_state.last_answer.model_dump())
