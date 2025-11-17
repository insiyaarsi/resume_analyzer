import spacy
from typing import List, Dict, Set, Tuple, Optional
import re
from collections import Counter
import sys
from pathlib import Path

# Ensure parent directories are in path
current_dir = Path(__file__).resolve().parent
app_dir = current_dir.parent
backend_dir = app_dir.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Now import with proper paths
try:
    from app.data.skills_database import (
        get_all_technical_skills,
        SOFT_SKILLS,
        JOB_TITLES,
        EDUCATION_KEYWORDS,
        COMPANY_INDICATORS,
        get_skill_category
    )
    from app.models.schemas import Skill, Experience, Education
except ModuleNotFoundError:
    # Fallback to relative imports
    import os
    import importlib.util
    
    # Load skills_database manually
    skills_db_path = app_dir / "data" / "skills_database.py"
    spec = importlib.util.spec_from_file_location("skills_database", skills_db_path)
    skills_db = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(skills_db)
    
    get_all_technical_skills = skills_db.get_all_technical_skills
    SOFT_SKILLS = skills_db.SOFT_SKILLS
    JOB_TITLES = skills_db.JOB_TITLES
    EDUCATION_KEYWORDS = skills_db.EDUCATION_KEYWORDS
    COMPANY_INDICATORS = skills_db.COMPANY_INDICATORS
    get_skill_category = skills_db.get_skill_category
    
    # Load schemas manually
    schemas_path = app_dir / "models" / "schemas.py"
    spec = importlib.util.spec_from_file_location("schemas", schemas_path)
    schemas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schemas)
    
    Skill = schemas.Skill
    Experience = schemas.Experience
    Education = schemas.Education


