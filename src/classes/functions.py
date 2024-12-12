import json


def read_settings_json(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data["database"]
