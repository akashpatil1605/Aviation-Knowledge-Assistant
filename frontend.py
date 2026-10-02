import os
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

load_dotenv(override=True)

for secret_name in ("GROQ_API_KEY", "TAVILY_API_KEY"):
    if os.getenv(secret_name):
        continue
    try:
        secret_value = st.secrets.get(secret_name)
    except StreamlitSecretNotFoundError:
        break
    if secret_value:
        os.environ[secret_name] = str(secret_value)

from main import app

st.set_page_config(
    page_title="Aviation Knowledge Assistant",
    page_icon="🔎",
    layout="wide",
)

with st.sidebar:
    st.title("Aviation Knowledge Assistant")
    st.caption("Tavily research + FAA maintenance references")

    st.subheader("Powered by")
    for tech in [
        "LangGraph",
        "Groq",
        "Tavily MCP Search",
        "Local FAA PDF RAG",
    ]:
        st.write(f"• {tech}")

    st.subheader("Agent Pipeline")
    for step in [
        "General questions -> Tavily Search Agent",
        "Aircraft maintenance -> FAA PDF RAG Agent",
    ]:
        st.write(step)

st.title("Aviation Knowledge Assistant")


user_query = st.text_area(
    "Your question",
    placeholder="Ask a general question or an FAA aircraft-maintenance question",
    height=110,
)

generate = st.button("Get Answer", type="primary", use_container_width=True)

AGENT_META = {
    "tavily_agent": ("🔎", "Tavily Search Agent"),
    "faa_maintenance_agent": ("🛠️", "FAA Maintenance RAG Agent"),
}

if generate:
    if not user_query.strip():
        st.warning("Enter a question first.")
    else:
        collected = {
            "tavily_results": "",
            "maintenance_results": "",
        }

        st.divider()
        st.subheader("Agent Pipeline — Live")

        for chunk in app.stream(
            {
                "user_query": user_query,
                "tavily_results": "",
                "maintenance_results": "",
            },
            stream_mode="updates",
        ):
            for node_name, state_update in chunk.items():
                icon, label = AGENT_META.get(node_name, ("🔧", node_name))

                with st.status(f"{icon} {label}", state="complete", expanded=False):
                    if node_name == "tavily_agent":
                        text = state_update.get("tavily_results", "")
                        collected["tavily_results"] = text

                    elif node_name == "faa_maintenance_agent":
                        text = state_update.get("maintenance_results", "")
                        collected["maintenance_results"] = text

        is_maintenance_answer = bool(collected["maintenance_results"])
        if is_maintenance_answer:
            st.subheader("FAA Maintenance Reference Answer")
            st.write(collected["maintenance_results"])
        elif collected["tavily_results"]:
            st.subheader("Tavily Answer")
            st.write(collected["tavily_results"])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = (
            f"faa_maintenance_answer_{timestamp}.txt"
            if is_maintenance_answer
            else f"tavily_answer_{timestamp}.txt"
        )
        output_folder = "answers"
        save_dir = os.path.join(os.path.dirname(__file__), output_folder)
        os.makedirs(save_dir, exist_ok=True)

        if is_maintenance_answer:
            file_content = (
                f"FAA Aircraft Maintenance Reference\n"
                f"Question: {user_query}\n"
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"\nAnswer:\n{collected['maintenance_results']}\n"
            )
        else:
            file_content = (
                f"Tavily Search Answer\n"
                f"Query: {user_query}\n"
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"\nAnswer:\n{collected['tavily_results'] or 'N/A'}\n"
            )

        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(file_content)

        dl_col, info_col = st.columns([1, 3])
        with dl_col:
            st.download_button(
                "Download Answer",
                data=file_content,
                file_name=filename,
                mime="text/plain",
                use_container_width=True,
            )
        with info_col:
            st.info(f"Auto-saved to {output_folder}/{filename}")
