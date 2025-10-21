"""Convert Excel files from Data Handler to CSV files in input_data folder."""

import os
import logging
import pandas as pd
from pathlib import Path
import argparse 
import shutil

# input dataset from parameter
parser = argparse.ArgumentParser(description="Convert Excel files to CSV.")
parser.add_argument(
    "-d",
    "--dataset",
    type=str,
    required=False,
    default="europe_v51",
    help="Name of the dataset folder in Data Handler to convert.",
)
args = parser.parse_args()
DATASET = args.dataset

SOURCE_DIR = Path(f"Data Handler/{DATASET}")
TARGET_DIR = Path(f"input_data/{DATASET}")



FILE_SUFFIX = ".csv"
ENCODING = "utf-8"

# skiprows before header
HEADER_ROWS = {
    "Sets.xlsx": {
        "Nodes": 0,
        "OffshoreNodes": 0,
        "StorageOfNodes": 2,
        "GeneratorsOfNode": 2,
        "GeneratorsOfTechnology": 2,
        "DirectionalLines": 2,
        "LineTypeOfDirectionalLines": 2,
    },
    "Generator.xlsx": {
        "FixedOMCosts": 2,
        "CapitalCosts": 2,
        "VariableOMCosts": 2,
        "FuelCosts": 2,
        "CCSCostTSVariable": 2,
        "Efficiency": 2,
        "RefInitialCap": 2,
        "ScaleFactorInitialCap": 2,
        "InitialCapacity": 2,
        "MaxBuiltCapacity": 2,
        "MaxInstalledCapacity": 2,
        "RampRate": 2,
        "GeneratorTypeAvailability": 2,
        "CO2Content": 2,
        "Lifetime": 2,
    },
    "Transmission.xlsx": {
        "lineEfficiency": 2,
        "MaxInstallCapacityRaw": 2,
        "MaxBuiltCapacity": 2,
        "Length": 2,
        "TypeCapitalCost": 2,
        "TypeFixedOMCost": 2,
        "InitialCapacity": 2,
        "Lifetime": 2,
    },
    "Node.xlsx": {
        "ElectricAnnualDemand": 2,
        "NodeLostLoadCost": 2,
        "HydroGenMaxAnnualProduction": 2,
    },
    "General.xlsx": {
        "seasonScale": 2,
        "CO2Cap": 2,
        "CO2Price": 2,
    },
    "Storage.xlsx": {
        "StorageBleedEfficiency": 2,
        "StorageChargeEff": 2,
        "StorageDischargeEff": 2,
        "StoragePowToEnergy": 2,
        "StorageInitialEnergyLevel": 2,
        "InitialPowerCapacity": 2,
        "PowerCapitalCost": 2,
        "PowerFixedOMCost": 2,
        "PowerMaxBuiltCapacity": 2,
        "EnergyCapitalCost": 2,
        "EnergyFixedOMCost": 2,
        "EnergyInitialCapacity": 2,
        "EnergyMaxBuiltCapacity": 2,
        "EnergyMaxInstalledCapacity": 2,
        "PowerMaxInstalledCapacity": 2,
        "Lifetime": 2,
    },
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def read_excel_with_header(excel: pd.ExcelFile, sheet: str, skiprows: int) -> pd.DataFrame:
    """Read Excel sheet with proper header and cleaning."""
    df = excel.parse(sheet, header=skiprows)
    df = df.dropna(how="all")  # remove empty rows
    df = df.replace(r"\s+", "", regex=True)  # clean whitespace
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(r"^Unnamed.*", "", regex=True)
    )
    df = df.loc[:, (df.columns != "")]
    return df


def convert_excel_to_subfolder(excel_path: Path, target_root: Path):
    """Convert one Excel file into a subfolder with one CSV per sheet."""
    subfolder = target_root / excel_path.stem
    subfolder.mkdir(parents=True, exist_ok=True)
    logger.info(f"Processing {excel_path.name} → {subfolder}")

    try:
        excel = pd.ExcelFile(excel_path)
    except Exception as e:
        logger.error(f"Could not open {excel_path.name}: {e}")
        return

    config = HEADER_ROWS.get(excel_path.name, {})
    for sheet in excel.sheet_names:
        try:
            skiprows = config.get(sheet, 0)
            df = read_excel_with_header(excel, sheet, skiprows)

            if df.empty:
                logger.warning(f"{excel_path.name} [{sheet}] is empty — skipped.")
                continue

            safe_name = f"{sheet.replace(' ', '_')}{FILE_SUFFIX}"
            output_file = subfolder / safe_name
            df.to_csv(output_file, index=False, encoding=ENCODING)

            logger.info(f"Saved {output_file.relative_to(target_root)} (header row {skiprows})")

        except Exception as e:
            logger.error(f"Error converting {excel_path.name} [{sheet}]: {e}")


def copy_scenario_data():
    # # copy the csv files in SOURCE_DIR/ScenarioData to TARGET_DIR/ScenarioData
    scenario_src = SOURCE_DIR / "ScenarioData"
    scenario_dest = TARGET_DIR / "ScenarioData"
    scenario_dest.mkdir(parents=True, exist_ok=True)
    for csv_file in scenario_src.glob("*.csv"):
        dest_file = scenario_dest / csv_file.name
        pd.read_csv(csv_file).to_csv(dest_file, index=False, encoding=ENCODING)
        logger.info(f"Copied scenario file {dest_file.relative_to(TARGET_DIR)}")
    return 

def copy_sources_file():
    # copy everything in SOURCE_DIR/Sources to TARGET_DIR/Sources, by zipping sources and copying 
    sources_src = SOURCE_DIR / "Sources"
    sources_dest = TARGET_DIR / "Sources"
    sources_dest.mkdir(parents=True, exist_ok=True)

    zip_path = sources_dest / "sources.zip"
    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', sources_src)
    logger.info(f"Copied sources to {zip_path.relative_to(TARGET_DIR)}")
    # unzip sources in sources_dest
    shutil.unpack_archive(zip_path, sources_dest)
    logger.info(f"Unzipped sources to {sources_dest.relative_to(TARGET_DIR)}")
    return 

def main():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    pattern = "*.xlsx"
    excel_files = list(SOURCE_DIR.glob(pattern))

    if not excel_files:
        logger.warning("No Excel files found.")
        return

    logger.info(f"Found {len(excel_files)} Excel file(s) in {SOURCE_DIR}")

    for excel_file in excel_files:
        convert_excel_to_subfolder(excel_file, TARGET_DIR)

    logger.info("Conversion complete.")
    copy_scenario_data()
    copy_sources_file()


if __name__ == "__main__":
    main()