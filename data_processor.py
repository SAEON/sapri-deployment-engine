from api_client import ApiClient
from database import get_db, Deployment
from sqlalchemy.orm import Session
from typing import List


class DataProcessor:
    """
    Orchestrates the data ingestion process.
    """

    def __init__(self, api_client: ApiClient):
        self.api_client = api_client

    def get_latest_deployment_dates(self, deployment_ids: List[str], db: Session) -> dict:
        """
        Fetches the latest `date_time` from the database for a given list of deployment IDs.

        Args:
            deployment_ids: A list of deployment IDs to query.
            db: The SQLAlchemy database session.

        Returns:
            A dictionary mapping deployment ID to its latest date_time.
        """
        latest_dates = {}
        if not deployment_ids:
            return latest_dates

        # Efficiently query the database for the latest date for each deployment_id
        results = db.query(
            Deployment.deployment_id,
            Deployment.date_time
        ).filter(
            Deployment.deployment_id.in_(deployment_ids)
        ).group_by(
            Deployment.deployment_id
        ).all()

        for deployment_id, date_time in results:
            latest_dates[deployment_id] = date_time

        return latest_dates

    def process_deployments(self):
        """
        Main function to check for new data and trigger downloads.
        """
        print("Starting data processing run...")

        api_deployments = self.api_client.get_deployments()
        if not api_deployments or 'deployment' not in api_deployments:
            print("No deployments found or API error.")
            return

        deployment_list = api_deployments['deployment']
        deployment_ids_to_check = [dep['id'] for dep in deployment_list]

        with get_db() as db:
            db_latest_dates = self.get_latest_deployment_dates(deployment_ids_to_check, db)

        for api_deployment in deployment_list:
            deployment_id = api_deployment['id']
            api_last_update_date = api_deployment['last_update_date']
            db_last_update_date = db_latest_dates.get(deployment_id)

            # Compare dates. If the API date is newer, or the deployment isn't in our DB, download the data.
            if db_last_update_date is None or api_last_update_date > db_last_update_date:
                print(f"New data detected for deployment ID: {deployment_id}. Downloading...")
                csv_data = self.api_client.download_deployment_data(deployment_id)

                if csv_data:
                    # TODO: Here is where you will add the logic to parse the CSV
                    # and ingest the data into your database.
                    # This will be completed once you inspect the CSV format.
                    print(f"Successfully downloaded data for {deployment_id}.")
                else:
                    print(f"Failed to download data for {deployment_id}.")

        print("Data processing run finished.")
