# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/data_structure/timeseries/plot.ipynb.

# %% auto 0
__all__ = ['DEFAULT_XFORMATTER', 'format_time_axis', 'hide_xaxis_labels', 'polish_plot', 'nested_get', 'format_da_attrs_tplot',
           'broadcast', 'standardize_to_matrix', 'tsplot']

# %% ../../../nbs/data_structure/timeseries/plot.ipynb 0
from xarray import DataArray
import holoviews as hv
import matplotlib.dates as mdates
import hvplot.xarray  # noqa

# %% ../../../nbs/data_structure/timeseries/plot.ipynb 1
DEFAULT_XFORMATTER = mdates.ConciseDateFormatter(
    mdates.AutoDateLocator(minticks=3, maxticks=5)
)


def format_time_axis(layout, xformatter=DEFAULT_XFORMATTER):
    for panel in layout:
        for e in panel:
            if hv.Store().current_backend == "matplotlib":
                e.opts(xformatter=xformatter)


def hide_xaxis_labels(layout):
    # Apply options to hide x-axis labels for all but the last plo
    for panel in list(layout)[0:-1]:
        panel.opts(xaxis=None)


def polish_plot(plots: list[list[hv.Element]]):
    overlay_plots = [hv.Overlay(plot) for plot in plots]
    layout = hv.Layout(overlay_plots).cols(1)
    hide_xaxis_labels(layout)
    format_time_axis(layout)
    return layout

# %% ../../../nbs/data_structure/timeseries/plot.ipynb 2
def nested_get(d, keys, default=None):
    """
    Safely get a value from a nested dictionary.

    Params
    ------
    d: The dictionary to search.
    keys: A list of keys representing the path to the desired value.
    default: The default value to return if any key is not found.
    """
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d


def format_da_attrs_tplot(da: DataArray):
    """Format attributes for `tplot` DataArray."""

    if da.attrs.get("long_name") is None:
        da.attrs["long_name"] = nested_get(
            da.attrs, ["plot_options", "yaxis_opt", "axis_label"]
        )
    if da.attrs.get("units") is None:
        units = nested_get(da.attrs, ["plot_options", "yaxis_opt", "axis_subtitle"], "")
        units = units.removeprefix("[").removesuffix("]")
        da.attrs["units"] = units
    return da

# %% ../../../nbs/data_structure/timeseries/plot.ipynb 3
def broadcast(iterable, func, *args, **kwargs):
    if isinstance(iterable, (list, tuple)):
        return type(iterable)(
            broadcast(item, func, *args, **kwargs) for item in iterable
        )
    else:
        return func(iterable, *args, **kwargs)


def standardize_to_matrix(lst):
    """Convert input to a list of lists"""
    if not isinstance(lst, list):
        lst = [lst]
    return [e if isinstance(e, list) else [e] for e in lst]


def _tsplot(data: DataArray):
    """time series plot for xarray dataarray"""
    data = format_da_attrs_tplot(data)
    by = "v_dim" if "v_dim" in data.dims else None
    labels = data.attrs.get("long_name")
    return data.hvplot(x="time", by=by, label=labels)


def tsplot(data):
    data = standardize_to_matrix(data)
    plots = broadcast(data, _tsplot)
    return polish_plot(plots)
