# HR Resume & LinkedIn Shortlisting Agent

This project helps HR teams evaluate candidates faster. It processes a Job Description and a batch of candidate profiles (resumes or LinkedIn data), applies semantic matching, and produces a structured shortlist with clear scoring reasons.

## Features
- **JD Parser:** Extracts structured requirements from a Job Description.
- **Resume/LinkedIn Ingestion:** Parses PDFs, DOCX, and JSON files into a unified candidate model.
- **Semantic Matching Engine:** Uses `all-MiniLM-L6-v2` embeddings to objectively compare Candidate skills to JD requirements.
- **Scoring Rubric:** Applies weighted scoring (Skills 30%, Exp 25%, Edu 15%, Projects 20%, Comm 10%) with model-generated justifications and Python-calculated deterministic totals.
- **Shortlist Report:** Generates HTML, PDF, and JSON reports detailing rankings and justifications.
- **Human-in-the-Loop:** HR can override scores via an API, which logs changes to an audit file.
- **Security Middleware:** Includes rate limiting and API key authentication.

## Architecture

1. **Ingestion Layer:** Uploads are processed via `pdf_parser`, `docx_parser`, and `candidate_extractor`.
2. **Semantic Engine:** Calculates cosine similarity for skill alignments.
3. **Scoring Engine:** Feeds context to the LLM (Gemini) for qualitative assessment and calculates deterministic weighted scores.
4. **API / Presentation Layer:** FastAPI endpoints handle requests and `report_generator` outputs HTML/PDF results.

## Folder Structure

```
project/
├── app/
│   ├── main.py
│   ├── api/          # FastAPI Endpoints
│   ├── services/     # JD parsing, Scoring Engine, Semantic Matcher
│   ├── parsers/      # PDF, DOCX, LinkedIn parsers & Extractors
│   ├── reporting/    # HTML & PDF generation (Jinja2, ReportLab)
│   ├── models/       # Pydantic Schemas
│   ├── security/     # Middleware (Auth & Rate Limit)
│   └── utils/        # Config and Paths
├── data/             # Persistent data (e.g., overrides.json)
├── uploads/          # Uploaded resumes
├── outputs/          # Generated HTML/PDF reports
├── sample_data/      # Test files (JD, Resumes)
├── README.md
├── SECURITY.md
├── .env.example
├── requirements.txt
└── docker-compose.yml
```

## Setup Instructions

1. Clone the repository and navigate to the `project` directory.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Google Gemini API Key and a custom Server API Key.
   ```bash
   cp .env.example .env
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`. API Docs are at `http://localhost:8000/docs`.

## API Usage

Include the `X-API-Key` header with requests.

- **`POST /api/v1/parse_jd`**: Pass `{"raw_text": "..."}` to extract structured JD.
- **`POST /api/v1/upload_resumes`**: Upload multipart/form-data files. Returns structured candidate JSON.
- **`POST /api/v1/analyze_candidates`**: Pass JD and Candidate JSONs. Returns scored and ranked candidates.
- **`POST /api/v1/generate_report`**: Pass results from `analyze_candidates` to generate HTML/PDF.
- **`POST /api/v1/override_score`**: Provide override details to manually adjust scores and log reasons.

## Technical Stack

- **LLM Chosen:** Gemini 2.5 Flash via Google GenAI.
  - *Rationale:* Offers excellent performance for structured output generation at a lower cost with high speed.
- **Agent Framework:** LangChain.
  - *Rationale:* Used `with_structured_output` wrapper for reliable Pydantic schema enforcement instead of complex multi-agent flows, ensuring robustness and reducing parsing errors.
- **Embeddings:** `all-MiniLM-L6-v2` (SentenceTransformers).
  - *Rationale:* Fast, local embedding model that doesn't incur API costs and keeps data private while providing robust semantic similarity for skill matching.
- **Web Framework:** FastAPI.
  - *Rationale:* High performance, native Pydantic integration, and auto-generated OpenAPI docs.

## Future Improvements
- Integrate a robust frontend (React/Streamlit).
- Use LangSmith for tracing and observability (environment variables are set up).
- Support OCR for scanned PDFs.
