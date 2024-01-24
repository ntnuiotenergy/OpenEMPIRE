import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from empire.input_client.client import EmpireInputClient
from empire.utils import scale_and_shift_series

logger = logging.getLogger(__name__)


class IDataManager(ABC):
    @abstractmethod
    def apply(self):
        pass


class AvailabilityManager(IDataManager):
    """
    Manager responsible for updating the availability/capacity factor for specific generator technologies within a
    given dataset.
    """

    def __init__(
        self,
        client: EmpireInputClient,
        generator_technology: str,
        availability: float,
    ) -> None:
        """
        Initializes the AvailabilityManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param generator_technology: The specific generator technology to be updated.
        :param availability: The new availability value to be set for the specified generator technology.
        """
        self.client = client
        self.generator_technology = generator_technology
        self.availability = availability
        self.validate()

    def validate(self) -> None:
        if self.availability < 0.0 or self.availability > 1.0:
            raise ValueError("availability has to be in range [0,1]")

    def apply(self) -> None:
        df_availability = self.client.generator.get_generator_type_availability()

        condition = df_availability["Generator"].isin([self.generator_technology])

        if not condition.any():
            raise ValueError(f"No rows found for technology {self.generator_technology}.")

        df_availability.loc[condition, "GeneratorTypeAvailability"] = self.availability

        logger.info(f"Setting availability to {self.availability} for {self.generator_technology}.")
        self.client.generator.set_generator_type_availability(df_availability)


class CapitalCostManager(IDataManager):
    """
    Manager responsible for updating the capital cost for specific generator technologies within a  given dataset.
    """

    def __init__(self, client: EmpireInputClient, generator_technology: str, capital_cost: float) -> None:
        """
        Initializes the CapitalCostManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param generator_technology: The specific generator technology to be updated.
        :param capital_cost: The new capital cost value to be set for the specified generator technology.
        """
        self.client = client
        self.generator_technology = generator_technology
        self.capital_cost = capital_cost

    def apply(self) -> None:
        df_capital_costs = self.client.generator.get_capital_costs()
        df_capital_costs.loc[
            df_capital_costs["GeneratorTechnology"] == self.generator_technology,
            "generatorCapitalCost in euro per kW",
        ] = self.capital_cost

        logger.info(f"Setting capital cost to {self.capital_cost} for {self.generator_technology}.")
        self.client.generator.set_capital_costs(df_capital_costs)


class FuelCostManager(IDataManager):
    """
    Manager responsible for updating the fuel cost for specific generator technologies within a  given dataset.
    """

    def __init__(self, client: EmpireInputClient, generator_technology: str, fuel_cost: float) -> None:
        """
        Initializes the FuelCostManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param generator_technology: The specific generator technology to be updated.
        :param fuel_cost: The new fuel cost value to be set for the specified generator technology in EUR/GJ.
        """
        self.client = client
        self.generator_technology = generator_technology
        self.fuel_cost = fuel_cost

    def apply(self) -> None:
        df_fuel_costs = self.client.generator.get_fuel_costs()
        df_fuel_costs.loc[
            df_fuel_costs["GeneratorTechnology"] == self.generator_technology,
            "generatorTypeFuelCost in euro per GJ",
        ] = self.fuel_cost

        logger.info(f"Setting fuel cost to {self.capital_cost} for {self.generator_technology}.")
        self.client.generator.set_fuel_costs(df_fuel_costs)


class CO2PricetManager(IDataManager):
    """
    Manager responsible for updating the CO2 price within a  given dataset.
    """

    def __init__(self, client: EmpireInputClient, periods: list[int], co2_prices: list[float]) -> None:
        """
        Initializes the CO2PricetManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param periods: The periods to set the co2 price for.
        :param co2_prices: The new co2 prices to be set for the specified periods in EUR/tCO2.
        """
        self.client = client
        self.periods = periods
        self.co2_prices = co2_prices

        if len(periods) != len(co2_prices):
            raise ValueError("Length of 'periods' have to match 'co2_prices'.")

    def apply(self) -> None:
        df_co2_price = self.client.general.get_co2_price()

        for p, c in zip(self.periods, self.co2_prices):
            df_co2_price.loc[
                df_co2_price["Period"] == p,
                "CO2price in euro per tCO2",
            ] = c

        logger.info(f"Setting CO2 price to {self.co2_prices} for the periods {self.periods}.")
        self.client.general.set_co2_price(df_co2_price)


