# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/19_speasy.ipynb.

# %% auto 0
__all__ = ['spzvar2pldf', 'spzvars2pldf', 'get_provider', 'get_dataset_index', 'Variables']

# %% ../../nbs/utils/19_speasy.ipynb 0
import speasy as spz
import polars as pl

from pydantic import model_validator
from ..core import Variables as Vs

from speasy.core.dataprovider import DataProvider
from speasy import SpeasyVariable
from speasy.core.inventory import DatasetIndex, ParameterIndex

from fastcore.all import patch

# %% ../../nbs/utils/19_speasy.ipynb 1
def spzvar2pldf(var: SpeasyVariable):
    # see SpeasyVariable.to_dataframe
    var = var.replace_fillval_by_nan()
    return pl.DataFrame(var.values, schema=var.columns).with_columns(
        time = pl.Series(var.time)
    ).lazy() # Need to `lazy` last or ShapeError: unable to add a column of length xxxx to a DataFrame of height yyyy
    
    
def spzvars2pldf(vars: list[SpeasyVariable]):
    # join all dataframes into a single one on the time column
    if len(vars) == 1:
        return spzvar2pldf(vars[0])
    return pl.concat([spzvar2pldf(var) for var in vars], how='align')

# %% ../../nbs/utils/19_speasy.ipynb 2
@patch
def time_resolutions(self: SpeasyVariable):
    return pl.Series(self.time).diff().describe()
        

# %% ../../nbs/utils/19_speasy.ipynb 3
def get_provider(v: str) -> DataProvider:
    if v == "cda":
        return spz.cda
    else:
        return spz.amda


def get_dataset_index(v: str, provider: str) -> DatasetIndex:
    return get_provider(provider).flat_inventory.datasets[v]


class Variables(Vs):
    products: list[str | ParameterIndex] = None

    data: list[SpeasyVariable] = None
    
    _disable_proxy: bool = True

    # initize products from provider and dataset if not provided
    @model_validator(mode="after")
    def check_products(self):
        if self.products is None and self.dataset:
            if self.parameters:
                self.products = [
                    f"{self.provider}/{self.dataset}/{var}" for var in self.parameters
                ]

            else:
                dataset_index = get_dataset_index(self.dataset, self.provider)
                self.products = [
                    member
                    for member in vars(dataset_index).values()
                    if isinstance(member, ParameterIndex)
                ]
                self.parameters = [member.spz_name() for member in self.products]
        return self

    def retrieve_data(self):
        # return Variables with data set
        if 'local' in self.provider:
            self.data = spz.get_data(
                self.products, self.timerange
            )
        else:
            self.data = spz.get_data(
                self.products, self.timerange, disable_proxy=self._disable_proxy
            )
        return self

    @property
    def time_resolutions(self) -> pl.DataFrame:
        return self.get_data()[0].time_resolutions()

    def to_polars(self):
        return spzvars2pldf(self.get_data())
