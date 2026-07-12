import pdfplumber
import json
import re

pdf = pdfplumber.open("pdf/Information_about_colleges_2026.pdf")

college_data = {}

for page_no in range(64, len(pdf.pages)):   # Page 65 onwards

    page = pdf.pages[page_no]

    text = page.extract_text()

    if not text:
        continue

    # ==================================================
# COLLEGE CODE
# ==================================================

    lines = text.split("\n")

    college_code = None

    if len(lines) > 0:

        first_line = lines[0].strip()

    # First word of first line
        first_word = first_line.split()[0]

    # If first word is a number -> that's the college code
        if first_word.isdigit():

            college_code = first_word

    # Otherwise first line starts with text,
    # so take first word of second line
        elif len(lines) > 1:

            second_line = lines[1].strip()

            second_word = second_line.split()[0]

            if second_word.isdigit():

                college_code = second_word

    print(f"College Code : {college_code}")

    # ==================================================
    # HOSTEL TABLE
    # ==================================================

    tables = page.extract_tables()

    hostel = {}

    website = ""
    
    dean_principal = ""

    collecting = False

    for table in tables:

        for row in table:

            if not row:
                continue

            # Website
            if row and row[0]:
                key = row[0].strip()

                if key == "Website":
                    website = row[1].strip() if len(row) > 1 and row[1] else ""

                if key == "Dean/Principal":
                    dean_principal = row[1].strip() if len(row) > 1 and row[1] else ""

            key = row[0].strip() if row[0] else ""

            # Start Hostel Table
            if key == "Hostel Facilities":
                collecting = True
                continue

            if collecting:

                boys = ""

                girls = ""

                if len(row) > 1 and row[1]:
                    boys = row[1].strip()

                if len(row) > 2 and row[2]:
                    girls = row[2].strip()
                else:
                    girls = boys

                hostel[key] = {
                    "boys": boys,
                    "girls": girls
                }

            # End Hostel Table
            if key == "Max Transport\nCharges":
                collecting = False

    college_data[college_code] = {
        "website":website,
        "dean_principal": dean_principal,
        "hostel": hostel
    }

# ==================================================
# SAVE JSON
# ==================================================

with open("college_details.json", "w", encoding="utf-8") as f:
    json.dump(college_data, f, indent=4, ensure_ascii=False)

print("\n✅ JSON Saved Successfully")

print(json.dumps(college_data, indent=4, ensure_ascii=False))