# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/data_structure/01_tplot.ipynb.

# %% auto 0
__all__ = ['FigureExtraOptions', 'OutputConfig', 'export2csv', 'magnitude', 'mva', 'magnitude_join', 'TransformOp',
           'ProcessConfig', 'TplotConfig', 'PanelConfig', 'Config', 'GraphicalConfig', 'update_panel', 'plot', 'export',
           'process', 'load_data', 'update_tvar', 'process_panel']

# %% ../../nbs/data_structure/01_tplot.ipynb 0
from pydantic import (
    BaseModel,
    StringConstraints,
    ConfigDict,
    model_validator,
    field_validator,
)
from datetime import datetime, date

from cdasws import CdasWs
import pyspedas
from pyspedas.cotrans.minvar_matrix_make import minvar_matrix_make
from pyspedas import tvector_rotate
from pyspedas.analysis.tvectot import tvectot

from pytplot import join_vec, split_vec, get_data, store_data
from pytplot import tplot, options, data_quants

from xarray import DataArray
from typing import Annotated

from matplotlib.pyplot import Figure, Axes
import matplotlib.pyplot as plt
from loguru import logger

# %% ../../nbs/data_structure/01_tplot.ipynb 1
class FigureExtraOptions(BaseModel):
    hide_legends: bool = False
    hide_ylabels: bool = False
    sync_legend_colors: bool = False
    hide_legend_lines: bool = False

    def process(self, fig: Figure, axes: list[Axes]) -> None:
        """Apply extra options to a matplotlib figure and its axes."""

        # Process each option through its dedicated method
        if self.hide_legends:
            self._hide_legends(axes)
        if self.hide_ylabels:
            self._hide_ylabels(axes)
        if self.sync_legend_colors:
            self._sync_legend_colors(axes)
        if self.hide_legend_lines:
            self._hide_legend_lines(axes)

    def _hide_legends(self, axes: list[Axes]) -> None:
        """Hide legends on all axes."""
        for ax in axes:
            legend = ax.get_legend()
            if legend:
                legend.remove()

    def _hide_ylabels(self, axes: list[Axes]) -> None:
        """Hide y-axis labels on all axes."""
        for ax in axes:
            ax.set_ylabel("")

    def _sync_legend_colors(self, axes: list[Axes]) -> None:
        """Synchronize legend text colors with their corresponding line colors."""
        for ax in axes:
            legend = ax.get_legend()
            if legend:
                for line, text in zip(legend.get_lines(), legend.get_texts()):
                    text.set_color(line.get_color())

    def _hide_legend_lines(self, axes: list[Axes]) -> None:
        """Hide legend lines on all axes."""
        for ax in axes:
            if ax.get_legend():
                for line in ax.get_legend().get_lines():
                    line.set_visible(False)


class OutputConfig(BaseModel):
    path: str = None
    filename: str = None

    formats: list[str] = list()
    display: bool = False

    figure: dict = dict()
    """Figure options"""

    figure_extra: FigureExtraOptions = FigureExtraOptions()
    """Extra figure options"""

# %% ../../nbs/data_structure/01_tplot.ipynb 2
def export2csv(tvars: list, path):
    fnames = []
    for tvar in tvars:
        da: DataArray = get_data(tvar, xarray=True)
        fname = f"{path}_{tvar}.csv"
        da.to_pandas().to_csv(fname)
        fnames.append(fname)
    return fnames

# %% ../../nbs/data_structure/01_tplot.ipynb 3
from typing import Callable

# if "slice-1" in config.trans:
#     tvar = split_vec(tvar)[:1]
# if "slice-3" in config.trans:
#     tvar = join_vec(split_vec(tvar)[:3])
# if "mva" in config.trans:
#     minvar_matrix_make(tvar)
#     tvar = tvector_rotate(tvar + "_mva_mat", tvar)[0]
#     legend_names = [r"$B_l$", r"$B_m$", r"$B_n$"]

