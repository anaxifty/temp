import re
import csv
import os
from datetime import datetime


# ─────────────────────────────────────────────
# CONFIGURATION — add any header/footer phrases
# you want removed (case-insensitive)
# ─────────────────────────────────────────────
HEADER_FOOTER_PATTERNS = [
    r"tourism\s+data\s+inventory",
    r"data\s+inventory",
    r"tourism\s+inventory",
    r"confidential",
    r"draft",
    r"all\s+rights\s+reserved",
    r"table\s+of\s+contents",
]

# Standalone page number patterns, e.g.:  "Page 1", "Page 1 of 10", "1", "- 1 -"
PAGE_NUMBER_PATTERNS = [
    r"^\s*-?\s*page\s+\d+(\s+of\s+\d+)?\s*-?\s*$",   # Page 1 / Page 1 of 10
    r"^\s*-\s*\d+\s*-\s*$",                            # - 1 -
    r"^\s*\d+\s*$",                                     # lone digit(s)
]


def is_page_number(line: str) -> bool:
    for pattern in PAGE_NUMBER_PATTERNS:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    return False


def is_header_footer(line: str) -> bool:
    for pattern in HEADER_FOOTER_PATTERNS:
        if re.fullmatch(pattern, line.strip(), re.IGNORECASE):
            return True
        if re.search(pattern, line.strip(), re.IGNORECASE) and len(line.strip().split()) <= 6:
            return True
    return False


def clean_lines(raw_text: str) -> list[str]:
    """Remove empty lines, page numbers, and header/footer lines."""
    cleaned = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if is_page_number(stripped):
            continue
        if is_header_footer(stripped):
            continue
        cleaned.append(stripped)
    return cleaned


def save_csv(lines: list[str], output_path: str):
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["line_number", "text"])          # header row
        for i, line in enumerate(lines, start=1):
            writer.writerow([i, line])


def get_multiline_input() -> str:
    print("=" * 60)
    print("  Text Cleaner → CSV Converter")
    print("=" * 60)
    print("\nPaste your text below.")
    print("When done, type  END  on a new line and press Enter.\n")

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)

    return "\n".join(lines)


def main():
    raw_text = get_multiline_input()

    if not raw_text.strip():
        print("\n⚠  No text entered. Exiting.")
        return

    cleaned = clean_lines(raw_text)

    if not cleaned:
        print("\n⚠  No usable lines found after cleaning. Exiting.")
        return

    # Auto-generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"cleaned_output_{timestamp}.csv"

    save_csv(cleaned, output_file)

    print(f"\n✅  Done!")
    print(f"   Lines before cleaning : {len(raw_text.splitlines())}")
    print(f"   Lines after cleaning  : {len(cleaned)}")
    print(f"   CSV saved to          : {os.path.abspath(output_file)}\n")

    # Preview first 5 rows
    print("── Preview (first 5 rows) " + "─" * 33)
    for i, line in enumerate(cleaned[:5], 1):
        print(f"  {i:>3}. {line}")
    if len(cleaned) > 5:
        print(f"       ... and {len(cleaned) - 5} more rows.")
    print("─" * 60)


if __name__ == "__main__":
    main()
