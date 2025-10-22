from pathlib import Path
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_file_csv(
    csv_folder: Path,
    sheet: str,
    columns: list[int],
    tab_file_path: Path,
    filename: str,
) -> None:
    """
    Reads a CSV file (sheet) from a folder and saves it as a .tab file.
    Preserves the same formatting as the original Excel->.tab process.
    """

    infile = csv_folder / f"{sheet}.csv"
    logger.info("Reading %s", infile)

    df = pd.read_csv(infile)
    df = df.iloc[:, columns]
    df.columns = df.columns.astype(str).str.replace(" ", "_")
    df = df.dropna(how="all").reset_index(drop=True)
    df = df.replace(r"\s+", "", regex=True)

    tab_file_path.mkdir(parents=True, exist_ok=True)
    outfile = tab_file_path / f"{filename}_{sheet}.tab"
    df.to_csv(outfile, sep="\t", index=False, header=True)
    logger.info("Saved %s", outfile)


def read_sets_csv(
    csv_folder: Path,
    sheet: str,
    tab_file_path: Path,
    filename: str,
) -> None:
    """
    Reads a CSV sheet from a folder and saves each column as a separate .tab file.
    """

    infile = csv_folder / f"{sheet}.csv"
    logger.info("Reading %s", infile)

    df = pd.read_csv(infile)
    df = df.dropna(how="all").reset_index(drop=True)

    for col in df.columns:
        col_df = df[[col]].dropna().replace(r"\s+", "", regex=True)
        tab_file_path.mkdir(parents=True, exist_ok=True)
        outfile = tab_file_path / f"{filename}_{col}.tab"
        col_df.to_csv(outfile, sep="\t", index=False, header=True)
        logger.info("Saved %s", outfile)


def generate_tab_from_csv(csv_root: Path, tab_file_path: Path) -> None:
    """
    Reads all CSV subfolders (one per Excel file) and regenerates the .tab files
    in exactly the same format as before.
    """

    logger.info("Generating .tab files from CSV folders...")

    # Example: Sets
    sets_folder = csv_root / "Sets"
    read_sets_csv(sets_folder, "Nodes", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "OffshoreNodes", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "Horizon", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "LineType", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "Technology", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "Storage", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "Generator", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "ThermalGenerators", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "HydroGenerator", tab_file_path, "Sets")
    read_sets_csv(sets_folder, "HydroGeneratorWithReservoir", tab_file_path, "Sets")
    read_file_csv(sets_folder, "StorageOfNodes", [0, 1], tab_file_path, "Sets")
    read_file_csv(sets_folder, "GeneratorsOfNode", [0, 1], tab_file_path, "Sets")
    read_file_csv(sets_folder, "GeneratorsOfTechnology", [0, 1], tab_file_path, "Sets")
    read_file_csv(sets_folder, "DirectionalLines", [0, 1], tab_file_path, "Sets")
    read_file_csv(sets_folder, "LineTypeOfDirectionalLines", [0, 1, 2], tab_file_path, "Sets")

    # Example: Generator
    gen_folder = csv_root / "Generator"
    read_file_csv(gen_folder, "FixedOMCosts", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "CapitalCosts", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "VariableOMCosts", [0, 1], tab_file_path, "Generator")
    read_file_csv(gen_folder, "FuelCosts", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "CCSCostTSVariable", [0, 1], tab_file_path, "Generator")
    read_file_csv(gen_folder, "Efficiency", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "RefInitialCap", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "ScaleFactorInitialCap", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "InitialCapacity", [0, 1, 2, 3], tab_file_path, "Generator")
    read_file_csv(gen_folder, "MaxBuiltCapacity", [0, 1, 2, 3], tab_file_path, "Generator")
    read_file_csv(gen_folder, "MaxInstalledCapacity", [0, 1, 2], tab_file_path, "Generator")
    read_file_csv(gen_folder, "RampRate", [0, 1], tab_file_path, "Generator")
    read_file_csv(gen_folder, "GeneratorTypeAvailability", [0, 1], tab_file_path, "Generator")
    read_file_csv(gen_folder, "CO2Content", [0, 1], tab_file_path, "Generator")
    read_file_csv(gen_folder, "Lifetime", [0, 1], tab_file_path, "Generator")