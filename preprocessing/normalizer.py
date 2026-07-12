import re
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Standard communities
COMMUNITY_ENUM = {'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST'}

# Predefined core branch mappings
CORE_BRANCH_MAP = {
    "COMPUTER SCIENCE AND ENGINEERING": ("CSE", "Computer Science and Engineering"),
    "ELECTRONICS AND COMMUNICATION ENGINEERING": ("ECE", "Electronics and Communication Engineering"),
    "ELECTRICAL AND ELECTRONICS ENGINEERING": ("EEE", "Electrical and Electronics Engineering"),
    "INFORMATION TECHNOLOGY": ("IT", "Information Technology"),
    "MECHANICAL ENGINEERING": ("MECH", "Mechanical Engineering"),
    "CIVIL ENGINEERING": ("CIVIL", "Civil Engineering"),
    "ARTIFICIAL INTELLIGENCE AND DATA SCIENCE": ("AIDS", "Artificial Intelligence and Data Science"),
    "ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING": ("AIML", "Artificial Intelligence and Machine Learning"),
    "BIOTECHNOLOGY": ("BT", "Biotechnology"),
    "BIOMEDICAL ENGINEERING": ("BME", "Biomedical Engineering"),
    "CHEMICAL ENGINEERING": ("CHEM", "Chemical Engineering"),
    "COMPUTER SCIENCE AND BUSINESS SYSTEMS": ("CSBS", "Computer Science and Business Systems"),
    "AERONAUTICAL ENGINEERING": ("AERO", "Aeronautical Engineering"),
    "AUTOMOBILE ENGINEERING": ("AUTO", "Automobile Engineering"),
    "MECHATRONICS ENGINEERING": ("MECHTRON", "Mechatronics Engineering"),
    "ROBOTICS AND AUTOMATION": ("ROB", "Robotics and Automation"),
    "FOOD TECHNOLOGY": ("FOOD", "Food Technology"),
    "TEXTILE TECHNOLOGY": ("TEXTILE", "Textile Technology"),
    "PHARMACEUTICAL TECHNOLOGY": ("PHARM", "Pharmaceutical Technology"),
}

# Synonyms for branch cleanup (normalized uppercase)
BRANCH_SYNONYMS = {
    "AGRICULTURE ENGINEERING": "AGRICULTURAL ENGINEERING",
    "BIO TECHNOLOGY": "BIOTECHNOLOGY",
    "BIO MEDICAL ENGINEERING": "BIOMEDICAL ENGINEERING",
    "COMPUTER SCIENCE AND BUSSINESS SYSTEM": "COMPUTER SCIENCE AND BUSINESS SYSTEMS",
    "COMPUTER SCIENCE AND BUSINESS SYSTEM": "COMPUTER SCIENCE AND BUSINESS SYSTEMS",
    "PRINTING & PACKING TECHNOLOGY": "PRINTING AND PACKING TECHNOLOGY",
    "COMPUTER SCIENCE AND ENGINEERING (AI AND MACHINE LEARNING)": "COMPUTER SCIENCE AND ENGINEERING (ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING)",
    "COMPUTER SCIENCE AND ENGINEERING(ARTIFICIAL INTELLIGENCE)": "COMPUTER SCIENCE AND ENGINEERING (ARTIFICIAL INTELLIGENCE)",
    "ELECTRONICS ENGINEERING (VLSI DESIGN AND TECHNOLOGY)": "ELECTRONICS ENGINEERING (VLSI DESIGN AND TECHNOLOGY)",
    "VLSI DESIGN AND TECHNOLOGY": "ELECTRONICS ENGINEERING (VLSI DESIGN AND TECHNOLOGY)",
    "MECHATRONICS": "MECHATRONICS ENGINEERING",
}

