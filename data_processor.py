import json
import os
import logging
from api_client import ApiClient

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        self.info_filepath = "./data/deployment_info.json"

    def _load_local_info(self):
        """
        Loads deployment info from the local JSON file.
        Creates an empty file if it does not exist.
        """
        if not os.path.exists(self.info_filepath):
            logger.info(f"Info file not found. Creating a new empty file at {self.info_filepath}.")
            try:
                with open(self.info_filepath, 'w') as f:
                    json.dump({}, f)
                return {}
            except IOError:
                logger.exception(f"CRITICAL: Could not create info file at {self.info_filepath}.")
                return {}

        try:
            with open(self.info_filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not decode JSON from {self.info_filepath}. Treating as empty.")
            return {}
        except IOError:
            logger.exception(f"Error reading info file at {self.info_filepath}.")
            return {}

    def _save_local_info(self, data):
        """Saves the updated deployment info to the JSON file."""
        try:
            with open(self.info_filepath, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info("Successfully updated deployment info file.")
        except IOError:
            logger.exception(f"Could not write to {self.info_filepath}.")

    def process_deployments(self):
        """
        Main function to check for new data and trigger downloads.
        """
        logger.info("Starting data processing run...")

        local_info = self._load_local_info()
        updated_info = local_info.copy()

        deployment_list = self.api_client.get_deployments()

        if not deployment_list:
            logger.warning("No deployments found or API error. Ending run.")
            return

        i = 0
        for deployment in deployment_list:
            if i > 2:
                logger.debug("Breaking loop after 3 items for testing.")
                break
            i += 1

            deployment_id = str(deployment['id'])
            api_update_date = deployment['last_update_date']

            stored_entry = local_info.get(deployment_id)
            stored_update_date = stored_entry.get('last_update_date') if stored_entry else None

            if stored_update_date is None or api_update_date > stored_update_date:
                if stored_update_date is None:
                    logger.info(f"New deployment found: {deployment_id}. Downloading data...")
                else:
                    logger.info(f"Deployment {deployment_id} has been updated. Downloading new data...")

                zip_data = self.api_client.download_deployment_data(deployment_id)

                if zip_data:
                    filename = f"./data/deployment_{deployment_id}_data.zip"
                    try:
                        with open(filename, 'wb') as f:
                            f.write(zip_data)
                        logger.info(f"Successfully saved ZIP file to {filename}.")

                        entry_to_update = updated_info.get(deployment_id, {})
                        entry_to_update['last_update_date'] = api_update_date
                        updated_info[deployment_id] = entry_to_update

                    except IOError:
                        logger.exception(f"Failed to save file {filename}.")
                else:
                    logger.error(f"Failed to download data for {deployment_id}.")
            else:
                logger.info(f"Deployment {deployment_id} is already up to date. Skipping.")

        if updated_info != local_info:
            self._save_local_info(updated_info)

        logger.info("Data processing run finished.")
