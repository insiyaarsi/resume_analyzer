import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict
from ..models.schemas import ParsedResume, JobDescription, ScoreBreakdown, Skill
from .nlp_analyzer import NLPAnalyzer


class ResumeScorer:
    """
    Calculate comprehensive scores for resume-job matching.
    Uses multiple factors: skills, experience, impact, ATS compatibility.
    """
    
    def __init__(self):
        self.nlp_analyzer = NLPAnalyzer()
        
        # Scoring weights
        self.weights = {
            "skills_match": 0.40,      # 40% - Most important
            "experience_match": 0.30,   # 30% - Very important
            "impact_score": 0.20,       # 20% - Important
            "ats_compatibility": 0.10   # 10% - Good to have
        }
    
    def calculate_score(
        self,
        parsed_resume: ParsedResume,
        job_description: JobDescription
    ) -> ScoreBreakdown:
        """
        Calculate comprehensive score breakdown.
        """
        # Calculate individual scores
        skills_score = self._calculate_skills_match(parsed_resume, job_description)
        experience_score = self._calculate_experience_match(parsed_resume, job_description)
        impact_score = self._calculate_impact_score(parsed_resume)
        ats_score = self._calculate_ats_compatibility(parsed_resume)
        
        # Calculate weighted overall score
        overall_score = (
            skills_score["score"] * self.weights["skills_match"] +
            experience_score["score"] * self.weights["experience_match"] +
            impact_score["score"] * self.weights["impact_score"] +
            ats_score["score"] * self.weights["ats_compatibility"]
        )
        
        # Compile strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if skills_score["score"] >= 70:
            strengths.append(f"Strong skills match ({skills_score['matched_count']}/{skills_score['total_required']} required skills)")
        else:
            weaknesses.append(f"Missing key skills: {', '.join(skills_score['missing'][:3])}")
        
        if experience_score["score"] >= 70:
            strengths.append("Relevant work experience demonstrated")
        else:
            weaknesses.append("Limited relevant experience keywords")
        
        if impact_score["score"] >= 70:
            strengths.append("Strong impact statements with metrics")
        else:
            weaknesses.append("Add more quantifiable achievements")
        
        if ats_score["score"] >= 80:
            strengths.append("Excellent ATS compatibility")
        else:
            weaknesses.append("Improve ATS formatting")
        
        return ScoreBreakdown(
            overall_score=round(overall_score, 1),
            skills_match=round(skills_score["score"], 1),
            experience_match=round(experience_score["score"], 1),
            impact_score=round(impact_score["score"], 1),
            ats_compatibility=round(ats_score["score"], 1),
            skills_matched=skills_score["matched"],
            skills_missing=skills_score["missing"],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _calculate_skills_match(
        self,
        parsed_resume: ParsedResume,
        job_description: JobDescription
    ) -> Dict:
        """Calculate skill matching score."""
        # Get all required and preferred skills from job
        all_job_skills = set(
            [s.lower() for s in job_description.required_skills] +
            [s.lower() for s in job_description.preferred_skills]
        )
        
        # Get resume skills
        resume_skills = set([s.name.lower() for s in parsed_resume.skills])
        
        # Find matches
        matched_skills = resume_skills.intersection(all_job_skills)
        missing_skills = all_job_skills - resume_skills
        
        # Calculate score
        if len(all_job_skills) == 0:
            score = 50.0  # Neutral if no skills specified
        else:
            score = (len(matched_skills) / len(all_job_skills)) * 100
        
        # Bonus for having extra relevant skills
        extra_relevant = len(resume_skills) - len(matched_skills)
        bonus = min(10, extra_relevant * 2)  # Max 10 points bonus
        score = min(100, score + bonus)
        
        return {
            "score": score,
            "matched": list(matched_skills),
            "missing": list(missing_skills),
            "matched_count": len(matched_skills),
            "total_required": len(all_job_skills)
        }
    
    def _calculate_experience_match(
        self,
        parsed_resume: ParsedResume,
        job_description: JobDescription
    ) -> Dict:
        """Calculate experience relevance score."""
        # Use keyword matching between experience descriptions and job description
        all_experience_text = " ".join([
            " ".join(exp.description)
            for exp in parsed_resume.experience
        ])
        
        if not all_experience_text:
            return {"score": 30.0}  # Low score if no experience
        
        keyword_match = self.nlp_analyzer.calculate_keyword_match(
            all_experience_text,
            job_description.description
        )
        
        # Base score from keyword match
        score = keyword_match["match_percentage"]
        
        # Bonus for number of experiences (shows stability)
        num_experiences = len(parsed_resume.experience)
        if num_experiences >= 3:
            score += 10
        elif num_experiences >= 2:
            score += 5
        
        # Cap at 100
        score = min(100, score)
        
        return {"score": score}
    
    def _calculate_impact_score(self, parsed_resume: ParsedResume) -> Dict:
        """
        Calculate impact score based on quantifiable achievements.
        Looks for numbers, percentages, metrics in descriptions.
        """
        total_bullets = 0
        bullets_with_metrics = 0
        
        # Patterns for metrics
        metric_patterns = [
            r'\d+%',  # Percentages
            r'\$\d+[KMB]?',  # Money
            r'\d+\+?\s*(users?|customers?|clients?)',  # Users/customers
            r'\d+\s*(months?|years?)',  # Time periods
            r'\d+x',  # Multipliers
            r'reduced?\s+\w+\s+by\s+\d+',  # Reductions
            r'increased?\s+\w+\s+by\s+\d+',  # Increases
            r'improved?\s+\w+\s+by\s+\d+',  # Improvements
        ]
        
        import re
        
        for exp in parsed_resume.experience:
            for desc in exp.description:
                total_bullets += 1
                
                # Check if this bullet has any metrics
                has_metric = any(
                    re.search(pattern, desc, re.IGNORECASE)
                    for pattern in metric_patterns
                )
                
                if has_metric:
                    bullets_with_metrics += 1
        
        # Calculate score
        if total_bullets == 0:
            score = 50.0  # Neutral if no bullets
        else:
            # Aim for 60%+ of bullets to have metrics
            ratio = bullets_with_metrics / total_bullets
            score = min(100, ratio * 150)  # Scale so 67% = 100
        
        return {"score": score}
    
    def _calculate_ats_compatibility(self, parsed_resume: ParsedResume) -> Dict:
        """
        Calculate ATS (Applicant Tracking System) compatibility score.
        Checks for common ATS-friendly practices.
        """
        score = 100.0
        
        # Check for contact info
        contact = parsed_resume.contact_info
        if not contact.get("email"):
            score -= 15
        if not contact.get("phone"):
            score -= 10
        
        # Check for clear sections
        if not parsed_resume.experience:
            score -= 20
        if not parsed_resume.education:
            score -= 15
        if not parsed_resume.skills:
            score -= 20
        
        # Check resume length (ATS prefers 1-2 pages ~ 3000-6000 chars)
        text_length = len(parsed_resume.raw_text)
        if text_length < 1000:
            score -= 10  # Too short
        elif text_length > 10000:
            score -= 5  # Too long
        
        # Bonus for having LinkedIn/GitHub
        if contact.get("linkedin"):
            score += 5
        if contact.get("github"):
            score += 5
        
        return {"score": max(0, min(100, score))}