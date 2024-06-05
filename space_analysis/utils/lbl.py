# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/io/31_lbl.ipynb.

# %% auto 0
__all__ = ['HTTP_PROTOCOLS', 'load_lbl']

# %% ../../nbs/io/31_lbl.ipynb 2
import pandas
import pdr

# %% ../../nbs/io/31_lbl.ipynb 3
HTTP_PROTOCOLS = ("http", "https")


def load_lbl(filepath: str, type: str = "table") -> pandas.DataFrame:
    """Load LBL data.

    Args:
        filepath: File path to load the data from.
        type: Type of data to load. Options are 'table' and 'index'.

    Returns:
        A pandas DataFrame containing the loaded data.
    """
    if type == "table":
        df = pdr.read(filepath).TABLE
    elif type == "index":
        df = pandas.read_csv(filepath, delimiter=",", quotechar='"')
        df.columns = df.columns.str.replace(" ", "")

    return df
