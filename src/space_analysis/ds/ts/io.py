# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../../nbs/data_structure/timeseries/io.ipynb.

# %% auto 0
__all__ = ['df2ts']

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 0
from xarray import DataArray
import polars as pl
import pandas as pd
import numpy as np

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 1
def create_data_array(data: np.ndarray, time, cols: list | str, **kwargs):
    if isinstance(cols, str) and len(data.shape) > 1:
        element_len = data.shape[1]
        v_dim = [cols + str(i) for i in range(element_len)]
    else:
        v_dim = cols

    coords = {"time": time, "v_dim": v_dim}
    return DataArray(data, coords=coords, **kwargs)

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 2
def pddf2ts(df: pd.DataFrame, cols: list | str = None, **kwargs):
    cols = cols or df.columns.tolist()
    data = df[cols].to_numpy()
    time = df.index
    return create_data_array(data, time, cols, **kwargs)

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 3
def get_columns(df: pl.DataFrame | pl.LazyFrame):
    if isinstance(df, pl.LazyFrame):
        return df.collect_schema().names()
    return df.columns


def pldf2ts(
    df: pl.DataFrame | pl.LazyFrame,
    cols: list | str = None,
    time_col="time",
    **kwargs,
):
    cols = cols or get_columns(df)
    if time_col in cols:
        cols.remove(time_col)
    if isinstance(df, pl.LazyFrame):
        df = df.collect()
    data = df[cols].to_numpy()
    time = df[time_col]
    return create_data_array(data, time, cols, **kwargs)

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 4
def df2ts(
    df,
    cols: list | str = None,
    **kwargs,
):
    """Convert DataFrame to TimeSeries"""
    if isinstance(df, (pl.DataFrame, pl.LazyFrame)):
        return pldf2ts(df, cols, **kwargs)
    elif isinstance(df, pd.DataFrame):
        return pddf2ts(df, cols, **kwargs)
