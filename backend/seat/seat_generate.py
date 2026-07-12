import pdfplumber
import json
import re

pdf = pdfplumber.open("../pdf/Information_about_colleges_2026.pdf")

seat_matrix = {}

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

    branch_intake = {}

    collecting = False

    for table in tables:

        for row in table:

            if not row:
                continue

            first = row[0].strip() if row[0] else ""

        # Header detect
            if first == "SL.No":
                collecting = True
                continue

            if collecting:

                if len(row) >= 3:

                    branch = row[1].strip() if row[1] else ""
                    intake = row[2].strip() if row[2] else ""

                    if re.fullmatch(r"[A-Z]{2}", branch) and intake.isdigit():
                        branch_intake[branch] = int(intake)

    seat_matrix[college_code] = branch_intake

# ==================================================
# SAVE JSON
# ==================================================

with open("college_seat.json", "w", encoding="utf-8") as f:
    json.dump(seat_matrix, f, indent=4, ensure_ascii=False)

print("\n✅ JSON Saved Successfully")

print(json.dumps(seat_matrix, indent=4, ensure_ascii=False))