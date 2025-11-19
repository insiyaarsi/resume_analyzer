"""
Enhanced Gradio interface for ResumeForge.
Features: ATS simulation, side-by-side comparison, detailed analysis.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr
import tempfile
from datetime import datetime
from app.services.pdf_parser import PDFParser
from app.services.nlp_analyzer import NLPAnalyzer
from app.services.scorer import ResumeScorer
from app.services.ats_simulator import ATSSimulator, ATSSystem
from app.models.schemas import ParsedResume, JobDescription


class ResumeForgeApp:
    """Enhanced Gradio application for ResumeForge."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.nlp_analyzer = NLPAnalyzer()
        self.scorer = ResumeScorer()
        self.ats_simulator = ATSSimulator()
        self.current_resume = None  # Store for comparison
    
    def analyze_resume(self, pdf_file, job_description_text, ats_system_choice):
        """
        Main analysis function with ATS simulation.
        """
        if pdf_file is None:
            return self._empty_results()
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_file)
                tmp_path = tmp.name
            
            # Parse PDF
            text = self.pdf_parser.extract_text(tmp_path)
            contact_info = self.pdf_parser.extract_contact_info(text)
            sections = self.pdf_parser.detect_sections(text)
            metadata = self.pdf_parser.get_metadata(tmp_path)
            
            # Extract structured data
            skills = self.nlp_analyzer.extract_skills(text)
            
            experience_text = self.pdf_parser.extract_section_text(text, "experience")
            experiences = self.nlp_analyzer.extract_experience(text, experience_text)
            
            education_text = self.pdf_parser.extract_section_text(text, "education")
            educations = self.nlp_analyzer.extract_education(text, education_text)
            
            # Create ParsedResume object
            parsed_resume = ParsedResume(
                raw_text=text,
                contact_info=contact_info,
                experience=experiences,
                education=educations,
                skills=skills,
                sections={name: text[start:end] for name, (start, end) in sections.items()},
                metadata=metadata
            )
            
            # Store for comparison
            self.current_resume = parsed_resume
            
            # Format outputs
            basic_analysis = self._format_basic_analysis(parsed_resume)
            skills_analysis = self._format_skills_analysis(parsed_resume)
            experience_analysis = self._format_experience_analysis(parsed_resume)
            
            # ATS Simulation
            ats_analysis = self._format_ats_analysis(
                parsed_resume, 
                ats_system_choice
            )
            
            # Job matching (if provided)
            if job_description_text and len(job_description_text.strip()) > 50:
                job_match = self._analyze_job_match(parsed_resume, job_description_text)
            else:
                job_match = "**No job description provided.**\n\nAdd a job description to see match analysis and optimization suggestions."
            
            # Comparison view
            comparison = self._format_comparison_view(parsed_resume, job_description_text)
            
            # Clean up temp file
            Path(tmp_path).unlink()
            
            return basic_analysis, skills_analysis, experience_analysis, ats_analysis, job_match, comparison
            
        except Exception as e:
            error_msg = f"❌ **Error analyzing resume:** {str(e)}\n\n"
            error_msg += "**Troubleshooting:**\n"
            error_msg += "- Ensure the PDF is not corrupted\n"
            error_msg += "- Try a different PDF format\n"
            error_msg += "- Check that the file is a valid resume\n"
            return error_msg, "", "", "", "", ""
    
    def _empty_results(self):
        """Return empty results for all tabs."""
        empty = "**Please upload a resume PDF to begin analysis.**"
        return empty, empty, empty, empty, empty, empty
    
    def _format_basic_analysis(self, resume: ParsedResume) -> str:
        """Format basic resume information."""
        output = "# 📄 Resume Analysis Overview\n\n"
        
        # Quick stats box
        output += "## Quick Stats\n\n"
        output += "| Metric | Value |\n"
        output += "|--------|-------|\n"
        output += f"| **Resume Length** | {len(resume.raw_text):,} characters |\n"
        output += f"| **Skills Detected** | {len(resume.skills)} |\n"
        output += f"| **Work Experience** | {len(resume.experience)} positions |\n"
        output += f"| **Education** | {len(resume.education)} entries |\n"
        output += f"| **Sections Found** | {len(resume.sections)} |\n\n"
        
        # Contact Info
        output += "## 📧 Contact Information\n\n"
        contact_found = False
        
        if resume.contact_info.get("email"):
            output += f"✅ **Email:** {resume.contact_info['email']}\n\n"
            contact_found = True
        else:
            output += f"❌ **Email:** Not found (Critical for ATS)\n\n"
        
        if resume.contact_info.get("phone"):
            output += f"✅ **Phone:** {resume.contact_info['phone']}\n\n"
            contact_found = True
        else:
            output += f"⚠️ **Phone:** Not found\n\n"
        
        if resume.contact_info.get("linkedin"):
            output += f"✅ **LinkedIn:** {resume.contact_info['linkedin']}\n\n"
            contact_found = True
        
        if resume.contact_info.get("github"):
            output += f"✅ **GitHub:** {resume.contact_info['github']}\n\n"
            contact_found = True
        
        if resume.contact_info.get("location"):
            output += f"📍 **Location:** {resume.contact_info['location']}\n\n"
        
        if not contact_found:
            output += "⚠️ **Warning:** Missing critical contact information\n\n"
        
        # Sections detected
        output += "## 📑 Resume Structure\n\n"
        if resume.sections:
            output += f"**Sections Found:** {', '.join(resume.sections.keys())}\n\n"
        else:
            output += "⚠️ No clear sections detected - consider adding headers\n\n"
        
        # Quality indicators
        output += "## 🎯 Quality Indicators\n\n"
        
        quality_checks = []
        if len(resume.skills) >= 10:
            quality_checks.append("✅ Strong skills section (10+ skills)")
        elif len(resume.skills) >= 5:
            quality_checks.append("⚠️ Adequate skills (5-9 skills) - consider adding more")
        else:
            quality_checks.append("❌ Weak skills section (<5 skills)")
        
        if len(resume.experience) >= 3:
            quality_checks.append("✅ Solid work history (3+ positions)")
        elif len(resume.experience) >= 1:
            quality_checks.append("⚠️ Limited work history (1-2 positions)")
        else:
            quality_checks.append("❌ No work experience detected")
        
        if len(resume.education) >= 1:
            quality_checks.append("✅ Education section present")
        else:
            quality_checks.append("⚠️ No education detected")
        
        # Check for metrics in experience
        has_metrics = False
        for exp in resume.experience:
            if any(char.isdigit() for desc in exp.description for char in desc):
                has_metrics = True
                break
        
        if has_metrics:
            quality_checks.append("✅ Contains quantifiable achievements")
        else:
            quality_checks.append("⚠️ Missing quantifiable metrics - add numbers!")
        
        output += "\n".join(quality_checks) + "\n\n"
        
        return output
    
    def _format_skills_analysis(self, resume: ParsedResume) -> str:
        """Format detailed skills analysis."""
        output = "# 💻 Skills Analysis\n\n"
        
        if not resume.skills:
            output += "❌ **No skills detected.**\n\n"
            output += "**Recommendations:**\n"
            output += "- Add a dedicated 'Skills' section\n"
            output += "- List technical skills explicitly\n"
            output += "- Include both hard and soft skills\n"
            return output
        
        output += f"**Total Skills Identified:** {len(resume.skills)}\n\n"
        
        # Group skills by category
        from collections import defaultdict
        skills_by_category = defaultdict(list)
        
        for skill in resume.skills:
            category = skill.category if skill.category else "other"
            skills_by_category[category].append(skill)
        
        # Technical skills first
        tech_categories = [k for k in skills_by_category.keys() if k.startswith("technical_")]
        other_categories = [k for k in skills_by_category.keys() if not k.startswith("technical_")]
        
        sorted_categories = sorted(tech_categories, key=lambda x: len(skills_by_category[x]), reverse=True)
        sorted_categories.extend(sorted(other_categories, key=lambda x: len(skills_by_category[x]), reverse=True))
        
        for category in sorted_categories:
            skills = skills_by_category[category]
            category_name = category.replace("technical_", "").replace("_", " ").title()
            
            output += f"### {category_name} ({len(skills)} skills)\n\n"
            
            # Show all skills in this category with confidence bars
            sorted_skills = sorted(skills, key=lambda x: x.confidence, reverse=True)
            
            for skill in sorted_skills[:20]:  # Show up to 20 per category
                confidence_bar = "█" * int(skill.confidence * 10)
                confidence_pct = f"{skill.confidence:.0%}"
                output += f"- **{skill.name}** `{confidence_bar}` {confidence_pct}\n"
            
            if len(skills) > 20:
                output += f"\n*...and {len(skills) - 20} more skills in this category*\n"
            
            output += "\n"
        
        # Top 10 overall
        output += "### 🏆 Top 10 Skills (Overall)\n\n"
        top_skills = sorted(resume.skills, key=lambda x: x.confidence, reverse=True)[:10]
        
        for i, skill in enumerate(top_skills, 1):
            output += f"{i}. **{skill.name}** ({skill.confidence:.0%} confidence)\n"
        
        output += "\n"
        
        return output
    
    def _format_experience_analysis(self, resume: ParsedResume) -> str:
        """Format experience analysis with metrics detection."""
        output = "# 💼 Experience Analysis\n\n"
        
        if not resume.experience:
            output += "❌ **No work experience detected.**\n\n"
            output += "**This could be due to:**\n"
            output += "- Non-standard formatting\n"
            output += "- Missing date ranges\n"
            output += "- No clear section headers\n"
            return output
        
        output += f"**Total Positions:** {len(resume.experience)}\n\n"
        
        # Analyze metrics across all experiences
        total_bullets = sum(len(exp.description) for exp in resume.experience)
        bullets_with_numbers = sum(
            1 for exp in resume.experience 
            for desc in exp.description 
            if any(char.isdigit() for char in desc)
        )
        
        if total_bullets > 0:
            metrics_percentage = (bullets_with_numbers / total_bullets) * 100
            output += f"**Quantifiable Achievements:** {bullets_with_numbers}/{total_bullets} bullets ({metrics_percentage:.0f}%)\n"
            
            if metrics_percentage >= 60:
                output += "✅ Excellent use of metrics!\n\n"
            elif metrics_percentage >= 40:
                output += "⚠️ Good, but add more quantifiable achievements\n\n"
            else:
                output += "❌ Add more numbers and metrics to strengthen impact\n\n"
        
        # Detail each position
        for i, exp in enumerate(resume.experience, 1):
            output += f"## Position {i}\n\n"
            
            if exp.title:
                output += f"**Title:** {exp.title}\n\n"
            else:
                output += f"**Title:** *Not detected*\n\n"
            
            if exp.company:
                output += f"**Company:** {exp.company}\n\n"
            else:
                output += f"**Company:** *Not detected*\n\n"
            
            if exp.duration:
                output += f"**Duration:** {exp.duration}\n\n"
            
            if exp.skills_used:
                output += f"**Technologies Used:** {', '.join(exp.skills_used[:10])}"
                if len(exp.skills_used) > 10:
                    output += f" (+{len(exp.skills_used)-10} more)"
                output += "\n\n"
            
            if exp.description:
                output += f"**Responsibilities & Achievements** ({len(exp.description)} items):\n\n"
                
                for j, desc in enumerate(exp.description[:5], 1):
                    # Check if this bullet has metrics
                    has_numbers = any(char.isdigit() for char in desc)
                    icon = "📊" if has_numbers else "•"
                    
                    output += f"{icon} {desc}\n\n"
                
                if len(exp.description) > 5:
                    output += f"*...and {len(exp.description) - 5} more bullet points*\n\n"
            
            output += "---\n\n"
        
        return output
    
    def _format_ats_analysis(self, resume: ParsedResume, ats_system: str) -> str:
        """Format ATS simulation analysis."""
        output = "# 🤖 ATS Compatibility Analysis\n\n"
        
        # Map dropdown choice to enum
        ats_map = {
            "Workday": ATSSystem.WORKDAY,
            "Greenhouse": ATSSystem.GREENHOUSE,
            "Lever": ATSSystem.LEVER,
            "Taleo (Oracle)": ATSSystem.TALEO,
            "iCIMS": ATSSystem.ICIMS,
            "Jobvite": ATSSystem.JOBVITE,
            "All Systems": None
        }
        
        selected_ats = ats_map.get(ats_system)
        
        if selected_ats:
            # Simulate single ATS
            result = self.ats_simulator.simulate_ats_parsing(
                resume.raw_text,
                resume.contact_info,
                resume.sections,
                resume.metadata,
                selected_ats
            )
            
            output += f"## {result['ats_system']} Analysis\n\n"
            
            # Score with visual indicator
            score = result['compatibility_score']
            if score >= 90:
                score_color = "🟢"
            elif score >= 70:
                score_color = "🟡"
            else:
                score_color = "🔴"
            
            output += f"### Compatibility Score: {score_color} {score}/100\n\n"
            
            # Grade
            grade = self.ats_simulator._get_grade(score)
            output += f"**Grade:** {grade}\n\n"
            
            # Issues
            if result['issues']:
                output += "### ❌ Critical Issues\n\n"
                for issue in result['issues']:
                    output += f"- {issue}\n"
                output += "\n"
            
            # Warnings
            if result['warnings']:
                output += "### ⚠️ Warnings\n\n"
                for warning in result['warnings']:
                    output += f"- {warning}\n"
                output += "\n"
            
            # Recommendations
            if result['recommendations']:
                output += "### 💡 Recommendations\n\n"
                for i, rec in enumerate(result['recommendations'], 1):
                    output += f"{i}. {rec}\n"
                output += "\n"
            
            # Capabilities
            output += "### ATS Capabilities\n\n"
            caps = result['capabilities']
            output += f"- **Two-column support:** {'✅ Yes' if caps['handles_two_columns'] else '❌ No'}\n"
            output += f"- **Table support:** {'✅ Yes' if caps['handles_tables'] else '❌ No'}\n"
            output += f"- **Graphics support:** {'✅ Yes' if caps['handles_graphics'] else '❌ No'}\n"
            output += f"- **Max file size:** {caps['max_file_size_mb']}MB\n"
            output += f"- **Formatting strictness:** {'🔴 Strict' if caps['strict_formatting'] else '🟢 Flexible'}\n\n"
            
        else:
            # Simulate all ATS systems
            results = self.ats_simulator.simulate_all_ats(
                resume.raw_text,
                resume.contact_info,
                resume.sections,
                resume.metadata
            )
            
            output += f"## Overall Compatibility: {results['average_compatibility']}/100\n\n"
            output += f"**Grade:** {results['overall_grade']}\n\n"
            
            output += f"**Best Compatibility:** {results['best_compatibility'][0]} ({results['best_compatibility'][1]}/100)\n\n"
            output += f"**Worst Compatibility:** {results['worst_compatibility'][0]} ({results['worst_compatibility'][1]}/100)\n\n"
            
            output += "### Individual ATS Scores\n\n"
            output += "| ATS System | Score | Grade |\n"
            output += "|------------|-------|-------|\n"
            
            sorted_results = sorted(
                results['individual_results'].items(),
                key=lambda x: x[1]['compatibility_score'],
                reverse=True
            )
            
            for ats_name, data in sorted_results:
                score = data['compatibility_score']
                grade = self.ats_simulator._get_grade(score)
                
                if score >= 90:
                    icon = "🟢"
                elif score >= 70:
                    icon = "🟡"
                else:
                    icon = "🔴"
                
                output += f"| {ats_name} | {icon} {score}/100 | {grade} |\n"
            
            output += "\n"
            
            # Common issues across all systems
            all_issues = set()
            for data in results['individual_results'].values():
                all_issues.update(data['issues'])
            
            if all_issues:
                output += "### 🚨 Common Issues (Fix These First)\n\n"
                for issue in all_issues:
                    output += f"- {issue}\n"
                output += "\n"
        
        return output
    
    def _analyze_job_match(self, resume: ParsedResume, job_text: str) -> str:
        """Analyze resume against job description."""
        output = "# 🎯 Job Match Analysis\n\n"
        
        # Extract skills from job description
        job_skills = self.nlp_analyzer.extract_skills(job_text)
        
        # Create job description object
        job_description = JobDescription(
            title="Target Position",
            description=job_text,
            required_skills=[s.name for s in job_skills if s.confidence > 0.85][:20],
            preferred_skills=[s.name for s in job_skills if s.confidence <= 0.85][:15]
        )
        
        # Calculate score
        score = self.scorer.calculate_score(resume, job_description)
        
        # Overall score with visual
        overall = score.overall_score
        if overall >= 80:
            emoji = "🟢"
            verdict = "Excellent Match"
        elif overall >= 60:
            emoji = "🟡"
            verdict = "Good Match"
        else:
            emoji = "🔴"
            verdict = "Needs Improvement"
        
        output += f"## Overall Match: {emoji} {overall:.1f}/100\n"
        output += f"**Verdict:** {verdict}\n\n"
        
        # Score breakdown chart
        output += "### Score Breakdown\n\n"
        output += "| Category | Score | Status |\n"
        output += "|----------|-------|--------|\n"
        
        scores = [
            ("Skills Match", score.skills_match),
            ("Experience Relevance", score.experience_match),
            ("Impact & Metrics", score.impact_score),
            ("ATS Compatibility", score.ats_compatibility)
        ]
        
        for category, value in scores:
            bar = "█" * int(value / 10)
            status = "✅" if value >= 70 else "⚠️" if value >= 50 else "❌"
            output += f"| {category} | {bar} {value:.1f}/100 | {status} |\n"
        
        output += "\n"
        
        # Skills matched
        if score.skills_matched:
            output += f"### ✅ Matching Skills ({len(score.skills_matched)})\n\n"
            
            # Group in columns for better display
            for i in range(0, len(score.skills_matched[:20]), 2):
                skills_pair = score.skills_matched[i:i+2]
                output += f"- {skills_pair[0]}"
                if len(skills_pair) > 1:
                    output += f" | {skills_pair[1]}"
                output += "\n"
            
            if len(score.skills_matched) > 20:
                output += f"\n*...and {len(score.skills_matched) - 20} more matching skills*\n"
            output += "\n"
        
        # Missing skills (high priority)
        if score.skills_missing:
            output += f"### ❌ Missing Skills ({len(score.skills_missing)})\n\n"
            output += "**Add these to improve your match:**\n\n"
            
            for i, skill in enumerate(score.skills_missing[:15], 1):
                output += f"{i}. **{skill}**\n"
            
            if len(score.skills_missing) > 15:
                output += f"\n*...and {len(score.skills_missing) - 15} more*\n"
            output += "\n"
        
        # Strengths
        if score.strengths:
            output += "### 💪 Your Strengths\n\n"
            for strength in score.strengths:
                output += f"✓ {strength}\n"
            output += "\n"
        
        # Areas for improvement
        if score.weaknesses:
            output += "### 📈 Areas for Improvement\n\n"
            for i, weakness in enumerate(score.weaknesses, 1):
                output += f"{i}. {weakness}\n"
            output += "\n"
        
        return output
    
    def _format_comparison_view(self, resume: ParsedResume, job_text: str) -> str:
        """Create side-by-side comparison view."""
        output = "# 🔄 Side-by-Side Comparison\n\n"
        
        if not job_text or len(job_text.strip()) < 50:
            output += "**Add a job description to see side-by-side comparison.**\n\n"
            output += "This view will show:\n"
            output += "- Your skills vs. required skills\n"
            output += "- Experience alignment\n"
            output += "- Gap analysis\n"
            return output
        
        # Extract job requirements
        job_skills = self.nlp_analyzer.extract_skills(job_text)
        job_skills_set = set(s.name for s in job_skills)
        resume_skills_set = set(s.name for s in resume.skills)
        
        matched = resume_skills_set.intersection(job_skills_set)
        missing = job_skills_set - resume_skills_set
        extra = resume_skills_set - job_skills_set
        
        # Skills comparison table
        output += "## Skills Comparison\n\n"
        output += "| Your Skills | Status | Job Requirements |\n"
        output += "|-------------|--------|------------------|\n"
        
        # Show matched skills
        matched_list = sorted(list(matched))
        missing_list = sorted(list(missing))
        
        max_rows = max(len(matched_list), len(missing_list))
        
        for i in range(min(max_rows, 15)):
            your_skill = matched_list[i] if i < len(matched_list) else ""
            job_skill = missing_list[i] if i < len(missing_list) else ""
            status = "✅" if your_skill else "❌"
            
            output += f"| {your_skill} | {status} | {job_skill} |\n"
        
        if max_rows > 15:
            output += f"| *+{max_rows - 15} more* | ... | *+{max(0, len(missing_list) - 15)} more* |\n"
        
        output += "\n"
        
        # Match percentage
        if len(job_skills_set) > 0:
            match_pct = (len(matched) / len(job_skills_set)) * 100
            output += f"**Skills Match Rate:** {match_pct:.1f}% ({len(matched)}/{len(job_skills_set)} required skills)\n\n"
        
        # Experience keywords comparison
        output += "## Experience Keywords\n\n"
        
        all_exp_text = " ".join([" ".join(exp.description) for exp in resume.experience])
        job_keywords = self.nlp_analyzer.extract_keywords(job_text, top_n=15)
        
        output += "**Top Job Description Keywords:**\n\n"
        for keyword, freq in job_keywords[:10]:
            in_resume = keyword in all_exp_text.lower()
            status = "✅" if in_resume else "❌"
            output += f"- {status} **{keyword}** (mentioned {freq}x in job posting)\n"
        
        output += "\n"
        
        # Recommendations
        output += "## 🎯 Optimization Strategy\n\n"
        
        if len(matched) < len(job_skills_set) * 0.5:
            output += "**Priority: High** - Significant skill gaps detected\n\n"
            output += "1. Add the missing skills to your Skills section\n"
            output += "2. Incorporate these skills into your experience bullets\n"
            output += "3. Consider gaining experience with priority technologies\n\n"
        elif len(matched) < len(job_skills_set) * 0.7:
            output += "**Priority: Medium** - Good match, but room for improvement\n\n"
            output += "1. Emphasize matching skills more prominently\n"
            output += "2. Add missing skills if you have experience\n"
            output += "3. Quantify achievements related to key skills\n\n"
        else:
            output += "**Priority: Low** - Strong match!\n\n"
            output += "1. Fine-tune wording to match job description\n"
            output += "2. Add metrics to strengthen impact\n"
            output += "3. Ensure ATS compatibility\n\n"
        
        return output
    
    def create_interface(self):
        """Create enhanced Gradio interface."""
        
        # Custom CSS for better styling
        custom_css = """
        .output-markdown h1 { color: #2563eb; margin-top: 1em; }
        .output-markdown h2 { color: #3b82f6; margin-top: 0.8em; }
        .output-markdown h3 { color: #60a5fa; margin-top: 0.6em; }
        .output-markdown table { border-collapse: collapse; width: 100%; }
        .output-markdown th, .output-markdown td { padding: 8px; text-align: left; border: 1px solid #ddd; }
        .output-markdown th { background-color: #f3f4f6; }
        """
        
        with gr.Blocks(
            title="ResumeForge - AI Resume Analyzer",
            theme=gr.themes.Soft(),
            css=custom_css
        ) as interface:
            
            gr.Markdown("""
            # ResumeForge 🚀
            ### AI-Powered Resume Analysis, ATS Simulation & Optimization
            
            Upload your resume to get comprehensive analysis including skills extraction, 
            experience parsing, ATS compatibility testing, and job matching.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📤 Upload & Configure")
                    
                    pdf_input = gr.File(
                        label="Resume (PDF)",
                        file_types=[".pdf"],
                        type="binary"
                    )
                    
                    ats_choice = gr.Dropdown(
                        label="ATS System to Simulate",
                        choices=[
                            "Workday",
                            "Greenhouse",
                            "Lever",
                            "Taleo (Oracle)",
                            "iCIMS",
                            "Jobvite",
                            "All Systems"
                        ],
                        value="Workday",
                        info="Select which ATS to test against"
                    )
                    
                    job_input = gr.Textbox(
                        label="Job Description (Optional)",
                        placeholder="Paste the full job description here for detailed matching analysis...",
                        lines=12
                    )
                    
                    analyze_btn = gr.Button(
                        "🔍 Analyze Resume",
                        variant="primary",
                        size="lg"
                    )
                    
                    gr.Markdown("""
                    ---
                    **💡 Pro Tips:**
                    - Upload in PDF format for best results
                    - Include a job description for match analysis
                    - Try different ATS systems to see variations
                    """)
                
                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.Tab("📊 Overview"):
                            basic_output = gr.Markdown()
                        
                        with gr.Tab("💻 Skills"):
                            skills_output = gr.Markdown()
                        
                        with gr.Tab("💼 Experience"):
                            experience_output = gr.Markdown()
                        
                        with gr.Tab("🤖 ATS Compatibility"):
                            ats_output = gr.Markdown()
                        
                        with gr.Tab("🎯 Job Match"):
                            job_match_output = gr.Markdown()
                        
                        with gr.Tab("🔄 Comparison"):
                            comparison_output = gr.Markdown()
            
            gr.Markdown("""
            ---
            ### About ResumeForge
            
            ResumeForge uses advanced NLP and machine learning to analyze your resume:
            - **Skills Extraction:** Identifies 300+ technical and soft skills with confidence scoring
            - **ATS Simulation:** Tests compatibility with 6 major applicant tracking systems
            - **Job Matching:** Calculates fit score and identifies gaps
            - **Side-by-Side Comparison:** Shows exactly what to improve
            
            **Privacy:** All processing happens locally. No data is stored or transmitted.
            
            *Built with FastAPI, spaCy, Hugging Face Transformers, and Gradio*
            """)
            
            # Connect button to function
            analyze_btn.click(
                fn=self.analyze_resume,
                inputs=[pdf_input, job_input, ats_choice],
                outputs=[
                    basic_output,
                    skills_output,
                    experience_output,
                    ats_output,
                    job_match_output,
                    comparison_output
                ]
            )
        
        return interface


def main():
    """Launch enhanced Gradio app."""
    app = ResumeForgeApp()
    interface = app.create_interface()
    
    print("\n" + "="*70)
    print("🚀 ResumeForge - Enhanced Interface with ATS Simulation")
    print("="*70)
    print("\nFeatures:")
    print("  ✓ Advanced skills extraction (300+ skills)")
    print("  ✓ ATS compatibility testing (6 systems)")
    print("  ✓ Job matching with gap analysis")
    print("  ✓ Side-by-side comparison view")
    print("  ✓ Metrics detection in experience")
    print("  ✓ Actionable recommendations")
    print("\n" + "="*70 + "\n")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()