import streamlit as st
import requests
import json
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="HR Agent Prototype", layout="wide")
st.title("HR Resume & LinkedIn Shortlisting Agent")
st.markdown("Upload a Job Description and a batch of resumes to get an AI-scored shortlist.")

# Sidebar for JD
with st.sidebar:
    st.header("1. Job Description")
    jd_input_method = st.radio("Provide JD via:", ["Text", "File (.txt, .pdf)"])
    raw_jd_text = ""
    
    if jd_input_method == "Text":
        raw_jd_text = st.text_area("Paste Job Description Here", height=300)
    else:
        jd_file = st.file_uploader("Upload JD File", type=["txt", "pdf"])
        if jd_file:
            if jd_file.name.endswith(".pdf"):
                import fitz
                doc = fitz.open(stream=jd_file.read(), filetype="pdf")
                for page in doc:
                    raw_jd_text += page.get_text()
            else:
                raw_jd_text = jd_file.read().decode("utf-8")
            
    if st.button("Parse JD"):
        if not raw_jd_text:
            st.warning("Please provide a Job Description.")
        else:
            with st.spinner("Parsing JD with AI..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/parse_jd", json={"raw_text": raw_jd_text})
                    if res.status_code == 200:
                        st.session_state["jd"] = res.json()
                        st.success("JD Parsed Successfully!")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {e}")

if "jd" in st.session_state:
    with st.expander("Parsed Job Description Profile", expanded=False):
        st.json(st.session_state["jd"])

st.header("2. Upload Candidates")
candidate_files = st.file_uploader(
    "Upload Candidate Resumes or LinkedIn Profiles", 
    type=["pdf", "docx", "json"], 
    accept_multiple_files=True
)

if st.button("Analyze Candidates"):
    if "jd" not in st.session_state:
        st.error("Please parse the Job Description first.")
    elif not candidate_files:
        st.error("Please upload at least one candidate file.")
    else:
        # Step 1: Upload and extract candidates
        with st.spinner(f"Extracting profiles from {len(candidate_files)} files..."):
            files_payload = []
            for file in candidate_files:
                files_payload.append(("files", (file.name, file.getvalue(), file.type)))
            
            upload_res = requests.post(f"{API_BASE_URL}/upload_resumes", files=files_payload)
            
            if upload_res.status_code == 200:
                candidates_data = upload_res.json()["candidates"]
                st.success(f"Successfully extracted {len(candidates_data)} candidates.")
            else:
                st.error(f"Error extracting resumes: {upload_res.text}")
                st.stop()
                
        # Step 2: Analyze Candidates against JD
        with st.spinner("Scoring and ranking candidates..."):
            analysis_payload = {
                "jd": st.session_state["jd"],
                "candidates_data": candidates_data
            }
            
            analyze_res = requests.post(f"{API_BASE_URL}/analyze_candidates", json=analysis_payload)
            
            if analyze_res.status_code == 200:
                results = analyze_res.json()["results"]
                st.session_state["results"] = results
                st.success("Analysis Complete!")
            else:
                st.error(f"Error analyzing candidates: {analyze_res.text}")

if "results" in st.session_state:
    st.markdown("---")
    st.header("3. Ranked Shortlist")
    results = st.session_state["results"]
    
    # Display top summary metrics
    if len(results) > 0:
        top_cand = results[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Candidates Scored", len(results))
        col2.metric("Top Candidate", top_cand["candidate_name"])
        col3.metric("Top Score", f"{top_cand['final_score']} / 100")
    
    # Display in a dataframe
    df_data = []
    for r in results:
        df_data.append({
            "Candidate ID": r["candidate_id"],
            "Name": r["candidate_name"],
            "Final Score": r["final_score"],
            "Recommendation": r["recommendation"]
        })
    df = pd.DataFrame(df_data)
    st.dataframe(df.style.highlight_max(subset=['Final Score'], color='lightgreen'), use_container_width=True)
    
    # Generate HTML/PDF Reports
    st.markdown("### Export Results")
    if st.button("📄 Generate Downloadable Reports (PDF & HTML)", use_container_width=True):
        with st.spinner("Generating Reports..."):
            requests.post(f"{API_BASE_URL}/generate_report", json={"format": "html", "results": results})
            pdf_res = requests.post(f"{API_BASE_URL}/generate_report", json={"format": "pdf", "results": results})
            st.success(f"Reports saved to local 'outputs' directory! (See {pdf_res.json().get('path')})")
            
    # Detailed Expanders
    st.markdown("---")
    st.subheader("🔍 Detailed Scoring & Human Override")
    for idx, r in enumerate(results):
        # Use an expander for each candidate
        with st.expander(f"🏅 {r['candidate_name']} - Score: {r['final_score']} ({r['recommendation']})"):
            st.caption(f"Candidate ID: `{r['candidate_id']}`")
            
            # Display dimensions in columns
            dims = r["dimensions"]
            cols = st.columns(len(dims))
            for i, (dim_name, dim_data) in enumerate(dims.items()):
                with cols[i]:
                    st.metric(label=f"{dim_name.title()} ({dim_data['weight']*100}%)", value=f"{dim_data['score']}/10")
                    st.caption(f"_{dim_data['justification']}_")
            
            st.divider()
            
            # Human Override Section
            st.markdown("#### ⚖️ Human-in-the-Loop Override")
            col_o1, col_o2 = st.columns([1, 2])
            with col_o1:
                new_score = st.number_input("New Score (0-100)", min_value=0.0, max_value=100.0, value=float(r['final_score']), step=1.0, key=f"score_{idx}")
            with col_o2:
                override_reason = st.text_input("Reason for override", key=f"reason_{idx}", placeholder="E.g. Strong cultural fit after interview")
                
            if st.button("Apply Override", key=f"btn_{idx}"):
                if not override_reason:
                    st.error("Please provide a reason for the override.")
                else:
                    try:
                        override_res = requests.post(
                            f"{API_BASE_URL}/override_score", 
                            params={"candidate_id": r["candidate_id"], "new_score": new_score, "reason": override_reason}
                        )
                        if override_res.status_code == 200:
                            st.success(f"Override recorded! {r['candidate_name']}'s score changed to {new_score}.")
                        else:
                            st.error("Failed to record override.")
                    except Exception as e:
                        st.error(f"API Error: {e}")
