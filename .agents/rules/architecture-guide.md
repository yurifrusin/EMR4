* **Frontend:** Microsoft Word Web Add-in built with vanilla JavaScript, HTML, and CSS (located primarily in `src/taskpane/`).
* **Backend:** Python FastAPI server running via Uvicorn (located in `main.py`).
* **Data Flow:** Strict Pydantic models are used for all JSON validation and payload structures.
* **AI Engine:** Google Vertex AI (gemini-2.5-flash) handles all LLM inference.
* **Database:** Local PostgreSQL instance.
* **Strict Constraint:** Do not introduce new frameworks (like React, Vue, or Django) or rewrite vanilla JS into TypeScript without explicit permission.