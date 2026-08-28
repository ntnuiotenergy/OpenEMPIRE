import os
import logging
import shutil
import argparse
import pandas as pd
from pathlib import Path

# --------------------------------------------------------------------------------------
# Argument Parsing
# --------------------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Convert and clean Data Handler dataset.")
parser.add_argument(
    "-d",
    "--dataset",
    type=str,
    required=False,
    default="europe_v51",
    help="Dataset name under Data Handler/ to process."
)
args = parser.parse_args()
DATASET = args.dataset

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------

SOURCE_DIR = Path(f"Data Handler/{DATASET}")
INTERMEDIATE_DIR = Path(f"input_data_intermediate/{DATASET}")
CLEAN_DIR = Path(f"input_data/{DATASET}")
EXTRA_DIR = Path(f"input_data_extra/{DATASET}")

FILE_SUFFIX = ".csv"
ENCODING = "utf-8"

# skiprows per sheet
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

# columns to retain
RELEVANT_COLUMNS = {
    "Sets": {
        "Nodes": None,
        "OffshoreNodes": None,
        "Horizon": None,
        "LineType": None,
        "Technology": None,
        "Storage": None,
        "Generators": None,
        "StorageOfNodes": [0, 1],
        "GeneratorsOfNode": [0, 1],
        "GeneratorsOfTechnology": [0, 1],
        "DirectionalLines": [0, 1],
        "LineTypeOfDirectionalLines": [0, 1, 2],
    },
    "Generator": {
        "FixedOMCosts": [0, 1, 2],
        "CapitalCosts": [0, 1, 2],
        "VariableOMCosts": [0, 1],
        "FuelCosts": [0, 1, 2],
        "CCSCostTSVariable": [0, 1],
        "Efficiency": [0, 1, 2],
        "RefInitialCap": [0, 1, 2],
        "ScaleFactorInitialCap": [0, 1, 2],
        "InitialCapacity": [0, 1, 2, 3],
        "MaxBuiltCapacity": [0, 1, 2, 3],
        "MaxInstalledCapacity": [0, 1, 2],
        "RampRate": [0, 1],
        "GeneratorTypeAvailability": [0, 1],
        "CO2Content": [0, 1],
        "Lifetime": [0, 1],
    },
    "Transmission": {
        "lineEfficiency": [0, 1, 2],
        "MaxInstallCapacityRaw": [0, 1, 2, 3],
        "MaxBuiltCapacity": [0, 1, 2, 3],
        "Length": [0, 1, 2],
        "TypeCapitalCost": [0, 1, 2],
        "TypeFixedOMCost": [0, 1, 2],
        "InitialCapacity": [0, 1, 2, 3],
        "Lifetime": [0, 1, 2],
    },
    "Node": {
        "ElectricAnnualDemand": [0, 1, 2],
        "NodeLostLoadCost": [0, 1, 2],
        "HydroGenMaxAnnualProduction": [0, 1],
    },
    "General": {
        "seasonScale": [0, 1],
        "CO2Cap": [0, 1],
        "CO2Price": [0, 1],
    },
    "Storage": {
        "StorageBleedEfficiency": [0, 1],
        "StorageChargeEff": [0, 1],
        "StorageDischargeEff": [0, 1],
        "StoragePowToEnergy": [0, 1],
        "StorageInitialEnergyLevel": [0, 1],
        "InitialPowerCapacity": [0, 1, 2, 3],
        "PowerCapitalCost": [0, 1, 2],
        "PowerFixedOMCost": [0, 1, 2],
        "PowerMaxBuiltCapacity": [0, 1, 2, 3],
        "EnergyCapitalCost": [0, 1, 2],
        "EnergyFixedOMCost": [0, 1, 2],
        "EnergyInitialCapacity": [0, 1, 2, 3],
        "EnergyMaxBuiltCapacity": [0, 1, 2, 3],
        "EnergyMaxInstalledCapacity": [0, 1, 2],
        "PowerMaxInstalledCapacity": [0, 1, 2],
        "Lifetime": [0, 1],
    },
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------
# Excel Conversion
# --------------------------------------------------------------------------------------

def read_excel_with_header(excel: pd.ExcelFile, sheet: str, skiprows: int) -> pd.DataFrame:
    df = excel.parse(sheet, header=skiprows)
    df = df.dropna(how="all")
    df = df.replace(r"\s+", "", regex=True)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.replace(r"^Unnamed.*", "", regex=True)
    )
    df = df.loc[:, (df.columns != "")]
    return df


