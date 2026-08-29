# 🏎️ F1 Knowledge Chatbot

An interactive Streamlit chatbot for exploring Formula 1 race results. The
current MVP loads the 2025 Australian Grand Prix classification with FastF1
and uses a Groq-hosted language model to answer questions about the data.

## Features

- Downloads official F1 session data through FastF1
- Displays the race classification in an interactive table
- Answers natural-language questions about the loaded results
- Maintains chat history during the Streamlit session
- Caches downloaded race data locally for faster subsequent loads
- Keeps API credentials outside the repository

## Tech stack

- Python 3.13
- Streamlit
- FastF1 and pandas
- Groq via the OpenAI-compatible API
- `openai/gpt-oss-20b`
- uv for dependency management

## Setup

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/gautamikh/F1-Knowledge-Chatbot.git
cd F1-Knowledge-Chatbot
```

Install the dependencies:

```powershell
uv sync
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Create an API key from the [Groq Console](https://console.groq.com/keys).
Never commit the `.env` file or share your API key.

## Run the app

```powershell
uv run streamlit run app.py
```

Open `http://localhost:8501`, select **Load 2025 Australian Grand Prix
results**, and ask a question such as:

> Who won the race, and which team did they drive for?

## Current scope

The MVP currently answers questions using the 2025 Australian Grand Prix race
classification. Support for selecting other seasons, events, and session types
is planned for a future version.
