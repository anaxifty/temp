#!/usr/bin/env python3
import sys
import re
import csv
import os

def clean_and_export_tourism_data(input_stream, output_file='cleaned_tourism_data.csv'):
    # 1. Read all input from terminal
    raw_text = input_stream.read()
    if not raw_text.strip():
        print("❌ No data provided. Please paste the text or pipe a file.")
        sys.exit(1)

    # 2. Remove junk patterns (page headers, footers, repeated titles)
    text = re.sub(r'TOURISM DATA INVENTORY', '', raw_text, flags=re.IGNORECASE)
    text = re.sub(r'Page\s*\|\s*\d+', '', text)
    text = re.sub(r'Total Available Room\s*\d+', '', text)
    # Remove the repeated column header block (handles newlines/spaces variations)
    text = re.sub(r'SL\s*No\.\s+District\s+Accommodation\s+facility\s+Name\s+Location\s+Details\s+Category\s+No\s+of\s+Rooms\s+Contact\s+No', '', text, flags=re.IGNORECASE)

    # Split into lines and remove empty ones
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 3. Merge continuation lines
    # In copy-pasted PDFs, facility names or locations often wrap to the next line.
    # Lines starting with a number are new records; others are continuations.
    merged_lines = []
    for line in lines:
        if re.match(r'^\d+\s', line):
            merged_lines.append(line)
        elif merged_lines:
            merged_lines[-1] += ' ' + line

    # 4. Parse structured data
    categories = {'Economy', '3 Star', '4 Star', '5 Star', 'Residential', 'Boutique'}
    headers = ["SL No.", "District", "Accommodation facility Name", "Location Details", "Category", "No of Rooms", "Contact No"]
    rows = []

    for line in merged_lines:
        # Split by 2+ spaces or tabs. This preserves single spaces inside names/locations.
        parts = [p.strip() for p in re.split(r'\s{2,}|\t', line) if p.strip()]
        if len(parts) < 3:
            continue

        # Extract known fields from the END backwards (most reliable anchor)
        contact = ''
        rooms = ''
        category = ''
        end_idx = len(parts)

        # Contact number (digits, spaces, dashes, slashes, length >= 6)
        if re.match(r'^[\d\s\-\(\)\/\.]{6,}$', parts[-1]):
            contact = parts[-1]
            end_idx = len(parts) - 1

        # Room count (pure digits, ignore commas)
        if end_idx > 0 and parts[end_idx-1].replace(',', '').isdigit():
            rooms = parts[end_idx-1].replace(',', '')
            end_idx -= 1

        # Category (known set)
        if end_idx > 0 and parts[end_idx-1] in categories:
            category = parts[end_idx-1]
            end_idx -= 1

        # Remaining prefix: SL, District, Name & Location combined
        prefix = parts[:end_idx]
        sl = prefix[0] if len(prefix) > 0 else ''
        district = prefix[1] if len(prefix) > 1 else ''
        name_loc = ' '.join(prefix[2:]) if len(prefix) > 2 else ''

        # Append to rows (Location Details left blank as source merges it with Name)
        rows.append([sl, district, name_loc, '', category, rooms, contact])

    # 5. Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ Successfully processed {len(rows)} records.")
    print(f"📄 Output saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # Support: `python script.py < input.txt` OR `cat file.txt | python script.py` OR manual paste
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        out_file = sys.argv[2] if len(sys.argv) > 2 else 'cleaned_tourism_data.csv'
        if not os.path.exists(input_file):
            print(f"❌ Error: File '{input_file}' not found.")
            sys.exit(1)
        with open(input_file, 'r', encoding='utf-8') as f:
            clean_and_export_tourism_data(f, out_file)
    else:
        print("📥 Reading from terminal input. Paste your data below.")
        print("   💡 Finish input with: Ctrl+D (Linux/Mac) or Ctrl+Z then Enter (Windows)")
        clean_and_export_tourism_data(sys.stdin, 'cleaned_tourism_data.csv')
