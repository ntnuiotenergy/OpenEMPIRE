from pathlib import Path

import openpyxl
import pandas as pd

from Empire.input_client.excel_structure import sheets

class BaseClient:
    def _read_from_sheet(self, file_path: Path, sheet_name: str, **kwargs):
        return pd.read_excel(file_path, sheet_name=sheet_name, engine=self.engine, **kwargs)

    def _write_to_sheet(self, df: pd.DataFrame, file_path: Path, sheet_name: str, **kwargs):
        with pd.ExcelWriter(file_path, engine=self.engine, mode='a', if_sheet_exists="replace") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False, **kwargs)    

class SetsClient(BaseClient):
    def __init__(self, sets_path, engine: str = "openpyxl"):
        self.sets_path = sets_path
        self.engine = engine

    def get_nodes(self):
        return self._read_from_sheet(self.sets_path, "Nodes")

    def set_nodes(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.sets_path, "Nodes")

    def get_offshore_nodes(self):
        return self._read_from_sheet(self.sets_path, "OffshoreNodes")

    def set_offshore_nodes(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.sets_path, "OffshoreNodes")

    def get_technology(self):
        return self._read_from_sheet(self.sets_path, "Technology")

    def set_technology(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.sets_path, "Technology")

    def get_directional_lines(self):
        return self._read_from_sheet(self.sets_path, "DirectionalLines", skiprows=2)

    def set_directional_lines(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.sets_path, "DirectionalLines", startrow=2)


class GeneratorClient(BaseClient):
    def __init__(self, generator_path, engine: str = "openpyxl"):
        self.generator_path = generator_path
        self.engine = engine

    def get_captial_costs(self):
        return self._read_from_sheet(self.generator_path, "CapitalCosts", skiprows=2)

    def set_captial_costs(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "CapitalCosts", startrow=2)

    def get_fixed_om_costs(self):
        return self._read_from_sheet(self.generator_path, "FixedOMCosts", skiprows=2)

    def set_fixed_om_costs(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "FixedOMCosts", startrow=2)

    def get_variable_om_costs(self):
        return self._read_from_sheet(self.generator_path, "VariableOMCosts", skiprows=2)

    def set_variable_om_costs(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "VariableOMCosts", startrow=2)

    def get_fuel_costs(self):
        return self._read_from_sheet(self.generator_path, "FuelCosts", skiprows=2)

    def set_fuel_costs(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "FuelCosts", startrow=2)

    def get_efficiency(self):
        return self._read_from_sheet(self.generator_path, "Efficiency", skiprows=2)

    def set_efficiency(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "Efficiency", startrow=2)
    
    def get_ref_initial_capacity(self):
        return self._read_from_sheet(self.generator_path, "RefInitialCap", skiprows=2)

    def set_ref_initial_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "RefInitialCap", startrow=2)
    
    def get_scale_factor_initial_capacity(self):
        return self._read_from_sheet(self.generator_path, "ScaleFactorInitialCap", skiprows=2)

    def set_scale_factor_initial_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "ScaleFactorInitialCap", startrow=2)
    
    def get_max_built_capacity(self):
        return self._read_from_sheet(self.generator_path, "MaxBuiltCapacity", skiprows=2)

    def set_max_built_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "MaxBuiltCapacity", startrow=2)
    
    def get_max_installed_capacity(self):
        return self._read_from_sheet(self.generator_path, "MaxInstalledCapacity", skiprows=2, usecols=[0,1,2])

    def set_max_installed_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.generator_path, "MaxInstalledCapacity", startrow=2)

