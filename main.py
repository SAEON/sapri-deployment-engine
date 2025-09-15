from api_client import ApiClient
from data_processor import DataProcessor


def run_data_processor():
    """
    A standalone function to be called by the cron job.
    """
    print("Cron job triggered: running data processor...")

    api_client = ApiClient()
    data_processor = DataProcessor(api_client)

    data_processor.process_deployments()
    print("Data processor finished.")


if __name__ == "__main__":
    run_data_processor()
