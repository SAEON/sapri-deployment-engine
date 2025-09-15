import requests
import hmac
import hashlib
import xml.etree.ElementTree as et
from urllib.parse import urlencode

from config import config

ACCESS_KEY = config['API']['ACCESS_KEY']
SECRET_KEY = config['API']['SECRET_KEY']
API_URL = config['API']['URL']


class ApiClient:

    def _generate_hash(self, params: dict) -> str:
        """
        Generates a SHA256 HMAC hash from a dictionary of parameters.
        The parameters are first URL-encoded into a string.
        """
        param_string = urlencode(params)

        secret_bytes = SECRET_KEY.encode('utf-8')

        signature = hmac.new(
            secret_bytes,
            param_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def get_deployments(self) -> list:
        """
        Fetches the list of deployments using a POST request.
        """
        params = {"action": "get_deployments", "owner_id": "5429a3dfe36c4f7b437a4613"}
        hash_value = self._generate_hash(params)

        headers = {
            "X-Access": ACCESS_KEY,
            "X-Hash": hash_value
        }

        try:
            response = requests.post(API_URL, data=params, headers=headers)
            response.raise_for_status()

            root = et.fromstring(response.content)

            deployments_list = []

            for deployment_element in root.findall('deployment'):
                deployment_data = {
                    'id': deployment_element.find('id').text if deployment_element.find('id') is not None else None,
                    'last_update_date': int(
                        deployment_element.find('last_update_date').text) if deployment_element.find(
                        'last_update_date') is not None and deployment_element.find('last_update_date').text else None,
                }
                deployments_list.append(deployment_data)

            return deployments_list

        except requests.exceptions.RequestException as e:
            print(f"Error fetching deployments: {e}")
            return None
        except et.ParseError as e:
            print(f"Error parsing XML response: {e}")
            return None

    def download_deployment_data(self, deployment_id: str):
        """
        Downloads data for a specific deployment ID using a POST request.
        """
        params = {
            "action": "download_deployment",
            "id": deployment_id
        }
        hash_value = self._generate_hash(params)

        headers = {
            "X-Access": ACCESS_KEY,
            "X-Hash": hash_value
        }

        try:
            response = requests.post(API_URL, data=params, headers=headers)
            response.raise_for_status()

            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading data for deployment {deployment_id}: {e}")
            return None