class NodeClient(BaseClient):
    def __init__(self, node_path, engine: str = "openpyxl"):
        self.node_path = node_path
        self.engine = engine

    def get_electric_annual_demand(self):
        return self._read_from_sheet(self.node_path, "ElectricAnnualDemand", skiprows=2, usecols=[0,1,2])

    def set_electric_annual_demand(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.node_path, "ElectricAnnualDemand", startrow=2)
    
    def get_node_lost_load_cost(self):
        return self._read_from_sheet(self.node_path, "NodeLostNodeCost", skiprows=2, usecols=[0,1,2])

    def set_node_lost_load_cost(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.node_path, "NodeLostNodeCost", startrow=2)

    def get_hydro_generators_max_annual_production(self):
        return self._read_from_sheet(self.node_path, "HydroGenMaxAnnualProduction", skiprows=2, usecols=[0,1])

    def set_hydro_generators_max_annual_production(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.node_path, "HydroGenMaxAnnualProduction", startrow=2)

class TransmissionClient(BaseClient):
    def __init__(self, transmission_path, engine: str = "openpyxl"):
        self.transmission_path = transmission_path
        self.engine = engine

    def get_line_efficiency(self):
        return self._read_from_sheet(self.transmission_path, "lineEfficiency", skiprows=2, usecols=[0,1,2])

    def set_line_efficiency(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "lineEfficiency", startrow=2)

    def get_max_built_capacity(self):
        return self._read_from_sheet(self.transmission_path, "MaxBuiltCapacity", skiprows=2, usecols=[0,1,2,3])

    def set_max_built_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "MaxBuiltCapacity", startrow=2)

    def get_length(self):
        return self._read_from_sheet(self.transmission_path, "Length", skiprows=2, usecols=[0,1,2])

    def set_length(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "Length", startrow=2)
    
    def get_type_capital_cost(self):
        return self._read_from_sheet(self.transmission_path, "TypeCapitalCost", skiprows=2, usecols=[0,1,2])

    def set_type_capital_cost(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "TypeCapitalCost", startrow=2)

    def get_type_fixed_om_cost(self):
        return self._read_from_sheet(self.transmission_path, "TypeFixedOMCost", skiprows=2, usecols=[0,1,2])

    def set_type_fixed_om_cost(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "TypeFixedOMCost", startrow=2)

    def get_initial_capacity(self):
        return self._read_from_sheet(self.transmission_path, "InitialCapacity", skiprows=2, usecols=[0,1,2,3])

    def set_initial_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "InitialCapacity", startrow=2)

    def get_max_install_capacity_raw(self):
        return self._read_from_sheet(self.transmission_path, "MaxInstallCapacityRaw", skiprows=2, usecols=[0,1,2,3])

    def set_max_install_capacity_raw(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "MaxInstallCapacityRaw", startrow=2)

    def get_lifetime(self):
        return self._read_from_sheet(self.transmission_path, "Lifetime", skiprows=2, usecols=[0,1,2])

    def set_lifetime(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "Lifetime", startrow=2)

