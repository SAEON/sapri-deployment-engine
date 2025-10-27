import requests
import os
import logging

from config import config

logger = logging.getLogger(__name__)

NEXTCLOUD_URL = config['NEXTCLOUD']['URL']
NEXTCLOUD_USER = config['NEXTCLOUD']['USER']
NEXTCLOUD_PASSWORD = config['NEXTCLOUD']['PASSWORD']

LOCAL_FILE_PATH = "./data/"
REMOTE_PATH = "/SAPRI Deployment Data/"


def process_uploads(deployment_ids: list[str]):
    """
    Upload all deployment data files corresponding to ids to nextcloud
    :param deployment_ids: list of deployment IDs to upload
    """
    upload_attempt_counter = 0

    while deployment_ids.__len__() > 0 and upload_attempt_counter < 5:
        for deployment_id in deployment_ids:
            local_deployment_file_path = f'{LOCAL_FILE_PATH}{deployment_id}.zip'
            remote_deployment_file_path = f'{REMOTE_PATH}{deployment_id}.zip'
            if _upload_to_nextcloud(local_deployment_file_path, remote_deployment_file_path):
                deployment_ids.remove(deployment_id)

        upload_attempt_counter += 1


def _upload_to_nextcloud(local_path, remote_path) -> bool:
    """
    Uploads a local file to a Nextcloud instance via WebDAV.
    """
    if not os.path.exists(local_path):
        logger.error(f"Error: Local file not found at '{local_path}'")
        return False

    webdav_url = f"{NEXTCLOUD_URL}{remote_path}"

    logger.info(f"Uploading '{local_path}' to '{remote_path}'...")

    try:
        with open(local_path, 'rb') as f:
            file_data = f.read()

        response = requests.put(
            webdav_url,
            data=file_data,
            auth=(NEXTCLOUD_USER, NEXTCLOUD_PASSWORD)
        )

        if response.status_code == 201 or response.status_code == 204:
            logger.info(f"Success! File uploaded. Status code: {response.status_code}")
            return True
        else:
            logger.error(f"Error during upload. Status code: {response.status_code}")
            logger.error(f"Response body: {response.text}")

    except requests.exceptions.RequestException as e:
        logger.exception(f"An error occurred: {e}")

    return False
