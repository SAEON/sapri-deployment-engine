#!/usr/bin/env python

import logging

from api_client import ApiClient
from data_processor import DataProcessor
from nextcloud_uploader import process_uploads

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def run_data_processor():
    """
    Orchestrator to be called by the cron job.
    """
    logger.info("Cron job triggered: running data processor...")

    try:
        api_client = ApiClient()
        data_processor = DataProcessor(api_client)
        updated_deployment_ids = data_processor.process_deployments()
        process_uploads(updated_deployment_ids)
        logger.info("Data processor finished successfully.")
    except Exception:
        logger.exception("An unhandled exception occurred during the data processing run.")


if __name__ == "__main__":
    run_data_processor()
