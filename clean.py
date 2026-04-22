import re
import csv
import os

def process_tourism_data(input_file, output_file):
    # 1. Read the raw text
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # 2. Remove junk patterns (headers, page numbers, footers)
    text = re.sub(r'TOURISM DATA INVENTORY', '', text)
    text = re.sub(r'Page\s*\|\s*\d+', '', text)
    text = re.sub(r'Total Available Room\s*\d+', '', text)
    # Remove repeated column headers that appear after page breaks
    text = re.sub(r'SL No\.\s+District\s+Accommodation facility Name\s+Location Details\s+Category\s+No of\nRooms\s+Contact No', '', text)

    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 3. Merge continuation lines 
    # (In copy-pasted tables, location/name often wraps to the next line)
    merged_lines = []
    for line in lines:
        if re.match(r'^\d+\s', line):
            merged_lines.append(line)
        elif merged_lines:
            merged_lines[-1] += " " + line

    # 4. Parse each line into structured columns
    categories = {'Economy', '3 Star', '4 Star', '5 Star', 'Residential', 'Boutique'}
    headers = ["SL No.", "District", "Accommodation facility Name", "Location Details", "Category", "No of Rooms", "Contact No"]
    rows = []

    for line in merged_lines:
        # Split by 2+ spaces or tabs (standard delimiter for this dataset)
        parts = [p.strip() for p in re.split(r'\s{2,}|\t', line) if p.strip()]
        if len(parts) < 4:
            continue  # Skip malformed/empty lines

        # 🔍 Smart extraction from the END of the line (most reliable anchor)
        contact = parts[-1] if re.match(r'^[\d\s\-]{7,}$', parts[-1]) else ""
        rooms_idx = -2 if contact else -1
        rooms = parts[rooms_idx] if parts[rooms_idx].isdigit() else ""
        cat_idx = rooms_idx - 1
        category = parts[cat_idx] if parts[cat_idx] in categories else ""

        # Remaining parts are SL, District, Name, Location
        prefix = parts[:cat_idx]
        sl = prefix[0]
        district = prefix[1] if len(prefix) > 1 else ""
        
        # Combine remaining text into Name (Location often merges with Name in source)
        name_location = " ".join(prefix[2:]) if len(prefix) > 2 else ""

        rows.append([sl, district, name_location, "", category, rooms, contact])

    # 5. Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"✅ Successfully processed {len(rows)} records.")
    print(f"📄 Output saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # 🔧 Update these paths if your files are in different locations
    INPUT_FILE = "Pasted_Text_1776868852948.txt"
    OUTPUT_FILE = "tourism_accommodation_clean.csv"
    
    if os.path.exists(INPUT_FILE):
        process_tourism_data(INPUT_FILE, OUTPUT_FILE)
    else:
        print(f"❌ Input file '{INPUT_FILE}' not found. Please place it in the same directory or update the path.")
