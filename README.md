# Job Scheduler Microservice

A REST API for scheduling jobs with cron expressions. Supports different job types like email notifications and data processing.

## What it does

You can create jobs that run on a schedule (like every Monday at 9 AM), and the system will execute them automatically. The API lets you create, list, and view jobs. There's a background process that checks for jobs that need to run and executes them.

## Running it

First install the dependencies:

```bash
pip install -r requirements.txt
```

Then start the server:

```bash
python -m app.main
```

Go to http://localhost:8000/docs to see the API documentation.

## API endpoints

**POST /jobs** - Create a new job
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly backup",
    "cron_expression": "0 2 * * 1", 
    "job_type": "data_processing"
  }'
```

**GET /jobs** - List all jobs
```bash
curl http://localhost:8000/jobs
```

**GET /jobs/1** - Get details for job ID 1
```bash
curl http://localhost:8000/jobs/1
```

## Job examples

Send an email every day at 9 AM:
```json
{
  "name": "Daily reminder",
  "cron_expression": "0 9 * * *",
  "job_type": "email_notification",
  "parameters": {
    "recipient": "admin@company.com",
    "subject": "Daily report ready"
  }
}
```

Process data every hour:
```json
{
  "name": "Hourly data sync", 
  "cron_expression": "0 * * * *",
  "job_type": "data_processing",
  "parameters": {
    "dataset": "user_events"
  }
}
```

## Cron expressions

- `0 9 * * *` - Every day at 9 AM
- `0 9 * * 1` - Every Monday at 9 AM
- `*/15 * * * *` - Every 15 minutes
- `0 0 1 * *` - First day of each month at midnight

## Database setup

The app uses SQLite by default, so no database setup needed. If you want PostgreSQL for production:

1. Install PostgreSQL
2. Create a database called `scheduler_db`
3. Set the DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost/scheduler_db
   ```

## Configuration

You can set these environment variables:

- `DATABASE_URL` - Database connection string
- `DEBUG` - Set to "true" for debug mode
- `MAX_CONCURRENT_JOBS` - How many jobs can run at once

Create a `.env` file:
```
DATABASE_URL=sqlite:///scheduler.db
DEBUG=true
MAX_CONCURRENT_JOBS=5
```

## How it works

The main parts:

- **API layer** (main.py) - Handles HTTP requests
- **Database models** (models.py) - Job data structure  
- **Scheduler** (scheduler.py) - Background process that finds jobs to run
- **Job executor** (job_executor.py) - Actually runs the jobs

The scheduler runs in a loop every 60 seconds, checks the database for jobs where `next_run_at` is in the past, and executes them. After a job runs, it calculates the next run time based on the cron expression.

## Project structure

```
app/
├── main.py           # API endpoints
├── database.py       # Database setup
├── models.py         # Job table definition
├── schemas.py        # API request/response formats
├── crud.py           # Database queries
├── scheduler.py      # Background job scheduler
└── job_executor.py   # Job execution logic
```

## Common issues

If you get database connection errors, check that PostgreSQL is running or just use the default SQLite setup.

Jobs not running? Check the logs - probably a bad cron expression or the background scheduler isn't starting.

The background scheduler starts automatically when you run the app, but if jobs aren't executing, restart the application.

## Testing it out

1. Start the app
2. Go to http://localhost:8000/docs
3. Create a job that runs every minute: `* * * * *`
4. Check the logs to see it execute
5. Use GET /jobs to see the updated `last_run_at` timestamp

## Adding new job types

Edit `job_executor.py` and add a new method for your job type. The system will automatically route jobs based on the `job_type` field.
