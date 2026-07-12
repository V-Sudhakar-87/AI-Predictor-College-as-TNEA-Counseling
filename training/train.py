import os
import joblib
import pandas as pd
import numpy as np
import lightgbm as lgb
import logging

logger = logging.getLogger(__name__)

# Define features to use
CATEGORICAL_FEATURES = ['BranchCode', 'Community', 'District', 'DistrictConfidence']
NUMERICAL_FEATURES = [
    'prev_rank', 'prev_cutoff', 'prev2_rank', 'prev2_cutoff',
    'rolling_mean_rank', 'rolling_mean_cutoff', 'rolling_std_rank', 'rolling_std_cutoff',
    'slope_rank', 'slope_cutoff', 'data_completeness',
    'branch_popularity_cutoff', 'branch_popularity_rank',
    'college_trend_cutoff', 'college_trend_rank',
    'district_trend_cutoff', 'district_trend_rank'
]
FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

def train_tnea_models(features_df, output_path):
    """
    Trains two LightGBM models (Rank and Cutoff) using features_df,
    and saves the models alongside preprocessing lookup maps to output_path.
    """
    # 1. Cast categorical features to Pandas category dtype
    df_train = features_df.copy()
    for col in CATEGORICAL_FEATURES:
        df_train[col] = df_train[col].astype(str).astype('category')
        
    # 2. Train Rank Regressor
    # Keep only rows where target (ClosingRank) is not null
    rank_train_df = df_train[df_train['ClosingRank'].notna() & (df_train['ClosingRank'] > 0)]
    X_rank = rank_train_df[FEATURES]
    y_rank = rank_train_df['ClosingRank']
    
    logger.info(f"Training Rank Regressor with {len(X_rank)} rows...")
    rank_model = lgb.LGBMRegressor(
        n_estimators=150,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        verbosity=-1
    )
    rank_model.fit(X_rank, y_rank)
    logger.info("Rank Regressor trained successfully.")
    
    # 3. Train Cutoff Regressor
    # Keep only rows where target (CutoffMark) is not null
    cutoff_train_df = df_train[df_train['CutoffMark'].notna() & (df_train['CutoffMark'] >= 0)]
    X_cutoff = cutoff_train_df[FEATURES]
    y_cutoff = cutoff_train_df['CutoffMark']
    
    logger.info(f"Training Cutoff Regressor with {len(X_cutoff)} rows...")
    cutoff_model = lgb.LGBMRegressor(
        n_estimators=150,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        verbosity=-1
    )
    cutoff_model.fit(X_cutoff, y_cutoff)
    logger.info("Cutoff Regressor trained successfully.")
    
    # 4. Save trained models
    return rank_model, cutoff_model

def save_model_bundle(rank_model, cutoff_model, college_map, pincode_prefix_lookup, master_df, output_path):
    """
    Bundles the models and all preprocessing artifacts, saving them via joblib.
    """
    bundle = {
        'rank_model': rank_model,
        'cutoff_model': cutoff_model,
        'college_map': college_map,
        'pincode_prefix_lookup': pincode_prefix_lookup,
        'master_df': master_df,
        'categorical_features': CATEGORICAL_FEATURES,
        'numerical_features': NUMERICAL_FEATURES,
        'features': FEATURES
    }
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(bundle, output_path)
    logger.info(f"Successfully saved predictor bundle to {output_path}")

