# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../nbs/missions/juno/fgm.ipynb.

# %% auto 0
__all__ = ['JunoPhases', 'JunoFGMCoords', 'JunoFGMTimeResolutions', 'load_func', 'process_member', 'unpack_and_convert', 'Unpack',
           'download_data']

# %% ../../../nbs/missions/juno/fgm.ipynb 2
import pooch
import polars as pl

from tqdm import tqdm
from pipe import filter

from typing import Literal, Callable
from functools import partial

# %% ../../../nbs/missions/juno/fgm.ipynb 5
#| code-summary: type definitions
JunoPhases = Literal["CRUISE", "JUPITER"]
JunoFGMCoords = Literal['SE', 'SS', 'PL']
JunoFGMTimeResolutions = Literal["1SEC", "1MIN", "FULL"]

# %% ../../../nbs/missions/juno/fgm.ipynb 6
from ...utils.lbl import load_lbl

import os
from zipfile import ZipFile

from pooch.processors import ExtractorProcessor

import ray

# %% ../../../nbs/missions/juno/fgm.ipynb 7
def load_func(file: str):
    df: pl.DataFrame = pl.from_dataframe(load_lbl(file))
    return (
        df.lazy()
        .with_columns(
            time=pl.col("SAMPLE UTC").str.slice(0, 4).str.to_datetime("%Y")
            + pl.duration(
                milliseconds=(pl.col("DECIMAL DAY") - 1) * 24 * 60 * 60 * 1000
            )
        )
        .drop(["SAMPLE UTC", "DECIMAL DAY", "INSTRUMENT RANGE", "X", "Y", "Z"])
        .sort("time")
    )


@ray.remote
def process_member(
    member: str, fname: str, extract_dir, clean=True, fmt="arrow"
):
    with ZipFile(fname, "r") as zip_file:
        lbl_fp = zip_file.extract(member, path=extract_dir)
        sts_fp = zip_file.extract(member.replace(".lbl", ".sts"), path=extract_dir)

        # Convert the file to a different format
        output_fp = lbl_fp.replace("lbl", fmt)
        load_func(lbl_fp).collect().write_ipc(output_fp)

        # Remove the lbl and sts files
        if clean:
            os.remove(lbl_fp)
            os.remove(sts_fp)

        return output_fp


def unpack_and_convert(fname, extract_dir, process_func = process_member):
    """
    Post-processing hook to unzip a file and convert it to a different format in real-time. (Otherwise the files unzipped would take up too much space on the user's computer.)

    Parameters
    ----------
    fname : str
       Full path of the zipped file in local storage

    """

    with ZipFile(fname, "r") as zip_file:
        # Extract the data file from within the archive
        members = list(zip_file.namelist() | filter(lambda x: x.endswith(".lbl")))

    ray.init()
    
    func = partial(process_func.remote, fname=fname, extract_dir=extract_dir)
    futures = list(map(func, members))
    results = ray.get(futures)
    
    ray.shutdown()
    
    return results


class Unpack(ExtractorProcessor):

    suffix = ".unzip"

    def _extract_file(self, fname, extract_dir):
        unpack_and_convert(fname, extract_dir)

# %% ../../../nbs/missions/juno/fgm.ipynb 8
def download_data(
    dataset="JNO-SS-3-FGM-CAL-V1.0",
    phase: JunoPhases = "CRUISE",
    coord: JunoFGMCoords = "SE",
    datatype: JunoFGMTimeResolutions = "1SEC",  # time resolution
    processor: Callable = None,
    fmt="arrow",
) -> list[str]:

    url = f"https://pds-ppi.igpp.ucla.edu/ditdos/download?id=pds://PPI/{dataset}/DATA/{phase}/{coord}/{datatype}"

    if processor is None:
        processor = Unpack() # default processor, needed to be created here!!!

    files = pooch.retrieve(
        url=url,
        known_hash=None,
        progressbar=True,
        processor=processor,
    )

    return sorted(files | filter(lambda x: x.endswith(f".{fmt}")))
