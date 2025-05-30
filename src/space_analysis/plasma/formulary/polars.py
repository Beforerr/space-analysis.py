# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../../nbs/plasma/00_formulary_polars.ipynb.

# %% auto 0
__all__ = ['df_beta', 'df_Alfven_speed', 'ldf_Alfven_speed', 'df_Alfven_current', 'thermal_spd2temp', 'df_thermal_spd2temp',
           'df_inertial_length', 'df_gradient_current']

# %% ../../../../nbs/plasma/00_formulary_polars.ipynb 1
import astropy.units as u
from astropy.constants import m_p
from plasmapy.formulary import beta
from space_analysis.plasma.formulary.numpy import (
    np_Alfven_speed,
    np_Alfven_current,
    np_inertial_length,
    np_gradient_current,
)
import polars as pl

# %% ../../../../nbs/plasma/00_formulary_polars.ipynb 2
def df_beta(
    df: pl.DataFrame,
    T: str = "T",  # temperature of the plasma
    n: str = "plasma_density",  # particle density of the plasma
    B: str = "B",  # magnetic field in the plasma,
    col_name: str = "beta",
    T_unit: u.Unit = u.eV,
    n_unit: u.Unit = u.cm**-3,
    B_unit: u.Unit = u.nT,
) -> pl.DataFrame:
    _T = df[T].to_numpy() * T_unit
    _n = df[n].to_numpy() * n_unit
    _B = df[B].to_numpy() * B_unit

    _beta = beta(T=_T, n=_n, B=_B)

    return df.with_columns(pl.Series(_beta).alias(col_name))

# %% ../../../../nbs/plasma/00_formulary_polars.ipynb 3
def df_Alfven_speed(
    df: pl.DataFrame,
    B: str = "B",  # magnetic field in the plasma, could be a component, as plasmapy will take `abs` of it
    density: str = "plasma_density",  # particle density of the plasma
    col_name: str = "Alfven_speed",
    **kwargs,
):
    B_temp = df[B].to_numpy()
    n_temp = df[density].to_numpy()

    _Alfven_speed = np_Alfven_speed(B=B_temp, density=n_temp, **kwargs)
    return df.with_columns(pl.Series(_Alfven_speed).alias(col_name))


def ldf_Alfven_speed(ldf: pl.LazyFrame, **kwargs):
    return ldf.collect().pipe(df_Alfven_speed, **kwargs).lazy()


def df_Alfven_current(
    df: pl.DataFrame,
    Alfven_speed="Alfven_speed",
    density="plasma_density",
    col_name: str = "j_Alfven",
    **kwargs,
):
    Alfven_speed_np = df[Alfven_speed].to_numpy()
    density_np = df[density].to_numpy()
    result = np_Alfven_current(
        Alfven_speed=Alfven_speed_np, density=density_np, **kwargs
    )
    return df.with_columns(pl.Series(result).alias(col_name))

# %% ../../../../nbs/plasma/00_formulary_polars.ipynb 4
def thermal_spd2temp(speed, speed_unit=u.km / u.s):
    return (m_p * (speed * speed_unit) ** 2 / 2).to("eV").value


def df_thermal_spd2temp(df: pl.LazyFrame, speed_col, speed_unit=u.km / u.s):
    df = df.collect()
    return df.with_columns(
        plasma_temperature=thermal_spd2temp(df[speed_col].to_numpy(), speed_unit)
    ).lazy()

# %% ../../../../nbs/plasma/00_formulary_polars.ipynb 5
def df_inertial_length(
    df: pl.DataFrame,
    density="plasma_density",
    col_name: str = "ion_inertial_length",
    **kwargs,
):
    density_np = df[density].to_numpy()
    result = np_inertial_length(density=density_np, **kwargs)

    return df.with_columns(pl.Series(result).alias(col_name))

# %% ../../../../nbs/plasma/00_formulary_polars.ipynb 6
def df_gradient_current(df, B_gradient, speed, col_name, **kwargs):
    B_gradient_np = df[B_gradient].to_numpy()
    speed_np = df[speed].to_numpy()
    result = np_gradient_current(B_gradient=B_gradient_np, speed=speed_np, **kwargs)
    return df.with_columns(pl.Series(result).alias(col_name))
