import requests
import hmac
import hashlib
import xml.etree.ElementTree as et
from urllib.parse import urlencode

# Replace these with your actual keys
ACCESS_KEY = "lGy5GF6WG26Oix7x9s/5pboIqBrBzOMDzyd08u9vM+w="
SECRET_KEY = "yzAmYHsSfS3qEi3AF60Nad49/LxjZ9Z5rOpkTDq1rbg="
API_URL = "https://my.wildlifecomputers.com/services/"


class ApiClient:
    """
    A client for the external API, handling authentication and requests.
    """

    def _generate_hash(self, params: dict) -> str:
        """
        Generates the HMAC SHA256 hash for the request.
        """
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)

        # The secret key needs to be in bytes for HMAC
        secret_bytes = SECRET_KEY.encode('utf-8')

        # Calculate the HMAC SHA256 hash
        signature = hmac.new(
            secret_bytes,
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def get_deployments(self) -> list:
        """
        Queries the get_deployments endpoint and parses the XML response.

        Returns:
            A list of deployment dictionaries.
        """
        params = {"action": "get_deployments"}
        hash_value = self._generate_hash(params)

        headers = {
            "X-Access": ACCESS_KEY,
            "X-Hash": hash_value
        }

        try:
            response = requests.get(API_URL, params=params, headers=headers)
            response.raise_for_status()  # Raises an exception for bad status codes

            # Parse the XML content
            root = et.fromstring(response.content)

            deployments_list = []

            # Assuming the structure is <root><deployment>...</deployment></root>
            for deployment_element in root.findall('deployment'):
                deployment_data = {
                    'id': deployment_element.find('id').text if deployment_element.find('id') is not None else None,
                    'last_update_date': int(
                        deployment_element.find('last_update_date').text) if deployment_element.find(
                        'last_update_date') is not None and deployment_element.find('last_update_date').text else None,
                    # We'll need to parse other fields as needed
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
        Downloads data for a specific deployment ID.
        """
        params = {
            "action": "download_deployment",
            "deployment_id": deployment_id
        }
        hash_value = self._generate_hash(params)

        headers = {
            "X-Access": ACCESS_KEY,
            "X-Hash": hash_value
        }

        try:
            response = requests.get(API_URL, params=params, headers=headers)
            response.raise_for_status()

            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error downloading data for deployment {deployment_id}: {e}")
            return None
