"""
FastAPI Backend Application for FloodSense.

Serves endpoints for analyzing flood emergency messages:
- POST /api/analyze: Full 5-stage flood message analysis
- GET /api/info: Model and system metadata
- GET /health: Service health check
"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.analyzer import FloodSenseAnalyzer

# Global analyzer instance (loaded on startup)
analyzer: Optional[FloodSenseAnalyzer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global analyzer
    try:
        analyzer = FloodSenseAnalyzer()
    except Exception as e:
        print(f"Warning: Could not initialize analyzer on startup: {e}")
    yield


app = FastAPI(
    title="FloodSense Intelligence API",
    description="NLP-based flood emergency message classification and severity triage system.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Raw flood emergency message")


class SeverityResponse(BaseModel):
    level: str
    severity_rank: int
    reasoning: str
    confidence_assessment: Optional[str] = None
    evidence_snippets: List[str] = []


class ScoreBreakdownItem(BaseModel):
    factor: str
    points: int
    type: Optional[str] = None
    evidence: Optional[Any] = None


class PriorityResponse(BaseModel):
    score: int
    tier: str
    score_breakdown: List[ScoreBreakdownItem] = []


class HumanitarianContextResponse(BaseModel):
    category: Optional[str] = None
    confidence: Optional[float] = None
    note: str


class AnalyzeResponse(BaseModel):
    message: str
    flood_detected: bool
    flood_detection_reason: str
    severity: SeverityResponse
    priority: PriorityResponse
    humanitarian_context: Optional[HumanitarianContextResponse] = None
    supporting_indicators: List[str] = []
    disclaimer: str


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": "FloodSense Intelligence API",
        "analyzer_ready": analyzer is not None,
    }


@app.get("/api/info", tags=["Info"])
def system_info():
    return {
        "system": "FloodSense",
        "version": "1.0.0",
        "architecture": "Severity-First 5-Stage Emergency Triage",
        "models": {
            "humanitarian_classifier": "TF-IDF + Calibrated LinearSVC (10 HumAID classes)",
            "severity_classifier": "Grounded Context-Aware Rules (Low/Moderate/High/Critical)",
            "priority_scorer": "Additive Indicator Rubric (0 - 100)",
        },
        "disclaimer": (
            "Provisional baseline system for emergency situational awareness. "
            "Not an official dispatch standard."
        ),
    }


@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
def analyze_message(req: AnalyzeRequest):
    global analyzer
    if analyzer is None:
        try:
            analyzer = FloodSenseAnalyzer()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analyzer initialization failed: {str(e)}")

    try:
        result = analyzer.analyze(req.message)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
