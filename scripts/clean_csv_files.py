import pandas as pd
from pathlib import Path
import shutil
import numpy as np


RELEVANT_COLUMNS = {
    "Sets": {
        "Nodes": None,                      # read_sets() → full sheet
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

def _unique_preserve_order(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def clean_input_data(src_folder: Path, clean_folder: Path, extra_folder: Path):
    """
    Copy CSVs from src_folder into clean_folder with only relevant columns.
    Save the removed columns in extra_folder.

    Special-case:
      - Splits 'Sets/Generators.csv' into one CSV per header column.
    """
    # Remove old output if exists
    if clean_folder.exists():
        shutil.rmtree(clean_folder)
    if extra_folder.exists():
        shutil.rmtree(extra_folder)

    for category, files in RELEVANT_COLUMNS.items():
        src_dir = src_folder / category
        clean_dir = clean_folder / category
        extra_dir = extra_folder / category

        clean_dir.mkdir(parents=True, exist_ok=True)
        extra_dir.mkdir(parents=True, exist_ok=True)

        for filename, usecols in files.items():
            csv_path = src_dir / f"{filename}.csv"
            if not csv_path.exists():
                print(f"⚠️ Skipping missing file: {csv_path}")
                continue
            # Special-case handling of Sets that contain multiple columns. These columns are split into separate files for pyomo. 
            if category == "Sets" and filename in ["Generators", "Storage"]:
                df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
                # Strip whitespace from string values
                df = df.map(lambda v: v.strip() if isinstance(v, str) else v)

                for col in df.columns:
                    series = df[col].replace("", pd.NA).dropna()
                    unique_vals = _unique_preserve_order(list(series))
                    out_df = pd.DataFrame({col: unique_vals})
                    out_path = clean_dir / f"{col}.csv"
                    out_df.to_csv(out_path, index=False)
                    print(f"✅ Split {csv_path.name} -> {out_path}")
                continue

            # Generic handling:
            df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
            # Trim whitespace for all string cells
            df = df.map(lambda v: v.strip() if isinstance(v, str) else v)

            if usecols is None:
                # keep whole sheet as-is (clean copy), no extras
                df.to_csv(clean_dir / f"{filename}.csv", index=False)
                # create empty extras file for structure parity
                (extra_dir / f"{filename}_extra.csv").touch()
                print(f"✅ Copied full sheet {category}/{filename}.csv")
                continue

            # use integer-location based selection (works in modern pandas)
            try:
                df_relevant = df.iloc[:, usecols]
            except Exception as exc:
                raise RuntimeError(f"Failed to select usecols={usecols} in {csv_path}: {exc}")

            # Determine column names that were kept
            relevant_cols = list(df_relevant.columns)

            # Extra columns are those not in relevant_cols
            extra_cols = [c for c in df.columns if c not in relevant_cols]
            df_extra = df[extra_cols] if extra_cols else pd.DataFrame()

            # Drop rows which are fully empty in the relevant columns (optional)
            # If you want to mirror previous behavior of dropna(), uncomment:
            # df_relevant = df_relevant.dropna(how='all')

            # Save cleaned data
            df_relevant.to_csv(clean_dir / f"{filename}.csv", index=False)

            # Save extra columns (if any)
            if not df_extra.empty:
                df_extra.to_csv(extra_dir / f"{filename}_extra.csv", index=False)
            else:
                # Create empty file to preserve structure
                (extra_dir / f"{filename}_extra.csv").touch()

            print(f"✅ Processed {category}/{filename}.csv (kept columns: {relevant_cols})")


# Example usage
if __name__ == "__main__":
    src = Path("input_data/test")
    clean = Path("input_data_clean/test")
    extra = Path("input_data_extra/test")

    clean_input_data(src, clean, extra)