class StorageClient(BaseClient):
    def __init__(self, storage_path, engine: str = "openpyxl"):
        self.storage_path = storage_path
        self.engine = engine

    def get_initial_power_capacity(self):
        return self._read_from_sheet(self.transmission_path, "InitialPowerCapacity", skiprows=2, usecols=[0,1,2,3])

    def set_initial_power_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "InitialPowerCapacity", startrow=2)

    def get_power_capital_cost(self):
        return self._read_from_sheet(self.transmission_path, "PowerCapitalCost", skiprows=2, usecols=[0,1,2])

    def set_power_capital_cost(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "PowerCapitalCost", startrow=2)

    def get_power_max_built_capacity(self):
        return self._read_from_sheet(self.transmission_path, "PowerMaxBuiltCapacity", skiprows=2, usecols=[0,1,2,3])

    def set_power_max_built_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "PowerMaxBuiltCapacity", startrow=2)

    def getEnergyCapitalCost(self):
        return self._read_from_sheet(self.transmission_path, "EnergyCapitalCost", skiprows=2, usecols=[0,1,2])

    def setEnergyCapitalCost(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "EnergyCapitalCost", startrow=2)

    def get_energy_initial_capacity(self):
        return self._read_from_sheet(self.transmission_path, "EnergyInitialCapacity", skiprows=2, usecols=[0,1,2,3])

    def set_energy_initial_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "EnergyInitialCapacity", startrow=2)

    def get_energy_max_built_capacity(self):
        return self._read_from_sheet(self.transmission_path, "EnergyMaxBuiltCapacity", skiprows=2, usecols=[0,1,2,3])

    def set_energy_max_built_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "EnergyMaxBuiltCapacity", startrow=2)

    def get_energy_max_installed_capacity(self):
        return self._read_from_sheet(self.transmission_path, "EnergyMaxInstalledCapacity", skiprows=2, usecols=[0,1,2])

    def set_energy_max_installed_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "EnergyMaxInstalledCapacity", startrow=2)

    def get_power_max_installed_capacity(self):
        return self._read_from_sheet(self.transmission_path, "PowerMaxInstalledCapacity", skiprows=2, usecols=[0,1,2])

    def set_power_max_installed_capacity(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "PowerMaxInstalledCapacity", startrow=2)

    def get_storage_initial_energy_level(self):
        return self._read_from_sheet(self.transmission_path, "StorageInitialEnergyLevel", skiprows=2, usecols=[0,1])

    def set_storage_initial_energy_level(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "StorageInitialEnergyLevel", startrow=2)

    def get_storage_charge_efficiency(self):
        return self._read_from_sheet(self.transmission_path, "StorageChargeEff", skiprows=2, usecols=[0,1])

    def set_storage_charge_efficiency(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "StorageChargeEff", startrow=2)

    def get_storage_discharge_efficiency(self):
        return self._read_from_sheet(self.transmission_path, "StorageDischargeEff", skiprows=2, usecols=[0,1])

    def set_storage_discharge_efficiency(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "StorageDischargeEff", startrow=2)

    def get_storage_power_to_energt(self):
        return self._read_from_sheet(self.transmission_path, "StoragePowToEnergy", skiprows=2, usecols=[0,1])

    def set_storage_power_to_energt(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "StoragePowToEnergy", startrow=2)

    def get_lifetime(self):
        return self._read_from_sheet(self.transmission_path, "Lifetime", skiprows=2, usecols=[0,1])

    def set_lifetime(self, df: pd.DataFrame):
        self._write_to_sheet(df, self.transmission_path, "Lifetime", startrow=2)

class EmpireInputClient(BaseClient):
    def __init__(self, dataset_path: Path, engine: str = "openpyxl"):
        self.dataset_path = dataset_path
        self.engine = engine
        self.sets = SetsClient(dataset_path / "Sets.xlsx")
        self.generator = GeneratorClient(dataset_path / "Generator.xlsx")
        self.nodes = NodeClient(dataset_path / "Node.xlsx")
        self.transmission = TransmissionClient(dataset_path / "Transmission.xlsx")
        self.storage = StorageClient(dataset_path / "Storage.xlsx")

        # self.validate()

    def validate(self):
        wbs = [
            ("Sets", self.sets_path), ("Generator", self.generators_path),
            ("Nodes", self.nodes_path), ("Transmission", self.transmission_path),
            ("Storages", self.storages_path)
        ]
        for name, paths in wbs:
            wb = openpyxl.load_workbook(paths)
            if wb.sheetnames != sheets[name]:
                raise ValueError(f"Sheetnames of {name} does not match {sheets[name]}") 


# Example usage:
if __name__ == "__main__":
    
    #%%
    
    dataset_path = Path.cwd() / "Data handler/europe_v51"
    client = EmpireInputClient(dataset_path)
    # client.get_nodes()
    
    # df = client.get_directional_lines()
    # client.set_directional_lines(df)

    df = client.generator.get_captial_costs()
    df = client.generator.get_max_installed_capacity()

    client.transmission.get_lifetime()
    

    