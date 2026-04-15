import json
import os
import tempfile

import httpx
import streamlit as st
from pdfminer.high_level import extract_text

from skills import job_skill_map, skills_list


st.set_page_config(page_title="AI Job & Skill Gap Analyzer", page_icon="🎯", layout="wide")

# Custom CSS for UI elements
st.markdown("""
<style>
/* Main Gradient Title */
.gradient-title {
    background: linear-gradient(135deg, #ff7e5f, #feb47b, #ff7e5f);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.5rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 10px;
    animation: gradientShift 5s ease infinite;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Colorful Metric Cards */
.colorful-card {
    border-radius: 20px;
    padding: 25px 20px;
    color: white;
    text-align: center;
    box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    margin-bottom: 25px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.colorful-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.25);
}
.card-score { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.card-match { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.card-job { background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%); }

.card-value { font-size: 2.8rem; font-weight: 800; margin: 15px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
.card-label { font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.9; font-weight: 600; }

/* Subtitle */
.subtitle-text {
    text-align: center;
    font-size: 1.2rem;
    color: #64748b;
    margin-bottom: 40px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

/* Skill Chips */
.skill-chip {
    display: inline-block;
    padding: 8px 16px;
    margin: 6px;
    border-radius: 25px;
    font-size: 15px;
    font-weight: 600;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    transition: transform 0.2s;
}
.skill-chip:hover {
    transform: scale(1.05);
}
@media (prefers-color-scheme: dark) {
    .chip-blue { background: linear-gradient(135deg, #3b82f6, #0ea5e9); color: white; border: none; }
    .chip-green { background: linear-gradient(135deg, #10b981, #34d399); color: white; border: none; }
    .chip-red { background: linear-gradient(135deg, #ef4444, #f87171); color: white; border: none; }
    .chip-gray { background: linear-gradient(135deg, #64748b, #94a3b8); color: white; border: none; }
}
@media (prefers-color-scheme: light) {
    .chip-blue { background: linear-gradient(135deg, #60a5fa, #38bdf8); color: white; border: none; }
    .chip-green { background: linear-gradient(135deg, #34d399, #6ee7b7); color: white; border: none; }
    .chip-red { background: linear-gradient(135deg, #f87171, #fca5a5); color: white; border: none; }
    .chip-gray { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: white; border: none; }
}

/* Empty State Box */
.empty-state-box {
    text-align: center;
    padding: 60px 30px;
    background: linear-gradient(135deg, rgba(255, 126, 95, 0.05) 0%, rgba(254, 180, 123, 0.05) 100%);
    border: 3px dashed #ffb47b;
    border-radius: 25px;
    margin-top: 40px;
    animation: pulseBorder 2s infinite;
}
@keyframes pulseBorder {
    0% { border-color: rgba(255, 180, 123, 0.5); }
    50% { border-color: rgba(255, 126, 95, 1); }
    100% { border-color: rgba(255, 180, 123, 0.5); }
}
.empty-icon { font-size: 5rem; margin-bottom: 20px; }
.empty-title { font-size: 1.8rem; font-weight: 700; color: #ff7e5f; margin-bottom: 10px; }
.empty-desc { font-size: 1.1rem; color: #64748b; }

</style>
""", unsafe_allow_html=True)

def render_chips(skills, chip_class="chip-gray"):
    if not skills:
        return "<p style='color: gray; font-style: italic;'>None detected</p>"
    chips_html = "".join([f"<span class='skill-chip {chip_class}'>{skill}</span>" for skill in skills])
    return f"<div>{chips_html}</div>"


def check_ollama_status():
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "tinyllama:latest")

    try:
        response = httpx.get(f"{ollama_base_url}/api/tags", timeout=5.0)
        response.raise_for_status()
        models = response.json().get("models", [])
        model_names = {model.get("name", "") for model in models}
        return {
            "available": ollama_model in model_names,
            "base_url": ollama_base_url,
            "model": ollama_model,
            "models": sorted(model_names),
            "error": None if ollama_model in model_names else f"Model '{ollama_model}' is not installed.",
        }
    except Exception as exc:
        return {
            "available": False,
            "base_url": ollama_base_url,
            "model": ollama_model,
            "models": [],
            "error": str(exc),
        }


def extract_resume_text(file_path):
    return extract_text(file_path)


def extract_skills(text):
    text = text.lower()
    found_skills = []
    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)
    return sorted(set(found_skills))


def calculate_resume_score(skills):
    return min(len(skills) * 12, 100)


def recommend_job(skills):
    best_job = "Software Developer"
    best_score = -1

    for job_name, target_skills in job_skill_map.items():
        overlap = len(set(skills) & set(target_skills))
        if overlap > best_score:
            best_score = overlap
            best_job = job_name

    return best_job


