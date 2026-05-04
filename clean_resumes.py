import argparse
import re
from pathlib import Path


MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    "january": "01", "february": "02", "march": "03", "april": "04", "june": "06",
    "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12"
}


def standardize_dates(text: str) -> str:
    # Match Month YYYY or Month Year
    # e.g., "Jan 2020" -> "2020-01"
    months_pattern = "|".join(MONTH_MAP.keys())
    # Use double braces to escape them in f-string
    pattern = rf"\b({months_pattern})\s+(\d{{4}})\b"
    
    def replace_date(match):
        month = match.group(1).lower()
        year = match.group(2)
        return f"{year}-{MONTH_MAP[month]}"
        
    return re.sub(pattern, replace_date, text, flags=re.IGNORECASE)


def merge_phone_numbers(text: str) -> str:
    # Match common phone number formats (7-15 digits, handles spaces, dashes, and parens)
    # e.g., 555-322-7337, (555) 322-7337, +91 9876543210
    pattern = r"(?:\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}"
    
    def replace_phone(match):
        phone = match.group(0)
        # Strip spaces, dashes, and parentheses
        return re.sub(r"[\s\-\(\)]", "", phone)
        
    return re.sub(pattern, replace_phone, text)


TYPO_FIXES = {
    r"\bMisrosoft\b": "Microsoft",
    r"\bAssociats\b": "Associates",
    r"\bE-Mait\b": "E-Mail",
    r"\bJou mal\b": "Journal",
    r"\bAccountanat\b": "Accountant",
    r"\bAccountat\b": "Accountant",
    r"\bmat-tasking\b": "multi-tasking",
    r"\bPeach tree\b": "Peachtree",
    r"\bPandL\b": "P and L",
}


def clean_text(text: str, lowercase: bool = False) -> str:
    # 1. Horizontal lines and bullet markers
    text = re.sub(r"_{3,}", "", text)
    text = re.sub(r"-{3,}", "", text)
    text = re.sub(r"[•⚫■★\*·❘]", "", text)
    text = re.sub(r"[\[\]\(\)]", "", text)
    
    # 2. Aggressive Label & Noise Removal (C, E, M, P, O)
    # Using \b to ensure we only catch isolated characters
    text = re.sub(r"\s+\b[CEMPO]\b\s+", " ", text)
    text = re.sub(r"^\b[CEMPO]\b\s+", "", text)
    
    # 3. Spelling Correction
    for pattern, replacement in TYPO_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # 4. Standardize Symbols
    text = text.replace("&", "and")
    text = text.replace("|", "")
    
    # 5. Noise Tokens
    text = re.sub(r"(?i)Page \d+ of \d+", "", text)
    text = re.sub(r"(?i)Nnovoresume\.com", "", text)
    
    # 6. Phone Number Merging
    text = merge_phone_numbers(text)
    
    # 7. Date Standardization
    text = standardize_dates(text)
    
    # 8. Fix artifacts and duplicates
    text = text.replace("mailto:", "")
    text = re.sub(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\1", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)

    # 9. Normalize Whitespace (Remove All Blank Lines)
    # Collapse multiple spaces on a line
    text = re.sub(r"[ \t]+", " ", text)
    # Remove all blank lines and strip each line
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    
    # 10. Final Cleanup
    # Remove single alphanumeric characters (like grades A, B, C, D, 8) at the end of lines or between spaces
    text = re.sub(r"\s+\b[A-Za-z0-9]\b(?=\s|$)", "", text)
    
    # Remove single digits not followed by a capitalized word
    text = re.sub(r"\s\d\s+(?![A-Z])", " ", text)
    # Remove trailing single character noise
    text = re.sub(r"\s[a-zA-Z0-9]\s*$", "", text)

    if lowercase:
        text = text.lower()

    return text.strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean all resume text files")
    parser.add_argument("--resume-dir", default="Assets/resumes", help="Folder containing resume .txt files")
    parser.add_argument("--output-dir", default="Assets/resume_clean", help="Folder to save cleaned files")
    parser.add_argument("--lowercase", action="store_true", help="Convert text to lowercase")
    args = parser.parse_args()

    resume_dir = Path(args.resume_dir)
    output_dir = Path(args.output_dir)
    
    if not resume_dir.exists():
        raise FileNotFoundError(f"Resume directory not found: {resume_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(resume_dir.glob("*.txt"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem)
    if not files:
        raise SystemExit(f"No .txt files found in {resume_dir}")

    print(f"Cleaning {len(files)} files from {resume_dir} → {output_dir}")

    for path in files:
        original = path.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_text(original, lowercase=args.lowercase)
        
        out_path = output_dir / path.name
        out_path.write_text(cleaned, encoding="utf-8")

    print(f"Successfully cleaned all files.")
    print(f"Lowercase applied: {args.lowercase}")


if __name__ == "__main__":
    main()
