"""Autonomous Certification API R22 - Main Application"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

app = FastAPI(
    title="Autonomous Certification API R22",
    description="API for autonomous certification management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class Certificate(BaseModel):
    id: str
    subject: str
    issuer: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: str = "active"


class CertificationRequest(BaseModel):
    subject: str
    issuer: str
    duration_days: Optional[int] = 365


# In-memory storage (replace with database in production)
certificates: dict = {}


@app.get("/")
async def root():
    return {"message": "Autonomous Certification API R22", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/certifications", response_model=Certificate, status_code=status.HTTP_201_CREATED)
async def create_certification(request: CertificationRequest):
    """Create a new certification."""
    cert_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    expires = None
    if request.duration_days:
        from datetime import timedelta
        expires = now + timedelta(days=request.duration_days)
    
    certificate = Certificate(
        id=cert_id,
        subject=request.subject,
        issuer=request.issuer,
        created_at=now,
        expires_at=expires,
        status="active"
    )
    
    certificates[cert_id] = certificate
    return certificate


@app.get("/certifications", response_model=List[Certificate])
async def list_certifications(status: Optional[str] = None):
    """List all certifications, optionally filtered by status."""
    if status:
        return [c for c in certificates.values() if c.status == status]
    return list(certificates.values())


@app.get("/certifications/{cert_id}", response_model=Certificate)
async def get_certification(cert_id: str):
    """Get a certification by ID."""
    if cert_id not in certificates:
        raise HTTPException(status_code=404, detail="Certification not found")
    return certificates[cert_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)