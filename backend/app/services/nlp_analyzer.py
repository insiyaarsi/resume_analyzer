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
    
        # Import updated functions
        from app.data.skills_database import (
            get_all_technical_skills,
            SOFT_SKILLS,
            SKILL_SYNONYMS,
            ACRONYMS,
            normalize_skill,
            get_skill_variations,
            get_skill_category
        )
        
        # Load skills databases
        self.technical_skills = set(get_all_technical_skills())
        self.soft_skills = set(SOFT_SKILLS)
        self.all_skills = self.technical_skills.union(self.soft_skills)
        self.skill_synonyms = SKILL_SYNONYMS
        self.acronyms = ACRONYMS
        self.normalize_skill = normalize_skill
        self.get_skill_variations = get_skill_variations
        self.get_skill_category = get_skill_category
        
        # Remove old skill_variations building
        # self.skill_variations = self._build_skill_variations()
        
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
        Extract skills from text using multiple advanced methods.
        Returns list of Skill objects with confidence scores.
        """
        text_lower = text.lower()
        found_skills = {}
        
        # Method 1: Direct string matching with word boundaries
        for skill in self.all_skills:
            pattern = r'\b' + re.escape(skill) + r'\b'
            
            if re.search(pattern, text_lower):
                confidence = 0.9
                count = len(re.findall(pattern, text_lower))
                confidence = min(0.99, confidence + (count - 1) * 0.02)
                
                # Normalize the skill
                normalized = self.normalize_skill(skill)
                if normalized in found_skills:
                    found_skills[normalized] = max(found_skills[normalized], confidence)
                else:
                    found_skills[normalized] = confidence
        
        # Method 2: Check skill variations and synonyms
        for canonical, variations in self.skill_synonyms.items():
            for variant in variations:
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, text_lower):
                    if canonical in found_skills:
                        found_skills[canonical] = min(0.99, found_skills[canonical] + 0.03)
                    else:
                        found_skills[canonical] = 0.87
        
        # Method 3: Acronym detection (case-sensitive)
        for acronym, full_form in self.acronyms.items():
            # Look for uppercase acronyms
            pattern = r'\b' + re.escape(acronym.upper()) + r'\b'
            if re.search(pattern, text):
                if full_form in found_skills:
                    found_skills[full_form] = min(0.99, found_skills[full_form] + 0.05)
                else:
                    found_skills[full_form] = 0.85
        
        # Method 4: Use spaCy NER for additional context
        doc = self.nlp(text)
        
        action_verbs = {
            "developed", "built", "created", "designed", "implemented",
            "deployed", "optimized", "improved", "led", "managed",
            "architected", "engineered", "programmed", "coded", "configured",
            "maintained", "automated", "migrated", "integrated", "scaled"
        }
        
        for token in doc:
            if token.lemma_ in action_verbs:
                window = 15
                start = max(0, token.i - window)
                end = min(len(doc), token.i + window)
                
                context = doc[start:end].text.lower()
                for skill in self.all_skills:
                    normalized = self.normalize_skill(skill)
                    if skill in context and normalized in found_skills:
                        found_skills[normalized] = min(0.99, found_skills[normalized] + 0.05)
        
        # Method 5: Section-based boosting (skills mentioned in "Skills" section)
        skills_section_patterns = [
            r'(skills?|technical skills?|core competencies|expertise)[\s\S]{0,500}',
        ]
        
        for pattern in skills_section_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                skills_text = match.group(0)
                for skill in self.all_skills:
                    normalized = self.normalize_skill(skill)
                    if skill in skills_text and normalized in found_skills:
                        found_skills[normalized] = min(0.99, found_skills[normalized] + 0.08)
        
        # Convert to Skill objects
        skills_list = []
        for skill_name, confidence in found_skills.items():
            category = self.get_skill_category(skill_name)
            
            skills_list.append(Skill(
                name=skill_name,
                category=category,
                confidence=confidence
            ))
        
        # Sort by confidence
        skills_list.sort(key=lambda x: x.confidence, reverse=True)
        
        return skills_list
    
    def extract_metrics_from_text(self, text: str) -> List[Dict[str, str]]:
        """
        Extract quantifiable metrics from text.
        Returns list of metrics found with their context.
        """
        metrics = []
        
        # Metric patterns
        patterns = [
            # Percentages: "increased by 40%", "95% accuracy"
            (r'(\d+(?:\.\d+)?)\s*%', 'percentage'),
            
            # Money: "$50K", "$1.5M", "$500,000"
            (r'\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*([KMB])?', 'money'),
            
            # Numbers with units: "500 users", "10K customers", "2M downloads"
            (r'(\d+(?:\.\d+)?)\s*([KMB])?\s*(users?|customers?|clients?|people|employees?|members?)', 'users'),
            
            # Time periods: "within 6 months", "in 3 weeks"
            (r'(\d+)\s*(weeks?|months?|years?|days?|hours?)', 'time'),
            
            # Multipliers: "3x faster", "10x improvement"
            (r'(\d+(?:\.\d+)?)\s*x\s*(faster|improvement|increase|growth|reduction)', 'multiplier'),
            
            # Performance improvements: "reduced latency by 200ms"
            (r'reduced?\s+(\w+)\s+by\s+(\d+(?:\.\d+)?)\s*(%|ms|seconds?|minutes?)?', 'reduction'),
            (r'increased?\s+(\w+)\s+by\s+(\d+(?:\.\d+)?)\s*(%|x)?', 'increase'),
            (r'improved?\s+(\w+)\s+by\s+(\d+(?:\.\d+)?)\s*(%|x)?', 'improvement'),
            
            # Team size: "led team of 5", "managed 10 engineers"
            (r'(led|managed|supervised)\s+(?:team\s+of\s+)?(\d+)\s*(engineers?|developers?|people|members?)?', 'team_size'),
            
            # Scale: "processed 1M records", "handled 10K requests"
            (r'(processed|handled|managed|served)\s+(\d+(?:\.\d+)?)\s*([KMB])?\s*(records?|requests?|transactions?|queries?)', 'scale'),
        ]
        
        for pattern, metric_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                metrics.append({
                    'type': metric_type,
                    'value': match.group(0),
                    'position': match.start()
                })
        
        return metrics
    
    def extract_experience(self, text: str, section_text: Optional[str] = None) -> List[Experience]:
        """
        Extract work experience entries from resume.
        Enhanced with metrics detection and better parsing.
        """
        experiences = []
        target_text = section_text if section_text else text
        
        # Use spaCy for entity recognition
        doc = self.nlp(target_text)
        
        # Find organizations (potential companies)
        organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Enhanced date patterns
        date_patterns = [
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—to]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—to]\s*Present\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—to]\s*Current\b',
            r'\b\d{4}\s*[-–—to]\s*\d{4}\b',
            r'\b\d{4}\s*[-–—to]\s*(Present|Current|Now)\b',
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4}\s*[-–—]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4}\b',
        ]
        
        # Split text into potential job entries
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
                # Common formats:
                # "Job Title at Company Name | Date"
                # "Job Title - Company Name | Date"
                # "Job Title, Company Name | Date"
                
                # Remove date from line first
                line_without_date = line
                for pattern in date_patterns:
                    line_without_date = re.sub(pattern, '', line_without_date, flags=re.IGNORECASE)
                
                # Try different separators
                separators = [r'\s+at\s+', r'\s+[@|]\s+', r'\s+-\s+', r',\s+']
                
                for separator in separators:
                    parts = re.split(separator, line_without_date, maxsplit=1, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        current_experience.title = parts[0].strip(' |–—-,')
                        current_experience.company = parts[1].strip(' |–—-,')
                        break
                
                # If we didn't find title/company, try to identify job title
                if not current_experience.title:
                    from app.data.skills_database import JOB_TITLES
                    for job_title in JOB_TITLES:
                        if job_title in line_stripped.lower():
                            current_experience.title = line_stripped.strip()
                            break
            
            elif current_experience:
                # This is a description line
                if line_stripped.startswith(('•', '-', '*', '◦', '▪', '▫', '–', '—')):
                    # Bullet point
                    description = line_stripped.lstrip('•-*◦▪▫–— ')
                    
                    if description:  # Only add non-empty descriptions
                        current_experience.description.append(description)
                        
                        # Extract skills from this bullet point
                        skills = self.extract_skills(description)
                        for skill in skills:
                            if skill.name not in current_experience.skills_used:
                                current_experience.skills_used.append(skill.name)
                        
                        # Extract metrics from this bullet point
                        metrics = self.extract_metrics_from_text(description)
                        if metrics:
                            # Mark this bullet as having metrics (useful for impact scoring)
                            if not hasattr(current_experience, 'metrics_count'):
                                current_experience.metrics_count = 0
                            current_experience.metrics_count += len(metrics)
                            
                elif len(line_stripped) > 20:  # Ignore very short lines
                    # Paragraph-style description
                    current_experience.description.append(line_stripped)
                    
                    # Also extract skills from paragraph
                    skills = self.extract_skills(line_stripped)
                    for skill in skills:
                        if skill.name not in current_experience.skills_used:
                            current_experience.skills_used.append(skill.name)
        
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