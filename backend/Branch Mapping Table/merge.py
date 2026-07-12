import json

# Load files
with open("college_seat.json", "r", encoding="utf-8") as f:
    college_seat = json.load(f)

with open("branch_mapping.json", "r", encoding="utf-8") as f:
    branch_map = json.load(f)

final_data = {}
missing_codes = set()

for college_code, branches in college_seat.items():

    final_data[college_code] = {}

    for branch_code, intake in branches.items():

        # Branch code -> Full branch name
        full_name = branch_map.get(branch_code)

        if full_name:
            # Proper title case (optional)
            full_name = full_name.title()
            final_data[college_code][full_name] = intake
        else:
            # If mapping missing
            final_data[college_code][branch_code + " __UNMATCHED__"] = intake
            missing_codes.add(branch_code)

# Save output
with open("final_seat_matrix.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=4, ensure_ascii=False)

print("✅ final_seat_matrix.json generated")

if missing_codes:
    print("\nMissing Branch Codes:")
    print(sorted(missing_codes))
else:
    print("\n✅ All branch codes mapped successfully.")