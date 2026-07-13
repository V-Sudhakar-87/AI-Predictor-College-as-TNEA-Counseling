import os
import sys
import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import json


from fastapi.responses import FileResponse
from pydantic import BaseModel
from report.generate_pdf import generate_pdf

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from typing import Optional
# Ensure project root is in sys.path to import prediction, training, etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from prediction.predictor import load_predictor_bundle, predict

app = FastAPI(
    title="TNEA Counseling Predictor API",
    description="Backend API serving the LightGBM models for Tamil Nadu Engineering Admissions predictions",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global bundle variable
bundle = None

@app.on_event("startup")
def startup_event():
    global bundle
    try:
        # Load the predictor bundle from default path
        bundle = load_predictor_bundle()
        logger.info("Successfully loaded predictor bundle on FastAPI startup.")
    except Exception as e:
        logger.error(f"Error loading predictor bundle: {e}")

class PredictionRequest(BaseModel):
    rank: Optional[int] = Field(default=None, description="TNEA closing rank (better/smaller is better)")
    cutoff_mark: Optional[float] = Field(default=None, description="TNEA cutoff mark (scale 0-200, larger is better)")
    community: str = Field(default="OC", description="Student's community (OC, BC, BCM, MBC, SC, SCA, ST)")
    district: Optional[str] = Field(default=None, description="Optional district filter")

    preferred_colleges: List[str] = []

class BranchRecommendation(BaseModel):
    branch: str
    probability: int

class CollegeBranchRecommendation(BaseModel):
    code: str
    college: str
    district: str
    overall_probability: int 
    is_preferred: bool = False

    reason: Optional[str] = None
    branches: List[BranchRecommendation]

class PredictionResponse(BaseModel):
    recommendations: List[CollegeBranchRecommendation]
    total_found: int

class MetadataResponse(BaseModel):
    communities: List[str]
    districts: List[str]

class CollegeOption(BaseModel):
    code: str
    name: str
    district: str

class PDFRequest(BaseModel):
    student: dict
    recommendations: list

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "bundle_loaded": bundle is not None}

@app.get("/api/metadata", response_model=MetadataResponse)
def get_metadata():
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model bundle not loaded yet")
    
    master_df = bundle.get('master_df')
    if master_df is None:
        raise HTTPException(status_code=500, detail="master_df not found in bundle")
    
    # Extract unique valid communities
    communities = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    
    # Extract unique valid districts (sorted alphabetically, excluding Unknown/nan)
    raw_districts = master_df['District'].dropna().unique()
    districts = sorted([
        str(d).strip() for d in raw_districts 
        if str(d).strip() and str(d).lower() != 'unknown'
    ])
    
    return {
        "communities": communities,
        "districts": districts
    }

@app.get("/api/colleges", response_model=List[CollegeOption])
def get_colleges(district: Optional[str] = None):

    if bundle is None:
        raise HTTPException(
            status_code=503,
            detail="Model bundle not loaded yet"
        )

    master_df = bundle["master_df"]

    df = (
    master_df
    .sort_values("Year", ascending=False)
    .drop_duplicates(subset=["Code"])
    [["Code","College Name","District"]]
)

    if district and district.strip():

        df = df[
            df["District"].str.strip().str.lower()
            ==
            district.strip().lower()
        ]

    df = df.sort_values("College Name")

    return [

        {
            "code": str(row["Code"]),
            "name": row["College Name"],
            "district": row["District"]
        }

        for _, row in df.iterrows()

    ]


@app.post("/api/predict", response_model=PredictionResponse)
def get_predictions(req: PredictionRequest):
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model bundle not loaded yet")
        
    if req.rank is None and req.cutoff_mark is None:
        raise HTTPException(
            status_code=400, 
            detail="Either 'rank' or 'cutoff_mark' must be provided."
        )
        
    # Standardize community input
    comm = req.community.strip().upper()
    valid_comms = {'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST'}
    if comm not in valid_comms:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid community: {req.community}. Must be one of {list(valid_comms)}"
        )
        
    try:
        # Call the ML predictor logic
        results = predict(
            rank=req.rank,
            cutoff_mark=req.cutoff_mark,
            community=comm,
            district=req.district,
            preferred_colleges=req.preferred_colleges
        )
        
        # Structure the results
        recommendations = [
            CollegeBranchRecommendation(
                code=res['code'],
                college=res['college'],
                district=res['district'],
                overall_probability=res["overall_probability"],
                is_preferred=res["is_preferred"],

                reason=res["reason"],
                branches=res['branches']
            )
            for res in results
        ]
        
        return {
            "recommendations": recommendations,
            "total_found": len(recommendations)
        }
    except Exception as e:
        logger.error(f"Error during prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


#college hostal fees & link
with open("college_details.json", encoding="utf-8") as f:
    COLLEGE_DETAILS = json.load(f)
@app.get("/api/college-details/{college_code}")
def get_college_details(college_code: str):

    if college_code not in COLLEGE_DETAILS:
        return {
            "success": False,
            "message": "College not found"
        }

    return {
        "success": True,
        "data": COLLEGE_DETAILS[college_code]
    }
#pdf generate


@app.post("/api/download-pdf")
def download_pdf(req: PDFRequest):

    try:
        output_file = "report.pdf"

        generate_pdf(
            req.student,
            req.recommendations,
            output_file
        )

        print("PDF Exists:", os.path.exists(output_file))
        print("PDF Size:", os.path.getsize(output_file))

        return FileResponse(
            path=output_file,
            media_type="application/pdf",
            filename="TNEA_AI_Report.pdf"
        )

    except Exception as e:
        import traceback
        traceback.print_exc()   # Full error terminal-la print aagum
        raise HTTPException(status_code=500, detail=str(e))


# React assets
# Mount entire static folder
app.mount("/", StaticFiles(directory="static", html=True), name="static")

