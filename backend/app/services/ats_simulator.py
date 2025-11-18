"""
ATS (Applicant Tracking System) Simulator.
Simulates how different ATS systems parse and score resumes.
"""

import re
from typing import Dict, List, Optional
from enum import Enum


class ATSSystem(str, Enum):
    """Common ATS systems used by companies."""
    WORKDAY = "Workday"
    GREENHOUSE = "Greenhouse"
    LEVER = "Lever"
    TALEO = "Oracle Taleo"
    ICIMS = "iCIMS"
    JOBVITE = "Jobvite"


class ATSSimulator:
    """
    Simulates how different ATS systems parse resumes.
    Each system has different parsing capabilities and quirks.
    """
    
    def __init__(self):
        # ATS capabilities matrix
        self.ats_capabilities = {
            ATSSystem.WORKDAY: {
                "handles_two_columns": True,
                "handles_tables": True,
                "handles_graphics": False,
                "handles_headers_footers": True,
                "handles_text_boxes": False,
                "preferred_fonts": ["Arial", "Calibri", "Times New Roman", "Helvetica"],
                "max_file_size_mb": 5,
                "strict_formatting": False,
            },
            ATSSystem.GREENHOUSE: {
                "handles_two_columns": True,
                "handles_tables": True,
                "handles_graphics": False,
                "handles_headers_footers": True,
                "handles_text_boxes": False,
                "preferred_fonts": ["Arial", "Calibri", "Georgia"],
                "max_file_size_mb": 10,
                "strict_formatting": False,
            },
            ATSSystem.LEVER: {
                "handles_two_columns": True,
                "handles_tables": True,
                "handles_graphics": False,
                "handles_headers_footers": True,
                "handles_text_boxes": True,
                "preferred_fonts": ["Arial", "Calibri", "Helvetica"],
                "max_file_size_mb": 10,
                "strict_formatting": False,
            },
            ATSSystem.TALEO: {
                "handles_two_columns": False,  # Taleo struggles with columns
                "handles_tables": False,
                "handles_graphics": False,
                "handles_headers_footers": False,
                "handles_text_boxes": False,
                "preferred_fonts": ["Arial", "Times New Roman"],
                "max_file_size_mb": 2,
                "strict_formatting": True,  # Taleo is notoriously strict
            },
            ATSSystem.ICIMS: {
                "handles_two_columns": True,
                "handles_tables": True,
                "handles_graphics": False,
                "handles_headers_footers": True,
                "handles_text_boxes": False,
                "preferred_fonts": ["Arial", "Calibri"],
                "max_file_size_mb": 5,
                "strict_formatting": False,
            },
            ATSSystem.JOBVITE: {
                "handles_two_columns": True,
                "handles_tables": True,
                "handles_graphics": False,
                "handles_headers_footers": True,
                "handles_text_boxes": True,
                "preferred_fonts": ["Arial", "Helvetica", "Calibri"],
                "max_file_size_mb": 10,
                "strict_formatting": False,
            },
        }
    
    def simulate_ats_parsing(
        self,
        resume_text: str,
        contact_info: Dict,
        sections: Dict,
        metadata: Dict,
        ats_system: ATSSystem = ATSSystem.WORKDAY
    ) -> Dict:
        """
        Simulate how a specific ATS would parse the resume.
        Returns compatibility score and issues.
        """
        capabilities = self.ats_capabilities[ats_system]
        issues = []
        warnings = []
        score = 100.0
        
        # Check file size
        file_size_mb = metadata.get('file_size', 0) / (1024 * 1024)
        if file_size_mb > capabilities['max_file_size_mb']:
            issues.append(f"File size ({file_size_mb:.1f}MB) exceeds {ats_system} limit ({capabilities['max_file_size_mb']}MB)")
            score -= 20
        
        # Check for required sections
        required_sections = ['experience', 'education', 'skills']
        missing_sections = [s for s in required_sections if s not in sections]
        
        if missing_sections:
            issues.append(f"Missing critical sections: {', '.join(missing_sections)}")
            score -= 15 * len(missing_sections)
        
        # Check contact information
        if not contact_info.get('email'):
            issues.append("Missing email address - ATS cannot contact you")
            score -= 25
        
        if not contact_info.get('phone'):
            warnings.append("Missing phone number - limits contact options")
            score -= 10
        
        # Check for problematic formatting
        if self._detect_two_column_layout(resume_text) and not capabilities['handles_two_columns']:
            issues.append(f"{ats_system} struggles with two-column layouts - may scramble text")
            score -= 30
        
        if self._detect_tables(resume_text) and not capabilities['handles_tables']:
            issues.append(f"{ats_system} may not parse tables correctly")
            score -= 15
        
        if not capabilities['handles_headers_footers']:
            if self._detect_header_footer_content(resume_text):
                warnings.append(f"{ats_system} may ignore header/footer content")
                score -= 10
        
        # Check for special characters and formatting
        if self._has_special_characters(resume_text):
            if capabilities['strict_formatting']:
                issues.append(f"{ats_system} may misinterpret special characters")
                score -= 10
            else:
                warnings.append("Special characters detected - generally safe but monitor")
        
        # Check resume length
        char_count = len(resume_text)
        if char_count < 1000:
            warnings.append("Resume seems too short - may lack detail for ATS scoring")
            score -= 5
        elif char_count > 15000:
            warnings.append("Resume is very long - consider condensing to 1-2 pages")
            score -= 5
        
        # Bonus points for good practices
        if contact_info.get('linkedin'):
            score += 5
            warnings.append("LinkedIn profile found - good for ATS verification")
        
        if contact_info.get('github'):
            score += 5
            warnings.append("GitHub profile found - valuable for technical roles")
        
        # Cap score between 0 and 100
        score = max(0, min(100, score))
        
        return {
            "ats_system": ats_system,
            "compatibility_score": round(score, 1),
            "issues": issues,
            "warnings": warnings,
            "capabilities": capabilities,
            "recommendations": self._generate_recommendations(issues, warnings, ats_system)
        }
    
    def simulate_all_ats(
        self,
        resume_text: str,
        contact_info: Dict,
        sections: Dict,
        metadata: Dict
    ) -> Dict[str, Dict]:
        """Simulate parsing across all major ATS systems."""
        results = {}
        
        for ats_system in ATSSystem:
            results[ats_system.value] = self.simulate_ats_parsing(
                resume_text,
                contact_info,
                sections,
                metadata,
                ats_system
            )
        
        # Calculate average compatibility
        avg_score = sum(r['compatibility_score'] for r in results.values()) / len(results)
        
        # Find most and least compatible systems
        scores = [(name, data['compatibility_score']) for name, data in results.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "individual_results": results,
            "average_compatibility": round(avg_score, 1),
            "best_compatibility": scores[0],
            "worst_compatibility": scores[-1],
            "overall_grade": self._get_grade(avg_score)
        }
    
    def _detect_two_column_layout(self, text: str) -> bool:
        """Detect if resume likely uses two-column layout."""
        # Heuristic: if lines have significant whitespace in middle
        lines = text.split('\n')
        column_indicators = 0
        
        for line in lines[:50]:  # Check first 50 lines
            if len(line) > 40:
                # Count spaces in middle third of line
                mid_start = len(line) // 3
                mid_end = 2 * len(line) // 3
                mid_section = line[mid_start:mid_end]
                
                if mid_section.count(' ') > len(mid_section) * 0.7:
                    column_indicators += 1
        
        return column_indicators > 5
    
    def _detect_tables(self, text: str) -> bool:
        """Detect if resume contains table-like structures."""
        # Look for repeated patterns of aligned content
        lines = text.split('\n')
        table_indicators = 0
        
        for line in lines:
            # Tables often have multiple consecutive spaces or tabs
            if '  ' * 3 in line or '\t' in line:
                table_indicators += 1
        
        return table_indicators > 3
    
    def _detect_header_footer_content(self, text: str) -> bool:
        """Detect if there's likely header/footer content."""
        lines = text.split('\n')
        
        # Check first and last few lines for repeated patterns
        if len(lines) < 10:
            return False
        
        # Headers often have contact info in first 3 lines
        header_section = ' '.join(lines[:3])
        
        # Footers often have page numbers or repeated info
        footer_section = ' '.join(lines[-3:])
        
        # Simple heuristic
        return '@' in header_section or 'page' in footer_section.lower()
    
    def _has_special_characters(self, text: str) -> bool:
        """Check for potentially problematic special characters."""
        problematic_chars = ['►', '◄', '★', '☆', '●', '○', '■', '□', '▲', '▼']
        return any(char in text for char in problematic_chars)
    
    def _generate_recommendations(
        self,
        issues: List[str],
        warnings: List[str],
        ats_system: ATSSystem
    ) -> List[str]:
        """Generate actionable recommendations based on issues."""
        recommendations = []
        
        if any('two-column' in issue.lower() for issue in issues):
            recommendations.append("Convert to single-column layout for better ATS compatibility")
        
        if any('email' in issue.lower() for issue in issues):
            recommendations.append("Add email address at top of resume")
        
        if any('phone' in warning.lower() for warning in warnings):
            recommendations.append("Add phone number for better recruiter contact")
        
        if any('table' in issue.lower() for issue in issues):
            recommendations.append("Remove tables and use simple bullet points instead")
        
        if any('section' in issue.lower() for issue in issues):
            recommendations.append("Add clear section headers: Experience, Education, Skills")
        
        if any('special characters' in issue.lower() for issue in issues):
            recommendations.append("Replace special characters with standard bullets (•) or dashes (-)")
        
        if not recommendations:
            recommendations.append(f"Resume is well-formatted for {ats_system}")
        
        return recommendations
    
    def _get_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 90:
            return "A (Excellent)"
        elif score >= 80:
            return "B (Good)"
        elif score >= 70:
            return "C (Fair)"
        elif score >= 60:
            return "D (Needs Improvement)"
        else:
            return "F (Poor)"