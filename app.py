import json
import math
import os
import tempfile
import importlib.util
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for

try:
    from pdfminer.high_level import extract_text
except ImportError:
    extract_text = None

from config import chat_model
from langchain_core.messages import HumanMessage


# ══════════════════════════════════════════════════════════════════
# SKILLS DATA
# ══════════════════════════════════════════════════════════════════

def load_local_skills_data():
    skills_path = Path(__file__).with_name("skills.py")
    spec = importlib.util.spec_from_file_location("local_skills", skills_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load skills module from {skills_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    loaded_job_skill_map = getattr(module, "job_skill_map", None)
    loaded_skills_list   = getattr(module, "skills_list", None)
    if not isinstance(loaded_job_skill_map, dict):
        raise TypeError("skills.py must define job_skill_map as a dict")
    if not isinstance(loaded_skills_list, list):
        raise TypeError("skills.py must define skills_list as a list")
    return loaded_job_skill_map, loaded_skills_list


job_skill_map, skills_list = load_local_skills_data()


# ══════════════════════════════════════════════════════════════════
# ANALYSIS HELPERS
# ══════════════════════════════════════════════════════════════════

def extract_resume_text(file_path: str) -> str:
    if extract_text is None:
        raise RuntimeError("Install pdfminer.six: pip install pdfminer.six")
    return extract_text(file_path)


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    return sorted({s for s in skills_list if s in text_lower})


def calculate_resume_score(skills: list[str], expected_job: str = "") -> int:
    """
    Weighted resume score out of 100.

    Components:
      - Relevance (50 pts): % of target role's required skills present — heaviest factor.
      - Breadth   (30 pts): total distinct skills on resume (log scale).
      - Depth     (20 pts): bonus for well-rounded skill count (log scale).

    Clamped to [10, 98] — no one scores 0 or a perfect 100.
    """
    total = len(skills)
    if total == 0:
        return 10

    breadth = min(30, round(30 * math.log1p(total) / math.log1p(30)))

    target = job_skill_map.get(expected_job, [])
    if target:
        matched_count = len(set(skills) & set(target))
        relevance = round(50 * matched_count / len(target))
    else:
        relevance = min(35, round(total * 2.5))

    depth = min(20, round(20 * math.log1p(total) / math.log1p(20)))

    return max(10, min(98, breadth + relevance + depth))


def recommend_job(skills: list[str]) -> str:
    best_job, best_score = "Software Developer", -1
    for job_name, target in job_skill_map.items():
        overlap = len(set(skills) & set(target))
        if overlap > best_score:
            best_score, best_job = overlap, job_name
    return best_job


def analyze_expected_job(skills: list[str], expected_job: str) -> dict:
    target_skills = job_skill_map.get(expected_job, [])
    if target_skills:
        matched     = sorted(set(skills) & set(target_skills))
        missing     = sorted(set(target_skills) - set(skills))
        match_score = int(len(matched) / len(target_skills) * 100)
    else:
        matched, missing, match_score = [], [], 0
    return {
        "target_skills":  target_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score":    match_score,
    }


# ══════════════════════════════════════════════════════════════════
# FALLBACK GUIDANCE
# ══════════════════════════════════════════════════════════════════

def build_fallback_guidance(expected_job: str, recommended_job: str, gap: dict) -> dict:
    matched = ", ".join(gap["matched_skills"][:6]) or "No strong role-specific matches yet"
    missing = ", ".join(gap["missing_skills"][:6]) or "No major gaps detected"
    return {
        "summary": (
            f"Your resume is currently closest to {recommended_job}. "
            f"For {expected_job}, your present match is {gap['match_score']}%."
        ),
        "strengths": [
            f"Relevant strengths identified: {matched}.",
            "Your resume already includes skills that can be positioned for interviews.",
        ],
        "gaps": [
            f"Important skills to strengthen for {expected_job}: {missing}.",
            "Adding these through projects or certifications will improve your fit.",
        ],
        "free_steps": [
            f"Search YouTube and freeCodeCamp for tutorials on the missing skills: {missing}.",
            "Build a small personal project using your existing skills and push it to GitHub.",
            f"Read the official documentation for tools relevant to {expected_job}.",
            "Practice mock interviews using free platforms like Pramp or interviewing.io.",
        ],
        "paid_steps": [
            f"Enroll in a structured {expected_job} course on Udemy or Coursera (₹500–₹4,000).",
            "Get a role-relevant certification (e.g. AWS, Google, Meta) to signal credibility.",
            "Join a mentorship platform like MentorCruise or Topmate for 1-on-1 guidance.",
            "Use LinkedIn Premium for 1 month to access job insights and recruiter outreach.",
        ],
        "interview_answer": (
            f"I am interested in the {expected_job} role because it aligns with my current "
            f"skill set. My background reflects experience in {matched.lower()}, and I am "
            f"actively improving the remaining skills needed for this role."
        ),
        "source": "Built-in guidance",
    }


# ══════════════════════════════════════════════════════════════════
# AI GUIDANCE — LANGCHAIN + GROQ
# ══════════════════════════════════════════════════════════════════

def request_ai_guidance(
    expected_job: str,
    recommended_job: str,
    skills: list[str],
    gap: dict,
) -> tuple[dict, bool]:
    match_pct   = gap["match_score"]
    matched_str = ", ".join(gap["matched_skills"]) or "none"
    missing_str = ", ".join(gap["missing_skills"]) or "none"
    all_skills  = ", ".join(skills) or "none listed"

    prompt = f"""You are an experienced career coach reviewing a candidate's resume for a specific job role.

CANDIDATE PROFILE
-----------------
Target role      : {expected_job}
Best system match: {recommended_job}
Skills detected  : {all_skills}
Role match score : {match_pct}%
Skills matched   : {matched_str}
Skills missing   : {missing_str}

YOUR TASK
---------
Write honest, specific, human-sounding career guidance. Do NOT use generic filler phrases like
"leverage your skills" or "passionate professional". Be direct, practical, and encouraging.

Return ONLY a valid JSON object with these exact keys — no extra text, no markdown fences:

{{
  "summary": "2-3 sentence honest assessment of how well this candidate fits the {expected_job} role based on their actual skills. Mention the match score naturally.",
  "strengths": [
    "Specific strength 1 tied to an actual skill they have (name the skill)",
    "Specific strength 2 tied to an actual skill or combination of skills",
    "Specific strength 3 if applicable"
  ],
  "gaps": [
    "Specific gap 1 — name the missing skill and briefly explain why it matters for {expected_job}",
    "Specific gap 2 — name the missing skill and suggest a concrete way to fill it",
    "Specific gap 3 if applicable"
  ],
  "free_steps": [
    "Free action step 1 — a specific free resource, platform, or activity (e.g. YouTube channel, official docs, GitHub project, freeCodeCamp, Kaggle). Name the resource explicitly.",
    "Free action step 2 — another free option relevant to the missing skills for {expected_job}",
    "Free action step 3 — a free community, practice platform, or portfolio tip (e.g. Pramp, LeetCode, dev.to)",
    "Free action step 4 — a free resume or profile improvement action (e.g. update LinkedIn, add GitHub README)"
  ],
  "paid_steps": [
    "Paid option 1 — name a specific course on Udemy / Coursera / Pluralsight with approximate price and why it is worth it for {expected_job}",
    "Paid option 2 — a professional certification relevant to {expected_job} (name the cert, exam cost, and value)",
    "Paid option 3 — a mentorship, bootcamp, or coaching service that would accelerate growth",
    "Paid option 4 — a tool subscription or platform (e.g. LinkedIn Premium, DataCamp) that gives a measurable edge"
  ],
  "interview_answer": "A natural, confident 4-6 sentence first-person answer to 'Why are you a good fit for this {expected_job} role?' that references their actual matched skills without sounding rehearsed."
}}"""

    try:
        response = chat_model.invoke([HumanMessage(content=prompt)])
        raw = response.content.strip()

        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]

        llm_output = json.loads(raw.strip())

        required = {"summary", "strengths", "gaps", "free_steps", "paid_steps", "interview_answer"}
        if not required.issubset(llm_output):
            raise ValueError("Incomplete response from LLM")

        guidance = build_fallback_guidance(expected_job, recommended_job, gap)
        guidance.update({
            "summary":          llm_output["summary"],
            "strengths":        llm_output["strengths"],
            "gaps":             llm_output["gaps"],
            "free_steps":       llm_output["free_steps"],
            "paid_steps":       llm_output["paid_steps"],
            "interview_answer": llm_output["interview_answer"],
            "source":           "AI Guidance",
        })
        return guidance, True

    except Exception as exc:
        import traceback
        traceback.print_exc()
        fallback = build_fallback_guidance(expected_job, recommended_job, gap)
        fallback["source"] = f"Built-in guidance ({type(exc).__name__})"
        return fallback, False


# ══════════════════════════════════════════════════════════════════
# FULL PIPELINE
# ══════════════════════════════════════════════════════════════════

def run_analysis(file_storage, expected_job: str) -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file_storage.save(tmp.name)
        tmp_path = tmp.name
    try:
        text = extract_resume_text(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    skills      = extract_skills(text)
    score       = calculate_resume_score(skills, expected_job)
    recommended = recommend_job(skills)
    gap         = analyze_expected_job(skills, expected_job)
    guidance, llm_enabled = request_ai_guidance(expected_job, recommended, skills, gap)

    return {
        "skills":          skills,
        "score":           score,
        "recommended_job": recommended,
        "gap_analysis":    gap,
        "guidance":        guidance,
        "llm_enabled":     llm_enabled,
    }


# ══════════════════════════════════════════════════════════════════
# FLASK APP
# ══════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB


@app.route("/")
def index():
    return render_template("index.html", jobs=list(job_skill_map.keys()))


@app.route("/analyze", methods=["POST"])
def analyze():
    resume_file = request.files.get("resume")
    if not resume_file or resume_file.filename == "":
        return redirect(url_for("index"))

    if not resume_file.filename.lower().endswith(".pdf"):
        return render_template(
            "index.html",
            jobs=list(job_skill_map.keys()),
            error="Only PDF files are supported.",
        )

    expected_job = request.form.get("expected_job", "").strip()
    if not expected_job:
        return redirect(url_for("index"))

    try:
        result = run_analysis(resume_file, expected_job)
    except Exception as exc:
        return render_template(
            "index.html",
            jobs=list(job_skill_map.keys()),
            error=f"Analysis failed: {exc}",
        )

    gap      = result["gap_analysis"]
    guidance = result["guidance"]
    score    = result["score"]

    if score >= 80:
        score_label = ("Excellent", "score-excellent")
    elif score >= 60:
        score_label = ("Good", "score-good")
    elif score >= 40:
        score_label = ("Fair", "score-fair")
    else:
        score_label = ("Needs Work", "score-weak")

    match_score = gap["match_score"]
    if match_score >= 80:
        match_label = ("Strong Match", "match-strong")
    elif match_score >= 50:
        match_label = ("Partial Match", "match-partial")
    else:
        match_label = ("Low Match", "match-low")

    return render_template(
        "result.html",
        expected_job    = expected_job,
        recommended_job = result["recommended_job"],
        score           = score,
        score_label     = score_label,
        match_score     = match_score,
        match_label     = match_label,
        skills          = result["skills"],
        matched_skills  = gap["matched_skills"],
        missing_skills  = gap["missing_skills"],
        guidance        = guidance,
        llm_enabled     = result["llm_enabled"],
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
