import re
import pandas as pd
import numpy as np
import logging
from collections import Counter

logger = logging.getLogger(__name__)

DISTRICTS_LIST = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
    "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kanchipuram",
    "Kanyakumari", "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Nilgiris", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivaganga", "Tenkasi",
    "Thanjavur", "Theni", "Thoothukudi", "Tiruchirappalli", "Tirunelveli",
    "Tirupathur", "Tiruppur", "Tiruvallur", "Tiruvannamalai", "Tiruvarur",
    "Vellore", "Viluppuram", "Virudhunagar"
]

CITY_TO_DISTRICT = {
    "chennai": "Chennai",
    "coimbatore": "Coimbatore",
    "comibatore": "Coimbatore",
    "madurai": "Madurai",
    "trichy": "Tiruchirappalli",
    "tiruchirappalli": "Tiruchirappalli",
    "thiruchirappalli": "Tiruchirappalli",
    "salem": "Salem",
    "tirunelveli": "Tirunelveli",
    "thirunelveli": "Tirunelveli",
    "erode": "Erode",
    "vellore": "Vellore",
    "nagercoil": "Kanyakumari",
    "kanyakumari": "Kanyakumari",
    "kanyakumarai": "Kanyakumari",
    "nagapattinam": "Nagapattinam",
    "nagappattinam": "Nagapattinam",
    "nilgiris": "Nilgiris",
    "nilgiri": "Nilgiris",
    "thanjavur": "Thanjavur",
    "tanjore": "Thanjavur",
    "kanchipuram": "Kanchipuram",
    "kancheepuram": "Kanchipuram",
    "tiruvallur": "Tiruvallur",
    "thiruvallur": "Tiruvallur",
    "chengalpattu": "Chengalpattu",
    "cuddalore": "Cuddalore",
    "dindigul": "Dindigul",
    "thoothukudi": "Thoothukudi",
    "tuticorin": "Thoothukudi",
    "ooty": "Nilgiris",
    "udhagamandalam": "Nilgiris",
    "pollachi": "Coimbatore",
    "karaikudi": "Sivaganga",
    "hosur": "Krishnagiri",
    "krishnagiri": "Krishnagiri",
    "namakkal": "Namakkal",
    "karur": "Karur",
    "perambalur": "Perambalur",
    "ariyalur": "Ariyalur",
    "pudukkottai": "Pudukkottai",
    "sivaganga": "Sivaganga",
    "sivagangai": "Sivaganga",
    "ramanathapuram": "Ramanathapuram",
    "theni": "Theni",
    "virudhunagar": "Virudhunagar",
    "tiruppur": "Tiruppur",
    "tirupur": "Tiruppur",
    "tenkasi": "Tenkasi",
    "ranipet": "Ranipet",
    "tirupathur": "Tirupathur",
    "tirupattur": "Tirupathur",
    "kallakurichi": "Kallakurichi",
    "kallakkurichi": "Kallakurichi",
    "mayiladuthurai": "Mayiladuthurai",
    "tiruvarur": "Tiruvarur",
    "thiruvarur": "Tiruvarur",
    "dharmapuri": "Dharmapuri",
    "villupuram": "Viluppuram",
    "viluppuram": "Viluppuram",
    "tiruvannamalai": "Tiruvannamalai",
    "thiruvannamalai": "Tiruvannamalai",
    "avadi": "Tiruvallur",
    "tambaram": "Chengalpattu",
    "chromepet": "Chengalpattu",
    "guindy": "Chennai",
    "annamalai nagar": "Cuddalore",
    "chidambaram": "Cuddalore",
    "karaikal": "Puducherry",
    "pondy": "Puducherry",
    "pondicherry": "Puducherry",
}

def extract_pin_and_clean_name(name_str):
    """
    Extracts the 6-digit PIN code starting with '6' and returns
    (cleaned_name, pin_code). PIN code is returned as a 6-character string or None.
    """
    if not isinstance(name_str, str):
        return "", None
        
    # Match 6-digit PIN code (handles spaces, e.g. '600 025' or '600-025')
    pin_match = re.search(r'\b(6\d{2})\s*-?\s*(\d{3})\b', name_str)
    pin_code = None
    cleaned_name = name_str
    
    if pin_match:
        pin_code = f"{pin_match.group(1)}{pin_match.group(2)}"
        # Remove the match from the name string
        cleaned_name = name_str[:pin_match.start()] + name_str[pin_match.end():]
        
    # Standardize whitespace and remove trailing commas/hyphens/periods
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
    cleaned_name = cleaned_name.strip(' ,-.\t')
    return cleaned_name, pin_code

