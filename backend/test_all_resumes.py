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
    
    try:
        text = parser.extract_text(pdf_path)
        skills = nlp.extract_skills(text)
        contact = parser.extract_contact_info(text)
        sections = parser.detect_sections(text)
        experiences = nlp.extract_experience(text)
        educations = nlp.extract_education(text)
        
        print(f"\n{'='*60}")
        print(f"📄 {Path(pdf_path).name}")
        print(f"{'='*60}")
        print(f"📊 Characters: {len(text):,}")
        print(f"💻 Skills: {len(skills)}")
        if skills:
            print(f"   Top 5: {', '.join([s.name for s in skills[:5]])}")
        print(f"📧 Email: {contact.get('email', '❌ Not found')}")
        print(f"📱 Phone: {contact.get('phone', '❌ Not found')}")
        print(f"🔗 LinkedIn: {contact.get('linkedin', '❌ Not found')}")
        print(f"💼 GitHub: {contact.get('github', '❌ Not found')}")
        print(f"📍 Location: {contact.get('location', '❌ Not found')}")
        print(f"📑 Sections: {', '.join(sections.keys()) if sections else '❌ None detected'}")
        print(f"💼 Experiences: {len(experiences)}")
        print(f"🎓 Education: {len(educations)}")
        
        # Quality indicators
        quality_score = 0
        if contact.get('email'): quality_score += 20
        if contact.get('phone'): quality_score += 20
        if len(skills) > 5: quality_score += 20
        if len(experiences) > 0: quality_score += 20
        if len(educations) > 0: quality_score += 20
        
        print(f"\n📈 Parse Quality: {quality_score}/100")
        if quality_score >= 80:
            print("   ✅ Excellent parsing")
        elif quality_score >= 60:
            print("   ⚠️  Good parsing, minor issues")
        else:
            print("   ⚠️  Poor parsing, may need format adjustment")
            
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR: {Path(pdf_path).name}")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")

def main():
    data_dir = Path(__file__).parent.parent / "data" / "sample_resumes"
    resume_files = sorted(data_dir.glob("*.pdf"))
    
    if not resume_files:
        print("❌ No PDF files found in data/sample_resumes/")
        return
    
    print(f"\n🚀 Testing {len(resume_files)} resumes...")
    print(f"📂 Directory: {data_dir}\n")
    
    success_count = 0
    for resume in resume_files:
        try:
            quick_test_resume(str(resume))
            success_count += 1
        except Exception as e:
            print(f"\n❌ Fatal error with {resume.name}: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"✅ Testing Complete!")
    print(f"{'='*60}")
    print(f"✓ Successfully parsed: {success_count}/{len(resume_files)}")
    print(f"✗ Failed: {len(resume_files) - success_count}/{len(resume_files)}")
    print()

if __name__ == "__main__":
    main()