class FixedOMCostManager(IDataManager):
    """
    Manager responsible for updating the fixed o&m cost for specific generator technologies within a  given dataset.
    """

    def __init__(self, client: EmpireInputClient, generator_technology: str, fixed_om_cost: float) -> None:
        """
        Initializes the FixedOMCostManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param generator_technology: The specific generator technology to be updated.
        :param fixed_om_cost: The new capital cost value to be set for the specified generator technology.
        """
        self.client = client
        self.generator_technology = generator_technology
        self.fixed_om_cost = fixed_om_cost

    def apply(self) -> None:
        df_fixed_om_costs = self.client.generator.get_fixed_om_costs()

        y = "generatorFixedOMCost in euro per kW"
        if y not in df_fixed_om_costs.columns:  # NB: Bug in excel sheet
            y = "generatorCapitalCost in euro per kW"

        df_fixed_om_costs.loc[
            df_fixed_om_costs["GeneratorTechnology"] == self.generator_technology,
            y,
        ] = self.fixed_om_cost

        logger.info(f"Setting fixed o&m cost to {self.fixed_om_cost} for {self.generator_technology}.")
        self.client.generator.set_fixed_om_costs(df_fixed_om_costs)


class MaxInstalledCapacityManager(IDataManager):
    """
    Manager responsible for updating the maximum installed capacities for specific generator technologies within a
    given dataset.
    """

    def __init__(
        self,
        client: EmpireInputClient,
        generator_technology: str,
        nodes: list[str],
        max_installed_capacity: float,
    ) -> None:
        """
        Initializes the MaxInstalledCapacityManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param generator_technology: The specific generator technology to be updated.
        :param nodes: List of node names where the generator technology is applied.
        :param max_installed_capacity: The new maximum installed capacity value to be set for the specified generator technology.
        """
        self.client = client
        self.generator_technology = generator_technology
        self.nodes = nodes
        self.max_installed_capacity = max_installed_capacity

    def apply(self) -> None:
        df_max_installed = self.client.generator.get_max_installed_capacity()

        condition = df_max_installed["Node"].isin(self.nodes) & df_max_installed["GeneratorTechnology"].isin(
            [self.generator_technology]
        )

        if not condition.any():
            raise ValueError(f"No rows found for nodes {self.nodes} and technology {self.generator_technology}.")

        df_max_installed.loc[condition, "generatorMaxInstallCapacity  in MW"] = self.max_installed_capacity

        logger.info(
            f"Setting max installed capacity to {self.max_installed_capacity} for {self.generator_technology} in nodes {self.nodes}."
        )
        self.client.generator.set_max_installed_capacity(df_max_installed)


class MaxTransmissionCapacityManager(IDataManager):
    """
    Manager responsible for updating the maximum installed transmission capacity.
    """

    def __init__(
        self,
        client: EmpireInputClient,
        from_node: str,
        to_node: str,
        max_installed_capacity: float,
    ) -> None:
        """
        Initializes the MaxTransmissionCapacityManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param from_node: From node.
        :param to_node: To node.
        :param max_installed_capacity: The new maximum installed capacity value.
        """
        self.client = client
        self.from_node = from_node
        self.to_node = to_node
        self.max_installed_capacity = max_installed_capacity

    def apply(self) -> None:
        df_max_installed = self.client.transmission.get_max_install_capacity_raw()

        condition = df_max_installed["InterconnectorLinks"].isin([self.from_node]) & df_max_installed["ToNode"].isin(
            [self.to_node]
        )

        if not condition.any():
            raise ValueError(f"No transmissoion connection found between {self.from_node} and {self.to_node}.")

        df_max_installed.loc[condition, "MaxRawNotAdjustWithInitCap in MW"] = self.max_installed_capacity

        logger.info(
            f"Setting transmission capacity between {self.from_node} and {self.to_node} to {self.max_installed_capacity}"
        )
        self.client.transmission.set_max_install_capacity_raw(df_max_installed)