def analyze_expected_job(skills, expected_job):
    # Use existing map if available, otherwise just return empty target skills for the LLM to figure out
    target_skills = job_skill_map.get(expected_job, [])
    
    if target_skills:
        matched_skills = sorted(set(skills) & set(target_skills))
        missing_skills = sorted(set(target_skills) - set(skills))
        match_score = int((len(matched_skills) / len(target_skills)) * 100)
    else:
        matched_skills = []
        missing_skills = []
        match_score = 0 # Will be overridden by LLM if possible

    return {
        "target_skills": target_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
    }


def build_fallback_guidance(expected_job, recommended_job, gap_analysis):
    matched = ", ".join(gap_analysis["matched_skills"][:6]) or "No strong role-specific matches yet"
    missing = ", ".join(gap_analysis["missing_skills"][:6]) or "No major gaps detected"
    
    # Handle case where user entered custom job without Ollama active
    if not gap_analysis["target_skills"]:
        missing = f"Please enable LLM to get specific missing skills for {expected_job}."

    return {
        "summary": (
            f"Your resume is currently closest to {recommended_job}. "
            f"For {expected_job}, your present match is {gap_analysis['match_score']}%."
        ),
        "strengths": [
            f"Relevant strengths identified: {matched}.",
            "Your resume already includes skills that can be positioned for interviews and applications.",
        ],
        "gaps": [
            f"Important skills to strengthen for {expected_job}: {missing}.",
            "Adding these skills through projects, certifications, or portfolio work will improve your fit.",
        ],
        "next_steps": [
            f"Tailor your resume headline and project section toward {expected_job}.",
            "Highlight measurable outcomes, tools used, and real projects with business impact.",
            "Prepare role-specific interview answers around your strongest matching skills.",
        ],
        "interview_answer": (
            f"I am interested in the {expected_job} role because it aligns with my current skill set and the kind of problems I enjoy solving. "
            f"My background already reflects experience in {matched.lower()}, and I am actively improving the remaining skills needed for this role. "
            f"I can contribute quickly, learn fast, and bring practical project-based experience to the team."
        ),
        "source": "Built-in guidance",
    }


