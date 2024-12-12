import json


def read_settings_json(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
        file.close()
    return data


def write_settings_json(filepath, host, port, db_name, user, password):
    data = read_settings_json(filepath)

    data["database"]["host"] = host
    data["database"]["port"] = port
    data["database"]["db_name"] = db_name
    data["database"]["user"] = user
    data["database"]["password"] = password

    with open(filepath, "w") as file:
        json.dump(data, file)
        file.close()