class ElectricLoadManager(IDataManager):
    """
    Manager responsible for adjusting the electric load.
    """

    def __init__(
        self,
        client: EmpireInputClient,
        scenario_data_path: Path,
        node: str,
        scale: float,
        shift: float,
        datetime_format: str = "%d/%m/%Y %H:%M",
    ) -> None:
        """
        Initializes the ElectricLoadManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param scenario_data_path: Path to where scenario data is stored.
        :param node: Node.
        :param scale: Value to scale the existing load with.
        :param shift: Value to shift the load with in MW.
        """
        self.client = client
        self.scenario_data_path = scenario_data_path
        self.node = node
        self.scale = scale
        self.shift = shift
        self.datetime_format = datetime_format

    def apply(self) -> None:
        """
        Shift the load profile, then adjust the annual demand. Note that load in the first period is used for scaling.
        """
        df_electricload = pd.read_csv(self.scenario_data_path / "electricload.csv")

        if self.node not in df_electricload.columns[1:]:
            raise ValueError(f"Node {self.node} not found in 'electricload.csv'.")

        df_electric_annual_demand = self.client.nodes.get_electric_annual_demand()

        period = df_electric_annual_demand["Period"].unique()[0]  # NB! Scales only against the first period
        cond = (df_electric_annual_demand["Nodes"] == self.node) & (df_electric_annual_demand["Period"] == period)

        scale = self.scale * df_electric_annual_demand.loc[cond, "ElectricAdjustment in MWh per hour"][0] / 8760

        df_electric_annual_demand.loc[cond, "ElectricAdjustment in MWh per hour"] = (scale + self.shift) * 8760

        df_electricload.loc[:, self.node] = scale_and_shift_series(
            df_electricload[self.node], scale=scale, shift=self.shift
        )

        self.client.nodes.set_electric_annual_demand(df_electric_annual_demand)

        logger.info(f"Scaling load in node {self.node} by {self.scale} and shifting by {self.shift}")
        df_electricload.to_csv(
            self.scenario_data_path / "electricload.csv", index=False, date_format=self.datetime_format
        )


if __name__ == "__main__":
    from pathlib import Path

    dataset_path = Path(
        "/Users/martihj/gitsource/OpenEMPIRE/Results/norway_analysis/ncc6000.0_na0.95_w0.0_wog0.0_pTrue/Input/Xlsx"
    )
    input_client = EmpireInputClient(dataset_path=dataset_path)

    transmission_manager = MaxTransmissionCapacityManager(
        client=input_client, from_node="SorligeNordsjoII", to_node="UtsiraNord", max_installed_capacity=0.0
    )

    transmission_manager.apply()

    # Remove international connections
    remove_transmission = [
        ["HollandseeKust", "DoggerBank"],
        ["Nordsoen", "DoggerBank"],
        ["SorligeNordsjoII", "DoggerBank"],
        ["Borssele", "EastAnglia"],
        ["SorligeNordsjoI", "FirthofForth"],
        ["Nordsoen", "HelgolanderBucht"],
        ["SorligeNordsjoI", "HelgolanderBucht"],
        ["SorligeNordsjoII", "HelgolanderBucht"],
        ["Borssele", "Hornsea"],
        ["HollandseeKust", "Hornsea"],
        ["UtsiraNord", "MorayFirth"],
        ["Borssele", "Norfolk"],
        ["HollandseeKust", "Norfolk"],
        ["HollandseeKust", "Belgium"],
        ["Hornsea", "DoggerBank"],
        ["Borssele", "Netherlands"],
        ["HelgolanderBucht", "Netherlands"],
        ["SorligeNordsjoI", "Nordsoen"],
        ["SorligeNordsjoII", "Nordsoen"],
        ["UtsiraNord", "Nordsoen"],
    ]

    for from_node, to_node in remove_transmission:
        MaxTransmissionCapacityManager(
            client=input_client, from_node=from_node, to_node=to_node, max_installed_capacity=0.0
        ).apply()
