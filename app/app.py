import json
import os
import sys
from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.parser import extract_text, extract_contact_info, detect_sections, compute_section_hygiene
from src.matcher import calculate_ats_score, extract_skills, load_taxonomy
from src.analyzer import analyze_skill_gap, generate_learning_roadmap
from src.feedback import audit_action_verbs, audit_ats_hygiene, star_rewrite_suggestion

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="SkillBridge AI - Resume Screener & Skill-Gap Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 24px 32px;
        border-radius: 14px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(30, 58, 138, 0.2);
    }
    .main-header h1 {
        color: white !important;
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #E0E7FF;
        font-size: 1.02rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1E293B;
    }
    .metric-label {
        font-size: 0.88rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .skill-chip {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .chip-matched {
        background-color: #DEF7EC;
        color: #03543F;
        border: 1px solid #31C48D;
    }
    .chip-missing {
        background-color: #FDE8E8;
        color: #9B1C1C;
        border: 1px solid #F98080;
    }
    .chip-secondary {
        background-color: #FEF08A;
        color: #713F12;
        border: 1px solid #FACC15;
    }
    .roadmap-card {
        background: white;
        border-left: 5px solid #3B82F6;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .badge-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================
# BENCHMARKS & SAMPLE LOADER
# ==========================================
@st.cache_data
def load_benchmarks() -> Dict[str, Dict[str, Any]]:
    bench_dir = os.path.join(BASE_DIR, "data", "benchmarks")
    benchmarks = {}
    if os.path.exists(bench_dir):
        for f in os.listdir(bench_dir):
            if f.endswith(".json"):
                path = os.path.join(bench_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        benchmarks[data.get("id", f[:-5])] = data
                except Exception:
                    pass
    return benchmarks


@st.cache_data
def load_sample_resumes() -> Dict[str, str]:
    sample_dir = os.path.join(BASE_DIR, "data", "sample_resumes")
    samples = {}
    if os.path.exists(sample_dir):
        for f in os.listdir(sample_dir):
            if f.endswith(".txt"):
                path = os.path.join(sample_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as sf:
                        samples[f] = sf.read()
                except Exception:
                    pass
    return samples


benchmarks = load_benchmarks()
sample_resumes = load_sample_resumes()


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/resume.png",
        width=64,
    )
    st.markdown("### **SkillBridge AI**")
    st.caption("Automated ATS Resume Screener & Skill-Gap Diagnostic System")
    st.divider()

    st.markdown("#### 🎯 **1. Target Role & Benchmark**")
    benchmark_options = {
        "sde_intern": "Software Development Engineer (SDE-1)",
        "data_scientist": "Data Scientist / Analytics Specialist",
        "frontend_developer": "Frontend Engineer (React / TypeScript)",
        "devops_engineer": "Cloud & DevOps Engineer (Associate)",
        "ml_engineer": "Machine Learning Engineer (Graduate)",
        "fullstack_developer": "Full-Stack Software Engineer",
        "custom": "Custom Job Description (Paste Below)",
    }

    selected_role_key = st.selectbox(
        "Select Target Tech Role:",
        options=list(benchmark_options.keys()),
        format_func=lambda k: benchmark_options[k],
        index=0,
    )

    st.markdown("#### 📂 **2. Fast Test Sample Resumes**")
    sample_options = {
        "none": "Use Uploaded Resume (Upload on right)",
        "cs_fresher_high_match.txt": "⭐ Aarav Sharma (B.Tech CSE - High Match)",
        "data_intern_medium_match.txt": "⚖️ Priya Verma (B.Tech IT - Medium Match)",
        "unformatted_weak_resume.txt": "⚠️ Rahul Kumar (Unformatted - High Risk)",
    }
    selected_sample = st.selectbox(
        "Pre-load Real Student Resume:",
        options=list(sample_options.keys()),
        format_func=lambda k: sample_options[k],
        index=0,
    )

    with st.expander("⚙️ **ATS Scoring Weights Calibration**"):
        st.caption("Adjust sub-score weights according to company hiring priority:")
        w_hard = st.slider("Hard Skills Coverage", 0.1, 0.6, 0.35, 0.05)
        w_sim = st.slider("Semantic / TF-IDF Match", 0.1, 0.5, 0.25, 0.05)
        w_proj = st.slider("Projects & Experience Depth", 0.1, 0.5, 0.20, 0.05)
        w_edu = st.slider("Education Qualifications", 0.05, 0.3, 0.10, 0.05)
        w_fmt = st.slider("ATS Formatting Hygiene", 0.05, 0.3, 0.10, 0.05)
        custom_weights = {
            "hard_skills": w_hard,
            "semantic_similarity": w_sim,
            "projects_experience": w_proj,
            "education": w_edu,
            "formatting_hygiene": w_fmt,
        }

    st.divider()
    st.markdown(
        """
        **Project Details:**  
        🎓 **Author:** Khushi Yadav ([@khushiyadav35](https://github.com/khushiyadav35))  
        🏛️ **Domain:** NLP, Information Retrieval, EdTech  
        📜 **Degree:** B.Tech Computer Science & Engineering  
        ⭐ **Repository:** [GitHub](https://github.com/khushiyadav35/resume-screener-skill-gap-analyzer)
        """
    )


# ==========================================
# MAIN APP HEADER
# ==========================================
st.markdown(
    """
    <div class="main-header">
        <h1>📄 SkillBridge AI: ATS Resume Screener & Skill-Gap Analyzer</h1>
        <p>Empowering engineering students with real-time ATS compatibility scoring, granular skill-gap diagnostics, and structured learning roadmaps.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# INPUT SECTION (RESUME + JOB DESCRIPTION)
# ==========================================
col_resume, col_jd = st.columns(2)

with col_resume:
    st.subheader("1. Candidate Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, or TXT):",
        type=["pdf", "docx", "txt", "md"],
        help="Upload candidate resume in standard formats.",
    )

    resume_text = ""
    source_filename = ""

    if uploaded_file is not None:
        source_filename = uploaded_file.name
        resume_text = extract_text(uploaded_file.getvalue(), source_filename)
        st.success(f"Loaded: `{source_filename}` ({len(resume_text.split())} words)")
    elif selected_sample != "none" and selected_sample in sample_resumes:
        source_filename = selected_sample
        resume_text = sample_resumes[selected_sample]
        st.info(f"Loaded Sample Resume: `{sample_options[selected_sample]}`")
    else:
        # Default placeholder
        if "cs_fresher_high_match.txt" in sample_resumes:
            source_filename = "cs_fresher_high_match.txt"
            resume_text = sample_resumes["cs_fresher_high_match.txt"]
            st.info("Loaded default demo: Aarav Sharma (B.Tech CSE)")

    with st.expander("👁️ View Extracted Resume Plaintext", expanded=False):
        st.text_area("Extracted Resume Text", resume_text, height=220)

with col_jd:
    st.subheader("2. Target Job Description (JD)")

    current_benchmark: Optional[Dict[str, Any]] = None
    if selected_role_key in benchmarks and selected_role_key != "custom":
        current_benchmark = benchmarks[selected_role_key]
        st.markdown(f"**Selected Role:** `{current_benchmark.get('title')}`")
        st.caption(f"**Target Company Tier:** {current_benchmark.get('company_tier')}")
        jd_text = st.text_area(
            "Target Job Description:",
            value=current_benchmark.get("job_description", ""),
            height=260,
        )
    else:
        jd_text = st.text_area(
            "Paste Target Job Description (Requirements, Responsibilities, Skills):",
            value="We are hiring a Software Engineer. Must know Python, SQL, Docker, FastAPI, and Git. Experience with PostgreSQL and Redis is a plus.",
            height=260,
        )


# ==========================================
# EVALUATION & PIPELINE EXECUTION
# ==========================================
if not resume_text.strip():
    st.warning("Please upload a resume or select a sample resume from the sidebar to begin analysis.")
    st.stop()

if not jd_text.strip():
    st.warning("Please enter or select a Job Description.")
    st.stop()

# Run full ATS evaluation
eval_result = calculate_ats_score(
    resume_text,
    jd_text,
    benchmark=current_benchmark,
    weights=custom_weights,
)

contacts = eval_result["contacts"]
sections = eval_result["sections"]
hygiene = eval_result["hygiene"]
sub_scores = eval_result["sub_scores"]
overall_score = eval_result["overall_score"]
tier = eval_result["tier"]

# Run Skill Gap Analysis
target_core = current_benchmark.get("core_skills", []) if current_benchmark else eval_result["matched_skills"]["core"] + eval_result["missing_skills"]["critical"]
target_bonus = current_benchmark.get("bonus_skills", []) if current_benchmark else eval_result["matched_skills"]["bonus"] + eval_result["missing_skills"]["secondary"]
resume_skills_list = extract_skills(resume_text)["skills"]

gap_report = analyze_skill_gap(resume_skills_list, target_core, target_bonus)
roadmap = generate_learning_roadmap(gap_report.priority_skills_to_learn, max_skills=4)
hygiene_audit = audit_ats_hygiene(resume_text, sections, contacts)


# ==========================================
# HERO SCORE BANNER
# ==========================================
st.markdown("---")
col_score, col_stats1, col_stats2, col_stats3, col_stats4 = st.columns([1.5, 1, 1, 1, 1])

with col_score:
    st.markdown(
        f"""
        <div style="background: white; border: 2px solid {eval_result['tier_color']}; border-radius: 12px; padding: 18px; text-align: center;">
            <div style="font-size: 0.88rem; color: #64748B; font-weight: 700; text-transform: uppercase;">Overall ATS Match Score</div>
            <div style="font-size: 2.8rem; font-weight: 900; color: {eval_result['tier_color']}; margin: 4px 0;">{overall_score}%</div>
            <span class="badge-pill" style="background-color: {eval_result['tier_color']}20; color: {eval_result['tier_color']};">
                {eval_result['tier_badge']}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_stats1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #10B981;">{sub_scores['hard_skills']}%</div>
            <div class="metric-label">Hard Skills Match</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_stats2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #3B82F6;">{sub_scores['semantic_similarity']}%</div>
            <div class="metric-label">Semantic Match</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_stats3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #8B5CF6;">{sub_scores['projects_experience']}%</div>
            <div class="metric-label">Project Depth</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_stats4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #F59E0B;">{hygiene_audit['grade']}</div>
            <div class="metric-label">Formatting Grade</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(f"💡 **Assessment Summary:** {eval_result['tier_description']}")


# ==========================================
# DETAILED DIAGNOSTIC TABS
# ==========================================
tab_exec, tab_gap, tab_roadmap, tab_optimizer, tab_export = st.tabs([
    "📊 Executive Scorecard",
    "🎯 Skill-Gap Matrix",
    "🗺️ Learning Roadmap",
    "✍️ Bullet Optimizer",
    "📄 Placement Audit Report",
])

# ------------------------------------------
# TAB 1: EXECUTIVE SCORECARD
# ------------------------------------------
with tab_exec:
    st.markdown("### 📊 Comprehensive ATS Diagnostic Breakdown")
    col_chart, col_details = st.columns([1.3, 1])

    with col_chart:
        categories = [
            "Hard Skills",
            "Semantic Match",
            "Projects Depth",
            "Education Fit",
            "Formatting & Hygiene",
        ]
        values = [
            sub_scores["hard_skills"],
            sub_scores["semantic_similarity"],
            sub_scores["projects_experience"],
            sub_scores["education"],
            sub_scores["formatting_hygiene"],
        ]

        fig_radar = go.Figure(
            data=go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(59, 130, 246, 0.25)",
                line=dict(color="#2563EB", width=2.5),
                marker=dict(size=7, color="#1D4ED8"),
            )
        )
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
            ),
            showlegend=False,
            height=340,
            margin=dict(l=40, r=40, t=20, b=20),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_details:
        st.markdown("#### 👤 Extracted Candidate Profile")
        st.write(f"**Name:** {contacts.get('name') or 'Not Detected'}")
        st.write(f"**Email:** {contacts.get('email') or '❌ Missing'}")
        st.write(f"**Phone:** {contacts.get('phone') or '❌ Missing'}")
        st.write(f"**GitHub:** {contacts.get('github') or '⚠️ Missing'}")
        st.write(f"**LinkedIn:** {contacts.get('linkedin') or '⚠️ Missing'}")
        if contacts.get("portfolio"):
            st.write(f"**Portfolio:** {contacts.get('portfolio')}")

        st.markdown("#### 📋 Section Presence Audit")
        present_secs = hygiene["present_sections"]
        st.write(
            f"**Detected Sections:** {', '.join([s.title() for s in present_secs]) if present_secs else 'None'}"
        )
        if hygiene["missing_core_sections"]:
            st.error(f"Missing Essential Sections: {', '.join([s.title() for s in hygiene['missing_core_sections']])}")
        else:
            st.success("All essential engineering resume sections present!")


# ------------------------------------------
# TAB 2: SKILL-GAP MATRIX
# ------------------------------------------
with tab_gap:
    st.markdown("### 🎯 Skill-Gap Analysis & Domain Competency Breakdown")
    col_gap_left, col_gap_right = st.columns([1, 1])

    with col_gap_left:
        st.markdown("#### ✅ Matched Competencies in Resume")
        if gap_report.matched_skills:
            chips_html = "".join([f'<span class="skill-chip chip-matched">✓ {s}</span>' for s in gap_report.matched_skills])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.info("No matching skills detected from job requirements.")

    with col_gap_right:
        st.markdown("#### 🚨 Missing Critical Skills (Priority to Learn)")
        if gap_report.missing_critical_skills:
            chips_html = "".join([f'<span class="skill-chip chip-missing">✕ {s}</span>' for s in gap_report.missing_critical_skills])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.success("Candidate possesses all core critical skills!")

        if gap_report.missing_secondary_skills:
            st.markdown("##### 💡 Recommended Bonus Skills:")
            chips_bonus_html = "".join([f'<span class="skill-chip chip-secondary">+ {s}</span>' for s in gap_report.missing_secondary_skills])
            st.markdown(chips_bonus_html, unsafe_allow_html=True)

    st.markdown("#### 📊 Domain-by-Domain Coverage")
    cat_data = []
    for cat, info in gap_report.category_breakdown.items():
        cat_data.append({
            "Domain": cat.replace("_", " ").title(),
            "Matched": info["matched_count"],
            "Target Total": info["target_count"],
            "Coverage %": info["coverage_percentage"],
        })
    if cat_data:
        df_cat = pd.DataFrame(cat_data)
        fig_bar = px.bar(
            df_cat,
            x="Domain",
            y="Coverage %",
            color="Coverage %",
            color_continuous_scale="Viridis",
            text="Coverage %",
            range_y=[0, 105],
        )
        fig_bar.update_layout(height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)


# ------------------------------------------
# TAB 3: PERSONALIZED LEARNING ROADMAP
# ------------------------------------------
with tab_roadmap:
    st.markdown("### 🗺️ Tailored Student Skill Acquisition Roadmap")
    st.caption("Closing technical skill gaps with structured timelines, free verified courses, and resume-ready capstone projects.")

    if not roadmap:
        st.success("🎉 Outstanding! Your resume matches all core technical competencies for this role.")
    else:
        for card in roadmap:
            st.markdown(
                f"""
                <div class="roadmap-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #1E3A8A;">Step {card['step']}: Master <strong>{card['skill']}</strong></h4>
                        <span style="background: #EFF6FF; color: #1D4ED8; padding: 4px 10px; border-radius: 12px; font-size: 0.82rem; font-weight: 700;">
                            ⏱️ {card['time_estimate']} | ⚡ {card['difficulty']}
                        </span>
                    </div>
                    <p style="margin-top: 8px; color: #475569; font-size: 0.93rem;">{card['summary']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_m1, col_m2 = st.columns([1.2, 1])
            with col_m1:
                st.markdown("**Structured Milestone Plan:**")
                for ms in card["milestones"]:
                    st.markdown(f"- {ms}")

            with col_m2:
                st.markdown("**Free Learning Resources:**")
                for res in card["free_resources"]:
                    st.markdown(f"- [{res['title']}]({res['url']})")

                st.markdown(f"**Resume Portfolio Project:**")
                proj = card["portfolio_project"]
                st.info(f"**{proj['title']}**: {proj['description']}")
                st.code(f"Resume Bullet: \"{proj['bullet_point']}\"", language="markdown")

            st.divider()


# ------------------------------------------
# TAB 4: BULLET OPTIMIZER & HYGIENE
# ------------------------------------------
with tab_optimizer:
    st.markdown("### ✍️ Action Verb Audit & STAR Bullet Point Enhancer")

    col_opt1, col_opt2 = st.columns(2)

    with col_opt1:
        st.markdown("#### ⚡ Active vs Passive Verb Audit")
        verb_audit = hygiene_audit["action_verb_audit"]
        st.write(f"**Active Strong Verbs Detected ({verb_audit['strong_count']}):**")
        st.write(", ".join(verb_audit["strong_verbs_found"]) if verb_audit["strong_verbs_found"] else "None")

        if verb_audit["weak_verbs_found"]:
            st.warning(f"Passive/Weak Verbs Found ({verb_audit['weak_count']}): {', '.join(verb_audit['weak_verbs_found'])}")
            st.caption("Replace passive verbs with impactful power verbs from engineering disciplines.")
        else:
            st.success("No weak passive verbs detected!")

    with col_opt2:
        st.markdown("#### 🧪 Live STAR Bullet Tester")
        test_bullet = st.text_input(
            "Paste a single resume bullet point to test:",
            value="Worked on backend APIs using FastAPI and helped optimize database queries.",
        )
        if test_bullet:
            res_bullet = star_rewrite_suggestion(test_bullet)
            st.metric("Bullet Quality Score", f"{res_bullet['quality_score']}/100")
            if res_bullet["improvement_feedback"]:
                for tip in res_bullet["improvement_feedback"]:
                    st.warning(tip)
            else:
                st.success("Strong STAR bullet! Combines decisive action verb and quantifiable metric.")

    st.markdown("---")
    st.markdown("#### 🏆 Benchmark Student STAR Transformations")
    for ex in hygiene_audit["star_examples"]:
        with st.expander(f"Role: {ex['role']}"):
            st.markdown(f"❌ **Weak / Passive Version:** `{ex['weak']}`")
            st.markdown(f"✅ **STAR Optimized Version:** `{ex['star']}`")
            st.caption(f"🔍 **Formula:** {ex['breakdown']}")


# ------------------------------------------
# TAB 5: PLACEMENT AUDIT REPORT EXPORT
# ------------------------------------------
with tab_export:
    st.markdown("### 📄 Placement Readiness & ATS Diagnostic Report")
    st.caption("Generate a structured audit report for Training & Placement Cells (TPO) and student portfolios.")

    # Generate Report Content
    report_text = f"""================================================================================
SKILLBRIDGE AI: STUDENT ATS RESUME & SKILL-GAP DIAGNOSTIC REPORT
================================================================================
Generated for: {contacts.get('name') or 'Candidate'}
Target Role: {current_benchmark.get('title') if current_benchmark else 'Custom Job Description'}
Evaluation Date: 2026-11-09

1. EXECUTIVE SUMMARY & PLACEMENT READINESS
--------------------------------------------------------------------------------
Overall ATS Match Score: {overall_score} / 100
Placement Readiness Tier: {eval_result['tier']} ({eval_result['tier_badge']})
Assessment Summary: {eval_result['tier_description']}

Sub-Score Breakdown:
- Hard Technical Skills:       {sub_scores['hard_skills']}%
- Semantic / TF-IDF Match:     {sub_scores['semantic_similarity']}%
- Projects & Experience Depth: {sub_scores['projects_experience']}%
- Education Qualifications:    {sub_scores['education']}%
- Formatting & Contact Hygiene: {sub_scores['formatting_hygiene']}%

2. CONTACTS & RESUME HYGIENE AUDIT
--------------------------------------------------------------------------------
Email: {contacts.get('email') or 'MISSING'}
Phone: {contacts.get('phone') or 'MISSING'}
GitHub: {contacts.get('github') or 'MISSING'}
LinkedIn: {contacts.get('linkedin') or 'MISSING'}
Total Word Count: {hygiene['total_words']} words
Bullet Points Count: {hygiene['bullet_count']}
Quantifiable Metrics Found: {hygiene['metrics_count']} ({', '.join(hygiene['metrics_examples'][:5])})
Formatting Grade: {hygiene_audit['grade']}

3. SKILL GAP MATRIX
--------------------------------------------------------------------------------
Matched Skills ({gap_report.total_matched}):
{', '.join(gap_report.matched_skills) if gap_report.matched_skills else 'None'}

Missing Critical Skills ({len(gap_report.missing_critical_skills)}):
{', '.join(gap_report.missing_critical_skills) if gap_report.missing_critical_skills else 'None'}

Missing Secondary Skills ({len(gap_report.missing_secondary_skills)}):
{', '.join(gap_report.missing_secondary_skills) if gap_report.missing_secondary_skills else 'None'}

4. PRIORITY STUDENT LEARNING ROADMAP
--------------------------------------------------------------------------------
"""
    for idx, card in enumerate(roadmap, start=1):
        report_text += f"\nStep {idx}: Master {card['skill']} ({card['time_estimate']} | {card['difficulty']})\n"
        report_text += f"Summary: {card['summary']}\n"
        report_text += "Milestones:\n"
        for ms in card["milestones"]:
            report_text += f"  - {ms}\n"
        report_text += f"Recommended Project: {card['portfolio_project']['title']}\n"
        report_text += f"STAR Bullet: \"{card['portfolio_project']['bullet_point']}\"\n"

    report_text += """
================================================================================
Report generated by SkillBridge AI | Developed by Khushi Yadav
GitHub: https://github.com/khushiyadav35/resume-screener-skill-gap-analyzer
================================================================================
"""

    st.text_area("Audit Report Preview", report_text, height=320)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="📥 Download Diagnostic Report (.txt)",
            data=report_text,
            file_name=f"SkillBridge_Report_{contacts.get('name') or 'Candidate'}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col_d2:
        json_export = json.dumps(
            {
                "candidate": contacts,
                "overall_score": overall_score,
                "tier": eval_result["tier"],
                "sub_scores": sub_scores,
                "matched_skills": gap_report.matched_skills,
                "missing_skills": gap_report.missing_critical_skills,
                "hygiene": hygiene_audit,
            },
            indent=2,
        )
        st.download_button(
            label="📥 Download Structured JSON Data",
            data=json_export,
            file_name=f"SkillBridge_Data_{contacts.get('name') or 'Candidate'}.json",
            mime="application/json",
            use_container_width=True,
        )
