import fitz  # PyMuPDF
import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """
    Robust PDF parser that handles various resume formats.
    Uses multiple extraction methods for reliability.
    """
    
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+')
        self.github_pattern = re.compile(r'github\.com/[\w-]+')
        
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using multiple methods for reliability.
        """
        try:
            # Method 1: PyMuPDF (fast, good for most PDFs)
            text_pymupdf = self._extract_with_pymupdf(pdf_path)
            
            # Method 2: pdfplumber (better for tables and columns)
            text_pdfplumber = self._extract_with_pdfplumber(pdf_path)
            
            # Choose the better extraction
            if len(text_pdfplumber) > len(text_pymupdf) * 0.9:
                return text_pdfplumber
            return text_pymupdf
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise ValueError(f"Could not extract text from PDF: {str(e)}")
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract using PyMuPDF (fitz)."""
        doc = fitz.open(pdf_path)
        text = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text("text")
            
        doc.close()
        return self._clean_text(text)
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract using pdfplumber (better for complex layouts)."""
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return self._clean_text(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove page numbers and headers/footers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip likely page numbers
            if re.match(r'^\d+$', line):
                continue
            # Skip very short lines that are likely artifacts
            if len(line) > 2:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume text."""
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "location": None
        }
        
        # Extract email
        email_match = self.email_pattern.search(text)
        if email_match:
            contact_info["email"] = email_match.group()
        
        # Extract phone
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            contact_info["phone"] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_match = self.linkedin_pattern.search(text)
        if linkedin_match:
            contact_info["linkedin"] = linkedin_match.group()
        
        # Extract GitHub
        github_match = self.github_pattern.search(text)
        if github_match:
            contact_info["github"] = github_match.group()
        
        # Extract location (basic implementation)
        location = self._extract_location(text)
        if location:
            contact_info["location"] = location
        
        return contact_info
    
    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from resume.
        Looks for common patterns like "City, State" or "City, Country".
        """
        # Common location patterns
        location_patterns = [
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z]{2})',  # City, ST
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)*,\s*[A-Z][a-z]+)',  # City, Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text[:500])  # Check first 500 chars
            if match:
                return match.group(1)
        
        return None
    
    def detect_sections(self, text: str) -> Dict[str, Tuple[int, int]]:
        """
        Detect resume sections and their positions.
        Returns dict of {section_name: (start_pos, end_pos)}
        """
        sections = {}
        
        # Common section headers (case-insensitive)
        section_patterns = {
            "experience": r'\b(experience|work history|employment|professional experience)\b',
            "education": r'\b(education|academic background|qualifications)\b',
            "skills": r'\b(skills|technical skills|competencies|expertise)\b',
            "summary": r'\b(summary|objective|profile|about me)\b',
            "projects": r'\b(projects|personal projects|portfolio)\b',
            "certifications": r'\b(certifications|certificates|licenses)\b',
        }
        
        lines = text.split('\n')
        
        for idx, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            for section_name, pattern in section_patterns.items():
                if re.search(pattern, line_lower) and len(line.strip()) < 50:
                    # Found a section header
                    start_pos = text.find(line)
                    sections[section_name] = start_pos
        
        # Calculate end positions
        section_list = sorted(sections.items(), key=lambda x: x[1])
        for i, (section_name, start) in enumerate(section_list):
            if i < len(section_list) - 1:
                end = section_list[i + 1][1]
            else:
                end = len(text)
            sections[section_name] = (start, end)
        
        return sections
    
    def extract_section_text(self, text: str, section_name: str) -> Optional[str]:
        """Extract text for a specific section."""
        sections = self.detect_sections(text)
        
        if section_name in sections:
            start, end = sections[section_name]
            return text[start:end].strip()
        
        return None
    
    def get_metadata(self, pdf_path: str) -> Dict[str, any]:
        """Extract PDF metadata."""
        metadata = {}
        
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                "page_count": len(doc),
                "file_size": Path(pdf_path).stat().st_size,
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
            }
            doc.close()
        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")
        
        return metadata