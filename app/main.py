from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from . import models, schemas, crud
from .database import SessionLocal, engine, get_db
from .scheduler import JobScheduler

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Scheduler Microservice",
    description="A microservice for scheduling and managing jobs",
    version="1.0.0"
)

# Initialize scheduler - this will run in background
scheduler = JobScheduler()

@app.on_event("startup")
async def startup_event():
    """Start the background scheduler when app starts"""
    await scheduler.start()

@app.on_event("shutdown") 
async def shutdown_event():
    """Cleanup when app shuts down"""
    await scheduler.stop()

# The three required endpoints

@app.get("/jobs", response_model=List[schemas.Job])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    GET /jobs - List all available jobs
    Added pagination because with 10k users, we'll have lots of jobs
    """
    jobs = crud.get_jobs(db, skip=skip, limit=limit)
    return jobs

@app.get("/jobs/{job_id}", response_model=schemas.Job)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    GET /jobs/:id - Get detailed info about a specific job
    Including scheduling details as required
    """
    job = crud.get_job(db, job_id=job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/jobs", response_model=schemas.Job)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    POST /jobs - Create new jobs
    Validates input data and adds to scheduling table
    """
    # Validate the cron expression before creating
    if not crud.validate_cron_expression(job.cron_expression):
        raise HTTPException(status_code=400, detail="Invalid cron expression")
    
    return crud.create_job(db=db, job=job)

@app.get("/")
def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "message": "Job Scheduler is running"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)