# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['Variable', 'Variables']

# %% ../nbs/00_core.ipynb 3
from pydantic import BaseModel
import polars as pl

# %% ../nbs/00_core.ipynb 4
class Variable(BaseModel):
    name: str
    description: str = None
    unit: str = None
    data: list = None

class Variables(BaseModel):
    class Config:
        arbitrary_types_allowed = True  # RuntimeError: no validator found for <class 'speasy.products.variable.SpeasyVariable'>, see  `arbitrary_types_allowed` in Config

    products: list[str] = None
    timerange: list[str] = None

    provider: str = "cda"
    dataset: str = None
    parameters: list[str] = None

    data: list[Variable] = None
    
    def retrieve_data(self):
        pass

    def get_data(self):
        if self.data is None:
            self.retrieve_data()
        return self.data

    def to_polars(self) -> pl.LazyFrame:
        pass

    def preview(self):
        return self.to_polars().head().collect()