def clean_and_normalize_branch(raw_branch):
    """
    Cleans a branch name, extracts self-supporting/financing suffix, and maps to
    (canonical_code, display_name).
    """
    if pd.isna(raw_branch) or not isinstance(raw_branch, str):
        return "UNKNOWN", "Unknown Branch"
        
    # Convert to uppercase and collapse spaces
    b_upper = re.sub(r'\s+', ' ', raw_branch.strip().upper())
    
    # Detect and extract self-supporting/financing suffixes
    is_ss = False
    ss_patterns = [
        r'\b\(SS\)\b',
        r'\b\(SF\)\b',
        r'\b\(SELF\s*SUPPORTING\)\b',
        r'\b\(SELF\s*FINANCING\)\b',
        r'\bSELF\s*SUPPORTING\b',
        r'\bSELF\s*FINANCING\b'
    ]
    
    for pat in ss_patterns:
        if re.search(pat, b_upper):
            is_ss = True
            b_upper = re.sub(pat, '', b_upper).strip()
            
    # Remove any extra spaces/punctuation at edges
    b_upper = re.sub(r'\s+', ' ', b_upper).strip(' ,-.\t()')
    
    # Map synonyms
    if b_upper in BRANCH_SYNONYMS:
        b_upper = BRANCH_SYNONYMS[b_upper]
        
    # Find or generate canonical code and display name
    if b_upper in CORE_BRANCH_MAP:
        code, display = CORE_BRANCH_MAP[b_upper]
    else:
        # Fallback: Auto-generate code from first letters of words or first 6 letters
        words = b_upper.split()
        if len(words) >= 2:
            code = "".join([w[0] for w in words if w.isalnum()])
        else:
            code = b_upper[:6]
        # Standard title case for display
        display = b_upper.title()
        
    # Append SS indicators if relevant
    if is_ss:
        code = f"{code}_SS"
        display = f"{display} (SS)"
        
    return code, display

def build_canonical_college_mapping(df):
    """
    Builds a stable mapping of Code -> canonical display name.
    The canonical name is the most recent (highest Year) non-null name for that Code.
    """
    # Exclude rows with missing Year or Code or College Name
    valid_df = df.dropna(subset=['Year', 'Code', 'College Name']).copy()
    valid_df = valid_df[valid_df['College Name'].str.strip() != '']
    
    # Sort by Year descending
    valid_df.sort_values(by='Year', ascending=False, inplace=True)
    
    college_map = {}
    for _, row in valid_df.iterrows():
        code = str(row['Code']).strip()
        name = str(row['College Name']).strip()
        # Extract and clean name to title case
        # (clean trailing pincode and format)
        name_clean = re.sub(r'\s+', ' ', name)
        # We title-case for premium display, but preserve acronyms like CEG, ACT, PSG, CIT
        # Let's write a simple smart title casing
        name_title = name_clean.title()
        # Restore common acronyms in uppercase
        acronyms = ['Ceg', 'Act', 'Psg', 'Cit', 'Rit', 'Mit', 'Iit', 'Iiit', 'Nitt', 'Nirf', 'Csi', 'Srm', 'Ssn', 'Jnn', 'Dmi', 'J.J.', 'Jj', 'Vlsi', 'Sle']
        for acr in acronyms:
            name_title = re.sub(rf'\b{acr}\b', acr.upper(), name_title)
            
        if code not in college_map:
            college_map[code] = name_title
            
    logger.info(f"Built canonical college name mapping for {len(college_map)} codes.")
    return college_map

def normalize_dataframe(df, college_map=None):
    """
    Normalizes a DataFrame's college names, branch names, and community names.
    Also validates communities and drops invalid rows.
    """
    df = df.copy()
    
    # 1. Community validation
    initial_len = len(df)
    # Check for invalid communities
    invalid_comm_mask = ~df['Community'].isin(COMMUNITY_ENUM)
    invalid_comms = df[invalid_comm_mask]
    if len(invalid_comms) > 0:
        logger.warning(f"Dropping {len(invalid_comms)} rows with invalid community names: {invalid_comms['Community'].unique()}")
        df = df[~invalid_comm_mask]
        
    # 2. Canonical College Names
    if college_map is None:
        college_map = build_canonical_college_mapping(df)
        
    # Map college names
    df['College Name'] = df['Code'].map(college_map).fillna(df['College Name'])
    
    # 3. Branch Normalization
    branch_codes = []
    branch_displays = []
    
    for branch_str in df['Branch']:
        code, display = clean_and_normalize_branch(branch_str)
        branch_codes.append(code)
        branch_displays.append(display)
        
    df['BranchCode'] = branch_codes
    df['Branch'] = branch_displays  # overwrite raw Branch with standardized display name
    
    logger.info(f"Normalized {len(df)} rows. Dropped {initial_len - len(df)} invalid community rows.")
    return df, college_map
