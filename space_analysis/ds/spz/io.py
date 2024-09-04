# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/data_structure/speasy/01_io.ipynb.

# %% auto 0
__all__ = ['to_dataarray', 'to_dataarrays', 'spzvar2pldf', 'spzvars2pldf']

# %% ../../../nbs/data_structure/speasy/01_io.ipynb 0
from speasy import SpeasyVariable
import xarray as xr
import polars as pl

# %% ../../../nbs/data_structure/speasy/01_io.ipynb 2
def is_scalar(v: SpeasyVariable):
    """
    Related issue: [Scalar timeseries dimension · SciQLop/speasy](https://github.com/SciQLop/speasy/issues/149)
    """
    return len(v.shape) == 2 and v.shape[1] == 1


def get_data_and_time(v: SpeasyVariable):
    v = v.replace_fillval_by_nan()
    data = v.values
    time = v.time
    v_valid_mins = v.meta.get("VALIDMIN", [])
    v_valid_maxs = v.meta.get("VALIDMAX", [])

    all_cond_axis = tuple(range(1, data.ndim))
    for v_valid_min in v_valid_mins:
        cond = (data >= v_valid_min).all(axis=all_cond_axis)
        data, time = data[cond], time[cond]
    for v_valid_max in v_valid_maxs:
        cond = (data <= v_valid_max).all(axis=all_cond_axis)
        data, time = data[cond], time[cond]
    return data, time

# %% ../../../nbs/data_structure/speasy/01_io.ipynb 3
def to_dataarray(v: SpeasyVariable):
    """
    Notes: scalar timeseries of `ndim==2` is a design choice to be consistent with what Pandas does.
    """
    data, time = get_data_and_time(v)

    time_coord = xr.DataArray(time, dims="time")
    attrs = dict(v.meta, units=v.unit, long_name=v.name)
    if is_scalar(v):
        values, coords = data.squeeze(), [time_coord]
    else:
        values, coords = data, [time_coord, v.columns]
    return xr.DataArray(values, coords=coords, name=v.name, attrs=attrs)


def to_dataarrays(vs: list[SpeasyVariable]):
    return [to_dataarray(v) for v in vs]

# %% ../../../nbs/data_structure/speasy/01_io.ipynb 4
def spzvar2pldf(var: SpeasyVariable):
    # see SpeasyVariable.to_dataframe
    data, time = get_data_and_time(var)
    return (
        pl.DataFrame(data, schema=var.columns).with_columns(time=pl.Series(time)).lazy()
    )  # Need to `lazy` last or ShapeError: unable to add a column of length xxxx to a DataFrame of height yyyy


def spzvars2pldf(vars: list[SpeasyVariable]):
    # join all dataframes into a single one on the time column
    if len(vars) == 1:
        return spzvar2pldf(vars[0])
    return pl.concat([spzvar2pldf(var) for var in vars], how="align")
