# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/missions/stereo/index.ipynb.

# %% auto 0
__all__ = ['sta_l1_mag_rtn', 'sta_l2_pla']

# %% ../../../nbs/missions/stereo/index.ipynb 1
from ...meta import MagDataset, PlasmaDataset
from datetime import timedelta

# %% ../../../nbs/missions/stereo/index.ipynb 3
sta_l1_mag_rtn = MagDataset(
    dataset="STA_L1_MAG_RTN",
    parameters=["BFIELD"],
    B_cols=["BR", "BT", "BN"],
    ts=timedelta(seconds=0.125),
)

sta_l2_pla = PlasmaDataset(
    dataset="STA_L2_PLA_1DMAX_1MIN",
    parameters=[
        "proton_number_density",
        "proton_Vr_RTN",
        "proton_Vt_RTN",
        "proton_Vn_RTN",
        "proton_temperature",
    ],
    velocity_cols=["Vr", "Vt", "Vn"],
    links=[
        "https://cdaweb.gsfc.nasa.gov/cgi-bin/eval2.cgi?dataset=STA_L2_PLA_1DMAX_1MIN&index=sp_phys",
        "https://hpde.io/NASA/NumericalData/STEREO-A/PLASTIC/Protons/PT1M",
    ],
)
