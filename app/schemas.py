from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, Dict, Any

class JobBase(BaseModel):
    name: str
    description: Optional[str] = None
    cron_expression: str
    timezone: str = "UTC"
    job_type: str = "custom"
    parameters: Dict[str, Any] = {}
    is_active: bool = True
    created_by: Optional[str] = None

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Job name cannot be empty')
        return v.strip()

class JobCreate(JobBase):
    """Schema for creating new jobs"""
    pass

class Job(JobBase):
    """Schema for returning job data - includes all the required fields"""
    id: int
    status: str
    last_run_at: Optional[datetime]
    next_run_at: datetime
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JobUpdate(BaseModel):
    """For future PATCH endpoint if needed"""
    name: Optional[str] = None
    description: Optional[str] = None
    cron_expression: Optional[str] = None
    is_active: Optional[bool] = None