# if "magnitude" in trans:
#     tvar2plot = tvectot(tvar, join_component=False)
#     options(tvar2plot, "legend_names", None)

# if "magnitude_join" in trans:
#     tvar2plot = tvectot(tvar, join_component=True)
#     legend_names = legend_names + [r"$B_{total}$"]
#     options(tvar2plot, "legend_names", legend_names)

def magnitude(tvar: str):
    tvar2plot = tvectot(tvar, join_component=False)
    options(tvar2plot, "legend_names", None)
    return tvar2plot

def mva(tvar: str, prefix="B"):
    minvar_matrix_make(tvar)
    tvar2plot = tvector_rotate(tvar + "_mva_mat", tvar)[0]
    options(
        tvar2plot,
        "legend_names",
        [rf"${prefix}_l$", rf"${prefix}_m$", rf"${prefix}_n$"],
    )
    return tvar2plot


def magnitude_join(tvar: str):
    tvar2plot = tvectot(tvar, join_component=True)

    data_quants[tvar2plot].attrs["plot_options"]["yaxis_opt"]["legend_names"].append(
        r"$B_{total}$"
    )
    return tvar2plot


class TransformOp(BaseModel):
    """Transformation operation"""

    # allow addtional fields
    model_config = ConfigDict(extra="allow")

    name: str

    transform_func: Callable[[str], str] = None

    @model_validator(mode="after")
    def map_transform_func(self):
        transform_func_maps = {
            "avg": pyspedas.avg_data,
            "slice-1": lambda tvar: split_vec(tvar)[:1],
            "slice-3": lambda tvar: join_vec(split_vec(tvar)[:3]),
            "mva": mva,
            "magnitude": magnitude,
            "magnitude_join": magnitude_join,
        }
        self.transform_func = transform_func_maps.get(self.name)
        return self


class ProcessConfig(BaseModel):
    tvar: str = None
    trans: list[TransformOp] = list()

    @field_validator("trans", mode="before")
    @classmethod
    def check_transforms(cls, v: list[dict | str]):
        return [({"name": tran} if isinstance(tran, str) else tran) for tran in v]

# %% ../../nbs/data_structure/01_tplot.ipynb 4
class TplotConfig(BaseModel):
    tvar: str = None
    trans: list[str] = None

class PanelConfig(BaseModel):

    timerange: list[date | datetime] = None
    
    ds: str = None
    id: str = None
    name: str = None
    units: str = None
    labels: list[str] = list()
    
    satellite: Annotated[str, StringConstraints(to_lower=True)] = None
    instrument: Annotated[str, StringConstraints(to_lower=True)] = None
    datatype: str = None
    probe: str = None
    
    process: ProcessConfig = ProcessConfig()
    tplot: TplotConfig = TplotConfig()

class Config(BaseModel):
    panels: list[PanelConfig]
    timerange: list[datetime | date] = None
    output: OutputConfig = None
    backend: str = None
    
    @model_validator(mode='before')
    def set_default_timerange(cls, values):
        timerange = values.get('timerange', None)
        panels = values.get('panels', [])
        
        if timerange:
            for panel in panels:
                if not panel.get('timerange'):
                    panel['timerange'] = timerange
        return values

class GraphicalConfig(BaseModel):
    ylabel: str = None


# %% ../../nbs/data_structure/01_tplot.ipynb 5
def update_panel(ax: Axes, config: PanelConfig):
    pass


