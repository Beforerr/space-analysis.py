# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../../nbs/missions/wind/plasma.ipynb.

# %% auto 0
__all__ = ['DataVars', 'DataTypes', 'download_data', 'load_data']

# %% ../../../../nbs/missions/wind/plasma.ipynb 1
import polars as pl
from ...io.cdf import cdf2pl
import pyspedas

from functools import partial
from typing import Literal

# %% ../../../../nbs/missions/wind/plasma.ipynb 2
def download_data(**kwargs):
    return pyspedas.wind.swe(downloadonly=True, **kwargs)

# %% ../../../../nbs/missions/wind/plasma.ipynb 3
DataVars = Literal[
    "Np",  # Solar Wind Proton Number Density
    "Pressure",
    "V_GSE",
    "V_GSE_p",
    "THERMAL_SPD",
]

DataTypes = Literal["k0", "h0", "h5"]


def load_data(
    var_names: list[DataVars] = ["Np", "V_GSE", "THERMAL_SPD"],
    datatype: DataTypes = "k0",
    **kwargs,
):
    files = download_data(datatype=datatype, **kwargs)

    load_func = partial(cdf2pl, var_names=var_names)

    return pl.concat(load_func(file) for file in files)
