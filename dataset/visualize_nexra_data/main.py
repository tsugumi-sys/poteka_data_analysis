from itertools import groupby
import sys
import multiprocessing as mlp
import os
from typing import List, Union

from joblib import Parallel, delayed
from tqdm import tqdm

sys.path.append(".")
from common.progress_bar import custom_progressbar
from common.constants import DATAFOLDER
from dataset.visualize_nexra_data.visualize import FigureSettings, save_fig
from dataset.nexra_settings.filenames import FILENAMES, ParquetFileNames


def main(n_cpus: int):
    if n_cpus > mlp.cpu_count():
        n_cpus = mlp.cpu_count() - 1

    nexra_data_dir = os.path.join(DATAFOLDER.data_root_path, "nexra_data")
    for year in os.listdir(nexra_data_dir):
        for date in os.listdir(os.path.join(nexra_data_dir, year)):
            data_filenames = os.listdir(os.path.join(nexra_data_dir, year, date))
            grouped_uvwind_data_filenames = group_uvwind_data_filenames(data_filenames)
            with custom_progressbar(tqdm(desc="Running save fig", total=len(data_filenames))):
                Parallel(n_jobs=n_cpus)(
                    delayed(exec_save_fig)(root_dir_path=os.path.join(nexra_data_dir, year, date), data_filename=data_filename)
                    for data_filename in grouped_uvwind_data_filenames
                )


def group_uvwind_data_filenames(data_filenames: List[str]) -> List[Union[str, List[str]]]:
    grouped_uvwind_data_filenames = []

    def get_hour(val):
        return int(val[:2])

    sorted_filenames = sorted(data_filenames, key=get_hour)
    grouped_filenames = [list(it) for _, it in groupby(sorted_filenames, get_hour)]
    for filenames in grouped_filenames:
        uvwind_filenames = []
        for filename in filenames:
            if ParquetFileNames.uwind_filename in filename or ParquetFileNames.vwind_filename in filename:
                uvwind_filenames.append(filename)
            else:
                grouped_uvwind_data_filenames.append(filename)

            grouped_uvwind_data_filenames.append(uvwind_filenames)

    return grouped_uvwind_data_filenames


def exec_save_fig(root_dir_path: str, data_filename: Union[str, List[str]]):
    if isinstance(data_filename, list):
        data_file_path = []
        for i in data_filename:
            data_file_path.append(os.path.join(root_dir_path, i))
        save_fig_path = data_file_path[0].replace("parquet.gzip", "png")
    else:
        data_file_path = os.path.join(root_dir_path, data_filename)
        save_fig_path = data_file_path.replace("parquet.gzip", "png")

    if isinstance(data_filename, list):
        # Wind data
        save_fig(
            data_file_path=data_file_path,
            save_fig_path=save_fig_path,
            color_bar_label=FigureSettings.wind_cbar_label,
            cmap=FigureSettings.wind_cmap,
            clevs=FigureSettings.wind_clevs,
        )
    else:
        if ParquetFileNames.rainfall_filename in data_filename:
            save_fig(
                data_file_path=data_file_path,
                save_fig_path=save_fig_path,
                color_bar_label=FigureSettings.rainfall_cbar_label,
                cmap=FigureSettings.rainfall_cmap,
                clevs=FigureSettings.rainfall_clevs,
            )
        elif ParquetFileNames.humidity_filename in data_filename:
            save_fig(
                data_file_path=data_file_path,
                save_fig_path=save_fig_path,
                color_bar_label=FigureSettings.humidity_cbar_label,
                cmap=FigureSettings.humidity_cmap,
                clevs=FigureSettings.humidity_clevs,
            )
        elif ParquetFileNames.sealevel_pressure_filename in data_filename:
            save_fig(
                data_file_path=data_file_path,
                save_fig_path=save_fig_path,
                color_bar_label=FigureSettings.sealevel_pressure_cbar_label,
                cmap=FigureSettings.sealevel_pressure_cmap,
                clevs=FigureSettings.sealevel_pressure_clevs,
            )

