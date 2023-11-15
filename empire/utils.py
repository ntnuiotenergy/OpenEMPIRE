import shutil
from argparse import ArgumentTypeError
from datetime import datetime
from pathlib import Path


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
