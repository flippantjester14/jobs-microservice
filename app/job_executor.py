import asyncio
import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class JobExecutor:
    """
    Executes different types of jobs
    Currently implements dummy jobs as requested (email, number crunching, etc.)
    """
    
    async def execute_job(self, job) -> bool:
        """
        Main job execution method
        Routes to specific job type handlers
        """
        try:
            job_type = job.job_type.lower()
            
            if job_type == "email_notification":
                return await self._execute_email_job(job)
            elif job_type == "data_processing":
                return await self._execute_data_job(job)
            elif job_type == "report_generation":  
                return await self._execute_report_job(job)
            else:
                return await self._execute_custom_job(job)
                
        except Exception as e:
            logger.error(f"Job execution failed: {e}")
            return False
    
    async def _execute_email_job(self, job):
        """Dummy email notification job"""
        logger.info(f"Sending email notification: {job.name}")
        
        # Simulate email sending
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate occasional failures (10% chance)
        if random.random() < 0.1:
            logger.error("Email server unavailable")
            return False
            
        # Get email details from job parameters
        recipient = job.parameters.get("recipient", "default@example.com")
        subject = job.parameters.get("subject", job.name)
        
        logger.info(f"Email sent to {recipient}: {subject}")
        return True
    
    async def _execute_data_job(self, job):
        """Dummy data processing job (number crunching)"""
        logger.info(f"Processing data: {job.name}")
        
        # Simulate data processing time
        processing_time = random.uniform(1, 5)
        await asyncio.sleep(processing_time)
        
        # Simulate processing some records
        records_processed = random.randint(100, 1000)
        logger.info(f"Processed {records_processed} records in {processing_time:.2f}s")
        
        return True
    
    async def _execute_report_job(self, job):
        """Dummy report generation job"""
        logger.info(f"Generating report: {job.name}")
        
        # Simulate report generation
        await asyncio.sleep(random.uniform(2, 4))
        
        report_type = job.parameters.get("report_type", "daily")
        logger.info(f"Generated {report_type} report")
        
        return True
        
    async def _execute_custom_job(self, job):
        """Generic custom job handler"""
        logger.info(f"Executing custom job: {job.name}")
        
        # Simulate some work
        await asyncio.sleep(1)
        
        logger.info(f"Custom job {job.name} completed")
        return True