import json
import pandas as pd
import datetime

def celsius_to_fahr(temp_c):
    """
        Convert Celsius to Fahrenheit
    """
    temp_f = temp_c * 9 / 5 + 32

    return temp_f

def utc_to_pst(time):
    """
        Convert TimeZone UTC to Pacific
    """
    time_utc = pd.to_datetime(time)
    time_pst = time_utc - datetime.timedelta(hours=8)

    return time_pst

def energy_summary_parser(argv):
    """
        Parses json blob for energy summary page and returns the argument fields
        as individual dictionaries in json form
    """
    # sets serialized_farm_data to data
    data = argv[-1]
    # pulls device data from the json
    farm_data = [ json.loads(row.get("device_data")) for row in data ]
    # creates dataframe with argument fields as columns

    farm_df = pd.DataFrame(farm_data)[argv[:-1]]
    farm_df["timestamp"] = utc_to_pst(farm_df["timestamp"])

    # average every 10 minute time interval
    farm_df = farm_df.resample('15Min', on="timestamp").mean().reset_index()

    # prepares json to be sent to javascript
    return farm_df.to_json(date_format="iso")


def local_fan_info_parser(data):
    """
        Parses json blob for local fan info page and returns the argument fields
        as individual dictionaries in json form
    """
    with open('response.json') as json_file:
        data1 = json.load(json_file)
    farm_data = data1[0].get("device_data")
    columns = {"frq", "pv_power", "grid_power", "a2", "a3", "serial_number"}
    farm_df = pd.DataFrame(farm_data)[columns]

    return farm_df.to_json()


def main_farm_parser(data):
    """
        Parses json blob for device_id = 17 and returns processed data
    """
    device_data = json.loads(data["device_data"])
    farm_data = device_data.get("processed")
    return farm_data


def main_power_parser(data):
    """
        Parses json blob for device_id = 17 and returns processed data
        Converts power from W to kW and adds field energy to the dataframe
    """
    farm_data = [ main_farm_parser(row) for row in data if main_farm_parser != None]

    farm_df = pd.DataFrame(farm_data)
    farm_df["POWER_TEST_PEN"] = farm_df["POWER_TEST_PEN"].abs() / 1000
    farm_df["energy"] = farm_df["POWER_TEST_PEN"] / 12
    # timezone changed from utc to pacific
    farm_df["timestamp"] = utc_to_pst(farm_df["timestamp"])

    return farm_df.to_json(date_format="iso")
