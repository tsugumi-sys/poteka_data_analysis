import sys
from typing import Optional, Union, List

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

sys.path.append(".")
from dataset.nexra_settings.filenames import ParquetFileNames


class FigureSettings:
    # 1 hour cumulative rainfall settings
    rainfall_cmap = cm.Blues
    rainfall_cbar_label = "1 hour cumulative rainfall (mm)"
    rainfall_clevs = None

    # cumulative humidity amout setings
    humidity_cmap = cm.Blues
    humidity_cbar_label = "Cumulative water vapor amount (kg/m^2)"
    humidity_clevs = None

    # Sea level correction pressure settings
    sealevel_pressure_cmap = cmap = cm.Blues
    sealevel_pressure_cbar_label = "Sea level correction pressure (hPa)"
    sealevel_pressure_clevs = None

    # Wind settings
    wind_cmap = cm.viridis_r
    wind_cbar_label = "Wind Speed (m/s)"
    wind_clevs = None


def save_fig(data_file_path: Union[str, List[str]], save_fig_path: str, color_bar_label: str, cmap, clevs: Optional[List] = None) -> None:
    if isinstance(data_file_path, list):
        # u, v wind data
        for file_path in data_file_path:
            if ParquetFileNames.uwind_filename in file_path:
                uwind_df = pd.read_parquet(file_path)
            elif ParquetFileNames.vwind_filename in file_path:
                vwind_df = pd.read_parquet(file_path)

        wind_speed_arr = np.stack((uwind_df.to_numpy(), vwind_df.to_numpy()), axis=-1)

        def abs_val(a):
            return np.sqrt(np.square(a).sum())

        abs_wind_arr = np.apply_along_axis(func1d=abs_val, axis=-1, arr=wind_speed_arr)
        data = pd.DataFrame(data=abs_wind_arr, index=uwind_df.index, columns=uwind_df.columns)
    else:
        data = pd.read_parquet(data_file_path)

        # Convert 1 hour cumulative rainfall
        if ParquetFileNames.rainfall_filename in data_file_path:
            data *= 3600

    grid_mesh = np.meshgrid(data.columns.astype(np.float32).to_numpy(), data.index.astype(np.float32).to_numpy())
    x_grid, y_grid = grid_mesh[0], grid_mesh[1]

    plt.figure(figsize=(16, 8), dpi=80)
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([90, 155, -10, 40])
    ax.add_feature(cfeature.COASTLINE)
    gl = ax.gridlines(draw_labels=True, alpha=0)
    gl.right_labels = False
    gl.top_labels = False

    if clevs is not None:
        norm = mcolors.BoundaryNorm(clevs, cmap.N)
        cs = ax.contourf(x_grid, y_grid, data, clevs, cmap=cmap, norm=norm)
    else:
        cs = ax.contourf(x_grid, y_grid, data, cmap=cmap)

    cbar = plt.colorbar(cs, orientation="vertical")

    if isinstance(data_file_path, list):
        # Wind arrow
        ax.quiver(
            uwind_df.columns.astype(np.float32).to_numpy(),
            uwind_df.index.to_numpy(),
            uwind_df.to_numpy(),
            vwind_df.to_numpy(),
            color="red",
            scale=550,
        )

    # Fig Info
    cbar.set_label(color_bar_label)

    plt.savefig(save_fig_path)
    plt.close()
