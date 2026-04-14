from flask import Flask, render_template, request
import json
import os
from pdfminer.high_level import extract_text
import httpx
from werkzeug.utils import secure_filename
from skills import job_skill_map, skills_list

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extract text from PDF
def extract_resume_text(file_path):
    return extract_text(file_path)

# Extract skills
def extract_skills(text):
    text = text.lower()
    found_skills = []
    for skill in skills_list:
        if skill in text:
            found_skills.append(skill)
    return list(set(found_skills))

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
    target_skills = job_skill_map.get(expected_job, [])
    matched_skills = sorted(set(skills) & set(target_skills))
    missing_skills = sorted(set(target_skills) - set(skills))
    match_score = int((len(matched_skills) / len(target_skills)) * 100) if target_skills else 0

    return {
        "target_skills": target_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
    }

def build_fallback_guidance(expected_job, recommended_job, gap_analysis):
    matched = ", ".join(gap_analysis["matched_skills"][:6]) or "No strong role-specific matches yet"
    missing = ", ".join(gap_analysis["missing_skills"][:6]) or "No major gaps detected"

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
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    prompt = f"""
You are a career guidance assistant for a resume analyzer web app.
Return ONLY valid JSON with these keys:
summary, strengths, gaps, next_steps, interview_answer, source

Rules:
- "summary" must be a short string.
- "strengths", "gaps", and "next_steps" must each be arrays of 2 to 4 short strings.
- "interview_answer" must be a short first-person answer suitable for "Why are you fit for this job?"
- "source" must be "Ollama ({ollama_model})".

Candidate skills: {", ".join(skills) or "None"}
Expected job: {expected_job}
Recommended job: {recommended_job}
Matched skills for expected job: {", ".join(gap_analysis["matched_skills"]) or "None"}
Missing skills for expected job: {", ".join(gap_analysis["missing_skills"]) or "None"}
Match score: {gap_analysis["match_score"]}%
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
            timeout=25.0,
        )
        response.raise_for_status()
        payload = response.json()
        llm_output = json.loads(payload.get("response", "{}"))

        required_keys = {"summary", "strengths", "gaps", "next_steps", "interview_answer", "source"}
        if not required_keys.issubset(llm_output):
            raise ValueError("Incomplete LLM response")

        return llm_output, True
    except Exception:
        return build_fallback_guidance(expected_job, recommended_job, gap_analysis), False

@app.route('/')
def home():
    return render_template('index.html', jobs=job_skill_map.keys())

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('resume')
    expected_job = request.form.get('expected_job', '').strip() or "Software Developer"

    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    if not filename.lower().endswith(".pdf"):
        return "Please upload a PDF resume", 400

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    text = extract_resume_text(path)
    skills = extract_skills(text)
    score = calculate_resume_score(skills)
    recommended_job = recommend_job(skills)
    gap_analysis = analyze_expected_job(skills, expected_job)
    guidance, llm_enabled = request_free_llm_guidance(
        expected_job,
        recommended_job,
        skills,
        gap_analysis,
    )

    return render_template('result.html',
                           skills=skills,
                           score=score,
                           jobs=job_skill_map.keys(),
                           expected_job=expected_job,
                           recommended_job=recommended_job,
                           target_skills=gap_analysis["target_skills"],
                           matched_skills=gap_analysis["matched_skills"],
                           missing_skills=gap_analysis["missing_skills"],
                           match_score=gap_analysis["match_score"],
                           guidance=guidance,
                           llm_enabled=llm_enabled)

if __name__ == '__main__':
    app.run(debug=True)
