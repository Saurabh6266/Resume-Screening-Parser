"""
Resume Parser Module
Extracts text from PDF, DOCX, TXT files and parses JSONL format
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import shutil
import subprocess
import tempfile

try:
    import PyPDF2
except Exception:  
    PyPDF2 = None

try:
    from docx import Document
except Exception:  
    Document = None


class ResumeParser:
    """Parse resumes from various formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
    
    def parse_file(self, file_path: str) -> Dict[str, str]:
        """
        Parse a single resume file and extract text
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary with resume data including extracted text
        """
        if not isinstance(file_path, (str, Path)):
            raise TypeError("file_path must be a str or pathlib.Path")
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        # Extract text based on file type
        if file_ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_ext == '.docx':
            text = self._extract_docx(file_path)
        elif file_ext == '.doc':
            # Convert legacy .doc to .docx using LibreOffice, then extract
            converted = self._convert_doc_to_docx(file_path)
            try:
                text = self._extract_docx(converted)
            finally:
                # cleanup converted file (best-effort)
                try:
                    if converted.exists():
                        converted.unlink()
                except Exception:
                    pass
        elif file_ext == '.txt':
            text = self._extract_txt(file_path)
        else:
            text = ""
        
        return {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'text': text,
            'source': 'file'
        }
    
    def _extract_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        if PyPDF2 is None:
            raise RuntimeError("PyPDF2 is required to extract text from PDF files. Install with 'pip install PyPDF2'")
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        
        return text.strip()
    
    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        if Document is None:
            raise RuntimeError("python-docx is required to extract text from DOCX files. Install with 'pip install python-docx'")
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
        
        return text.strip()

    def _convert_doc_to_docx(self, file_path: Path) -> Path:
        """Convert a legacy `.doc` file to `.docx` using LibreOffice (`soffice`).

        Returns a Path to the converted `.docx` file (stored in a temporary directory).
        Raises RuntimeError when `soffice` isn't available or conversion fails.
        """
        
        if shutil.which("soffice") is None:
            raise RuntimeError("LibreOffice ('soffice') not found in PATH; required to convert .doc files to .docx")

        outdir = Path(tempfile.mkdtemp())
        proc = subprocess.run([
            "soffice",
            "--headless",
            "--convert-to",
            "docx",
            "--outdir",
            str(outdir),
            str(file_path),
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if proc.returncode != 0:
            raise RuntimeError(f"Conversion failed: {proc.stderr.strip() or proc.stdout.strip()}")

        converted = outdir / (file_path.stem + ".docx")
        if not converted.exists():
            raise RuntimeError("Conversion reported success but output .docx file was not found")

        return converted
    
    def _extract_txt(self, file_path: Path) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
            return ""
    
    def parse_jsonl(self, jsonl_path: str) -> List[Dict[str, str]]:
        """
        Parse resumes from JSONL file
        
        Args:
            jsonl_path: Path to the JSONL file
            
        Returns:
            List of resume dictionaries
        """
        if not isinstance(jsonl_path, (str, Path)):
            raise TypeError("jsonl_path must be a str or pathlib.Path")
        jsonl_path = Path(jsonl_path)
        
        if not jsonl_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")
        
        resumes = []
        
        try:
            with open(jsonl_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        resume = json.loads(line)
                        # Combine all text fields for comprehensive matching
                        text_content = self._combine_text_fields(resume)
                        
                        resumes.append({
                            'resume_id': resume.get('ResumeID', f'RESUME_{line_num}'),
                            'name': resume.get('Name', 'Unknown'),
                            'email': resume.get('Email', ''),
                            'phone': resume.get('Phone', ''),
                            'category': resume.get('Category', ''),
                            'text': text_content,
                            'source': 'jsonl'
                        })
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
        
        except Exception as e:
            print(f"Error reading JSONL file: {e}")
        
        return resumes
    
    def _combine_text_fields(self, resume: Dict) -> str:
        """Combine all text fields from JSONL resume for comprehensive analysis"""
        text_parts = []
        
        # Priority fields for text extraction
        fields = ['Text', 'Experience', 'Skills', 'Summary', 'Education']
        
        for field in fields:
            if field in resume and resume[field]:
                text_parts.append(str(resume[field]))
        
        # If no text found, try to combine all fields
        if not text_parts:
            for key, value in resume.items():
                if key not in ['ResumeID', 'Name', 'Email', 'Phone', 'Location', 'Source']:
                    if value:
                        text_parts.append(str(value))
        
        return " ".join(text_parts).strip()
    
    def parse_directory(self, directory_path: str) -> List[Dict[str, str]]:
        """
        Parse all resume files in a directory
        
        Args:
            directory_path: Path to directory containing resumes
            
        Returns:
            List of parsed resumes
        """
        if not isinstance(directory_path, (str, Path)):
            raise TypeError("directory_path must be a str or pathlib.Path")
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")
        
        resumes = []
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    resume = self.parse_file(str(file_path))
                    resumes.append(resume)
                except Exception as e:
                    print(f"Error parsing {file_path.name}: {e}")
        
        return resumes


if __name__ == "__main__":
    # Test the parser
    parser = ResumeParser()
    
    # Test JSONL parsing
    jsonl_path = "../resumes_dataset.jsonl"
    if os.path.exists(jsonl_path):
        print("Testing JSONL parsing...")
        resumes = parser.parse_jsonl(jsonl_path)
        print(f"Parsed {len(resumes)} resumes from JSONL")
        if resumes:
            print(f"Sample resume: {resumes[0]['name']} - {len(resumes[0]['text'])} characters")
            