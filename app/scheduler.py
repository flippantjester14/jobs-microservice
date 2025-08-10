import asyncio
import logging
from datetime import datetime
from .database import SessionLocal
from . import crud
from .job_executor import JobExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScheduler:
    """
    Background scheduler that checks for jobs and executes them
    """
    
    def __init__(self):
        self.running = False
        self.executor = JobExecutor()
        
    async def start(self):
        """Start the scheduler loop"""
        self.running = True
        logger.info("Job scheduler starting...")
        asyncio.create_task(self._scheduler_loop())
        
    async def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Job scheduler stopping...")
        
    async def _scheduler_loop(self):
        """
        Main scheduler loop - checks every 60 seconds for jobs to run
        """
        while self.running:
            try:
                await self._check_and_run_jobs()
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
                
    async def _check_and_run_jobs(self):
        """Check database for jobs ready to run"""
        db = SessionLocal()
        try:
            jobs_to_run = crud.get_jobs_ready_to_run(db)
            
            if jobs_to_run:
                logger.info(f"Found {len(jobs_to_run)} jobs ready to run")
                
            for job in jobs_to_run:
                # Mark as running immediately
                crud.update_job_after_execution(
                    db, job.id, "running", success=True
                )

                # Pass only the job ID to avoid DetachedInstanceError
                asyncio.create_task(self._execute_job(job.id))
                
        finally:
            db.close()
            
    async def _execute_job(self, job_id):
        """Execute a single job using fresh session"""
        db = SessionLocal()
        try:
            job = crud.get_job(db, job_id)
            if not job:
                logger.error(f"Job with ID {job_id} not found")
                return

            logger.info(f"Executing job: {job.name} (ID: {job.id})")
            success = await self.executor.execute_job(job)
            status = "completed" if success else "failed"
            crud.update_job_after_execution(db, job.id, status, success)

            if success:
                logger.info(f"Job {job.name} completed successfully")
            else:
                logger.error(f"Job {job.name} failed")

        except Exception as e:
            logger.error(f"Error executing job {job_id}: {e}")
            crud.update_job_after_execution(db, job_id, "failed", False)
        finally:
            db.close()
