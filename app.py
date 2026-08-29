import os
from pathlib import Path

import fastf1
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

st.set_page_config(
    page_title="F1 Knowledge Chatbot",
    page_icon=":material/sports_motorsports:",
)

st.title("🏎️ F1 Knowledge Chatbot")
st.write("Load race results and ask questions about them.")

st.session_state.setdefault("results", None)
st.session_state.setdefault("messages", [])


@st.cache_data(show_spinner=False)
def load_race_results() -> pd.DataFrame:
    session = fastf1.get_session(2025, "Australian Grand Prix", "R")
    session.load(
        laps=False,
        telemetry=False,
        weather=False,
        messages=False,
    )

    columns = [
        "Position",
        "FullName",
        "Abbreviation",
        "TeamName",
        "Status",
        "Points",
    ]
    return session.results.loc[:, columns].copy()


@st.cache_resource
def get_groq_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1",
    )


if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY was not found in your .env file.")
    st.stop()


if st.button("Load 2025 Australian Grand Prix results"):
    try:
        with st.spinner("Loading race results..."):
            st.session_state.results = load_race_results()

        st.session_state.messages = []
        st.success("Race results loaded.")
    except Exception as error:
        st.error(f"Could not load the race: {error}")


results = st.session_state.results

if results is not None:
    st.dataframe(results, hide_index=True, width="stretch")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input(
        "Ask about these race results",
        submit_mode="disable",
    )

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.write(question)

        race_context = results.to_csv(index=False)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an accurate Formula 1 data assistant. "
                    "Answer using the supplied 2025 Australian Grand Prix "
                    "results. If the answer is not present in the data, say so.\n\n"
                    f"Race results:\n{race_context}"
                ),
            },
            *st.session_state.messages,
        ]

        try:
            with st.chat_message("assistant"):
                response = get_groq_client().chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages,
                    temperature=0.2,
                )
                answer = response.choices[0].message.content
                st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
        except Exception as error:
            st.error(f"Groq request failed: {error}")
else:
    st.info("Load the race results to enable the chatbot.")