import json
import os
from pathlib import Path

def convert_to_jsonl(input_dir, output_file):
    input_path = Path(input_dir)
    files = sorted(input_path.glob("*.txt"), key=lambda p: int(p.stem) if p.stem.isdigit() else p.stem)
    
    with open(output_file, 'w', encoding="utf-8-sig") as f:
        for filepath in files:
            text = filepath.read_text(encoding="utf-8-sig").strip()
            # Wrap in a dictionary with an ID
            entry = {
                "id": filepath.stem,
                "text": text
            }
            f.write(json.dumps(entry) + '\n')
            
    print(f"Successfully converted {len(files)} files to {output_file}")

if __name__ == "__main__":
    convert_to_jsonl("Assets/resume_clean", "resumes.jsonl")
