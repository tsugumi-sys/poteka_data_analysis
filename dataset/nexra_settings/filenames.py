class ParquetFileNames:
    rainfall_filename = "Time_accumulated_rainfall_(1hour).parquet.gzip"
    humidity_filename = "Cumulative_water_vapor_amount.parquet.gzip"
    sealevel_pressure_filename = "Sea_level_correction_pressure.parquet.gzip"
    uwind_filename = "Surface_wind_speed_(U).parquet.gzip"
    vwind_filename = "Surface_wind_speed_(V).parquet.gzip"


class FILENAMES:
    # List[Dict(grd_file, ctl_file, tag, parquet_filename)]
    filenames_list = [
        {
            "grd_filename": "ss_vap_atm.grd",
            "ctl_filename": "ss_vap_atm.ctl",
            "tag": "Cumulative water vapor amount",
            "parquet_filename": ParquetFileNames.humidity_filename,
        },
        {
            "grd_filename": "ss_ps.grd",
            "ctl_filename": "ss_ps.ctl",
            "tag": "Sea level correction pressure",
            "parquet_filename": ParquetFileNames.sealevel_pressure_filename,
        },
        {
            "grd_filename": "sa_tppn.grd",
            "ctl_filename": "sa_tppn.ctl",
            "tag": "Time accumulated rainfall (1hour)",
            "parquet_filename": ParquetFileNames.rainfall_filename,
        },
        {
            "grd_filename": "ss_u10m.grd",
            "ctl_filename": "ss_u10m.ctl",
            "tag": "Surface wind speed (U)",
            "parquet_filename": ParquetFileNames.uwind_filename,
        },
        {
            "grd_filename": "ss_v10m.grd",
            "ctl_filename": "ss_v10m.ctl",
            "tag": "Surface wind speed (V)",
            "parquet_filename": ParquetFileNames.vwind_filename,
        },
    ]