class NLPAnalyzer:
    """
    Advanced NLP analyzer for resume parsing.
    Uses spaCy for entity recognition and custom logic for skill extraction.
    """
    
    def __init__(self):
        """Initialize spaCy model and skill databases."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise RuntimeError(
                "spaCy model not found. Run: python -m spacy download en_core_web_sm"
            )
        
        # Load skills databases
        self.technical_skills = set(get_all_technical_skills())
        self.soft_skills = set(SOFT_SKILLS)
        self.all_skills = self.technical_skills.union(self.soft_skills)
        
        # Create skill variations (e.g., "react" -> ["react", "react.js", "reactjs"])
        self.skill_variations = self._build_skill_variations()
        
    def _build_skill_variations(self) -> Dict[str, Set[str]]:
        """Build a mapping of skills to their variations."""
        variations = {}
        
        # Common patterns
        patterns = {
            "react": {"react", "react.js", "reactjs"},
            "node": {"node", "node.js", "nodejs"},
            "next": {"next", "next.js", "nextjs"},
            "vue": {"vue", "vue.js", "vuejs"},
            "angular": {"angular", "angularjs", "angular.js"},
            "typescript": {"typescript", "ts"},
            "javascript": {"javascript", "js"},
            "python": {"python", "py"},
            "postgresql": {"postgresql", "postgres", "psql"},
            "mongodb": {"mongodb", "mongo"},
        }
        
        # Add patterns
        for base_skill, vars in patterns.items():
            if base_skill in self.all_skills:
                variations[base_skill] = vars
        
        return variations
    
    def extract_skills(self, text: str) -> List[Skill]:
        """
        Extract skills from text using multiple methods.
        Returns list of Skill objects with confidence scores.
        """
        text_lower = text.lower()
        found_skills = {}
        
        # Method 1: Direct string matching with word boundaries
        for skill in self.all_skills:
            # Create regex pattern with word boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
            
            if re.search(pattern, text_lower):
                confidence = 0.9  # High confidence for exact match
                
                # Boost confidence if mentioned multiple times
                count = len(re.findall(pattern, text_lower))
                confidence = min(0.99, confidence + (count - 1) * 0.02)
                
                found_skills[skill] = confidence
        
        # Method 2: Check skill variations
        for base_skill, variations in self.skill_variations.items():
            for variant in variations:
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, text_lower) and base_skill not in found_skills:
                    found_skills[base_skill] = 0.85
        
        # Method 3: Use spaCy NER for additional context
        doc = self.nlp(text)
        
        # Look for skills near action verbs (stronger signal)
        action_verbs = {
            "developed", "built", "created", "designed", "implemented",
            "deployed", "optimized", "improved", "led", "managed",
            "architected", "engineered", "programmed", "coded"
        }
        
        for token in doc:
            if token.lemma_ in action_verbs:
                # Check nearby tokens for skills
                window = 10  # tokens
                start = max(0, token.i - window)
                end = min(len(doc), token.i + window)
                
                context = doc[start:end].text.lower()
                for skill in self.all_skills:
                    if skill in context and skill in found_skills:
                        # Boost confidence if skill appears near action verb
                        found_skills[skill] = min(0.99, found_skills[skill] + 0.05)
        
        # Convert to Skill objects
        skills_list = []
        for skill_name, confidence in found_skills.items():
            category = get_skill_category(skill_name)
            
            skills_list.append(Skill(
                name=skill_name,
                category=category,
                confidence=confidence
            ))
        
        # Sort by confidence
        skills_list.sort(key=lambda x: x.confidence, reverse=True)
        
        return skills_list
    
    def extract_experience(self, text: str, section_text: Optional[str] = None) -> List[Experience]:
        """
        Extract work experience entries from resume.
        Focuses on the experience section if provided.
        """
        experiences = []
        target_text = section_text if section_text else text
        
        # Use spaCy for entity recognition
        doc = self.nlp(target_text)
        
        # Find organizations (potential companies)
        organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Find date ranges
        date_patterns = [
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]\s*Present\b',
            r'\b\d{4}\s*[-–—]\s*\d{4}\b',
            r'\b\d{4}\s*[-–—]\s*Present\b',
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, target_text, re.IGNORECASE))
        
        # Split text into potential job entries (by date ranges or organizations)
        lines = target_text.split('\n')
        current_experience = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Check if line contains a date range (likely a job entry header)
            has_date = any(re.search(pattern, line, re.IGNORECASE) for pattern in date_patterns)
            
            if has_date:
                # Save previous experience
                if current_experience:
                    experiences.append(current_experience)
                
                # Start new experience
                current_experience = Experience()
                
                # Extract duration
                for pattern in date_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        current_experience.duration = match.group(0)
                        break
                
                # Try to extract title and company from this line
                # Common format: "Job Title at Company Name | Date"
                parts = re.split(r'\s+at\s+|\s+[@|]\s+', line, flags=re.IGNORECASE)
                
                if len(parts) >= 2:
                    current_experience.title = parts[0].strip()
                    # Remove date from company name
                    company = parts[1]
                    for pattern in date_patterns:
                        company = re.sub(pattern, '', company, flags=re.IGNORECASE)
                    current_experience.company = company.strip(' |–—-')
                else:
                    # Try to identify job title from common titles
                    for job_title in JOB_TITLES:
                        if job_title in line_stripped.lower():
                            current_experience.title = line_stripped
                            break
            
            elif current_experience:
                # This is a description line
                if line_stripped.startswith(('•', '-', '*', '◦')):
                    # Bullet point
                    description = line_stripped.lstrip('•-*◦ ')
                    current_experience.description.append(description)
                    
                    # Extract skills from this bullet point
                    skills = self.extract_skills(description)
                    for skill in skills:
                        if skill.name not in current_experience.skills_used:
                            current_experience.skills_used.append(skill.name)
                elif len(line_stripped) > 20:  # Ignore very short lines
                    current_experience.description.append(line_stripped)
        
        # Don't forget the last experience
        if current_experience:
            experiences.append(current_experience)
        
        return experiences
    
    def extract_education(self, text: str, section_text: Optional[str] = None) -> List[Education]:
        """
        Extract education entries from resume.
        """
        educations = []
        target_text = section_text if section_text else text
        
        # Common degree patterns
        degree_patterns = [
            r'\b(Bachelor|B\.?S\.?|B\.?A\.?|Master|M\.?S\.?|M\.?A\.?|MBA|Ph\.?D\.?|Doctorate)\b[^,\n]*',
            r'\b(Associate|Diploma|Certificate)\b[^,\n]*',
        ]
        
        # Year pattern
        year_pattern = r'\b(19|20)\d{2}\b'
        
        lines = target_text.split('\n')
        current_education = None
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Check if line contains degree keywords
            has_degree = any(re.search(pattern, line, re.IGNORECASE) for pattern in degree_patterns)
            
            if has_degree:
                if current_education:
                    educations.append(current_education)
                
                current_education = Education()
                
                # Extract degree
                for pattern in degree_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        current_education.degree = match.group(0).strip()
                        break
                
                # Extract year
                year_match = re.search(year_pattern, line)
                if year_match:
                    current_education.year = year_match.group(0)
                
                # Try to find institution name (usually the longest proper noun phrase)
                doc = self.nlp(line)
                orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                if orgs:
                    current_education.institution = orgs[0]
            
            elif current_education:
                # Check for GPA
                gpa_pattern = r'\b(GPA|CGPA)[:\s]*(\d+\.?\d*)\s*/\s*(\d+\.?\d*)\b'
                gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
                if gpa_match:
                    current_education.gpa = f"{gpa_match.group(2)}/{gpa_match.group(3)}"
                
                # If line contains institution name and we haven't found one yet
                if not current_education.institution:
                    doc = self.nlp(line)
                    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
                    if orgs:
                        current_education.institution = orgs[0]
        
        if current_education:
            educations.append(current_education)
        
        return educations
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        Extract important keywords using NLP.
        Returns list of (keyword, frequency) tuples.
        """
        doc = self.nlp(text.lower())
        
        # Extract nouns and proper nouns (most meaningful)
        keywords = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 2:
                keywords.append(token.lemma_)
        
        # Count frequencies
        keyword_counts = Counter(keywords)
        
        # Return top N
        return keyword_counts.most_common(top_n)
    
    def calculate_keyword_match(self, resume_text: str, job_description: str) -> Dict:
        """
        Calculate keyword overlap between resume and job description.
        """
        resume_keywords = dict(self.extract_keywords(resume_text, top_n=50))
        job_keywords = dict(self.extract_keywords(job_description, top_n=50))
        
        # Find common keywords
        common_keywords = set(resume_keywords.keys()).intersection(set(job_keywords.keys()))
        
        # Calculate match percentage
        if len(job_keywords) == 0:
            match_percentage = 0
        else:
            match_percentage = (len(common_keywords) / len(job_keywords)) * 100
        
        return {
            "match_percentage": round(match_percentage, 2),
            "matched_keywords": list(common_keywords),
            "missing_keywords": list(set(job_keywords.keys()) - common_keywords),
            "total_job_keywords": len(job_keywords),
            "total_matched": len(common_keywords)
        }