def plot(
    tvars2plot: list[str],
    config: Config,
    fig: Figure = None,
    axes: list[Axes] = None,
    **kwargs,
) -> tuple[Figure, list[Axes]]:
    if not isinstance(tvars2plot, list):
        tvars2plot = [tvars2plot]
        
    panel_configs = config.panels
    output_config = config.output

    if fig is None or axes is None:
        nrows = len(tvars2plot)
        fig, axes = plt.subplots(nrows=nrows, sharex=True, **kwargs)
        axes = [axes] if isinstance(axes, Axes) else axes

    for ax, tvar, panel_config in zip(axes, tvars2plot, panel_configs):
        tplot(tvar, fig=fig, axis=ax, display=False)
        update_panel(ax, panel_config)

    fig.set(**output_config.figure)
    output_config.figure_extra.process(fig, axes)
    
    return fig, axes


def export(tvars2plot: list, config: Config, plot_kwargs: dict = None, **kwargs):

    fig, axes = plot(tvars2plot, config, **plot_kwargs)

    output_config = config.output
    path = output_config.path

    for fmt in output_config.formats:
        match fmt:
            case "csv":
                export2csv(tvars2plot, path)
            case "display":
                fig.show()
            case _:
                fig.savefig(f"{path}.{fmt}", **kwargs)

    return fig, axes

# %% ../../nbs/data_structure/01_tplot.ipynb 6
def process(tvar: str | list[str], config: ProcessConfig):
    for tran in config.trans:
        tvar = tran.transform_func(
            tvar, **tran.model_dump(exclude=["name", "transform_func"])
        )
    return tvar

    # if config.trans:
    #     if "slice-1" in config.trans:
    #         tvar = split_vec(tvar)[:1]
    #     if "slice-3" in config.trans:
    #         tvar = join_vec(split_vec(tvar)[:3])
    #     if "mva" in config.trans:
    #         minvar_matrix_make(tvar)
    #         tvar = tvector_rotate(tvar + "_mva_mat", tvar)[0]
    #         legend_names = [r"$B_l$", r"$B_m$", r"$B_n$"]

    #     if "magnitude" in trans:
    #         tvar2plot = tvectot(tvar, join_component=False)
    #         options(tvar2plot, "legend_names", None)

    #     if "magnitude_join" in trans:
    #         tvar2plot = tvectot(tvar, join_component=True)
    #         legend_names = legend_names + [r"$B_{total}$"]
    #         options(tvar2plot, "legend_names", legend_names)

    # else:
    #     tvar2plot = tvar

# %% ../../nbs/data_structure/01_tplot.ipynb 7
def load_data(config: PanelConfig, load_func=None):

    timerange = [time.isoformat() for time in config.timerange]
    var = config.id

    if load_func is None:
        if config.satellite and config.instrument:
            mod = getattr(pyspedas, config.satellite)
            load_func = getattr(mod, config.instrument)
        elif config.ds:
            cdas = CdasWs()
            status, data = cdas.get_data(config.ds, var, timerange[0], timerange[1])
            store_data(var, {"x": data[var].Epoch, "y": data[var]})
            return var
        else:
            logger.error("No load function provided")
            return None

    load_args = {
        "trange": timerange,
        "time_clip": True,
        "varnames": config.id,
    }

    # Conditionally add the 'datatype' and 'probe' argument
    if config.datatype is not None:
        load_args["datatype"] = config.datatype
    if config.probe is not None:
        load_args["probe"] = config.probe

    return load_func(**load_args)


def update_tvar(tvar, config: PanelConfig):
    options(tvar, "thick", 2)
    # options(tvar, "char_size", 16)
    if config.name is not None:
        options(tvar, "ytitle", f"{config.name}")
    if config.units is not None:
        if config.units == "":
            options(tvar, "ysubtitle", "")
        options(tvar, "ysubtitle", f"[{config.units}]")

    return tvar


def process_panel(
    config: PanelConfig,
    process_func=process,
    load_func=load_data,
    update_func=update_tvar,
):
    tvar = load_func(config)

    if isinstance(tvar, list):
        tvar = tvar[0]

    tvar_processed = process_func(tvar, config=config.process)
    logger.debug(f"Processed tvar: {tvar_processed}")
    return update_func(tvar_processed, config=config)