def resolve_district_rules(name_str):
    """
    Applies the first two rules:
    1. Check for '<Name> District/Dist/Dt'
    2. Check for known cities/towns in the name string
    Returns (district, confidence_flag) or (None, None).
    """
    # Rule 1: Check for '<Name> District/Dist/Dt'
    dist_match = re.search(r'\b([A-Za-z]+)\s*(?:District|Dist|Dt)\b', name_str, re.IGNORECASE)
    if dist_match:
        cand = dist_match.group(1).lower()
        if cand in CITY_TO_DISTRICT:
            return CITY_TO_DISTRICT[cand], "regex_district_word"
        for d in DISTRICTS_LIST:
            if d.lower() == cand:
                return d, "regex_district_word"
                
    # Rule 2: Check for known cities/towns
    for city, dist in CITY_TO_DISTRICT.items():
        if re.search(rf'\b{re.escape(city)}\b', name_str, re.IGNORECASE):
            return dist, "known_city"
            
    return None, None

def apply_district_extraction(df, pincode_prefix_lookup=None):
    """
    Applies district extraction to the DataFrame.
    If pincode_prefix_lookup is provided, it is used for Rule 3.
    Otherwise, a lookup table is generated from the resolved rows in df.
    Returns (processed_df, pincode_prefix_lookup).
    """
    df = df.copy()
    
    # First, extract PIN code and clean name
    pins = []
    cleaned_names = []
    for name in df['College Name']:
        cleaned, pin = extract_pin_and_clean_name(name)
        pins.append(pin)
        cleaned_names.append(cleaned)
        
    df['PinCode'] = pins
    df['CleanCollegeName'] = cleaned_names
    
    # Try Rule 1 & Rule 2
    districts = []
    confidences = []
    
    for cleaned_name in df['CleanCollegeName']:
        dist, conf = resolve_district_rules(cleaned_name)
        districts.append(dist)
        confidences.append(conf)
        
    df['District'] = districts
    df['DistrictConfidence'] = confidences
    
    # Build PIN prefix lookup table if not provided
    if pincode_prefix_lookup is None:
        pincode_prefix_lookup = {}
        # Get all rows that successfully resolved via Rule 1 or 2 and have a PinCode
        resolved_mask = df['District'].notna() & df['PinCode'].notna()
        resolved_df = df[resolved_mask]
        
        prefix_groups = {}
        for _, row in resolved_df.iterrows():
            pref = row['PinCode'][:3]
            dist = row['District']
            if pref not in prefix_groups:
                prefix_groups[pref] = []
            prefix_groups[pref].append(dist)
            
        for pref, dists in prefix_groups.items():
            pincode_prefix_lookup[pref] = Counter(dists).most_common(1)[0][0]
            
        logger.info(f"Built PIN prefix lookup table with {len(pincode_prefix_lookup)} prefixes.")
        
    # Rule 3: Fallback to PIN code prefix lookup for unresolved rows
    final_districts = []
    final_confidences = []
    
    for idx, row in df.iterrows():
        dist = row['District']
        conf = row['DistrictConfidence']
        
        if pd.isna(dist) or dist is None:
            pin = row['PinCode']
            if pin is not None:
                pref = pin[:3]
                if pref in pincode_prefix_lookup:
                    final_districts.append(pincode_prefix_lookup[pref])
                    final_confidences.append("pincode_lookup")
                    continue
            # Default fallback
            final_districts.append("Unknown")
            final_confidences.append("unknown")
        else:
            final_districts.append(dist)
            final_confidences.append(conf)
            
    df['District'] = final_districts
    df['DistrictConfidence'] = final_confidences
    
    # Drop temporary cleaning columns
    df.drop(columns=['CleanCollegeName'], inplace=True)
    
    return df, pincode_prefix_lookup
