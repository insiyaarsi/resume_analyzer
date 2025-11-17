"""
Gradio interface for ResumeForge.
Quick MVP for testing the NLP pipeline.
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
from app.models.schemas import ParsedResume, JobDescription


class ResumeForgeApp:
    """Gradio application for ResumeForge."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.nlp_analyzer = NLPAnalyzer()
        self.scorer = ResumeScorer()
    
    def analyze_resume(self, pdf_file, job_description_text):
        """
        Main analysis function.
        Takes PDF file and job description, returns analysis.
        """
        if pdf_file is None:
            return "Please upload a resume PDF.", "", "", ""
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(pdf_file)
                tmp_path = tmp.name
            
            # Parse PDF
            text = self.pdf_parser.extract_text(tmp_path)
            contact_info = self.pdf_parser.extract_contact_info(text)
            sections = self.pdf_parser.detect_sections(text)
            
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
                metadata=self.pdf_parser.get_metadata(tmp_path)
            )
            
            # Format basic analysis
            basic_analysis = self._format_basic_analysis(parsed_resume)
            
            # Skills analysis
            skills_analysis = self._format_skills_analysis(parsed_resume)
            
            # Experience analysis
            experience_analysis = self._format_experience_analysis(parsed_resume)
            
            # Job matching (if provided)
            if job_description_text and len(job_description_text.strip()) > 50:
                job_match = self._analyze_job_match(parsed_resume, job_description_text)
            else:
                job_match = "**No job description provided.**\n\nAdd a job description to see match analysis."
            
            # Clean up temp file
            Path(tmp_path).unlink()
            
            return basic_analysis, skills_analysis, experience_analysis, job_match
            
        except Exception as e:
            return f"Error analyzing resume: {str(e)}", "", "", ""
    
    def _format_basic_analysis(self, resume: ParsedResume) -> str:
        """Format basic resume information."""
        output = "# Resume Analysis\n\n"
        
        # Contact Info
        output += "## Contact Information\n"
        if resume.contact_info.get("email"):
            output += f"- **Email:** {resume.contact_info['email']}\n"
        if resume.contact_info.get("phone"):
            output += f"- **Phone:** {resume.contact_info['phone']}\n"
        if resume.contact_info.get("linkedin"):
            output += f"- **LinkedIn:** {resume.contact_info['linkedin']}\n"
        if resume.contact_info.get("github"):
            output += f"- **GitHub:** {resume.contact_info['github']}\n"
        if resume.contact_info.get("location"):
            output += f"- **Location:** {resume.contact_info['location']}\n"
        
        if not any(resume.contact_info.values()):
            output += "*No contact information detected*\n"
        output += "\n"
        
        # Sections found
        output += "## Sections Detected\n"
        if resume.sections:
            output += f"Found {len(resume.sections)} sections: {', '.join(resume.sections.keys())}\n\n"
        else:
            output += "*No clear sections detected*\n\n"
        
        # Summary stats
        output += "## Summary Statistics\n"
        output += f"- **Total Characters:** {len(resume.raw_text):,}\n"
        output += f"- **Skills Identified:** {len(resume.skills)}\n"
        output += f"- **Work Experiences:** {len(resume.experience)}\n"
        output += f"- **Education Entries:** {len(resume.education)}\n"
        
        return output
    
    def _format_skills_analysis(self, resume: ParsedResume) -> str:
        """Format skills analysis."""
        output = "# Skills Analysis\n\n"
        
        if not resume.skills:
            return output + "*No skills detected. This might indicate parsing issues.*"
        
        # Group skills by category
        from collections import defaultdict
        skills_by_category = defaultdict(list)
        
        for skill in resume.skills:
            category = skill.category if skill.category else "other"
            skills_by_category[category].append(skill)
        
        # Sort categories
        sorted_categories = sorted(skills_by_category.items(), 
                                  key=lambda x: len(x[1]), 
                                  reverse=True)
        
        output += f"**Total Skills Found:** {len(resume.skills)}\n\n"
        
        for category, skills in sorted_categories:
            category_name = category.replace("_", " ").title()
            output += f"### {category_name} ({len(skills)} skills)\n\n"
            
            # Show top skills in this category
            top_skills = sorted(skills, key=lambda x: x.confidence, reverse=True)[:10]
            for skill in top_skills:
                confidence_bar = "█" * int(skill.confidence * 10)
                output += f"- **{skill.name}** {confidence_bar} ({skill.confidence:.0%})\n"
            
            if len(skills) > 10:
                output += f"\n*...and {len(skills) - 10} more*\n"
            
            output += "\n"
        
        return output
    
    def _format_experience_analysis(self, resume: ParsedResume) -> str:
        """Format experience analysis."""
        output = "# Experience Analysis\n\n"
        
        if not resume.experience:
            return output + "*No work experience detected.*"
        
        output += f"**Total Positions:** {len(resume.experience)}\n\n"
        
        for i, exp in enumerate(resume.experience, 1):
            output += f"## Position {i}\n\n"
            
            if exp.title:
                output += f"**Title:** {exp.title}\n\n"
            if exp.company:
                output += f"**Company:** {exp.company}\n\n"
            if exp.duration:
                output += f"**Duration:** {exp.duration}\n\n"
            
            if exp.skills_used:
                output += f"**Skills Used:** {', '.join(exp.skills_used[:8])}\n\n"
            
            if exp.description:
                output += "**Key Responsibilities:**\n\n"
                for desc in exp.description[:5]:
                    output += f"- {desc}\n"
                if len(exp.description) > 5:
                    output += f"\n*...and {len(exp.description) - 5} more bullet points*\n"
            
            output += "\n---\n\n"
        
        return output
    
    def _analyze_job_match(self, resume: ParsedResume, job_text: str) -> str:
        """Analyze resume against job description."""
        output = "# Job Match Analysis\n\n"
        
        # Extract skills from job description
        job_skills = self.nlp_analyzer.extract_skills(job_text)
        
        # Create job description object
        job_description = JobDescription(
            title="Target Position",
            description=job_text,
            required_skills=[s.name for s in job_skills if s.confidence > 0.8][:15],
            preferred_skills=[s.name for s in job_skills if s.confidence <= 0.8][:15]
        )
        
        # Calculate score
        score = self.scorer.calculate_score(resume, job_description)
        
        # Format output
        output += f"## Overall Match Score: {score.overall_score:.1f}/100\n\n"
        
        # Score breakdown
        output += "### Score Breakdown\n\n"
        output += f"- **Skills Match:** {score.skills_match:.1f}/100\n"
        output += f"- **Experience Relevance:** {score.experience_match:.1f}/100\n"
        output += f"- **Impact & Metrics:** {score.impact_score:.1f}/100\n"
        output += f"- **ATS Compatibility:** {score.ats_compatibility:.1f}/100\n\n"
        
        # Matched skills
        if score.skills_matched:
            output += "### ✅ Skills You Have\n\n"
            for skill in score.skills_matched[:15]:
                output += f"- {skill}\n"
            if len(score.skills_matched) > 15:
                output += f"\n*...and {len(score.skills_matched) - 15} more*\n"
            output += "\n"
        
        # Missing skills
        if score.skills_missing:
            output += "### ❌ Skills to Add\n\n"
            for skill in score.skills_missing[:10]:
                output += f"- {skill}\n"
            if len(score.skills_missing) > 10:
                output += f"\n*...and {len(score.skills_missing) - 10} more*\n"
            output += "\n"
        
        # Strengths
        if score.strengths:
            output += "### 💪 Strengths\n\n"
            for strength in score.strengths:
                output += f"- {strength}\n"
            output += "\n"
        
        # Weaknesses
        if score.weaknesses:
            output += "### 📈 Areas for Improvement\n\n"
            for weakness in score.weaknesses:
                output += f"- {weakness}\n"
            output += "\n"
        
        return output
    
    def create_interface(self):
        """Create Gradio interface."""
        with gr.Blocks(
            title="ResumeForge - AI Resume Analyzer",
            theme=gr.themes.Soft()
        ) as interface:
            gr.Markdown("""
            # ResumeForge
            ### AI-Powered Resume Analysis & Optimization
            
            Upload your resume and optionally add a job description to get detailed analysis and improvement suggestions.
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    pdf_input = gr.File(
                        label="Upload Resume (PDF)",
                        file_types=[".pdf"],
                        type="binary"
                    )
                    
                    job_input = gr.Textbox(
                        label="Job Description (Optional)",
                        placeholder="Paste the job description here to see how well your resume matches...",
                        lines=10
                    )
                    
                    analyze_btn = gr.Button("Analyze Resume", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.Tab("Basic Info"):
                            basic_output = gr.Markdown()
                        
                        with gr.Tab("Skills"):
                            skills_output = gr.Markdown()
                        
                        with gr.Tab("Experience"):
                            experience_output = gr.Markdown()
                        
                        with gr.Tab("Job Match"):
                            job_match_output = gr.Markdown()
            
            gr.Markdown("""
            ---
            **Note:** This is a development version. All processing happens locally and no data is stored.
            """)
            
            # Connect button to function
            analyze_btn.click(
                fn=self.analyze_resume,
                inputs=[pdf_input, job_input],
                outputs=[basic_output, skills_output, experience_output, job_match_output]
            )
        
        return interface


def main():
    """Launch Gradio app."""
    app = ResumeForgeApp()
    interface = app.create_interface()
    
    print("\n" + "="*60)
    print("Starting ResumeForge Gradio Interface")
    print("="*60 + "\n")
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()