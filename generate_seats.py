"""
Generate frontend/src/data/seats.js from the 5-year TNEA dataset.
Uses AICTE intake norms to estimate seat counts per college-branch.
"""
import json
import joblib
import pandas as pd

# ── Load the model bundle (contains master_df with all 5 years) ──────────────
bundle = joblib.load('saved_models/tnea_predictor_bundle.joblib')
master_df = bundle['master_df']

# ── Get unique college-branch pairs from 2025 (most recent year) ─────────────
year2025 = master_df[master_df['Year'] == 2025].copy()
pairs = year2025[['Code', 'Branch', 'College Name']].drop_duplicates().reset_index(drop=True)
pairs['branch_lower'] = pairs['Branch'].str.lower().str.strip()

# ── Estimate intake based on AICTE / TNEA norms ──────────────────────────────
"""
def estimate_intake(row):
    code = int(row['Code'])
    branch = row['branch_lower']
    college = str(row['College Name']).lower()

    # Anna University own departments (codes 1-5) = selective, 60 seats
    if code <= 5:
        return 60

    is_govt = 'government' in college or 'govt' in college

    is_cs = any(k in branch for k in [
        'computer science', 'information technology',
        'artificial intelligence', 'data science',
        'cyber security', 'cloud computing', 'machine learning'
    ])
    is_mech = 'mechanical engineering' in branch and 'mechatronics' not in branch
    is_civil = 'civil engineering' in branch
    is_niche = any(k in branch for k in [
        'naval', 'aerospace', 'mining', 'petroleum',
        'textile', 'fashion', 'rubber', 'printing',
        'agricultural', 'marine', 'metallurgical'
    ])

    if is_niche:
        return 60
    if is_govt and (is_mech or is_civil):
        return 120
    if not is_govt and is_cs:
        return 120
    return 60


pairs['seats'] = pairs.apply(estimate_intake, axis=1)

# ── Build nested dict: { "code": { "Branch": seats, ... }, ... } ─────────────
result = {}
for _, row in pairs.iterrows():
    code = str(row['Code'])
    branch = str(row['Branch'])
    seats = int(row['seats'])
    if code not in result:
        result[code] = {}
    result[code][branch] = seats"""

# Read final seat json
with open("final_seat_matrix.json","r",encoding="utf-8") as f:
    result = json.load(f)

print(f"Loaded {len(result)} colleges")

print(f"Generated: {len(result)} colleges, {sum(len(v) for v in result.values())} college-branch entries")

# ── Write seats.js ────────────────────────────────────────────────────────────
seats_json = json.dumps(result, ensure_ascii=False, indent=2)

js_content = f'''/**
 * TNEA College Branch Seat Intake Data
 * Auto-generated from 5-year TNEA dataset (2021-2025) using AICTE intake norms.
 * Covers {len(result)} colleges and {sum(len(v) for v in result.values())} college-branch pairs across Tamil Nadu.
 *
 * Intake logic (based on AICTE approval norms):
 *   CS / IT / AI / DS branches at private colleges  → 120 seats
 *   Mech / Civil at Government aided colleges       → 120 seats
 *   ECE, EEE, and most other branches              →  60 seats
 *   Niche / specialized branches                   →  60 seats
 *
 * TO UPDATE WITH REAL DATA after counselling:
 *   Replace individual values below with actual seat intake from TNEA seat matrix.
 *   The college code matches the CODE shown on each result card.
 */

export const SEATS_BY_COLLEGE = {seats_json};

/**
 * Fallback defaults when a specific college-branch entry is not found.
 */
export const DEFAULT_SEATS_BY_BRANCH = {{
  'computer science and engineering': 120,
  'computer science': 120,
  'information technology': 120,
  'artificial intelligence': 120,
  'artificial intelligence and data science': 120,
  'artificial intelligence and machine learning': 120,
  'data science': 120,
  'cyber security': 120,
  'electronics and communication engineering': 60,
  'electrical and electronics engineering': 60,
  'mechanical engineering': 60,
  'civil engineering': 60,
  'chemical engineering': 60,
  'biotechnology': 60,
  'biomedical engineering': 60,
  'aerospace engineering': 60,
  'automobile engineering': 60,
  'mechatronics': 60,
  'robotics and automation': 60,
  'instrumentation and control': 60,
  'production engineering': 60,
}};

/**
 * Returns the seat count for a given college + branch.
 * Priority: college-specific lookup → branch keyword match → 60 (fallback).
 *
 * @param {{string}} collegeCode  - College code string (e.g. "1234")
 * @param {{string}} branchName   - Branch name as returned by the API
 * @returns {{number}}            - Seat count
 */
export function getSeats(collegeCode, branchName) {{
  const collegeSeats = SEATS_BY_COLLEGE[String(collegeCode)];
  if (collegeSeats) {{
    const exact = collegeSeats[branchName];
    if (exact !== undefined) return exact;
    const bl = branchName.toLowerCase();
    for (const [key, val] of Object.entries(collegeSeats)) {{
      if (key.toLowerCase() === bl) return val;
    }}
  }}
  const bl = branchName.toLowerCase();
  for (const [kw, seats] of Object.entries(DEFAULT_SEATS_BY_BRANCH)) {{
    if (bl.includes(kw)) return seats;
  }}
  return 60;
}}
'''

output_path = 'frontend/src/data/seats.js'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Written to {output_path}")
print(f"File size: {len(js_content):,} chars")
