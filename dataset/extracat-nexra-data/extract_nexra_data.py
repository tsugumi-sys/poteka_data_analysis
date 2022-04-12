import os
import sys
import logging
import argparse
import re
from typing import Tuple
import multiprocessing as mlp
from joblib import Parallel, delayed

import numpy as np
import pandas as pd
from tqdm import tqdm

sys.path.append(".")
from common.constants import DATAFOLDER
from common.progress_bar import custom_progressbar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExtractNexraDataLogger")


def main(save_dir_path: str, n_cpus: int):
    if n_cpus > mlp.cpu_count():
        n_cpus = mlp.cpu_count() - 1

    root_dir = "/Users/akiranoda/Desktop"
    years = ["2020", "2019"]
    for y in years:
        datetime_dirs = os.listdir(os.path.join(root_dir, y))
        datetime_dirs = [i for i in datetime_dirs if re.match("[0-9]{10}", i) is not None]
        with custom_progressbar(tqdm(desc=f"Save Parquet {y} data ...", total=len(datetime_dirs))):
            Parallel(n_jobs=n_cpus)(
                delayed(save_parquet_file)(
                        save_dir_path=os.path.join(save_dir_path, y, datetime_dir[:8]),
                        data_folder_path=os.path.join(root_dir, y, datetime_dir),
                    )
                    for datetime_dir in datetime_dirs
            )


def save_parquet_file(save_dir_path: str, data_folder_path: str) -> None:
    os.makedirs(save_dir_path, exist_ok=True)
    for filenames in FILENAMES.filenames_list:
        grd_filename = filenames["grd_filename"]
        ctl_filename = filenames["ctl_filename"]
        param_tag = filenames["tag"].replace(" ", "_")

        data = load_grd_file(os.path.join(data_folder_path, grd_filename))
        longitudes, latitudes = get_lon_lat_from_ctl(os.path.join(data_folder_path, ctl_filename))

        data = data[:len(longitudes)*len(latitudes)].reshape((len(latitudes), len(longitudes)))

        df = pd.DataFrame(data=data, index=latitudes, columns=longitudes.astype(str))

        time_dir_name = data_folder_path.split("/")[-1]
        save_filename = f"{time_dir_name[8:]}_{param_tag}.parquet.gzip"
        df.to_parquet(os.path.join(save_dir_path, save_filename), compression="gzip")


class FILENAMES:
    # List[Dict(grd_file, ctl_file, tag)]
    filenames_list = [
        {"grd_filename": "ss_vap_atm.grd", "ctl_filename": "ss_vap_atm.ctl", "tag": "Cumulative water vapor amount"},
        {"grd_filename": "ss_ps.grd", "ctl_filename": "ss_ps.ctl", "tag": "Sea level correction pressure"},
        {"grd_filename": "sa_tppn.grd", "ctl_filename": "sa_tppn.ctl", "tag": "Time accumulated rainfall (1hour)"},
        {"grd_filename": "ss_u10m.grd", "ctl_filename": "ss_u10m.ctl", "tag": "Surface wind speed (U)"},
        {"grd_filename": "ss_v10m.grd", "ctl_filename": "ss_v10m.ctl", "tag": "Surface wind speed (V)"},
    ]


def load_grd_file(file_path: str) -> np.ndarray:
    return np.fromfile(file_path, dtype=">f").astype(np.float32)


def load_ctl_file(file_path: str) -> list[str]:
    with open(file_path, "rb") as f:
        f = f.read()

    decoded_data = f.decode("ascii")
    return re.split("\s", decoded_data)


def get_lon_lat_from_ctl(file_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Get longitude and latitude from ctl file of nexra data.

    Args:
        file_path (str): ctl file path.

    Raises:
        ValueError: if the length of longitudes array doesn't match the original length written in ctl file.
        ValueError: if the length of latitudes array doesn't match the original length written in ctl file.

    Returns:
        Tuple[np.ndarray]: (np.ndarray(longitudes), np.ndarray(latitudes))
    """
    splited_data = load_ctl_file(file_path)

    # Parameters
    is_xdef = False
    is_ydef = False
    x_size = None
    y_size = None
    longitudes, latitudes = [], []

    float_pattern = "[-+]?[0-9]+[\.][0-9]+"
    float_prog = re.compile(float_pattern)

    positive_int_pattern = "[0-9]{3}"
    positive_int_prog = re.compile(positive_int_pattern)

    for i in splited_data:
        if "XDEF" == i:
            is_ydef = False
            is_xdef = True

        if "YDEF" == i:
            is_xdef = False
            is_ydef = True

        match_positive_int = positive_int_prog.match(i)
        match_float = float_prog.match(i)

        if x_size is None and is_xdef is True and match_positive_int is not None:
            x_size = int(match_positive_int.group(0))

        if is_xdef is True and match_float is not None:
            longitudes.append(float(match_float.group(0)))

        if y_size is None and is_ydef is True and match_positive_int is not None:
            y_size = int(match_positive_int.group(0))

        if is_ydef is True and match_float is not None:
            latitudes.append(float(match_float.group(0)))


    if len(longitudes) != x_size:
        raise ValueError(f"x_size: {x_size} doesn't match the longitudes length: {len(longitudes)} in {file_path}")

    if len(latitudes) != y_size:
        raise ValueError(f"y_size: {y_size} doesn't match the latitudes length: {len(latitudes)} in {file_path}")

    return np.array(longitudes), np.array(latitudes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="NEXRA data extracting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--save_dir_path",
        type=str,
        default="/nexra_data",
        help="absolute save directory path",
    )
    parser.add_argument(
        "--n_cpus",
        type=int,
        default="4",
        help="cpu to use for multiprocessing",
    )

    args = parser.parse_args()

    main(save_dir_path=args.save_dir_path, n_cpus=args.n_cpus)
