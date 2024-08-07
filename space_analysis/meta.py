# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/data_structure/00_meta.ipynb.

# %% auto 0
__all__ = ['MagDataset', 'PlasmaDataset', 'TempDataset', 'MissionMeta']

# %% ../nbs/data_structure/00_meta.ipynb 0
from .core import Mission, Dataset

# %% ../nbs/data_structure/00_meta.ipynb 1
class MagDataset(Dataset):
    B_cols: list[str] = None


class PlasmaDataset(Dataset):
    density_col: str = None
    velocity_cols: list[str] = None
    speed_col: str = None
    temperature_col: str = None


class TempDataset(Dataset):
    para_col: str = None
    perp_cols: list[str] = None

# %% ../nbs/data_structure/00_meta.ipynb 2
class MissionMeta(Mission):
    mag_ds: MagDataset
    plasma_ds: PlasmaDataset
    ion_temp_ds: TempDataset
    e_temp_ds: TempDataset
