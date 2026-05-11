from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from typing import List, Optional, Any
from pydantic import BaseModel
import shutil
import os
import json
from datetime import datetime

from app.utils.config import settings
from app.services.jd_parser import parse_jd
from app.models.jd import JobDescription
from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx
from app.parsers.candidate_extractor import extract_candidate_from_text
from app.services.scoring_engine import calculate_score
from app.reporting.html_report import generate_html_report
from app.reporting.pdf_report import generate_pdf_report

router = APIRouter()

# --- Schemas ---
class JDPayload(BaseModel):
    raw_text: str

class OverridePayload(BaseModel):
    candidate_id: str
    new_score: float
    reason: str
    status: str # approved, rejected, needs_review

class AnalysisPayload(BaseModel):
    jd: JobDescription
    candidates_data: List[dict] # Extracted candidates as dicts

class ReportPayload(BaseModel):
    format: str # html, pdf, json
    results: List[dict]

# --- Endpoints ---

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

@router.post("/parse_jd", response_model=JobDescription)
async def api_parse_jd(payload: JDPayload):
    try:
        jd = parse_jd(payload.raw_text)
        return jd
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_resumes")
async def api_upload_resumes(files: List[UploadFile] = File(...)):
    parsed_candidates = []
    
    for file in files:
        file_path = settings.UPLOADS_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        text = ""
        source = "unknown"
        if file.filename.endswith(".pdf"):
            text = parse_pdf(str(file_path))
            source = "pdf"
        elif file.filename.endswith(".docx"):
            text = parse_docx(str(file_path))
            source = "docx"
        elif file.filename.endswith(".json"):
            # Assume LinkedIn or predefined JSON
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                text = json.dumps(data)
                source = "json"
        
        if text:
            import time
            time.sleep(5)  # Prevent Gemini RPM Free Tier Rate Limits
            candidate = extract_candidate_from_text(text, source)
            parsed_candidates.append(candidate.model_dump())
            
    return {"message": "Files processed", "candidates": parsed_candidates}

@router.post("/analyze_candidates")
async def api_analyze_candidates(payload: AnalysisPayload):
    from app.models.candidate import Candidate
    import time
    
    results = []
    for cand_dict in payload.candidates_data:
        cand = Candidate(**cand_dict)
        time.sleep(5) # Prevent Gemini RPM Free Tier Rate Limits
        score_result = calculate_score(payload.jd, cand)
        results.append(score_result)
        
    # Sort by score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return {"results": results}

@router.post("/generate_report")
async def api_generate_report(payload: ReportPayload):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if payload.format == "html":
        out_path = settings.OUTPUTS_DIR / f"report_{timestamp}.html"
        generate_html_report(payload.results, str(out_path))
        return {"message": "HTML Report generated", "path": str(out_path)}
    elif payload.format == "pdf":
        out_path = settings.OUTPUTS_DIR / f"report_{timestamp}.pdf"
        generate_pdf_report(payload.results, str(out_path))
        return {"message": "PDF Report generated", "path": str(out_path)}
    elif payload.format == "json":
        out_path = settings.OUTPUTS_DIR / f"report_{timestamp}.json"
        with open(out_path, "w") as f:
            json.dump(payload.results, f, indent=4)
        return {"message": "JSON Report generated", "path": str(out_path)}
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use html, pdf, or json.")

@router.post("/override_score")
async def api_override_score(payload: OverridePayload):
    # Load existing overrides
    overrides = []
    if settings.OVERRIDES_FILE.exists():
        with open(settings.OVERRIDES_FILE, "r") as f:
            try:
                overrides = json.load(f)
            except json.JSONDecodeError:
                pass
                
    # Append new override
    override_record = {
        "candidate_id": payload.candidate_id,
        "new_score": payload.new_score,
        "reason": payload.reason,
        "status": payload.status,
        "timestamp": datetime.now().isoformat()
    }
    overrides.append(override_record)
    
    # Save back
    with open(settings.OVERRIDES_FILE, "w") as f:
        json.dump(overrides, f, indent=4)
        
    return {"message": "Override saved successfully", "override": override_record}