def request_free_llm_guidance(expected_job, recommended_job, skills, gap_analysis):
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_url = os.getenv("OLLAMA_URL", f"{ollama_base_url}/api/generate")
    ollama_model = os.getenv("OLLAMA_MODEL", "tinyllama:latest")

    prompt = f"""
You are a career guidance assistant for a resume analyzer web app.
The user wants to apply for the role: "{expected_job}".
Their current skills extracted from the resume are: {", ".join(skills) or "None"}.
Their closest matching standard role is: "{recommended_job}".

Return ONLY valid JSON with these keys:
- "summary": a short string explaining their fit.
- "strengths": array of 2 to 4 short strings highlighting their best matching areas.
- "gaps": array of 2 to 4 short strings explaining what they should learn next.
- "next_steps": array of 2 to 4 short strings of actionable career advice.
- "interview_answer": a short first-person answer to "Why are you fit for this job?"
- "source": must be exactly "Ollama ({ollama_model})".

Do not include any extra text outside the JSON.
Use these computed facts exactly:
- matched skills: {", ".join(gap_analysis["matched_skills"]) or "None"}
- missing skills: {", ".join(gap_analysis["missing_skills"]) or "None"}
- match score: {gap_analysis["match_score"]}%
"""

    try:
        response = httpx.post(
            ollama_url,
            json={
                "model": ollama_model,
                "prompt": prompt.strip(),
                "stream": False,
                "format": "json",
            },
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        llm_output_text = payload.get("response", "{}").strip()
        
        # Clean up markdown code blocks if the LLM adds them
        if llm_output_text.startswith("```json"):
            llm_output_text = llm_output_text[7:]
        elif llm_output_text.startswith("```"):
            llm_output_text = llm_output_text[3:]
        if llm_output_text.endswith("```"):
            llm_output_text = llm_output_text[:-3]
            
        llm_output = json.loads(llm_output_text.strip())

        fallback = build_fallback_guidance(expected_job, recommended_job, gap_analysis)
        required_keys = {"summary", "strengths", "gaps", "next_steps", "interview_answer"}

        if not required_keys.issubset(llm_output):
            raise ValueError("Incomplete LLM guidance response")

        fallback.update({
            "summary": llm_output["summary"],
            "strengths": llm_output["strengths"],
            "gaps": llm_output["gaps"],
            "next_steps": llm_output["next_steps"],
            "interview_answer": llm_output["interview_answer"],
            "source": f"Ollama ({ollama_model})",
        })

        return fallback, True, gap_analysis
    except Exception as e:
        fallback = build_fallback_guidance(expected_job, recommended_job, gap_analysis)
        fallback["source"] = f"Built-in guidance ({type(e).__name__})"
        fallback["error"] = str(e)
        return fallback, False, gap_analysis


def analyze_uploaded_resume(uploaded_file, expected_job):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    try:
        text = extract_resume_text(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    skills = extract_skills(text)
    score = calculate_resume_score(skills)
    recommended_job = recommend_job(skills)
    gap_analysis = analyze_expected_job(skills, expected_job)
    guidance, llm_enabled, updated_gap_analysis = request_free_llm_guidance(
        expected_job,
        recommended_job,
        skills,
        gap_analysis,
    )

    return {
        "skills": skills,
        "score": score,
        "recommended_job": recommended_job,
        "gap_analysis": updated_gap_analysis,
        "guidance": guidance,
        "llm_enabled": llm_enabled,
    }


# --- MAIN UI LAYOUT ---

st.markdown('<div class="gradient-title">🎯 AI Job & Skill Gap Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Upload your PDF resume, choose your expected role, and get a polished report with detected skills, role match percentage, missing skills, and AI-guided interview prep.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📄 Upload & Setup")
    ollama_status = check_ollama_status()
    
    # Allow custom job input or predefined selection
    job_options = list(job_skill_map.keys()) + ["Other (Type your own)"]
    selected_job = st.selectbox("Select Expected Job Role", job_options)
    
    if selected_job == "Other (Type your own)":
        expected_job = st.text_input("Enter your target job role:")
    else:
        expected_job = selected_job

    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    st.markdown("---")
    if ollama_status["available"]:
        st.success(f"Ollama ready: {ollama_status['model']}")
    else:
        st.warning("Ollama is not fully ready. Built-in guidance will be used if generation fails.")
        if ollama_status["error"]:
            st.caption(ollama_status["error"])

    st.caption("Free LLM mode uses a local Ollama server if available. If not, the app still shows built-in guidance.")

if uploaded_file and expected_job:
    with st.spinner("Analyzing your resume and fetching AI guidance..."):
        result = analyze_uploaded_resume(uploaded_file, expected_job)

    gap_analysis = result["gap_analysis"]
    guidance = result["guidance"]

    st.success("✅ Analysis Complete!")

    # Top Dashboard Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="colorful-card card-score">
            <div class="card-label">Overall Resume Score</div>
            <div class="card-value">{result['score']}/100</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="colorful-card card-match">
            <div class="card-label">Target Match</div>
            <div class="card-value">{gap_analysis['match_score']}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        # Scale down text slightly for longer job titles
        st.markdown(f"""
        <div class="colorful-card card-job">
            <div class="card-label">Best Matched Role</div>
            <div class="card-value" style="font-size: 2.2rem; padding-top: 5px;">{result["recommended_job"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(gap_analysis['match_score'] / 100.0, text=f"Match Progress: {gap_analysis['match_score']}%")
    st.markdown("<hr>", unsafe_allow_html=True)

    # Use Tabs for a cleaner layout
    tab1, tab2, tab3 = st.tabs(["📊 Skill Analysis", "🎯 Role Match", "💡 AI Career Guidance"])

    with tab1:
        st.subheader("Detected Skills")
        st.info(f"We found {len(result['skills'])} skills in your resume matching our database.")
        st.markdown(render_chips(result["skills"], "chip-blue"), unsafe_allow_html=True)

    with tab2:
        st.subheader(f"Comparison: {expected_job}")
        
        col_match, col_miss = st.columns(2)
        with col_match:
            st.markdown("#### ✅ Matched Skills")
            st.markdown(render_chips(gap_analysis["matched_skills"], "chip-green"), unsafe_allow_html=True)
            
        with col_miss:
            st.markdown("#### ❌ Missing Skills")
            st.markdown(render_chips(gap_analysis["missing_skills"], "chip-red"), unsafe_allow_html=True)

    with tab3:
        st.subheader("Career Guidance")
        
        llm_status_badge = "🟢 Live LLM" if result["llm_enabled"] else "🟡 Fallback Mode"
        st.markdown(f"**Source:** `{guidance['source']}` ({llm_status_badge})")
        st.write(guidance["summary"])
        
        if not result["llm_enabled"]:
            st.warning("Ollama response was unavailable. Using built-in offline guidance.")
            if guidance.get("error"):
                st.caption(f"Reason: {guidance['error']}")

        with st.expander("💪 Strengths", expanded=True):
            for item in guidance["strengths"]:
                st.markdown(f"- {item}")

        with st.expander("📉 Skill Gaps", expanded=True):
            for item in guidance["gaps"]:
                st.markdown(f"- {item}")

        with st.expander("🚀 Next Steps", expanded=True):
            for item in guidance["next_steps"]:
                st.markdown(f"- {item}")

        st.markdown("### 🎙️ Interview Prep Answer")
        st.info("Use this as a baseline for 'Why are you a good fit for this role?'")
        st.markdown(f"> *\"{guidance['interview_answer']}\"*")

else:
    # Empty State
    st.markdown("""
        <div class="empty-state-box">
            <div class="empty-icon">📄</div>
            <div class="empty-title">Awaiting Resume Upload</div>
            <div class="empty-desc">Please upload a PDF from the sidebar to begin the analysis.</div>
        </div>
    """, unsafe_allow_html=True)
