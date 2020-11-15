import os
from typing import Dict

from django.conf import settings
import json


class UserKeys:
    path_to_file = settings.MEDIA_ROOT + "user"

    def __init__(self, id: int, username: str, public_key: str, private_key: str):
        self.id = id
        self.username = username
        self.public_key = public_key
        self.secret_key = private_key

    def get_json(self) -> Dict[str, str]:
        json_object = {
            "id": self.id,
            "username": self.username,
            "public_key": self.public_key,
            "private_key": self.secret_key,
        }
        return json_object

    def save_to_file(self):
        json_object = self.get_json()

        with open(os.path.join(self.path_to_file, f"user_{self.username}.json"), 'w') as outfile:
            json.dump(json_object, outfile,indent=4)

    @staticmethod
    def get_from_file(username: int):
        with open(os.path.join(UserKeys.path_to_file, f"user_{username}.json")) as json_file:
            json_object = json.load(json_file)
            return json_object
