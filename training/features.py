import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def compute_slope(row):
    """
    Fits a linear regression line to row values (indices are years)
    and returns the slope. Returns NaN if < 2 points are valid.
    """
    valid = row.dropna()
    if len(valid) < 2:
        return np.nan
    x = valid.index.values.astype(float)
    y = valid.values.astype(float)
    # Simple linear regression formula for slope
    n = len(x)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)
    if denominator == 0:
        return np.nan
    return numerator / denominator

def extract_features_for_year(df, target_year):
    """
    Computes features for target_year using data from prior years (Year < target_year).
    Returns a DataFrame of features for each unique (Code, BranchCode, Community) group.
    """
    prior_df = df[df['Year'] < target_year].copy()
    if len(prior_df) == 0:
        logger.warning(f"No prior data available to build features for target year {target_year}")
        return pd.DataFrame()
        
    prior_years = sorted(prior_df['Year'].unique())
    logger.info(f"Building features for year {target_year} using historical years: {prior_years}")
    
    # 1. Pivot ranks and cutoffs across prior years to easily calculate rolling stats and lags
    pivot_rank = prior_df.pivot_table(
        index=['Code', 'BranchCode', 'Community'],
        columns='Year',
        values='ClosingRank',
        aggfunc='first'
    ).reindex(columns=prior_years)
    
    pivot_cutoff = prior_df.pivot_table(
        index=['Code', 'BranchCode', 'Community'],
        columns='Year',
        values='CutoffMark',
        aggfunc='first'
    ).reindex(columns=prior_years)
    
    # Initialize features DataFrame
    features = pd.DataFrame(index=pivot_rank.index)
    
    # 2. Lag Features
    # T-1
    t1 = target_year - 1
    features['prev_rank'] = pivot_rank[t1] if t1 in prior_years else np.nan
    features['prev_cutoff'] = pivot_cutoff[t1] if t1 in prior_years else np.nan
    
    # T-2
    t2 = target_year - 2
    features['prev2_rank'] = pivot_rank[t2] if t2 in prior_years else np.nan
    features['prev2_cutoff'] = pivot_cutoff[t2] if t2 in prior_years else np.nan
    
    # 3. Rolling Statistics (Mean and Volatility/Std Dev)
    features['rolling_mean_rank'] = pivot_rank.mean(axis=1)
    features['rolling_mean_cutoff'] = pivot_cutoff.mean(axis=1)
    features['rolling_std_rank'] = pivot_rank.std(axis=1)
    features['rolling_std_cutoff'] = pivot_cutoff.std(axis=1)
    
    # 4. Multi-year Trend (Slope of rank and cutoff)
    features['slope_rank'] = pivot_rank.apply(compute_slope, axis=1)
    features['slope_cutoff'] = pivot_cutoff.apply(compute_slope, axis=1)
    
    # 5. Data Completeness
    features['data_completeness'] = pivot_rank.notna().sum(axis=1) + pivot_cutoff.notna().sum(axis=1)
    
    # Reset index to merge metadata
    features.reset_index(inplace=True)
    
    # Merge metadata columns from the latest record of each group
    latest_rec = prior_df.sort_values(by='Year').groupby(['Code', 'BranchCode', 'Community']).last().reset_index()
    meta_cols = ['Code', 'BranchCode', 'Community', 'College Name', 'Branch', 'District', 'DistrictConfidence', 'PinCode']
    latest_rec = latest_rec[[c for c in meta_cols if c in latest_rec.columns]]
    features = pd.merge(features, latest_rec, on=['Code', 'BranchCode', 'Community'], how='left')
    
    # 6. YoY Changes at Group Level
    # Calculate group-level change from T-2 to T-1
    if t1 in prior_years and t2 in prior_years:
        group_diff_cutoff = pivot_cutoff[t1] - pivot_cutoff[t2]
        # For rank, smaller rank is tighter, so let's do T-2 minus T-1 (positive means rank got tighter/improved)
        group_diff_rank = pivot_rank[t2] - pivot_rank[t1]
    else:
        # Fallback to mean YoY change if T-1 or T-2 is missing
        diff_cutoff_df = pivot_cutoff.diff(axis=1)
        group_diff_cutoff = diff_cutoff_df.mean(axis=1)
        
        diff_rank_df = -pivot_rank.diff(axis=1)  # negated so improvement is positive
        group_diff_rank = diff_rank_df.mean(axis=1)
        
    features['group_diff_cutoff'] = features.set_index(['Code', 'BranchCode', 'Community']).index.map(group_diff_cutoff).values
    features['group_diff_rank'] = features.set_index(['Code', 'BranchCode', 'Community']).index.map(group_diff_rank).values
    
    # 7. Branch Popularity (change in cutoff/rank for branch + community across all colleges)
    # Average change in cutoff/rank within the branch-community
    branch_popularity_cutoff = features.groupby(['BranchCode', 'Community'])['group_diff_cutoff'].transform('mean')
    branch_popularity_rank = features.groupby(['BranchCode', 'Community'])['group_diff_rank'].transform('mean')
    features['branch_popularity_cutoff'] = branch_popularity_cutoff
    features['branch_popularity_rank'] = branch_popularity_rank
    
    # 8. College-level Trend (average change across all branches in the college)
    college_trend_cutoff = features.groupby('Code')['group_diff_cutoff'].transform('mean')
    college_trend_rank = features.groupby('Code')['group_diff_rank'].transform('mean')
    features['college_trend_cutoff'] = college_trend_cutoff
    features['college_trend_rank'] = college_trend_rank
    
    # 9. District-level Trend (average change across all colleges in the district)
    district_trend_cutoff = features.groupby('District')['group_diff_cutoff'].transform('mean')
    district_trend_rank = features.groupby('District')['group_diff_rank'].transform('mean')
    features['district_trend_cutoff'] = district_trend_cutoff
    features['district_trend_rank'] = district_trend_rank
    
    # Add target year column
    features['Year'] = target_year
    
    return features

def build_all_features(df, prediction_mode=False):
    """
    Builds features for all target years.
    If prediction_mode is True, it will also build the feature set for target_year = 2026.
    """
    years = sorted(df['Year'].unique())
    # Minimum 2 years of history needed to train/predict
    target_years = [y for y in years if y > min(years)]
    
    all_features = []
    for y in target_years:
        f_yr = extract_features_for_year(df, y)
        if len(f_yr) > 0:
            # Join target values for target year 'y'
            targets = df[df['Year'] == y][['Code', 'BranchCode', 'Community', 'ClosingRank', 'CutoffMark']].copy()
            f_yr = pd.merge(f_yr, targets, on=['Code', 'BranchCode', 'Community'], how='left')
            all_features.append(f_yr)
            
    if prediction_mode:
        # Build features for 2026 (the year after the last year of data in df)
        next_year = max(years) + 1
        logger.info(f"Building prediction features for Year {next_year}")
        f_next = extract_features_for_year(df, next_year)
        if len(f_next) > 0:
            f_next['ClosingRank'] = np.nan
            f_next['CutoffMark'] = np.nan
            all_features.append(f_next)
            
    return pd.concat(all_features, ignore_index=True)
