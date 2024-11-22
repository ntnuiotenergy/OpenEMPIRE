import shutil
from argparse import ArgumentTypeError
from datetime import datetime
from pathlib import Path

import pandas as pd


def copy_dataset(src_path: Path, dest_path: Path):
    """
    Copy dataset from source to destination folder.

    :param src_path: Folder containing dataset
    :param dest_path: Folder to copy the dataset
    """
    if not src_path.is_dir():
        raise ValueError(f"'{src_path}' is not a directory!")

    for file in ["General", "Generator", "Node", "Sets", "Storage", "Transmission"]:
        shutil.copyfile(src_path / f"{file}.xlsx", dest_path / f"{file}.xlsx")


def copy_scenario_data(base_dataset, scenario_data_path, use_scenario_generation, use_fixed_sample):
    """
    Copy scenario data from base dataset to active Empire dataset.

    :param base_dataset: path to base Empire dataset.
    :param scenario_data_path: path to scenario data in active Empire dataset.
    :param use_scenario_generation: Compute new scenarios or not.
    :param use_fixed_sample: Use fixed samples or not.
    """
    for csv_file in (base_dataset / "ScenarioData").glob("*.csv"):
        if csv_file.name == "sampling_key.csv" and not use_fixed_sample:
            continue

        shutil.copyfile(csv_file, scenario_data_path / csv_file.name)

    if not use_scenario_generation:
        for tab_file in (base_dataset / "ScenarioData").glob("*.tab"):
            shutil.copyfile(tab_file, scenario_data_path / tab_file.name)


def copy_file(src_file: Path, dest_file: Path):
    """
    Copy file from source to destination.

    :param src_file: Source file
    :param dest_file: Destination file
    """
    if not src_file.is_file():
        raise ValueError(f"'{src_file}' is not a file!")

    shutil.copyfile(src_file, dest_file)


def get_run_name(empire_config, version: str):
    name = (
        f"{version}_reg{empire_config.length_of_regular_season}"
        + f"_peak{empire_config.len_peak_season}_sce{empire_config.number_of_scenarios}"
    )

    if empire_config.use_scenario_generation and not empire_config.use_fixed_sample:
        name = name + "_randomSGR"
    else:
        name = name + "_noSGR"
    name = name + str(datetime.now().strftime("_%Y%m%d%H%M"))

    return name


def create_if_not_exist(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True)
    return path


def restricted_float(x) -> float:
    x = float(x)
    if x < 0.0 or x > 1.0:
        raise ArgumentTypeError(f"{x} not in range [0.0, 1.0]")
    return x

def get_name_of_last_folder_in_path(path: Path) -> str:
    return str(path).split("/")[-1]

def scale_and_shift_series(profile: pd.Series, scale: float, shift: float):
    """
    The function returns a new profile that can be scaled by 'scale' + 'shift' while preserving the same 
    mean and standard deviation as a scaling and shifting of the original profile.
    
    :param profile: Profile to scale and shift, values within [0,1].
    :param scale: Scale value
    :param shift: Shift value
    :returns: profile that only needs to be scaled
    """
    if profile.max() > 1.0:
        raise ValueError("'profile' cannot be larger than 1.0.")
    
    if profile.min() < 0.0:
        raise ValueError("'profile' cannot be smaller than 0.0.")
    
    profile_adjusted = (scale + shift / profile) * profile
    profile_adjusted = profile_adjusted / profile_adjusted.max()
    return profile_adjusted
