# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/data_structure/tplot/01_tplot.ipynb.

# %% auto 0
__all__ = ['get_data', 'store_data', 'export2csv']

# %% ../../../nbs/data_structure/tplot/01_tplot.ipynb 0
import pytplot
from xarray import DataArray

# %% ../../../nbs/data_structure/tplot/01_tplot.ipynb 1
def _get_data(tvar: str) -> DataArray:
    return pytplot.data_quants[tvar]


def get_data(tvar: str | list[str], **args):
    if isinstance(tvar, str):
        return _get_data(tvar)
    elif isinstance(tvar, list):
        return [_get_data(t) for t in tvar]


def store_data(da: DataArray):
    pytplot.store_data(da.name, data={"x": da.time, "y": da.values})
    return da.name

# %% ../../../nbs/data_structure/tplot/01_tplot.ipynb 2
def export2csv(tvars: list, path):
    fnames = []
    for tvar in tvars:
        da: DataArray = get_data(tvar, xarray=True)
        fname = f"{path}_{tvar}.csv"
        da.to_pandas().to_csv(fname)
        fnames.append(fname)
    return fnames
