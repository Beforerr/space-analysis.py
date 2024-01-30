# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/io/30_cdf.ipynb.

# %% auto 0
__all__ = ['cdf2pl']

# %% ../../nbs/io/30_cdf.ipynb 1
import pycdfpp
import numpy as np
import polars as pl

# %% ../../nbs/io/30_cdf.ipynb 2
def cdf2pl(
    file_path: str, # The path to the CDF file.
    var_names: str | list[str] # The name(s) of the variable(s) to retrieve from the CDF file.
) -> pl.LazyFrame: # A lazy dataframe containing the requested data.
    """
    Convert a CDF file to Polars Dataframe.
    """
    
    # Ensure var_names is always a list
    if isinstance(var_names, str):
        var_names = [var_names]

    cdf = pycdfpp.load(file_path)
    epoch_var = cdf[var_names[0]].attributes['DEPEND_0'][0]
    epoch_time = pycdfpp.to_datetime64(cdf[epoch_var])
    
    columns = {"time": epoch_time}
    
    for var_name in var_names:
        
        var = cdf[var_name]
        var_values = var.values
        var_attrs = var.attributes
        
        # Handle FILLVAL
        if "FILLVAL" in var_attrs:
            fillval = var_attrs["FILLVAL"][0]
            var_values[var_values == fillval] = np.nan

        if var_values.shape[1] == 1:  # One-dimensional data
            columns[var_name] = var_values[:, 0]
        else:  # Multi-dimensional data
            # Dynamically create column names based on the shape of the field values
            
            # labels = cdf[var_attrs["LABL_PTR_1"][0]].values
            
            for i in range(var_values.shape[1]):
                columns[f"{var_name}_{i}"] = var_values[:, i]

    df = pl.DataFrame(columns).fill_nan(None).lazy()
    return df
