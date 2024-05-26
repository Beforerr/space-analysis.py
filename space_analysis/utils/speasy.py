# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/19_speasy.ipynb.

# %% auto 0
__all__ = ['spzvar2pldf', 'spzvars2pldf', 'get_time_resolution', 'get_provider', 'get_dataset_index', 'get_dataset_parameters',
           'get_parameter_index', 'Variable', 'Variables']

# %% ../../nbs/utils/19_speasy.ipynb 0
import speasy as spz
import polars as pl

from pydantic import model_validator
from functools import cached_property
from ..core import Variables as Vs
from ..core import Variable as V

from speasy.core.dataprovider import DataProvider
from speasy import SpeasyVariable
from speasy.core.inventory import DatasetIndex, ParameterIndex

import matplotlib.pyplot as plt
from matplotlib.pyplot import Axes

# %% ../../nbs/utils/19_speasy.ipynb 1
def spzvar2pldf(var: SpeasyVariable):
    # see SpeasyVariable.to_dataframe
    var = var.replace_fillval_by_nan()
    return (
        pl.DataFrame(var.values, schema=var.columns)
        .with_columns(time=pl.Series(var.time))
        .lazy()
    )  # Need to `lazy` last or ShapeError: unable to add a column of length xxxx to a DataFrame of height yyyy


def spzvars2pldf(vars: list[SpeasyVariable]):
    # join all dataframes into a single one on the time column
    if len(vars) == 1:
        return spzvar2pldf(vars[0])
    return pl.concat([spzvar2pldf(var) for var in vars], how="align")

# %% ../../nbs/utils/19_speasy.ipynb 2
def get_time_resolution(data: SpeasyVariable):
    return pl.Series(data.time).diff().describe()

# %% ../../nbs/utils/19_speasy.ipynb 3
def get_provider(v: str) -> DataProvider:
    if v == "cda":
        return spz.cda
    else:
        return spz.amda


def get_dataset_index(v: str, provider: str = "cda") -> DatasetIndex:
    return get_provider(provider).flat_inventory.datasets[v]


def get_dataset_parameters(v: str, provider: str = "cda"):
    # return vars(get_dataset_index(v, provider)).values()
    ds_info = vars(get_dataset_index(v, provider))
    return [member for member in ds_info.values() if isinstance(member, ParameterIndex)]


def get_parameter_index(param: str, ds: str) -> ParameterIndex:
    ds_info = vars(get_dataset_index(ds))
    return ds_info[param]

# %% ../../nbs/utils/19_speasy.ipynb 4
class Variable(V):

    def to_polars(self):
        return spzvar2pldf(self.data)

    @cached_property
    def data(self) -> SpeasyVariable:
        return spz.get_data(self.product, self.timerange)

    @property
    def time_resolution(self):
        return get_time_resolution(self.data)

    def plot(self, fig=None, ax: Axes = None):
        if fig is None and ax is None:
            fig, ax = plt.subplots()

        self.data.replace_fillval_by_nan().plot(ax=ax)

        if self.name:
            ax.set_ylabel(self.name)

        return fig, ax

# %% ../../nbs/utils/19_speasy.ipynb 5
class Variables(Vs):
    variables: list[Variable] = None
    products: list[str | ParameterIndex] = None

    # initize products from provider and dataset if not provided
    @model_validator(mode="after")
    def check_products(self):
        if self.products is None and self.dataset:
            if self.parameters:
                self.products = [
                    f"{self.provider}/{self.dataset}/{var}" for var in self.parameters
                ]

            else:
                self.products = get_dataset_parameters(self.dataset, self.provider)
                self.parameters = [member.spz_name() for member in self.products]
        return self

    @model_validator(mode="after")
    def check_variables(self):
        if self.variables is None:
            self.variables = [Variable(product=product) for product in self.products]
        # set the same timerange for all variables
        for var in self.variables:
            var.timerange = self.timerange
        return self

    @property
    def data(self) -> list[SpeasyVariable]:
        return [var.data for var in self.variables]

    @property
    def time_resolutions(self):
        return [var.time_resolution for var in self.variables]
    
    def to_polars(self):
        return spzvars2pldf(self.data)
    
    def plot(self, gridspec_kw: dict = {"hspace": 0}):
        vars = self.variables

        fig, axes = plt.subplots(nrows=len(vars), sharex=True, gridspec_kw=gridspec_kw)
        axes: list[Axes] = axes if len(vars) > 1 else [axes]

        for var, ax in zip(vars, axes):
            var.plot(ax=ax)

        return fig, axes
