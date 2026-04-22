import re
import csv
import os
from datetime import datetime


def remove_unwanted_lines(text: str) -> str:
    """Remove page numbers, headers, and footers from the text."""
    lines = text.splitlines()
    cleaned = []
    
    patterns_to_skip = [
        r"^TOURISM\s+DATA\s+INVENTORY\s*$",
        r"^Page\s*\|\s*\d+\s*$",
        r"^SL\s+No\.\s+District.*Contact\s+No\s*$",
        r"^Total\s+Available\s+Room\s+\d+\s*$",
    ]
    
    for line in lines:
        skip = False
        for pattern in patterns_to_skip:
            if re.match(pattern, line.strip(), re.IGNORECASE):
                skip = True
                break
        
        if not skip and line.strip():
            cleaned.append(line)
    
    return '\n'.join(cleaned)


def parse_row(line: str) -> dict:
    """Parse a single data row using flexible splitting."""
    # Remove extra spaces and split
    parts = line.split()
    
    if len(parts) < 2:
        return None
    
    # SL No is always first
    sl_no = parts[0]
    
    # District is typically 2nd (next meaningful part)
    # Names can have multiple words, locations can too
    # Contact is usually last (all digits or in pattern)
    # Category and Rooms are usually near end
    
    # Find contact number (usually all digits or pattern at end)
    contact = ""
    remainder = " ".join(parts[1:])
    
    # Extract last number-like token as contact
    contact_match = re.search(r'(\d{7,}|\d{4}-\d{6}|0\d{10})\s*$', remainder)
    if contact_match:
        contact = contact_match.group(1)
        remainder = remainder[:contact_match.start()].strip()
    
    # Extract rooms (usually a single number before contact)
    rooms_match = re.search(r'\b(\d+)\s+(' + '|'.join(['Economy', '3 Star', '4 Star', '5 Star', 'Boutique', 'Residential']) + r')\s*$', remainder, re.IGNORECASE)
    rooms = ""
    category = ""
    if rooms_match:
        rooms = rooms_match.group(1)
        category = rooms_match.group(2)
        remainder = remainder[:rooms_match.start()].strip()
    else:
        # Try to find category alone
        cat_match = re.search(r'\b(Economy|3 Star|4 Star|5 Star|Boutique|Residential)\s*$', remainder, re.IGNORECASE)
        if cat_match:
            category = cat_match.group(1)
            remainder = remainder[:cat_match.start()].strip()
    
    # Now remainder has: district, facility name, and location
    tokens = remainder.split()
    if len(tokens) >= 3:
        district = tokens[0]
        # Last token(s) before category could be location or facility name
        # This is tricky - we'll use a simple heuristic
        facility_name = " ".join(tokens[1:-1]) if len(tokens) > 2 else tokens[1]
        location = tokens[-1]
    elif len(tokens) == 2:
        district = tokens[0]
        facility_name = tokens[1]
        location = ""
    else:
        return None
    
    return {
        'SL No': sl_no,
        'District': district,
        'Facility Name': facility_name,
        'Location': location,
        'Category': category if category else "Economy",
        'Rooms': rooms,
        'Contact': contact,
    }


def convert_to_csv(input_text: str, output_file: str):
    """Convert cleaned text to CSV."""
    
    # Clean the text
    cleaned_text = remove_unwanted_lines(input_text)
    
    rows = []
    for line in cleaned_text.splitlines():
        if line.strip():
            parsed = parse_row(line)
            if parsed:
                rows.append(parsed)
    
    if not rows:
        print("❌ No valid rows found!")
        return False
    
    # Write to CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['SL No', 'District', 'Facility Name', 'Location', 'Category', 'Rooms', 'Contact']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return True, rows
    except Exception as e:
        print(f"❌ Error writing CSV: {e}")
        return False, None


def main():
    print("=" * 75)
    print("  TOURISM DATA CLEANER - CSV CONVERTER")
    print("=" * 75)
    print("\nChoose input method:")
    print("  1. Paste text directly")
    print("  2. Read from file")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        file_path = input("Enter file path: ").strip()
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            input_text = f.read()
    else:
        print("\n📋 Paste your data (type END on new line when done):\n")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            except EOFError:
                break
        input_text = "\n".join(lines)
    
    if not input_text.strip():
        print("❌ No input provided")
        return
    
    # Create output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"tourism_data_{timestamp}.csv"
    
    print(f"\n🔄 Converting to CSV...")
    result, rows = convert_to_csv(input_text, output_file)
    
    if result:
        print(f"\n✅ Success!")
        print(f"{'='*75}")
        print(f"  📁 Output file: {os.path.abspath(output_file)}")
        print(f"  📊 Total rows: {len(rows)}")
        print(f"{'='*75}\n")
        
        print("📋 First 5 rows:\n")
        for i, row in enumerate(rows[:5], 1):
            print(f"{i}. {row['District']:12} | {row['Facility Name']:30} | {row['Rooms']:>3} rooms")
        
        if len(rows) > 5:
            print(f"\n... and {len(rows) - 5} more rows\n")
    else:
        print("❌ Conversion failed")


if __name__ == "__main__":
    main()
