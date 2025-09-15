import logging
import sys
from api_client import ApiClient
from data_processor import DataProcessor

logger = logging.getLogger(__name__)


def run_data_processor():
    """
    A standalone function to be called by the cron job.
    """
    logger.info("Cron job triggered: running data processor...")

    try:
        api_client = ApiClient()
        data_processor = DataProcessor(api_client)
        data_processor.process_deployments()
        logger.info("Data processor finished successfully.")
    except Exception:
        logger.critical("An unhandled exception occurred during the data processing run.", exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    run_data_processor()
