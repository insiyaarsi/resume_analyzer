"""Test all resumes in the sample directory."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.pdf_parser import PDFParser
from app.services.nlp_analyzer import NLPAnalyzer

def quick_test_resume(pdf_path: str):
    """Quick analysis of a resume."""
    parser = PDFParser()
    nlp = NLPAnalyzer()
    
    text = parser.extract_text(pdf_path)
    skills = nlp.extract_skills(text)
    contact = parser.extract_contact_info(text)
    sections = parser.detect_sections(text)
    
    print(f"\n{'='*60}")
    print(f"Resume: {Path(pdf_path).name}")
    print(f"{'='*60}")
    print(f"Characters: {len(text):,}")
    print(f"Skills found: {len(skills)}")
    print(f"Top skills: {', '.join([s.name for s in skills[:5]])}")
    print(f"Email: {contact.get('email', 'Not found')}")
    print(f"Sections: {', '.join(sections.keys())}")

def main():
    data_dir = Path(__file__).parent.parent / "data" / "sample_resumes"
    resume_files = sorted(data_dir.glob("*.pdf"))
    
    print(f"\nTesting {len(resume_files)} resumes...\n")
    
    for resume in resume_files:
        try:
            quick_test_resume(str(resume))
        except Exception as e:
            print(f"\n❌ Error with {resume.name}: {str(e)}")
    
    print(f"\n{'='*60}")
    print("✅ All tests complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()