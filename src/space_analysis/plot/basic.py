# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/plot/01_matplotlib.ipynb.

# %% auto 0
__all__ = ['savefig']

# %% ../../../nbs/plot/01_matplotlib.ipynb 1
import matplotlib.pyplot as plt

# %% ../../../nbs/plot/01_matplotlib.ipynb 3
plt.rc("savefig", dpi=300)

# %% ../../../nbs/plot/01_matplotlib.ipynb 4
def savefig(
    name,  # name of the file
    dir="../figures",  # directory to save the file
    path=None,  # path to the file
    formats=["png", "pdf"],
    **kwargs,
):
    if path is None:
        path = f"{dir}/{name}"

    for fmt in formats:
        fname = f"{path}.{fmt}"
        plt.savefig(fname, bbox_inches="tight", **kwargs)
