# Security Mitigations

This document outlines the security risks and the mitigation strategies implemented in the HR Resume & LinkedIn Shortlisting Agent.

## 1. Prompt Injection
**Risk:** Malicious input in resumes manipulating agent behavior.
**Mitigation Strategy:**
- Uses Pydantic structured output validation with Langchain's `with_structured_output` to strictly enforce the output format from LLMs. This prevents the LLM from outputting malicious executable code or deviating from the defined schema.
- Input sanitization is inherently handled by defining strict field types (e.g., expecting specific formats for skills, experience).

## 2. Data Privacy / PII
**Risk:** Resume/LinkedIn data contains personal info.
**Mitigation Strategy:**
- All document processing (PDF, DOCX) is done locally before passing text to the LLM.
- The pipeline limits what is printed to the terminal, avoiding exposing full plain-text resumes in server logs.

## 3. API Key Exposure
**Risk:** LLM or server API keys leaked in code.
**Mitigation Strategy:**
- `.env` files are used for all secrets.
- `.env.example` is provided but contains no real keys.
- Keys are loaded securely via `pydantic-settings` using the `app/utils/config.py` setup, never hardcoded.

## 4. Hallucination Risk
**Risk:** LLM generating false scores or wrong candidate content.
**Mitigation Strategy:**
- Uses deterministic Python logic for the final weighted scoring computation instead of letting the LLM calculate the final score.
- The Semantic Engine utilizes local embedding models (`all-MiniLM-L6-v2`) via `SentenceTransformers` to objectively match skills with similarity thresholds.
- Requires justification for every dimension score assigned by the LLM.
- Includes a Human-in-the-Loop override mechanism via `POST /override_score` to let HR correct any AI inaccuracies.

## 5. Unauthorized Access
**Risk:** Anyone triggering the agent endpoint.
**Mitigation Strategy:**
- A custom FastAPI `SecurityMiddleware` enforces API Key authentication (`X-API-Key` header) for all sensitive endpoints.
- Basic in-memory rate limiting is applied (100 requests / 60 seconds per IP) to prevent DDoS or API abuse.
