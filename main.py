import sys
from data_processor import DataProcessor
from api_client import ApiClient
from database import init_db
from crontab import CronTab


def schedule_job():
    """
    Schedules the data processing job to run every 15 minutes.
    """
    print("Scheduling cron job...")

    # Use a specific user's crontab (e.g., the current user)
    cron = CronTab(user=True)

    # Check if a job with a specific comment already exists to avoid duplicates
    job = cron.find_comment('deployment_data_sync')
    if not job:
        # Create a new job if one doesn't exist
        # We use a standalone script name for the cron command
        job = cron.new(command=f'{sys.executable} -m {__name__}', comment='deployment_data_sync')

    # Schedule the job to run every 15 minutes
    job.minute.every(15)

    # Write the changes to the user's crontab
    cron.write()
    print("Cron job scheduled successfully to run every 15 minutes.")
    print("Run `crontab -l` to see the new entry.")


def run_data_processor():
    """
    A standalone function to be called by the cron job.
    """
    print("Cron job triggered: running data processor...")

    # Initialize the database table (if it doesn't exist)
    init_db()

    # Initialize the API client and data processor
    api_client = ApiClient()
    data_processor = DataProcessor(api_client)

    data_processor.process_deployments()
    print("Data processor finished.")


if __name__ == "__main__":
    run_data_processor()
