import os
import re

from common.constants import DATAFOLDER


param_dirs = ["abs_wind_image", "humidity_image", "rain_image", "seaLevel_pressure_image", "station_pressure_image", "temp_image", "wind_image"]


def main():
    for param_dir in param_dirs:
        for year in os.listdir(os.path.join(DATAFOLDER.data_root_path, param_dir)):
            for month in os.listdir(os.path.join(DATAFOLDER.data_root_path, param_dir, year)):
                for date in os.listdir(os.path.join(DATAFOLDER.data_root_path, param_dir, year, month)):
                    for filename in os.listdir(os.path.join(DATAFOLDER.data_root_path, param_dir, year, month, date)):
                        if re.match("[0-9]+-[0-9]*0", filename) is None:
                            os.remove(os.path.join(DATAFOLDER.data_root_path, param_dir, year, month, date, filename))


if __name__ == "__main__":
    main()
