from django.conf import settings
import json


class UserKeys:
    path_to_file = settings.MEDIA_ROOT + "user/user.txt"

    def __init__(self, id:int, username:str, public_key:str, private_key:str):
        self.id = id
        self.username = username
        self.public_key = public_key
        self.secret_key = private_key

    def get_json(self):
        json_object = {
            "id": self.id,
            "username": self.username,
            "public_key": self.public_key,
            "private_key": self.secret_key,
        }
        return json_object

    def save_to_file(self):
        json_object = self.get_json()

        with open(self.path_to_file, 'w') as outfile:
            json.dump(json_object, outfile)

    @staticmethod
    def get_from_file():
        with open(UserKeys.path_to_file) as json_file:
            json_object = json.load(json_file)
            return json_object
