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
    # convert time from non-nanoseconds into nanoseconds precision
    # https://github.com/pydata/xarray/issues/7493
    if time.dtype != "datetime64[ns]":
        time = time.astype("datetime64[ns]")

    if len(data.shape) == 1:
        coords = {"time": time}
    else:
        if isinstance(cols, str) and data.shape[1] > 1:
            v_dim = [f"{cols}_{i}" for i in range(data.shape[1])]
        else:
            v_dim = cols
        coords = {"time": time, "v_dim": v_dim}

    return DataArray(data, coords=coords, **kwargs)

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 2
def pddf2ts(df: pd.DataFrame, cols: list | str = None, time=None, **kwargs):
    cols = cols or df.columns.tolist()
    data = df[cols].to_numpy()
    times = df.index if time is None else df[time]
    return create_data_array(data, times, cols, **kwargs)

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 3
def get_columns(df: pl.DataFrame | pl.LazyFrame):
    if isinstance(df, pl.LazyFrame):
        return df.collect_schema().names()
    return df.columns


def pldf2ts(
    df: pl.DataFrame | pl.LazyFrame,
    cols: list | str = None,
    time="time",
    **kwargs,
):
    cols = cols or get_columns(df)
    if time in cols:
        cols.remove(time)
    if isinstance(df, pl.LazyFrame):
        df = df.collect()
    data = df[cols].to_numpy()
    times = df[time].to_numpy()
    return create_data_array(data, times, cols, **kwargs)

# %% ../../../../nbs/data_structure/timeseries/io.ipynb 5
def df2ts(
    df,
    cols: list | str = None,
    time: str = "time",
    **kwargs,
):
    """Convert DataFrame to TimeSeries"""
    if isinstance(df, (pl.DataFrame, pl.LazyFrame)):
        return pldf2ts(df, cols, time, **kwargs)
    elif isinstance(df, pd.DataFrame):
        return pddf2ts(df, cols, time, **kwargs)
