from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from .database import Base
import datetime

class Job(Base):
    """
    Main job table with all the fields mentioned in requirements
    Added some extra fields that make sense for a production scheduler
    """
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Scheduling info - this is the core requirement
    cron_expression = Column(String(100), nullable=False)  # "0 0 * * 1" for every Monday
    timezone = Column(String(50), default="UTC")
    
    # Timestamps as required
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=False)
    
    # Job execution details
    job_type = Column(String(50), default="custom")  # email, data_processing, etc
    parameters = Column(JSON, default={})  # Store job-specific config
    
    # Status and control
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    is_active = Column(Boolean, default=True)
    max_retries = Column(Integer, default=3)
    retry_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))

    def __repr__(self):
        return f"<Job(id={self.id}, name='{self.name}', next_run='{self.next_run_at}')>"