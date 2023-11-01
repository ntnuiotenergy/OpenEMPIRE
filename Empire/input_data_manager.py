import logging
from abc import ABC, abstractmethod

from empire.input_client.client import EmpireInputClient

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

    def __init__(self, client: EmpireInputClient, generator: str, availability: float):
        """
        Initializes the AvailabilityManager with the provided parameters.

        Parameters:
        -----------
        :param client: The client interface for retrieving and setting generator data.
        :param generator: The specific generator technology to be updated.
        :param availability: The new availability value to be set for the specified generator.
        """
        self.client = client
        self.generator = generator
        self.availability = availability
        self.validate()

    def validate(self) -> None:
        if self.availability < 0.0 or self.availability > 1.0:
            raise ValueError("availability has to be in range [0,1]")

    def apply(self) -> None:
        df_availability = self.client.generator.get_generator_type_availability()
        df_availability.loc[
            df_availability["Generator"] == self.generator, "GeneratorTypeAvailability"
        ] = self.availability

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
        df_capital_costs = self.client.generator.get_captial_costs()
        df_capital_costs.loc[
            df_capital_costs["GeneratorTechnology"] == self.generator_technology,
            "generatorCapitalCost in euro per kW",
        ] = self.capital_cost

        self.client.generator.set_captial_costs(df_capital_costs)


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
