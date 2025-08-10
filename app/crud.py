from sqlalchemy.orm import Session
from croniter import croniter
from datetime import datetime
import pytz

from . import models, schemas

def get_job(db: Session, job_id: int):
    """Get single job by ID"""
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def get_jobs(db: Session, skip: int = 0, limit: int = 100):
    """Get jobs with pagination - important for scalability"""
    return db.query(models.Job).offset(skip).limit(limit).all()

def create_job(db: Session, job: schemas.JobCreate):
    """
    Create new job and calculate initial next_run_at
    This is where the scheduling magic happens
    """
    # Calculate when this job should first run
    next_run_at = calculate_next_run(job.cron_expression, job.timezone)
    
    db_job = models.Job(
        **job.model_dump(),
        next_run_at=next_run_at,
        status="pending"
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_jobs_ready_to_run(db: Session):
    """
    Get jobs that should be executed now
    This is called by the scheduler background task
    """
    now = datetime.utcnow()
    return db.query(models.Job).filter(
        models.Job.next_run_at <= now,
        models.Job.is_active == True,
        models.Job.status.in_(["pending", "failed"])
    ).all()

def update_job_after_execution(db: Session, job_id: int, status: str, success: bool = True):
    """Update job after it runs"""
    job = get_job(db, job_id)
    if job:
        job.status = status
        job.last_run_at = datetime.utcnow()
        
        if success:
            # Calculate next run time for recurring jobs
            job.next_run_at = calculate_next_run(job.cron_expression, job.timezone)
            job.retry_count = 0
        else:
            job.retry_count += 1
            
        db.commit()
        db.refresh(job)
    return job

def calculate_next_run(cron_expression: str, timezone: str = "UTC"):
    """
    Calculate when a job should run next based on cron expression
    This handles the "every Monday" type scheduling requirement
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        # croniter handles the complex cron parsing
        cron = croniter(cron_expression, now)
        next_run = cron.get_next(datetime)
        
        # Store in UTC
        return next_run.astimezone(pytz.UTC).replace(tzinfo=None)
    except:
        # If something goes wrong, schedule for next hour
        return datetime.utcnow().replace(minute=0, second=0) + timedelta(hours=1)

def validate_cron_expression(cron_expr: str) -> bool:
    """Validate cron expression format"""
    try:
        croniter(cron_expr)
        return True
    except:
        return False