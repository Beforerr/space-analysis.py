# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/missions/stereo/index.ipynb.

# %% auto 0
__all__ = ['thb_l2_fgm', 'thb_l2_mom']

# %% ../../../nbs/missions/stereo/index.ipynb 1
from ...meta import MagDataset, PlasmaDataset

# %% ../../../nbs/missions/stereo/index.ipynb 3
thb_l2_fgm = MagDataset(dataset="THB_L2_FGM", parameters=["thb_fgl_gse"])

thb_l2_mom = PlasmaDataset(
    dataset="THB_L2_MOM",
    parameters=[
        "thb_peim_densityQ",
        "thb_peim_velocity_gseQ",
    ],
)
