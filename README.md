# Aviation Knowledge Assistant

This project demonstrates two focused question-answering routes: Tavily MCP search for general or current questions, and local PDF retrieval for FAA aircraft-maintenance questions.

---

# Requirements

## APIs

- Groq API: https://console.groq.com
- Tavily API: https://www.tavily.com/

## Tools

- Tavily MCP Server: https://docs.tavily.com/documentation/mcp

---

# Step 1: Create Python Environment


    python -m venv .venv


Activate:


    .venv\Scripts\activate


---

# Step 2: Install Dependencies


    pip install -r requirements.txt


---

# Step 3: Setup .env File

Create a `.env` file:

    GROQ_API_KEY=your_groq_api_key

    TAVILY_API_KEY=your_tavily_api_key

# Run the Application

## Terminal Version

    python main.py

## Streamlit Web App

    streamlit run frontend.py


---

# Example Questions

    What are the FAA requirements for a preventive-maintenance log entry?

    Find current travel advice for visiting Japan in October.


---

# Features

- Two-agent LangGraph routing
- Tavily MCP web search for general/current questions
- Local BM25 retrieval over short FAA reference PDFs
- Source-file and page citations for FAA answers
- Streamlit Web App

## FAA Aircraft Maintenance RAG

Questions containing aircraft-maintenance topics are routed to the local PDF agent. Other questions are sent to Tavily. The agent searches the short reference PDFs in `faa_maintenance_pdfs/` and grounds its answer in the retrieved pages.

The bundled one-page references cover Part 43 maintenance records and general work standards, plus preventive-maintenance scope and limits. They summarize the current eCFR and are educational references only, not aircraft-specific instructions or authorization to perform work. The agent cites PDF filenames and page numbers and directs users to current regulations and approved aircraft-specific data.
