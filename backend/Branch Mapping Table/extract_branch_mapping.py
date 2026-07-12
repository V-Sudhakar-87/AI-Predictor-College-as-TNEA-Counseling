import pdfplumber
import json

pdf = pdfplumber.open("../pdf/Information_about_colleges_2026.pdf")

branch_mapping = {}

for page in range(60,65):

    page = pdf.pages[page]

    tables = page.extract_tables()

    if not tables:
        continue

    for table in tables:

        for row in table:

            if not row or len(row) < 3:
                continue

            try:
                sno = str(row[0]).strip() if row[0] else ""
                code = str(row[1]).strip() if row[1] else ""
                name = str(row[2]).strip() if row[2] else ""

                # S.No numeric irukkanum
                if not sno.isdigit():
                    continue

                if code and name:
                    branch_mapping[code] = name

            except:
                pass

pdf.close()

with open("branch_mapping.json","w",encoding="utf-8") as f:
    json.dump(branch_mapping,f,indent=4,ensure_ascii=False)

print("✅ Branch Mapping Saved")
print(f"Total Branches : {len(branch_mapping)}")