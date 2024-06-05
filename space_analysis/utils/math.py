# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/utils/00_math.ipynb.

# %% auto 0
__all__ = ['cosd', 'sind']

# %% ../../nbs/utils/00_math.ipynb 1
import numpy as np

# %% ../../nbs/utils/00_math.ipynb 2
def cosd(x):
    return np.cos(np.deg2rad(x))


def sind(x):
    return np.sin(np.deg2rad(x))