def convert_excel_to_subfolder(excel_path: Path, target_root: Path):
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
        skiprows = config.get(sheet, 0)
        try:
            df = read_excel_with_header(excel, sheet, skiprows)
            if df.empty:
                continue
            df.to_csv(subfolder / f"{sheet.replace(' ', '_')}{FILE_SUFFIX}", index=False, encoding=ENCODING)
        except Exception as e:
            logger.error(f"Error converting {excel_path.name} [{sheet}]: {e}")


def copy_scenario_data():
    src = SOURCE_DIR / "ScenarioData"
    dst = CLEAN_DIR / "ScenarioData"
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.csv"):
        pd.read_csv(f).to_csv(dst / f.name, index=False, encoding=ENCODING)
    logger.info("Copied ScenarioData.")


def copy_sources_file():
    src = SOURCE_DIR / "Sources"
    dst = CLEAN_DIR / "Sources"
    dst.mkdir(parents=True, exist_ok=True)
    zip_path = dst / "sources.zip"
    shutil.make_archive(str(zip_path.with_suffix('')), 'zip', src)
    shutil.unpack_archive(zip_path, dst)
    logger.info("Copied and unpacked Sources.")

# --------------------------------------------------------------------------------------
# Cleaning Phase
# --------------------------------------------------------------------------------------

