import json
import pandas as pd
import os
from datetime import datetime


import os
import sys
import json


import os
import sys
import json


def get_settings_path():
    """Returns the correct path to settings.json, ensuring it remains writable."""
    if getattr(sys, "frozen", False):  # Running as a PyInstaller EXE
        base_path = os.path.dirname(sys.executable)  # Inside the installed directory
    else:  # Running as a script
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "settings")
        )

    settings_file = os.path.join(base_path, "settings.json")

    # Ensure settings directory exists
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)

    return settings_file


SETTINGS_FILEPATH = get_settings_path()


def read_settings_json():
    """Reads the settings.json file."""
    try:
        with open(SETTINGS_FILEPATH, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "database": {
                "host": "",
                "port": "",
                "db_name": "",
                "user": "",
                "password": "",
            }
        }


def write_settings_json(host, port, db_name, user, password):
    """Writes database settings to settings.json."""
    data = read_settings_json()

    data["database"]["host"] = host
    data["database"]["port"] = port
    data["database"]["db_name"] = db_name
    data["database"]["user"] = user
    data["database"]["password"] = password

    with open(SETTINGS_FILEPATH, "w") as file:
        json.dump(data, file, indent=4)


def export_array_to_excel(array, filepath):

    headers = [
        "ID",
        "Name",
        "Description",
        "Type",
        "Product Code",
        "Supplier",
        "Qty",
        "Allocated Qty",
        "Available Qty",
        "On-order",
        "Re-Order",
        "Location",
        "Bay",
        "Value",
    ]

    df = pd.DataFrame(array, columns=headers)

    timestamp = datetime.today()

    file_name = f"stock_export_{timestamp}.xlsx"

    export_path = os.path.join(filepath, file_name)

    df.to_excel(export_path, index=False)
