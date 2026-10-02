# Aviation Knowledge Assistant Test Cases

## Setup

1. Activate the project environment: `\.venv\Scripts\Activate.ps1`.
2. Confirm `.env` contains valid `GROQ_API_KEY` and `TAVILY_API_KEY` values. Do not put these values in test output or commit `.env`.
3. Start the app with `streamlit run frontend.py` and open `http://localhost:8501`.

## Manual Tests

### TC-01: Empty question

**Input:** Leave the question field blank and select **Get Answer**.

**Expected:** The UI displays `Enter a question first.` No agent runs and no answer file is created.

### TC-02: General current-information question

**Input:** `Find current travel advisories for Japan.`

**Expected:** The Tavily Search Agent runs. The answer reflects Tavily results and includes source URLs when the search results provide them.

### TC-03: Maintenance record requirements

**Input:** `What details are needed in a maintenance record under 14 CFR 43.9?`

**Expected:** The FAA Maintenance RAG Agent runs. The response contains verbatim text from `faa_maintenance_records_and_work_standards.pdf` with its page citation. It must not add an LLM-generated explanation.

### TC-04: Preventive-maintenance scope

**Input:** `Who may perform preventive maintenance and what are examples?`

**Expected:** The FAA Maintenance RAG Agent runs and returns verbatim material from `faa_preventive_maintenance_basics.pdf`, labeled with its page.

### TC-05: FAA topic not covered by the PDFs

**Input:** `What are the FAA drone registration requirements as of 2026?`

**Expected:** The question routes to FAA RAG, not Tavily. Since the provided PDFs do not cover drone registration, the entire answer is exactly `I don't know.`

### TC-06: Aircraft-specific procedure not covered by the PDFs

**Input:** `What torque is required for Cessna 172 landing gear maintenance?`

**Expected:** The question routes to FAA RAG. If retrieval has no supporting PDF page, the answer is exactly `I don't know.` Do not provide a torque value or procedure.

### TC-07: FAA response source-only check

**Input:** Run TC-03 or TC-04.

**Expected:** Compare the response text with the cited PDF page. The factual response is copied from that PDF; it contains no paraphrased or additional claims. The FAA agent does not call the LLM.

### TC-08: Shared answer folder

**Input:** Submit one Tavily question and one FAA maintenance question.

**Expected:** Both answer files are saved under `answers/`. Filenames remain distinguishable: `tavily_answer_...txt` and `faa_maintenance_answer_...txt`.

## Notes

- FAA-related questions always use the local PDF route, including FAA topics not covered by the PDFs.
- General non-FAA questions use Tavily.
- The bundled FAA PDFs are short educational summaries, not aircraft-specific maintenance instructions or authorization to perform work.
