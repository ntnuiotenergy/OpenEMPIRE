from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseClientCSV:
    """Base class for CSV clients."""

    def __init__(self, folder: Path, sheet_columns: dict):
        self.folder = folder
        self.sheet_columns = sheet_columns
        if not folder.exists():
            raise FileNotFoundError(f"CSV folder {folder} does not exist.")

    def _read_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Read a CSV sheet with optional column selection."""
        file_path = self.folder / f"{sheet_name}.csv"
        usecols = self.sheet_columns.get(sheet_name, None)
        logger.info("Reading CSV: %s", file_path)
        df = pd.read_csv(file_path, usecols=usecols)
        df = df.replace(r"\s+", "", regex=True)
        return df

    def _write_sheet(self, df: pd.DataFrame, sheet_name: str):
        """Write DataFrame to CSV sheet."""
        file_path = self.folder / f"{sheet_name}.csv"
        logger.info("Writing CSV: %s", file_path)
        df.to_csv(file_path, index=False)

class SetsClient(BaseClientCSV):
    """Client for all Sets data in CSV format."""

    DEFAULT_SHEET_COLUMNS = {
        "Nodes": [0],
        "OffshoreNodes": [0],
        "Horizon": [0],
        "LineType": [0],
        "Technology": [0],
        "Storage": [0, 1],
        "Generators": [0, 1, 2, 3],
        "StorageOfNodes": [0, 1],
        "GeneratorsOfNode": [0, 1],
        "GeneratorsOfTechnology": [0, 1],
        "DirectionalLines": [0, 1],
        "LineTypeOfDirectionalLines": [0, 1, 2],
        "Coords": [0, 1, 2],
    }

    def __init__(self, folder: Path):
        super().__init__(folder, self.DEFAULT_SHEET_COLUMNS)

    # Nodes
    def get_nodes(self) -> pd.DataFrame:
        return self._read_sheet("Nodes")

    def set_nodes(self, df: pd.DataFrame):
        self._write_sheet(df, "Nodes")

    # Offshore nodes
    def get_offshore_nodes(self) -> pd.DataFrame:
        return self._read_sheet("OffshoreNodes")

    def set_offshore_nodes(self, df: pd.DataFrame):
        self._write_sheet(df, "OffshoreNodes")

    # Horizon
    def get_horizon(self) -> pd.DataFrame:
        return self._read_sheet("Horizon")

    def set_horizon(self, df: pd.DataFrame):
        self._write_sheet(df, "Horizon")

    # Storage
    def get_storage(self) -> pd.DataFrame:
        return self._read_sheet("Storage")

    def set_storage(self, df: pd.DataFrame):
        self._write_sheet(df, "Storage")

    # Technology
    def get_technology(self) -> pd.DataFrame:
        return self._read_sheet("Technology")

    def set_technology(self, df: pd.DataFrame):
        self._write_sheet(df, "Technology")

    # Generators
    def get_generators(self) -> pd.DataFrame:
        return self._read_sheet("Generators")

    def set_generators(self, df: pd.DataFrame):
        self._write_sheet(df, "Generators")

    # Line types
    def get_line_type(self) -> pd.DataFrame:
        return self._read_sheet("LineType")

    def set_line_type(self, df: pd.DataFrame):
        self._write_sheet(df, "LineType")

    # Storage of nodes
    def get_storage_of_nodes(self) -> pd.DataFrame:
        return self._read_sheet("StorageOfNodes")

    def set_storage_of_nodes(self, df: pd.DataFrame):
        self._write_sheet(df, "StorageOfNodes")

    # Directional lines
    def get_directional_lines(self) -> pd.DataFrame:
        return self._read_sheet("DirectionalLines")

    def set_directional_lines(self, df: pd.DataFrame):
        self._write_sheet(df, "DirectionalLines")

    # Line type of directional lines
    def get_line_type_of_directional_lines(self) -> pd.DataFrame:
        return self._read_sheet("LineTypeOfDirectionalLines")

    def set_line_type_of_directional_lines(self, df: pd.DataFrame):
        self._write_sheet(df, "LineTypeOfDirectionalLines")

    # Generators of node
    def get_generators_of_node(self) -> pd.DataFrame:
        return self._read_sheet("GeneratorsOfNode")

    def set_generators_of_node(self, df: pd.DataFrame):
        self._write_sheet(df, "GeneratorsOfNode")

    # Generators of technology
    def get_generators_of_technology(self) -> pd.DataFrame:
        return self._read_sheet("GeneratorsOfTechnology")

    def set_generators_of_technology(self, df: pd.DataFrame):
        self._write_sheet(df, "GeneratorsOfTechnology")

    # Coordinates
    def get_coordinates(self) -> pd.DataFrame:
        return self._read_sheet("Coords")

    def set_coordinates(self, df: pd.DataFrame):
        self._write_sheet(df, "Coords")


class GeneratorClient(BaseClientCSV):
    """Client for all Generator data in CSV format."""

    DEFAULT_SHEET_COLUMNS = {
        "CapitalCosts": [0, 1, 2],
        "FixedOMCosts": [0, 1, 2],
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
    }

    def __init__(self, folder: Path):
        super().__init__(folder, self.DEFAULT_SHEET_COLUMNS)

    # Capital Costs
    def get_capital_costs(self) -> pd.DataFrame:
        return self._read_sheet("CapitalCosts")

    def set_capital_costs(self, df: pd.DataFrame):
        self._write_sheet(df, "CapitalCosts")

    # Fixed O&M Costs
    def get_fixed_om_costs(self) -> pd.DataFrame:
        return self._read_sheet("FixedOMCosts")

    def set_fixed_om_costs(self, df: pd.DataFrame):
        self._write_sheet(df, "FixedOMCosts")

    # Variable O&M Costs
    def get_variable_om_costs(self) -> pd.DataFrame:
        return self._read_sheet("VariableOMCosts")

    def set_variable_om_costs(self, df: pd.DataFrame):
        self._write_sheet(df, "VariableOMCosts")

    # Fuel Costs
    def get_fuel_costs(self) -> pd.DataFrame:
        return self._read_sheet("FuelCosts")

    def set_fuel_costs(self, df: pd.DataFrame):
        self._write_sheet(df, "FuelCosts")

    # CCS Cost TS Variable
    def get_ccs_cost_ts_variable(self) -> pd.DataFrame:
        return self._read_sheet("CCSCostTSVariable")

    def set_ccs_cost_ts_variable(self, df: pd.DataFrame):
        self._write_sheet(df, "CCSCostTSVariable")

    # Efficiency
    def get_efficiency(self) -> pd.DataFrame:
        return self._read_sheet("Efficiency")

    def set_efficiency(self, df: pd.DataFrame):
        self._write_sheet(df, "Efficiency")

    # Reference Initial Capacity
    def get_ref_initial_capacity(self) -> pd.DataFrame:
        return self._read_sheet("RefInitialCap")

    def set_ref_initial_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "RefInitialCap")

    # Scale Factor Initial Capacity
    def get_scale_factor_initial_capacity(self) -> pd.DataFrame:
        return self._read_sheet("ScaleFactorInitialCap")

    def set_scale_factor_initial_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "ScaleFactorInitialCap")

    # Initial Capacity
    def get_initial_capacity(self) -> pd.DataFrame:
        return self._read_sheet("InitialCapacity")

    def set_initial_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "InitialCapacity")

    # Max Built Capacity
    def get_max_built_capacity(self) -> pd.DataFrame:
        return self._read_sheet("MaxBuiltCapacity")

    def set_max_built_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "MaxBuiltCapacity")

    # Max Installed Capacity
    def get_max_installed_capacity(self) -> pd.DataFrame:
        return self._read_sheet("MaxInstalledCapacity")

    def set_max_installed_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "MaxInstalledCapacity")

    # Ramp Rate
    def get_ramp_rate(self) -> pd.DataFrame:
        return self._read_sheet("RampRate")

    def set_ramp_rate(self, df: pd.DataFrame):
        self._write_sheet(df, "RampRate")

    # Generator Type Availability
    def get_generator_type_availability(self) -> pd.DataFrame:
        return self._read_sheet("GeneratorTypeAvailability")

    def set_generator_type_availability(self, df: pd.DataFrame):
        self._write_sheet(df, "GeneratorTypeAvailability")

    # CO2 Content
    def get_co2_content(self) -> pd.DataFrame:
        return self._read_sheet("CO2Content")

    def set_co2_content(self, df: pd.DataFrame):
        self._write_sheet(df, "CO2Content")

    # Lifetime
    def get_lifetime(self) -> pd.DataFrame:
        return self._read_sheet("Lifetime")

    def set_lifetime(self, df: pd.DataFrame):
        self._write_sheet(df, "Lifetime")

class NodeClient(BaseClientCSV):
    """Client for all Node data in CSV format."""

    DEFAULT_SHEET_COLUMNS = {
        "ElectricAnnualDemand": [0, 1, 2],
        "NodeLostLoadCost": [0, 1, 2],
        "HydroGenMaxAnnualProduction": [0, 1],
    }

    def __init__(self, folder: Path):
        super().__init__(folder, self.DEFAULT_SHEET_COLUMNS)

    # Electric Annual Demand
    def get_electric_annual_demand(self) -> pd.DataFrame:
        return self._read_sheet("ElectricAnnualDemand")

    def set_electric_annual_demand(self, df: pd.DataFrame):
        self._write_sheet(df, "ElectricAnnualDemand")

    # Node Lost Load Cost
    def get_node_lost_load_cost(self) -> pd.DataFrame:
        return self._read_sheet("NodeLostLoadCost")

    def set_node_lost_load_cost(self, df: pd.DataFrame):
        self._write_sheet(df, "NodeLostLoadCost")

    # Hydro Generators Max Annual Production
    def get_hydro_generators_max_annual_production(self) -> pd.DataFrame:
        return self._read_sheet("HydroGenMaxAnnualProduction")

    def set_hydro_generators_max_annual_production(self, df: pd.DataFrame):
        self._write_sheet(df, "HydroGenMaxAnnualProduction")

class TransmissionClient(BaseClientCSV):
    """Client for all Transmission data in CSV format."""

    DEFAULT_SHEET_COLUMNS = {
        "lineEfficiency": [0, 1, 2],
        "MaxInstallCapacityRaw": [0, 1, 2, 3],
        "MaxBuiltCapacity": [0, 1, 2, 3],
        "Length": [0, 1, 2],
        "TypeCapitalCost": [0, 1, 2],
        "TypeFixedOMCost": [0, 1, 2],
        "InitialCapacity": [0, 1, 2, 3],
        "Lifetime": [0, 1, 2],
    }

    def __init__(self, folder: Path):
        super().__init__(folder, self.DEFAULT_SHEET_COLUMNS)

    # Line efficiency
    def get_line_efficiency(self) -> pd.DataFrame:
        return self._read_sheet("lineEfficiency")

    def set_line_efficiency(self, df: pd.DataFrame):
        self._write_sheet(df, "lineEfficiency")

    # Max built capacity
    def get_max_built_capacity(self) -> pd.DataFrame:
        return self._read_sheet("MaxBuiltCapacity")

    def set_max_built_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "MaxBuiltCapacity")

    # Length
    def get_length(self) -> pd.DataFrame:
        return self._read_sheet("Length")

    def set_length(self, df: pd.DataFrame):
        self._write_sheet(df, "Length")

    # Type capital cost
    def get_type_capital_cost(self) -> pd.DataFrame:
        return self._read_sheet("TypeCapitalCost")

    def set_type_capital_cost(self, df: pd.DataFrame):
        df = self._order_type_and_period(df)
        self._write_sheet(df, "TypeCapitalCost")

    # Type fixed O&M cost
    def get_type_fixed_om_cost(self) -> pd.DataFrame:
        return self._read_sheet("TypeFixedOMCost")

    def set_type_fixed_om_cost(self, df: pd.DataFrame):
        df = self._order_type_and_period(df)
        self._write_sheet(df, "TypeFixedOMCost")

    # Initial capacity
    def get_initial_capacity(self) -> pd.DataFrame:
        return self._read_sheet("InitialCapacity")

    def set_initial_capacity(self, df: pd.DataFrame):
        self._write_sheet(df, "InitialCapacity")

    # Max install capacity raw
    def get_max_install_capacity_raw(self) -> pd.DataFrame:
        return self._read_sheet("MaxInstallCapacityRaw")

    def set_max_install_capacity_raw(self, df: pd.DataFrame):
        self._write_sheet(df, "MaxInstallCapacityRaw")

    # Lifetime
    def get_lifetime(self) -> pd.DataFrame:
        return self._read_sheet("Lifetime")

    def set_lifetime(self, df: pd.DataFrame):
        self._write_sheet(df, "Lifetime")

    # Helper to fix column order
    @staticmethod
    def _order_type_and_period(df: pd.DataFrame) -> pd.DataFrame:
        """Ensure 'Type' and 'Period' columns are first."""
        cols = ["Type", "Period"]
        if set(cols).issubset(set(df.columns)) and df.columns[0] != "Type":
            return df[cols + list(set(df.columns).difference(set(cols)))]
        return df


class StorageClient(BaseClientCSV):
    """Client for storage data in CSV format."""

    DEFAULT_SHEET_COLUMNS = {
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
        "StorageInitialEnergyLevel": [0, 1],
        "StorageChargeEff": [0, 1],
        "StorageDischargeEff": [0, 1],
        "StoragePowToEnergy": [0, 1],
        "StorageBleedEfficiency": [0, 1],
        "Lifetime": [0, 1],
    }

    def __init__(self, folder: Path):
        super().__init__(folder, self.DEFAULT_SHEET_COLUMNS)

    # Power
    def get_initial_power_capacity(self): return self._read_sheet("InitialPowerCapacity")
    def set_initial_power_capacity(self, df): self._write_sheet(df, "InitialPowerCapacity")

    def get_power_capital_cost(self): return self._read_sheet("PowerCapitalCost")
    def set_power_capital_cost(self, df): self._write_sheet(df, "PowerCapitalCost")

    def get_power_fixed_om_cost(self): return self._read_sheet("PowerFixedOMCost")
    def set_power_fixed_om_cost(self, df): self._write_sheet(df, "PowerFixedOMCost")

    def get_power_max_built_capacity(self): return self._read_sheet("PowerMaxBuiltCapacity")
    def set_power_max_built_capacity(self, df): self._write_sheet(df, "PowerMaxBuiltCapacity")

    def get_power_max_installed_capacity(self): return self._read_sheet("PowerMaxInstalledCapacity")
    def set_power_max_installed_capacity(self, df): self._write_sheet(df, "PowerMaxInstalledCapacity")

    # Energy
    def get_energy_capital_cost(self): return self._read_sheet("EnergyCapitalCost")
    def set_energy_capital_cost(self, df): self._write_sheet(df, "EnergyCapitalCost")

    def get_energy_fixed_om_cost(self): return self._read_sheet("EnergyFixedOMCost")
    def set_energy_fixed_om_cost(self, df): self._write_sheet(df, "EnergyFixedOMCost")

    def get_initial_energy_capacity(self): return self._read_sheet("EnergyInitialCapacity")
    def set_initial_energy_capacity(self, df): self._write_sheet(df, "EnergyInitialCapacity")

    def get_energy_max_built_capacity(self): return self._read_sheet("EnergyMaxBuiltCapacity")
    def set_energy_max_built_capacity(self, df): self._write_sheet(df, "EnergyMaxBuiltCapacity")

    def get_energy_max_installed_capacity(self): return self._read_sheet("EnergyMaxInstalledCapacity")
    def set_energy_max_installed_capacity(self, df): self._write_sheet(df, "EnergyMaxInstalledCapacity")

    # Storage efficiencies
    def get_storage_initial_energy_level(self): return self._read_sheet("StorageInitialEnergyLevel")
    def set_storage_initial_energy_level(self, df): self._write_sheet(df, "StorageInitialEnergyLevel")

    def get_storage_charge_efficiency(self): return self._read_sheet("StorageChargeEff")
    def set_storage_charge_efficiency(self, df): self._write_sheet(df, "StorageChargeEff")

    def get_storage_discharge_efficiency(self): return self._read_sheet("StorageDischargeEff")
    def set_storage_discharge_efficiency(self, df): self._write_sheet(df, "StorageDischargeEff")

    def get_storage_power_to_energy(self): return self._read_sheet("StoragePowToEnergy")
    def set_storage_power_to_energy(self, df): self._write_sheet(df, "StoragePowToEnergy")

    def get_storage_bleed_efficiency(self): return self._read_sheet("StorageBleedEfficiency")
    def set_storage_bleed_efficiency(self, df): self._write_sheet(df, "StorageBleedEfficiency")

    # Lifetime
    def get_lifetime(self): return self._read_sheet("Lifetime")
    def set_lifetime(self, df): self._write_sheet(df, "Lifetime")

class GeneralClient(BaseClientCSV):
    """Client for general data in CSV format."""

    DEFAULT_SHEET_COLUMNS = {
        "seasonScale": [0, 1],
        "CO2Cap": [0, 1],
        "CO2Price": [0, 1],
    }

    def __init__(self, folder: Path):
        super().__init__(folder, self.DEFAULT_SHEET_COLUMNS)

    def get_season_scale(self): return self._read_sheet("seasonScale")
    def set_season_scale(self, df): self._write_sheet(df, "seasonScale")

    def get_co2_cap(self): return self._read_sheet("CO2Cap")
    def set_co2_cap(self, df): self._write_sheet(df, "CO2Cap")

    def get_co2_price(self): return self._read_sheet("CO2Price")
    def set_co2_price(self, df): self._write_sheet(df, "CO2Price")

class EmpireInputClient:
    """Unified interface for CSV-based Empire inputs."""

    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path

        self.sets = SetsClient(dataset_path / "Sets")
        self.generator = GeneratorClient(dataset_path / "Generator")
        self.nodes = NodeClient(dataset_path / "Node")
        self.transmission = TransmissionClient(dataset_path / "Transmission")
        self.storage = StorageClient(dataset_path / "Storage")
        self.general = GeneralClient(dataset_path / "General")