def _unique_preserve_order(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def clean_input_data(src_folder: Path, clean_folder: Path, extra_folder: Path):
    if clean_folder.exists():
        shutil.rmtree(clean_folder)
    if extra_folder.exists():
        shutil.rmtree(extra_folder)

    for category, files in RELEVANT_COLUMNS.items():
        src_dir = src_folder / category
        if not src_dir.exists():
            continue
        clean_dir = clean_folder / category
        extra_dir = extra_folder / category
        clean_dir.mkdir(parents=True, exist_ok=True)
        extra_dir.mkdir(parents=True, exist_ok=True)

        for filename, usecols in files.items():
            csv_path = src_dir / f"{filename}.csv"
            if not csv_path.exists():
                continue

            # special-case: split Sets/Generators and Sets/Storage
            if category == "Sets" and filename in ["Generators", "Storage"]:
                df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
                df = df.map(lambda v: v.strip() if isinstance(v, str) else v)
                for col in df.columns:
                    vals = df[col].replace("", pd.NA).dropna()
                    if not vals.empty:
                        unique_vals = _unique_preserve_order(list(vals))
                        pd.DataFrame({col: unique_vals}).to_csv(
                            clean_dir / f"{col}.csv", index=False
                        )
                continue

            df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
            df = df.map(lambda v: v.strip() if isinstance(v, str) else v)

            if usecols is None:
                df.to_csv(clean_dir / f"{filename}.csv", index=False)
                # No need to create empty extra file
                continue

            df_relevant = df.iloc[:, usecols]
            df_relevant.to_csv(clean_dir / f"{filename}.csv", index=False)

            extra_cols = [c for c in df.columns if c not in df_relevant.columns]
            if extra_cols:
                df_extra = df[extra_cols].dropna(how="all")
                if not df_extra.empty:
                    df_extra.to_csv(extra_dir / f"{filename}_extra.csv", index=False)




filename_dict = {
    "Sets": {
        "Generator": "Generator.csv",
        "ThermalGenerators": "ThermalGenerators.csv",
        "HydroGenerator": "HydroGenerator.csv",
        "RegHydroGenerator": "HydroGeneratorWithReservoir.csv",
        "Storage": "Storage.csv",
        "DependentStorage": "DependentStorage.csv",
        "Technology": "Technology.csv",
        "Node": "Nodes.csv",
        "Period": "Horizon.csv",
        "DirectionalLink": "DirectionalLines.csv",
        "TransmissionType": "LineType.csv",
        "TransmissionTypeOfDirectionalLink": "LineTypeOfDirectionalLines.csv",
        "GeneratorsOfTechnology": "GeneratorsOfTechnology.csv",
        "GeneratorsOfNode": "GeneratorsOfNode.csv",
        "StoragesOfNode": "StorageOfNodes.csv",
        "OffshoreNode": "OffshoreNodes.csv"
    },
    "Generator": {
        "genCapitalCost": "CapitalCosts.csv",
        "genFixedOMCost": "FixedOMCosts.csv",
        "genVariableOMCost": "VariableOMCosts.csv",
        "genFuelCost": "FuelCosts.csv",
        "CCSCostTSVariable": "CCSCostTSVariable.csv",
        "genEfficiency": "Efficiency.csv",
        "genRefInitCap": "RefInitialCap.csv",
        "genScaleInitCap": "ScaleFactorInitialCap.csv",
        "genInitCap": "InitialCapacity.csv",
        "genMaxBuiltCap": "MaxBuiltCapacity.csv",
        "genMaxInstalledCapRaw": "MaxInstalledCapacity.csv",
        "genRampUpCap": "RampRate.csv",
        "genCapAvailTypeRaw": "GeneratorTypeAvailability.csv",
        "genCO2TypeFactor": "CO2Content.csv",
        "genLifetime": "Lifetime.csv",
    },

    "Transmission": {
        "transmissionInitCap": "InitialCapacity.csv",
        "transmissionMaxBuiltCap": "MaxBuiltCapacity.csv",
        "transmissionMaxInstalledCapRaw": "MaxInstallCapacityRaw.csv",
        "transmissionLength": "Length.csv",
        "transmissionTypeCapitalCost": "TypeCapitalCost.csv",
        "transmissionTypeFixedOMCost": "TypeFixedOMCost.csv",
        "lineEfficiency": "lineEfficiency.csv",
        "transmissionLifetime": "Lifetime.csv",
    },

    "Storage": {
        "storageBleedEff": "StorageBleedEfficiency.csv",
        "storageChargeEff": "StorageChargeEff.csv",
        "storageDischargeEff": "StorageDischargeEff.csv",
        "storagePowToEnergy": "StoragePowToEnergy.csv",
        "storENCapitalCost": "EnergyCapitalCost.csv",
        "storENFixedOMCost": "EnergyFixedOMCost.csv",
        "storENInitCap": "EnergyInitialCapacity.csv",
        "storENMaxBuiltCap": "EnergyMaxBuiltCapacity.csv",
        "storENMaxInstalledCapRaw": "EnergyMaxInstalledCapacity.csv",
        "storOperationalInit": "StorageInitialEnergyLevel.csv",
        "storPWCapitalCost": "PowerCapitalCost.csv",
        "storPWFixedOMCost": "PowerFixedOMCost.csv",
        "storPWInitCap": "InitialPowerCapacity.csv",
        "storPWMaxBuiltCap": "PowerMaxBuiltCapacity.csv",   
        "storPWMaxInstalledCapRaw": "PowerMaxInstalledCapacity.csv",
        "storageLifetime": "Lifetime.csv",
    },
    "Node": {
        "nodeLostLoadCost": "NodeLostLoadCost.csv",
        "sloadAnnualDemand": "ElectricAnnualDemand.csv",
        "maxHydroNode": "HydroGenMaxAnnualProduction.csv",
    },
    "General": {
        "seasScale": "seasonScale.csv",
        "CO2cap": "CO2Cap.csv",
        "CO2price": "CO2Price.csv",
    },
}

def convert_csv_filenames(root_path: Path):
    for component, fn_dict in filename_dict.items():
        for var_name, file_name in fn_dict.items():
            src_path = root_path / component / file_name
            if src_path.exists():
                dst_path = root_path / component / f"{var_name}.csv"
                src_path.rename(dst_path)
            else:
                logger.warning(f"Expected file {src_path} not found.")
# --------------------------------------------------------------------------------------
# Main Pipeline
# --------------------------------------------------------------------------------------

def main():
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)

    excel_files = list(SOURCE_DIR.glob("*.xlsx"))
    if not excel_files:
        logger.warning(f"No Excel files found in {SOURCE_DIR}")
        return

    logger.info(f"Converting {len(excel_files)} Excel files...")
    for f in excel_files:
        convert_excel_to_subfolder(f, INTERMEDIATE_DIR)



    logger.info("Starting cleaning step...")
    clean_input_data(INTERMEDIATE_DIR, CLEAN_DIR, EXTRA_DIR)
    copy_scenario_data()
    copy_sources_file()
    shutil.rmtree("input_data_intermediate")     # remove intermediate folder
    # remove the intermediate folder itself, not only the contents
    convert_csv_filenames(CLEAN_DIR)


    logger.info("All steps complete.")
if __name__ == "__main__":
    main()