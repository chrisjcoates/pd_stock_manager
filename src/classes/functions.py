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
    """Get the correct path for settings.json whether running as a script or as a packaged exe."""
    if getattr(sys, "frozen", False):  # If running as a PyInstaller exe
        base_path = os.path.join(
            sys._MEIPASS, "settings"
        )  # Ensures settings.json is inside 'settings' folder
    else:
        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "settings")
        )

    return os.path.join(base_path, "settings.json")


def read_settings_json():
    """Read settings.json from the correct path."""
    filepath = get_settings_path()
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def write_settings_json(host, port, db_name, user, password):
    """Write to settings.json at the correct path."""
    filepath = get_settings_path()
    data = read_settings_json()

    data["database"]["host"] = host
    data["database"]["port"] = port
    data["database"]["db_name"] = db_name
    data["database"]["user"] = user
    data["database"]["password"] = password

    with open(filepath, "w") as file:
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

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    file_name = f"stock_export_{timestamp}.xlsx"

    export_path = os.path.join(filepath, file_name)

    df.to_excel(export_path, index=False)


def get_style_path():
    filename = "src/styles/style.qss"
    with open(filename, "r") as file:
        return file.read()
