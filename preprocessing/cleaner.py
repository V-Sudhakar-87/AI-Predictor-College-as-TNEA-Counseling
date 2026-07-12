import os
import glob
import re
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def clean_numeric(val):
    """
    Cleans a numeric string (handles commas, quotes, asterisks, em-dashes).
    Returns float or NaN.
    """
    if pd.isna(val):
        return np.nan
    if not isinstance(val, str):
        return float(val)
    
    val_clean = val.strip().replace('"', '').replace("'", '')
    if val_clean == '—' or val_clean == '' or val_clean.lower() == 'nan':
        return np.nan
        
    # Remove thousands separators and any trailing symbols like asterisks
    val_clean = val_clean.replace(',', '')
    val_clean = re.sub(r'[^\d\.]', '', val_clean)
    
    if val_clean == '':
        return np.nan
    try:
        return float(val_clean)
    except ValueError:
        logger.warning(f"Failed to parse numeric value: {repr(val)}")
        return np.nan

def load_and_melt_csv(filepath, value_name):
    """
    Loads a TNEA CSV file (either RankList or cutoff), melts the community columns,
    and returns a long-format DataFrame.
    """
    # Open with utf-8-sig to automatically strip BOM (\ufeff)
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    
    # Strip whitespace from column names
    df.columns = [col.strip() for col in df.columns]
    
    # Verify required base columns
    required_cols = ['Year', 'Code', 'College Name', 'Branch']
    for col in required_cols:
        if col not in df.columns:
            # Handle potential lowercase or misspelled columns
            matched = [c for c in df.columns if c.lower() == col.lower()]
            if matched:
                df.rename(columns={matched[0]: col}, inplace=True)
            else:
                raise ValueError(f"Required column '{col}' missing in {filepath}. Found columns: {list(df.columns)}")
                
    # Define community columns
    communities = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    # Filter to only keep columns that exist
    id_vars = [c for c in required_cols if c in df.columns]
    value_vars = [c for c in communities if c in df.columns]
    
    if not value_vars:
        raise ValueError(f"No community columns found in {filepath}. Expected some of {communities}")
        
    # Melt dataframe
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name='Community',
        value_name=value_name
    )
    
    # Pre-clean Year and Code to ensure stable joins
    df_long['Year'] = pd.to_numeric(df_long['Year'], errors='coerce').astype('Int64')
    # Code is read as string/float, let's cast to string then clean
    df_long['Code'] = df_long['Code'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    
    # Apply numeric cleaning to the rank or cutoff value
    df_long[value_name] = df_long[value_name].apply(clean_numeric)
    
    # Normalize spaces in string columns
    df_long['College Name'] = df_long['College Name'].astype(str).str.strip()
    df_long['Branch'] = df_long['Branch'].astype(str).str.strip()
    df_long['Community'] = df_long['Community'].astype(str).str.strip()
    
    return df_long

def assemble_master_dataset(raw_dir):
    """
    Reads all present RankList and cutoff files from raw_dir, melts them,
    and outer-joins them on (Year, Code, Branch, Community).
    """
    rank_files = glob.glob(os.path.join(raw_dir, "RankList_*.csv"))
    cutoff_files = glob.glob(os.path.join(raw_dir, "cutoff_*.csv"))
    
    logger.info(f"Found {len(rank_files)} rank files and {len(cutoff_files)} cutoff files.")
    
    rank_dfs = []
    for f in rank_files:
        try:
            logger.info(f"Loading and melting rank file: {os.path.basename(f)}")
            df_melted = load_and_melt_csv(f, 'ClosingRank')
            rank_dfs.append(df_melted)
        except Exception as e:
            logger.error(f"Error loading {f}: {e}")
            
    cutoff_dfs = []
    for f in cutoff_files:
        try:
            logger.info(f"Loading and melting cutoff file: {os.path.basename(f)}")
            df_melted = load_and_melt_csv(f, 'CutoffMark')
            cutoff_dfs.append(df_melted)
        except Exception as e:
            logger.error(f"Error loading {f}: {e}")
            
    if not rank_dfs and not cutoff_dfs:
        raise FileNotFoundError(f"No valid TNEA data files found in {raw_dir}")
        
    rank_all = pd.concat(rank_dfs, ignore_index=True) if rank_dfs else pd.DataFrame(columns=['Year', 'Code', 'College Name', 'Branch', 'Community', 'ClosingRank'])
    cutoff_all = pd.concat(cutoff_dfs, ignore_index=True) if cutoff_dfs else pd.DataFrame(columns=['Year', 'Code', 'College Name', 'Branch', 'Community', 'CutoffMark'])
    
    logger.info(f"Combined rank dataset: {len(rank_all)} rows.")
    logger.info(f"Combined cutoff dataset: {len(cutoff_all)} rows.")
    
    # Outer join on Year, Code, Branch, Community
    join_keys = ['Year', 'Code', 'Branch', 'Community']
    master_df = pd.merge(
        rank_all,
        cutoff_all,
        on=join_keys,
        how='outer',
        suffixes=('_rank', '_cutoff')
    )
    
    # Combine College Name columns
    if 'College Name_rank' in master_df.columns and 'College Name_cutoff' in master_df.columns:
        master_df['College Name'] = master_df['College Name_rank'].fillna(master_df['College Name_cutoff'])
        master_df.drop(columns=['College Name_rank', 'College Name_cutoff'], inplace=True)
    elif 'College Name_rank' in master_df.columns:
        master_df.rename(columns={'College Name_rank': 'College Name'}, inplace=True)
    elif 'College Name_cutoff' in master_df.columns:
        master_df.rename(columns={'College Name_cutoff': 'College Name'}, inplace=True)
        
    logger.info(f"Assembled master dataset: {len(master_df)} rows.")
    return master_df

def preprocess_tnea_data(raw_dir):
    """
    Orchestrates the entire preprocessing pipeline.
    """
    from preprocessing.district import apply_district_extraction
    from preprocessing.normalizer import normalize_dataframe
    
    # 1. Load and merge files
    df = assemble_master_dataset(raw_dir)
    
    # 2. Extract districts and pin codes
    df, pincode_prefix_lookup = apply_district_extraction(df)
    
    # 3. Normalize names and community
    df, college_map = normalize_dataframe(df)
    
    # 4. Drop duplicates
    initial_cnt = len(df)
    df.drop_duplicates(inplace=True)
    dup_cnt = initial_cnt - len(df)
    if dup_cnt > 0:
        logger.info(f"Dropped {dup_cnt} exact duplicate rows.")
        
    # 5. Drop structurally invalid rows
    final_cnt = len(df)
    
    # Check invalid code
    invalid_code = df['Code'].isna() | (df['Code'].str.strip() == '') | (df['Code'].str.lower() == 'nan')
    df_invalid_code = df[invalid_code]
    if len(df_invalid_code) > 0:
        logger.warning(f"Dropping {len(df_invalid_code)} rows with invalid or missing Code.")
        df = df[~invalid_code]
        
    # Check invalid year
    invalid_year = df['Year'].isna()
    df_invalid_year = df[invalid_year]
    if len(df_invalid_year) > 0:
        logger.warning(f"Dropping {len(df_invalid_year)} rows with missing Year.")
        df = df[~invalid_year]
        
    # Check invalid rank (must be positive if present)
    invalid_rank = df['ClosingRank'].notna() & (df['ClosingRank'] <= 0)
    df_invalid_rank = df[invalid_rank]
    if len(df_invalid_rank) > 0:
        logger.warning(f"Dropping {len(df_invalid_rank)} rows with non-positive ClosingRank.")
        df = df[~invalid_rank]
        
    # Check invalid cutoff mark (must be in [0, 200] if present)
    invalid_cutoff = df['CutoffMark'].notna() & ((df['CutoffMark'] < 0) | (df['CutoffMark'] > 200))
    df_invalid_cutoff = df[invalid_cutoff]
    if len(df_invalid_cutoff) > 0:
        logger.warning(f"Dropping {len(df_invalid_cutoff)} rows with CutoffMark outside [0, 200] range.")
        df = df[~invalid_cutoff]
        
    # Check if BOTH are null (nothing to predict)
    both_null = df['ClosingRank'].isna() & (df['CutoffMark'].isna())
    df_both_null = df[both_null]
    if len(df_both_null) > 0:
        logger.warning(f"Dropping {len(df_both_null)} rows where both ClosingRank and CutoffMark are null.")
        df = df[~both_null]
        
    dropped_cnt = final_cnt - len(df)
    logger.info(f"Dropped {dropped_cnt} structurally invalid rows in total. Remaining rows: {len(df)}.")
    
    return df, pincode_prefix_lookup, college_map

