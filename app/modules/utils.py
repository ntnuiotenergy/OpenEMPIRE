from pathlib import Path
import streamlit as st

def has_valid_data(folder_path: Path):
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
    
def get_valid_data_folders(root_dir: Path):
    """
    Return folders containig valid data for Empire runs.

    :param root_dir: Directory to search for valid data.
    """
    result_folders = []
    for folder in root_dir.rglob('*'):
        if folder.is_dir() and has_valid_data(folder):
            result_folders.append(folder)

    return result_folders


def get_active_results(result_folder: Path):
    
    valid_result_folders = get_valid_data_folders(result_folder)

    valid_result_folders_dict = {i.relative_to(result_folder): i for i in valid_result_folders}

    ### Get path to results folder
    results_folder_relative = st.sidebar.selectbox(
        "Choose results: ", list(valid_result_folders_dict.keys())
    )
    return valid_result_folders_dict[results_folder_relative]
