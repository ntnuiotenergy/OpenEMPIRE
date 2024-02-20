from pathlib import Path

import streamlit as st


def has_valid_data(folder_path: Path) -> bool:
    """
    Check that there is data to illustrate in the results

    :param folder_path: _description_
    :return: _description_
    """
    input_folder = folder_path / "Input/Xlsx/Sets.xlsx"
    if not input_folder.exists():
        return False
    results_file = folder_path / "Output/results_objective.csv"
    return results_file.exists()


def get_valid_data_folders(folders: list[Path]) -> dict[str, Path]:
    """
    Return folders containig valid data for Empire runs.

    :param folders: List of folders to search for valid data.
    """

    valid_result_folders_dict = {}
    for folder in folders:
        for f in folder.rglob("*"):
            if f.is_dir() and has_valid_data(f):
                relative_path = f.relative_to(folder)
                if relative_path in valid_result_folders_dict:
                    raise ValueError(
                        f"Warning relative path name already exists in other result folder. {relative_path}"
                    )
                valid_result_folders_dict[relative_path] = f

    return valid_result_folders_dict


def get_active_results(folders: list[Path]) -> Path:
    """
    Create streamlit sidebar with valid results and return path to the active results.

    :param folders: List of folders with results
    :return: Path to active results
    """

    valid_result_folders_dict = get_valid_data_folders(folders)

    ### Get path to results folder
    results_folder_relative = st.selectbox("Choose results: ", sorted(list(valid_result_folders_dict.keys())))
    return valid_result_folders_dict[results_folder_relative]
