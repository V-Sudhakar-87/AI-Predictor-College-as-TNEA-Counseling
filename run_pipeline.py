import os
import random
import logging
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from preprocessing.cleaner import preprocess_tnea_data
from training.features import build_all_features
from training.train import train_tnea_models, save_model_bundle
from prediction.predictor import predict, load_predictor_bundle

def run_backtesting(df_features):
    """
    Performs rolling-origin backtesting:
    - Fold 1: Train on <2024, predict on 2024
    - Fold 2: Train on <2025, predict on 2025
    """
    logger.info("\n=== STARTING ROLLING-ORIGIN BACKTESTING ===")
    
    # We will evaluate two folds: 2024 and 2025
    for eval_year in [2024, 2025]:
        logger.info(f"\n--- Backtesting for Target Year: {eval_year} ---")
        
        # Split features
        train_data = df_features[df_features['Year'] < eval_year].copy()
        test_data = df_features[df_features['Year'] == eval_year].copy()
        
        if len(train_data) == 0 or len(test_data) == 0:
            logger.warning(f"Insufficient data for backtesting year {eval_year}")
            continue
            
        # Import features list and cast categories
        from training.train import FEATURES, CATEGORICAL_FEATURES
        
        # Cast categories
        for col in CATEGORICAL_FEATURES:
            train_data[col] = train_data[col].astype(str).astype('category')
            test_data[col] = test_data[col].astype(str).astype('category')
            
        # 1. Evaluate Rank Regressor
        train_rank = train_data[train_data['ClosingRank'].notna() & (train_data['ClosingRank'] > 0)]
        test_rank = test_data[test_data['ClosingRank'].notna() & (test_data['ClosingRank'] > 0)]
        
        if len(train_rank) > 0 and len(test_rank) > 0:
            import lightgbm as lgb
            model_rank = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05, num_leaves=31, random_state=42, verbosity=-1)
            model_rank.fit(train_rank[FEATURES], train_rank['ClosingRank'])
            preds = model_rank.predict(test_rank[FEATURES])
            
            mae = mean_absolute_error(test_rank['ClosingRank'], preds)
            rmse = root_mean_squared_error(test_rank['ClosingRank'], preds)
            logger.info(f"ClosingRank Regression Metrics (Test Size={len(test_rank)}): MAE = {mae:.2f}, RMSE = {rmse:.2f}")
        else:
            logger.warning("No rank data available for this fold.")
            
        # 2. Evaluate Cutoff Regressor
        train_cutoff = train_data[train_data['CutoffMark'].notna() & (train_data['CutoffMark'] >= 0)]
        test_cutoff = test_data[test_data['CutoffMark'].notna() & (test_data['CutoffMark'] >= 0)]
        
        if len(train_cutoff) > 0 and len(test_cutoff) > 0:
            import lightgbm as lgb
            model_cutoff = lgb.LGBMRegressor(n_estimators=100, learning_rate=0.05, num_leaves=31, random_state=42, verbosity=-1)
            model_cutoff.fit(train_cutoff[FEATURES], train_cutoff['CutoffMark'])
            preds = model_cutoff.predict(test_cutoff[FEATURES])
            
            mae = mean_absolute_error(test_cutoff['CutoffMark'], preds)
            rmse = root_mean_squared_error(test_cutoff['CutoffMark'], preds)
            logger.info(f"CutoffMark Regression Metrics (Test Size={len(test_cutoff)}): MAE = {mae:.2f}, RMSE = {rmse:.2f}")
        else:
            logger.warning("No cutoff data available for this fold.")

