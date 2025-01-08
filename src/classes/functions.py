import json
import pandas as pd
import os
from datetime import datetime


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


def export_array_to_excel(array, filepath):

    headers = [
        "ID",
        "Name",
        "Description",
        "Type",
        "Product Code",
        "Qty",
        "Re-Order",
        "Supplier",
        "Location",
        "Bay",
        "Value",
    ]

    df = pd.DataFrame(array, columns=headers)

    timestamp = datetime.today()

    file_name = f"stock_export_{timestamp}.xlsx"

    export_path = os.path.join(filepath, file_name)

    df.to_excel(export_path, index=False)
