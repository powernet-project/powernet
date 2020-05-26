import json
import pandas as pd
import datetime


def farm_data_parser(argv):
    """
        Parses json blob and returns the argument fields as individual dictionaries
        in json form
    """
    # sets serialized_farm_data to data
    data = argv[-1]
    # pulls device data from the json
    farm_data = [ json.loads(row["device_data"]) for row in data ]
    # creates dataframe with argument fields as columns
    farm_df = pd.DataFrame(farm_data)[argv[:-1]]

    try:
        farm_df["timestamp"] = pd.to_datetime(farm_df["timestamp"])
    except KeyError:
        print("Timestamp column not found.")

    # prepares json to be sent to javascript
    return farm_df.to_json(date_format='iso')