def spot_check_districts(master_df, count=15):
    """
    Spot-checks district extraction accuracy by printing a sample of raw names and resolved districts.
    """
    logger.info(f"\n=== SPOT-CHECKING DISTRICT EXTRACTION ({count} random colleges) ===")
    unique_colleges = master_df.drop_duplicates(subset=['Code']).copy()
    
    # Sample from unique colleges
    sample = unique_colleges.sample(n=min(count, len(unique_colleges)), random_state=42)
    
    unknown_cnt = (unique_colleges['District'] == 'Unknown').sum()
    logger.info(f"Total unique college codes: {len(unique_colleges)}")
    logger.info(f"Unresolved colleges (District = 'Unknown'): {unknown_cnt} ({(unknown_cnt/len(unique_colleges))*100:.2f}%)")
    
    print("\n" + "="*80)
    print(f"{'Code':<6} | {'Resolved District':<20} | {'Confidence':<20} | {'Raw College Name'}")
    print("="*80)
    for _, row in sample.iterrows():
        # Get raw name from file to show the original string
        print(f"{row['Code']:<6} | {row['District']:<20} | {row['DistrictConfidence']:<20} | {row['College Name']}")
    print("="*80)

def main():
    raw_dir = r"F:\Counseling predictor\data\raw"
    bundle_path = r"F:\Counseling predictor\saved_models\tnea_predictor_bundle.joblib"
    
    logger.info("=== STARTING TNEA COUSELLING ML PIPELINE ===")
    
    # 1. Run Preprocessing
    master_df, pincode_prefix_lookup, college_map = preprocess_tnea_data(raw_dir)
    
    # 2. Run Feature Engineering (with prediction_mode=True to prepare 2026 features)
    features_df = build_all_features(master_df, prediction_mode=True)
    logger.info(f"Total features rows generated: {len(features_df)}")
    
    # 3. Perform Backtesting
    run_backtesting(features_df)
    
    # 4. Train Final Models on full dataset (Years 2021-2025)
    train_features = features_df[features_df['Year'] < 2026].copy()
    logger.info(f"\nTraining final models on all history (size={len(train_features)})...")
    rank_model, cutoff_model = train_tnea_models(train_features, bundle_path)
    
    # 5. Extract 2026 features for precomputed prediction
    precomputed_features = features_df[features_df['Year'] == 2026].copy()
    
    # 6. Save Bundle
    save_model_bundle(
        rank_model=rank_model,
        cutoff_model=cutoff_model,
        college_map=college_map,
        pincode_prefix_lookup=pincode_prefix_lookup,
        master_df=master_df,
        output_path=bundle_path
    )
    
    # Cache precomputed features inside the bundle file
    bundle = joblib.load(bundle_path)
    bundle['precomputed_features'] = precomputed_features
    joblib.dump(bundle, bundle_path)
    logger.info("Cached 2026 precomputed features into the bundle.")
    
    # 7. Run District Extraction Validation
    spot_check_districts(master_df, count=15)
    
    # 8. Test Predictor Interface
    logger.info("\n=== RUNNING SAMPLE PREDICTIVE QUERIES ===")
    # Load predictor bundle explicitly
    load_predictor_bundle(bundle_path)
    
    test_cases = [
        {"rank": 1500, "cutoff_mark": None, "community": "OC", "district": "Chennai"},
        {"rank": None, "cutoff_mark": 192.5, "community": "BC", "district": "Coimbatore"},
        {"rank": 12000, "cutoff_mark": 182.0, "community": "MBC", "district": None},
    ]
    
    for i, tc in enumerate(test_cases):
        logger.info(f"\nQuery {i+1}: Rank={tc['rank']}, Cutoff={tc['cutoff_mark']}, Community={tc['community']}, District={tc['district']}")
        results = predict(
            rank=tc['rank'],
            cutoff_mark=tc['cutoff_mark'],
            community=tc['community'],
            district=tc['district'],
            bundle_path=bundle_path
        )
        logger.info(f"Top 3 recommended colleges:")
        for col_dict in results[:3]:
            print(f" - {col_dict['college']}")
            print(f"   Branches: {col_dict['branches'][:5]}")
            
    logger.info("\n=== PIPELINE EXECUTION COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
