from abc import ABC, abstractmethod

from Empire.input_client.client import EmpireInputClient


class IDataManager(ABC):
    @abstractmethod
    def apply(self):
        pass


class AvailabilityManager(IDataManager):
    def __init__(self, client: EmpireInputClient, generator: str, availability: float):
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
    def __init__(
        self, client: EmpireInputClient, generator_technology: str, capital_cost: float
    ) -> None:
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

        condition = df_max_installed["Node"].isin(self.nodes) & df_max_installed[
            "GeneratorTechnology"
        ].isin([self.generator_technology])

        if not condition.any():
            raise ValueError(
                f"No rows found for nodes {self.nodes} and technology {self.generator_technology}."
            )

        df_max_installed.loc[
            condition, "generatorMaxInstallCapacity  in MW"
        ] = self.max_installed_capacity

        self.client.generator.set_max_installed_capacity(df_max_installed)
