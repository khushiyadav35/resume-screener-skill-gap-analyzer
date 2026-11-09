import io
import os
import re
import unicodedata
from typing import Dict, Optional, Union


def clean_text(text: str) -> str:
    """Normalize unicode characters, strip excess whitespaces, and tidy line breaks."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    # Replace non-breaking spaces and tabs with regular spaces
    text = text.replace("\u00a0", " ").replace("\t", " ")
    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple blank lines into max 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces and strip trailing whitespace on each line
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def extract_text_from_pdf(source: Union[str, bytes, io.BytesIO]) -> str:
    """Extract full plain text from a PDF file path or byte stream."""
    import pypdf

    if isinstance(source, (str, os.PathLike)):
        reader = pypdf.PdfReader(str(source))
    elif isinstance(source, bytes):
        reader = pypdf.PdfReader(io.BytesIO(source))
    elif isinstance(source, io.BytesIO):
        source.seek(0)
        reader = pypdf.PdfReader(source)
    else:
        raise ValueError(f"Unsupported PDF input source type: {type(source)}")

    extracted_pages = []
    for idx, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            extracted_pages.append(page_text)

    return clean_text("\n\n".join(extracted_pages))


def extract_text_from_docx(source: Union[str, bytes, io.BytesIO]) -> str:
    """Extract plain text from a Microsoft Word (.docx) document."""
    import docx

    if isinstance(source, (str, os.PathLike)):
        doc = docx.Document(str(source))
    elif isinstance(source, bytes):
        doc = docx.Document(io.BytesIO(source))
    elif isinstance(source, io.BytesIO):
        source.seek(0)
        doc = docx.Document(source)
    else:
        raise ValueError(f"Unsupported DOCX input source type: {type(source)}")

    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    # Also extract any text inside tables
    for table in doc.tables:
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_text:
                paragraphs.append(" | ".join(row_text))

    return clean_text("\n".join(paragraphs))


def extract_text(source: Union[str, bytes, io.BytesIO], filename: Optional[str] = None) -> str:
    """
    Unified text extraction dispatcher for PDF, DOCX, and TXT files.
    Determines parser based on filename extension or file path.
    """
    if isinstance(source, str) and os.path.exists(source):
        filename = source
        with open(source, "rb") as f:
            content_bytes = f.read()
    elif isinstance(source, bytes):
        content_bytes = source
    elif isinstance(source, io.BytesIO):
        source.seek(0)
        content_bytes = source.read()
    elif isinstance(source, str):
        # Direct raw text string passed
        return clean_text(source)
    else:
        raise ValueError(f"Unsupported input type for text extraction: {type(source)}")

    name_lower = (filename or "").lower()

    if name_lower.endswith(".pdf"):
        return extract_text_from_pdf(content_bytes)
    elif name_lower.endswith(".docx"):
        return extract_text_from_docx(content_bytes)
    elif name_lower.endswith(".txt") or name_lower.endswith(".md"):
        try:
            return clean_text(content_bytes.decode("utf-8"))
        except UnicodeDecodeError:
            return clean_text(content_bytes.decode("latin-1", errors="ignore"))
    else:
        # Fallback: attempt PDF, then UTF-8 decode
        try:
            return extract_text_from_pdf(content_bytes)
        except Exception:
            try:
                return clean_text(content_bytes.decode("utf-8"))
            except Exception:
                return clean_text(content_bytes.decode("latin-1", errors="ignore"))


def extract_contact_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract contact details: Email, Phone, LinkedIn, GitHub, Portfolio URL, and Name.
    """
    info: Dict[str, Optional[str]] = {
        "name": None,
        "email": None,
        "phone": None,
        "linkedin": None,
        "github": None,
        "portfolio": None,
    }

    if not text:
        return info

    # 1. Email extraction
    email_match = re.search(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        text,
    )
    if email_match:
        info["email"] = email_match.group(0).strip(".,")

    # 2. Phone extraction (supports +91-XXXXX XXXXX, (123) 456-7890, +91 9876543210, etc.)
    phone_pattern = r"(?:(?:\+?\d{1,3}[\s-]?)?\(?\d{2,5}\)?[\s-]?)?\d{3,5}[\s-]?\d{4,5}"
    for match in re.finditer(phone_pattern, text):
        candidate = match.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        # Standard valid mobile/landline numbers typically have 10 to 13 digits
        if 10 <= len(digits) <= 13:
            info["phone"] = candidate
            break

    # 3. LinkedIn profile extraction
    linkedin_match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)/?",
        text,
        re.IGNORECASE,
    )
    if linkedin_match:
        username = linkedin_match.group(1)
        info["linkedin"] = f"https://linkedin.com/in/{username}"

    # 4. GitHub profile extraction
    github_match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)/?",
        text,
        re.IGNORECASE,
    )
    if github_match:
        username = github_match.group(1)
        info["github"] = f"https://github.com/{username}"

    # 5. Portfolio / personal website extraction
    portfolio_patterns = [
        r"(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:dev|me|io|app|tech|in|com)/?[^\s,]*)",
    ]
    for pattern in portfolio_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate_url = match.group(0).strip(".,")
            if "linkedin.com" not in candidate_url and "github.com" not in candidate_url:
                if not candidate_url.startswith("http"):
                    candidate_url = "https://" + candidate_url
                info["portfolio"] = candidate_url
                break

    # 6. Candidate Name extraction heuristic:
    # First 3 non-empty lines that don't contain email, phone, or standard headers
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    for line in lines[:5]:
        clean_line = re.sub(r"[|\-•,].*", "", line).strip()
        words = clean_line.split()
        if 1 <= len(words) <= 4:
            # Check that it consists of alphabetic characters and not headers like 'RESUME'
            if re.match(r"^[A-Za-z\s.'-]+$", clean_line):
                upper_line = clean_line.upper()
                if not any(
                    hdr in upper_line
                    for hdr in ["RESUME", "CURRICULUM", "VITAE", "CV", "PAGE", "CONTACT"]
                ):
                    info["name"] = clean_line.title()
                    break

    return info
