import os
import joblib
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Global predictor bundle state
_bundle = None

def get_bundle_path():
    """
    Returns the default path to the predictor bundle.
    """
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(curr_dir), 'saved_models', 'tnea_predictor_bundle.joblib')

def load_predictor_bundle(bundle_path=None):
    """
    Loads the model bundle from disk and caches it.
    """
    global _bundle
    if bundle_path is None:
        bundle_path = get_bundle_path()
        
    if not os.path.exists(bundle_path):
        raise FileNotFoundError(f"TNEA Predictor bundle not found at: {bundle_path}. Please train the models first.")
        
    logger.info(f"Loading TNEA Predictor bundle from {bundle_path}...")
    _bundle = joblib.load(bundle_path)
    logger.info("Predictor bundle loaded successfully.")
    return _bundle

def predict(rank: int | None = None, cutoff_mark: float | None = None, community: str = 'OC',
            district: str | None = None, bundle_path: str | None = None) -> list[dict]:
    """
    Predicts and ranks the colleges and branches for a student.
    
    Inputs:
    - rank: Student's TNEA closing rank (better is smaller).
    - cutoff_mark: Student's TNEA cutoff mark (roughly 0-200 scale, better is higher).
    - community: One of 'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST'.
    - district: Optional case-insensitive district filter.
    
    Returns:
    - list[dict]: List of college dictionaries in the format:
      [{"college": "College Name", "branches": ["Branch A", "Branch B", ...]}, ...]
    """
    global _bundle
    if _bundle is None or bundle_path is not None:
        load_predictor_bundle(bundle_path)
        
    # 1. Input Validation & Normalization
    if rank is None and cutoff_mark is None:
        raise ValueError("Either 'rank' or 'cutoff_mark' must be provided.")
        
    comm_clean = str(community).strip().upper()
    valid_comms = {'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST'}
    if comm_clean not in valid_comms:
        raise ValueError(f"Invalid community: {community}. Must be one of {list(valid_comms)}")
        
    master_df = _bundle['master_df']
    precomputed_features = _bundle.get('precomputed_features', None)
    
    if precomputed_features is None:
        # Fallback to computing features on the fly for year 2026
        from training.features import extract_features_for_year
        logger.info("Computing features for 2026 on-the-fly...")
        precomputed_features = extract_features_for_year(master_df, 2026)
        _bundle['precomputed_features'] = precomputed_features
        
    # Filter precomputed features to the specified community
    features_comm = precomputed_features[precomputed_features['Community'] == comm_clean].copy()
    if len(features_comm) == 0:
        logger.warning(f"No historical records found for community: {comm_clean}")
        return []
        
    # 2. Historical Filtering Layer (Feasibility Check)
    # Get latest historical values per group to apply feasibility filtering
    latest_hist = master_df[master_df['Community'] == comm_clean].sort_values(by='Year').groupby(['Code', 'BranchCode']).last().reset_index()
    
    # We outer-join latest historical values with our features
    candidates = pd.merge(features_comm, latest_hist[['Code', 'BranchCode', 'ClosingRank', 'CutoffMark']], on=['Code', 'BranchCode'], how='inner', suffixes=('', '_hist'))
    
    # Filter candidates based on safe margins
    # If user provides rank, we check they are within 15% margin of the historical closing rank
    # If user provides cutoff, we check they are within 5 marks margin of the historical cutoff mark
    if rank is not None and cutoff_mark is not None:
        rank_mask = candidates['ClosingRank_hist'].notna() & (rank <= candidates['ClosingRank_hist'] * 1.15)
        cutoff_mask = candidates['CutoffMark_hist'].notna() & (cutoff_mark >= candidates['CutoffMark_hist'] - 5.0)
        intersection_mask = rank_mask & cutoff_mask
        if intersection_mask.any():
            filter_mask = intersection_mask
        else:
            # Fallback to OR if no colleges satisfy both due to inconsistent user inputs
            filter_mask = rank_mask | cutoff_mask
    elif rank is not None:
        filter_mask = candidates['ClosingRank_hist'].notna() & (rank <= candidates['ClosingRank_hist'] * 1.15)
    elif cutoff_mark is not None:
        filter_mask = candidates['CutoffMark_hist'].notna() & (cutoff_mark >= candidates['CutoffMark_hist'] - 5.0)
    else:
        filter_mask = pd.Series(True, index=candidates.index)
        
    candidates = candidates[filter_mask].copy()
    if len(candidates) == 0:
        return []
        
    # 3. District Filtering
   # if district is not None:
      #  dist_clean = str(district).strip().lower()
        #candidates = candidates[candidates['District'].str.strip().str.lower() == dist_clean].copy()
        #if len(candidates) == 0:
           # return []
    # 3. District Filtering
    if district and str(district).strip():

        dist_clean = str(district).strip().lower()

        candidates = candidates[
            candidates['District'].str.strip().str.lower() == dist_clean].copy()

        if len(candidates) == 0:
            return []
            
    # 4. Predict Expected Ranks and Cutoffs using LightGBM Models
    # Cast categorical features to Pandas category dtype as expected by LightGBM
    X_pred = candidates[_bundle['features']].copy()
    for col in _bundle['categorical_features']:
        X_pred[col] = X_pred[col].astype(str).astype('category')
        
    pred_ranks = _bundle['rank_model'].predict(X_pred)
    pred_cutoffs = _bundle['cutoff_model'].predict(X_pred)
    
    candidates['PredictedClosingRank'] = pred_ranks
    candidates['PredictedCutoffMark'] = pred_cutoffs
    
    # 5. Score Candidates by Admission Strength
    # Score is a measure of safety margin: higher is safer/better
    if rank is not None and cutoff_mark is not None:
        # Combine both margins
        rank_score = (candidates['PredictedClosingRank'] - rank) / (candidates['PredictedClosingRank'] + 1)
        cutoff_score = (cutoff_mark - candidates['PredictedCutoffMark']) / 20.0
        candidates['Score'] = 0.5 * rank_score + 0.5 * cutoff_score
    elif rank is not None:
        candidates['Score'] = (candidates['PredictedClosingRank'] - rank) / (candidates['PredictedClosingRank'] + 1)
    else:
        candidates['Score'] = (cutoff_mark - candidates['PredictedCutoffMark']) / 20.0
        
    # 6. Rank Colleges and Branches
    # Group by Code, sort colleges by their best branch score
    college_best_score = candidates.groupby('Code')['Score'].max().to_dict()
    candidates['CollegeBestScore'] = candidates['Code'].map(college_best_score)
    
    # Sort colleges by CollegeBestScore (descending), then sort branches within each college by Score (descending)
    candidates.sort_values(by=['CollegeBestScore', 'Code', 'Score'], ascending=[False, True, False], inplace=True)
    
    # 7. Format Output (No numeric scores or probabilities)
    results = []
    # Group by canonical college name while keeping the sorted order
    # Pandas groupby does not guarantee keeping the sorting of keys, so we iterate through unique sorted codes
    sorted_codes = candidates['Code'].unique()
    
    for code in sorted_codes:
        col_df = candidates[candidates['Code'] == code]
        college_name = col_df.iloc[0]['College Name']
        district_name = col_df.iloc[0]['District']
        branches = col_df['Branch'].tolist()
        results.append({
            "code": code,
            "college": college_name,
            "district": district_name,
            "branches": branches
        })
        
    return results
