import json
from app.models.jd import JobDescription
from app.models.candidate import Candidate
from app.services.scoring_engine import calculate_score
from app.reporting.html_report import generate_html_report
from app.reporting.pdf_report import generate_pdf_report
from app.utils.config import settings

def main():
    print("Loading JD...")
    jd = JobDescription(
        role="Senior Backend Engineer (Python)",
        required_skills=["Python", "FastAPI", "PostgreSQL", "LangChain", "Docker"],
        preferred_skills=["Kubernetes", "AWS", "Redis"],
        min_experience_years=4.0,
        education=["Bachelor's degree in Computer Science"],
        certifications=[],
        domain_keywords=["AI/ML APIs", "SaaS"],
        communication_requirements=["excellent written and verbal communication"]
    )
    
    candidates_data = []
    import glob
    for filepath in glob.glob("sample_data/*.json"):
        with open(filepath, "r") as f:
            candidates_data.append(json.load(f))
            
    results = []
    for cand_dict in candidates_data:
        print(f"Scoring {cand_dict['name']}...")
        cand = Candidate(**cand_dict)
        if not cand.id:
            cand.id = cand.name.lower().replace(" ", "_")
        score = calculate_score(jd, cand)
        results.append(score)
        
    results.sort(key=lambda x: x["final_score"], reverse=True)
    
    print("Generating Reports...")
    html_out = generate_html_report(results, "outputs/test_report.html")
    pdf_out = generate_pdf_report(results, "outputs/test_report.pdf")
    
    print(f"HTML Report: {html_out}")
    print(f"PDF Report: {pdf_out}")
    print("Test successful!")

if __name__ == "__main__":
    main()
