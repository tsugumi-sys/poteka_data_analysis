from typing import List, Generator
import os
from datetime import datetime, timedelta
from logging import getLogger

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

logger = getLogger(__name__)


def datetime_range(start: datetime, end: datetime, delta: timedelta) -> Generator[datetime, None, None]:
    current = start
    while current <= end:
        yield current
        current += delta


def calc_u_v(df: pd.DataFrame, observation_point_name: str) -> List:
    """Calculate u (east-west), v (north-south) wind
        from absolute wind speed and wind direction.

    Args:
        df (pd.DataFrame): [description]
        observation_point_name (str): [description]

    Returns:
        List: [description]
    """
    wind_direction = float(df["WD1"])
    wind_speed = float(df["WS1"])

    rads = np.radians(float(wind_direction))
    u_wind, v_wind = -1 * wind_speed * np.cos(rads), -1 * wind_speed * np.sign(rads)
    return [observation_point_name, round(u_wind, 5), round(v_wind, 5)]


def time_series_df(data_root_dir_path: str, year: str, month: str, date: str, start_time_h: int, end_time_h: int,) -> pd.DataFrame:
    """ dataframe of p-poteka data columns with time column.
        The columns are like "hour-rain", "AT1", "RH1", "WS1", "V-Wind", "U-Wind", "PRS", "Time"

    Args:
        data_root_dir_path: str
        year (str): [description]
        month (str): [description]
        date (str): [description]
        start_time(str):
        end_time(str)

    Returns:
        pd.DataFrame: [description]
    """
    if end_time_h > 23 or start_time_h > 24:
        raise ValueError("Invalid end_time or start_time. Max time_h is 23.")
    if end_time_h < 0 or start_time_h < 0:
        raise ValueError("time_h must be more than 0.")

    target_cols = ["hour-rain", "AT1", "RH1", "WS1", "WD1", "V-Wind", "U-Wind", "PRS", "Time", "Station_Name"]
    df = pd.DataFrame(columns=target_cols)
    time_steps = [
        f"{dt.hour}-{dt.minute}"
        for dt in datetime_range(datetime(2000, 1, 1, start_time_h), datetime(2000, 1, 1, end_time_h, 59), timedelta(minutes=10))
    ]
    for time_step in time_steps:
        parquet_file_path = os.path.join(data_root_dir_path, year, month, f"{year}-{month}-{date}", f"{time_step}.parquet.gzip")
        _df = pd.read_parquet(parquet_file_path, engine="pyarrow")
        _df["Station_Name"] = _df["Unnamed: 0"]
        time_step = f"{time_step}0" if time_step.split("-")[1] == "0" else time_step
        _df["Time"] = time_step.replace("-", ":")
        wind_df = pd.DataFrame([calc_u_v(_df.loc[i, :], i) for i in _df.index], columns=["OB-Point", "U-Wind", "V-Wind"])
        _df["V-Wind"], _df["U-Wind"] = wind_df["V-Wind"], wind_df["U-Wind"]
        df = pd.concat([df, _df], axis=0, ignore_index=True)
    return df[target_cols]


def time_series_plot(data_df: pd.DataFrame, target_cols: str, save_fig_dir: str, exclude_observation_points: List[str] = None) -> None:
    if not os.path.exists(save_fig_dir):
        raise ValueError(f"No such directory: {save_fig_dir}")

    y_labels = {
        "hour-rain": "Hourly rainfall (mm/h)",
        "AT1": "Temperature (℃)",
        "RH1": "Relative Humidity (%)",
        "WS1": "Wind Speed (m/s)",
        "V-Wind": "North-south wind speed(m/s)",
        "U-Wind": "East-west wind speed (m/s)",
        "PRS": "Station Pressure (hPa)",
    }

    time_idx_length = len(data_df["Time"].unique())

    if exclude_observation_points:
        data_df = data_df.loc[~data_df["Station_Name"].isin(exclude_observation_points)]

    for col in target_cols:
        if col in list(y_labels.keys()):
            # Check outliers
            ## 1. same value is continuing (except for hour-rain)
            grouped_by_station = data_df.groupby(by=["Station_Name"])
            if col != "hour-rain":
                check_same_value_df = data_df.sort_values(by=["Station_Name", "Time"])
                check_same_value_df["diff"] = check_same_value_df.groupby(by=["Station_Name"])[col].diff()
                zero_diff_count_series = check_same_value_df.groupby(by=["Station_Name"])["diff"].agg(get_zero_diff_count)
                for observation_name in zero_diff_count_series.index:
                    zero_diff_count = zero_diff_count_series[observation_name]
                    if zero_diff_count > time_idx_length * 0.3:
                        logger.warning(f"{col} data of {observation_name} has {zero_diff_count} zero different values.")
            ## 2. extreme value
            std_series = grouped_by_station[col].agg(is_std_normal)
            for observation_name in std_series.index:
                if not std_series[observation_name]:
                    logger.warning(f"{col} data of {observation_name} has abnormal value.")

            if "Wind" in col or "WS" in col:
                wind_check_serise = grouped_by_station[col].agg(is_wind_normal)
                for observation_name in wind_check_serise.index:
                    if not wind_check_serise[observation_name]:
                        logger.warning(f"{col} data of {observation_name} has abnormal value.")

            plt.figure(figsize=(6, 5))
            ax = sns.lineplot(data=data_df, x="Time", y=col, hue="Station_Name")
            ax.set_ylabel(y_labels[col])
            ax.set_xlabel("UTC")
            ax.get_legend().remove()
            plt.xticks(rotation=75)
            plt.tight_layout()
            plt.savefig(os.path.join(save_fig_dir, f"{col}.png"))
            plt.show()
            plt.close()


def get_zero_diff_count(series: pd.Series):
    return (series == 0).sum()


def is_std_normal(series: pd.Series):
    std, mean = series.std(), series.mean()
    for val in series:
        if abs(val - mean) > std * 5:
            return False
    return True


def is_wind_normal(series: pd.Series):
    for val in series:
        if val > 10 or val < -10:
            return False
    return True
