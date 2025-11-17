"""
Wrapper script to run NLP pipeline tests.
Handles Python path configuration.
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Now we can import from app
from app.services.pdf_parser import PDFParser
from app.services.nlp_analyzer import NLPAnalyzer
from app.services.scorer import ResumeScorer
from app.models.schemas import ParsedResume, JobDescription
import json


def test_resume_parsing(pdf_path: str):
    """Test parsing a single resume."""
    print(f"\n{'='*60}")
    print(f"Testing Resume: {Path(pdf_path).name}")
    print(f"{'='*60}\n")
    
    # Initialize parsers
    pdf_parser = PDFParser()
    nlp_analyzer = NLPAnalyzer()
    
    # Extract text
    print("📄 Extracting text from PDF...")
    text = pdf_parser.extract_text(pdf_path)
    print(f"✓ Extracted {len(text)} characters\n")
    
    # Extract contact info
    print("📧 Extracting contact information...")
    contact_info = pdf_parser.extract_contact_info(text)
    print(json.dumps(contact_info, indent=2))
    print()
    
    # Detect sections
    print("📑 Detecting resume sections...")
    sections = pdf_parser.detect_sections(text)
    print(f"✓ Found {len(sections)} sections: {list(sections.keys())}\n")
    
    # Extract skills
    print("💻 Extracting skills...")
    skills = nlp_analyzer.extract_skills(text)
    print(f"✓ Found {len(skills)} skills")
    print("\nTop 10 skills:")
    for skill in skills[:10]:
        print(f"  - {skill.name} ({skill.category}) - confidence: {skill.confidence:.2f}")
    print()
    
    # Extract experience
    print("💼 Extracting work experience...")
    experience_text = pdf_parser.extract_section_text(text, "experience")
    experiences = nlp_analyzer.extract_experience(text, experience_text)
    print(f"✓ Found {len(experiences)} experience entries")
    for i, exp in enumerate(experiences, 1):
        print(f"\n  Experience {i}:")
        print(f"    Title: {exp.title}")
        print(f"    Company: {exp.company}")
        print(f"    Duration: {exp.duration}")
        print(f"    Bullet points: {len(exp.description)}")
        if exp.skills_used:
            print(f"    Skills used: {', '.join(exp.skills_used[:5])}")
    print()
    
    # Extract education
    print("🎓 Extracting education...")
    education_text = pdf_parser.extract_section_text(text, "education")
    educations = nlp_analyzer.extract_education(text, education_text)
    print(f"✓ Found {len(educations)} education entries")
    for i, edu in enumerate(educations, 1):
        print(f"\n  Education {i}:")
        print(f"    Degree: {edu.degree}")
        print(f"    Institution: {edu.institution}")
        print(f"    Year: {edu.year}")
        if edu.gpa:
            print(f"    GPA: {edu.gpa}")
    print()
    
    # Create ParsedResume object
    parsed_resume = ParsedResume(
        raw_text=text,
        contact_info=contact_info,
        experience=experiences,
        education=educations,
        skills=skills,
        sections={name: text[start:end] for name, (start, end) in sections.items()}
    )
    
    return parsed_resume


def test_job_matching(parsed_resume: ParsedResume, job_desc_path: str):
    """Test matching resume against job description."""
    print(f"\n{'='*60}")
    print(f"Testing Job Match: {Path(job_desc_path).name}")
    print(f"{'='*60}\n")
    
    # Read job description
    with open(job_desc_path, 'r', encoding='utf-8') as f:
        job_text = f.read()
    
    # Parse job description
    print("📋 Analyzing job description...")
    nlp_analyzer = NLPAnalyzer()
    job_skills = nlp_analyzer.extract_skills(job_text)
    
    job_description = JobDescription(
        title="Sample Job",
        description=job_text,
        required_skills=[s.name for s in job_skills if s.confidence > 0.8][:10],
        preferred_skills=[s.name for s in job_skills if s.confidence <= 0.8][:10]
    )
    
    print(f"✓ Found {len(job_description.required_skills)} required skills")
    print(f"✓ Found {len(job_description.preferred_skills)} preferred skills\n")
    
    # Calculate score
    print("🎯 Calculating match score...")
    scorer = ResumeScorer()
    score = scorer.calculate_score(parsed_resume, job_description)
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}\n")
    
    print(f"Overall Score: {score.overall_score}/100")
    print(f"\nBreakdown:")
    print(f"  Skills Match:        {score.skills_match}/100")
    print(f"  Experience Match:    {score.experience_match}/100")
    print(f"  Impact Score:        {score.impact_score}/100")
    print(f"  ATS Compatibility:   {score.ats_compatibility}/100")
    
    print(f"\nSkills Matched ({len(score.skills_matched)}):")
    for skill in score.skills_matched[:10]:
        print(f"  ✓ {skill}")
    
    if score.skills_missing:
        print(f"\nSkills Missing ({len(score.skills_missing)}):")
        for skill in score.skills_missing[:5]:
            print(f"  ✗ {skill}")
    
    print(f"\nStrengths:")
    for strength in score.strengths:
        print(f"  💪 {strength}")
    
    print(f"\nAreas for Improvement:")
    for weakness in score.weaknesses:
        print(f"  📈 {weakness}")
    
    print()


def main():
    """Main test function."""
    # Get paths
    data_dir = Path(__file__).parent.parent / "data"
    resumes_dir = data_dir / "sample_resumes"
    jobs_dir = data_dir / "job_descriptions"
    
    # Find PDF files
    resume_files = list(resumes_dir.glob("*.pdf"))
    job_files = list(jobs_dir.glob("*.txt"))
    
    if not resume_files:
        print("❌ No resume PDFs found in data/sample_resumes/")
        print(f"   Looking in: {resumes_dir}")
        print("   Please add some PDF resumes to test.")
        return
    
    if not job_files:
        print("⚠️  No job descriptions found in data/job_descriptions/")
        print("   Will only test resume parsing.\n")
    
    # Test first resume
    print("Starting NLP Pipeline Test\n")
    print(f"Found {len(resume_files)} resume(s)")
    print(f"Testing: {resume_files[0].name}\n")
    
    parsed_resume = test_resume_parsing(str(resume_files[0]))
    
    # Test job matching if job descriptions available
    if job_files:
        test_job_matching(parsed_resume, str(job_files[0]))
    
    print(f"\n{'='*60}")
    print("✅ Test Complete!")
    print(f"{'='*60}\n")
    
    if len(resume_files) > 1:
        print(f"Note: Tested 1 of {len(resume_files)} resumes.")
        print(f"      Run again to test more.\n")


if __name__ == "__main__":
    main()