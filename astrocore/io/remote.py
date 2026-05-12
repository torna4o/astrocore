from .base import DataSource
import requests


class RemoteJSON(DataSource):

    def __init__(self, url):
        self.url = url

    def load(self):

        response = requests.get(self.url)
        data = response.json()

        return {
            "t": data["t"],
            "y": data["y"],
            "meta": {
                "source": "remote_json",
                "url": self.url
            }
        }
