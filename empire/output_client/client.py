import os
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from io import StringIO
from pathlib import Path

import pandas as pd


@dataclass
class ResultFile:
    curtailed_prod: str = "results_output_curtailed_prod.csv"
    curtailed_operational: str = "results_output_curtailed_operational.csv"
    transmision_operational: str = "results_output_transmision_operational.csv"
    stor: str = "results_output_stor.csv"
    operational: str = "results_output_Operational.csv"
    transmision: str = "results_output_transmision.csv"
    objective: str = "results_objective.csv"
    europe_plot: str = "results_output_EuropePlot.csv"
    europe_summary: str = "results_output_EuropeSummary.csv"
    gen: str = "results_output_gen.csv"


class EmpireOutputClient:
    """
    A output client for to the Empire dataset.

    Note that API calls are cached, and changes to underlying dataset will not be detected by the client. 
    """

    def __init__(self, output_path: Path):
        """
        Initialize an EmpireOutputClient with the given dataset path and engine.

        :param output_path: Directory containing run results.
        """
        self.output_path = output_path
        self.files = ResultFile()

    def _read_file_and_split(self, filename: str) -> list:
        """
        Helper method to read a file and split its content.

        :param filename: Name of the file to read.
        :return: List of split data.
        """
        with open(self.output_path / filename, "r") as file:
            data = file.read()
        return data.split('""\n')

    @lru_cache(maxsize=None)
    def get_europe_summary_emission_and_energy(self) -> pd.DataFrame:
        """
        Retrieve emission and energy data from the Europe summary.

        :return: DataFrame containing the data.
        """
        return pd.read_csv(StringIO(self._read_file_and_split(self.files.europe_summary)[0]))

    @lru_cache(maxsize=None)
    def get_europe_summary_generator_types(self) -> pd.DataFrame:
        """
        Retrieve generator types data from the Europe summary.

        :return: DataFrame containing the data.
        """
        return pd.read_csv(StringIO(self._read_file_and_split(self.files.europe_summary)[1]))

    @lru_cache(maxsize=None)
    def get_europe_summary_storage_types(self) -> pd.DataFrame:
        """
        Retrieve storage types data from the Europe summary.

        :return: DataFrame containing the data.
        """
        return pd.read_csv(StringIO(self._read_file_and_split(self.files.europe_summary)[2]))

    @lru_cache(maxsize=None)
    def _get_europe_plot_data(self, index: int) -> pd.DataFrame:
        """
        Retrieve specific data from the Europe plot based on the provided index.

        :param index: The index indicating which data to retrieve.
        :return: A DataFrame containing the requested data.
        """
        index_name, columns_name = self._read_file_and_split(self.files.europe_plot)[index].split("\n")[0].split(",")
        df = pd.read_csv(StringIO(self._read_file_and_split(self.files.europe_plot)[index]), index_col=0, header=1)
        df.index.name = index_name
        df.columns.name = columns_name
        return df

    def get_europe_plot_generator_installed_capacity(self) -> pd.DataFrame:
        """
        Retrieve the installed capacity of generators in each period. Values in MW.

        :return: A DataFrame containing the installed capacity of generators.
        """
        return self._get_europe_plot_data(index=0)

    def get_europe_plot_generator_annual_production(self) -> pd.DataFrame:
        """
        Retrieve the expected annual production of generators in each period. Values in GWh.

        :return: A DataFrame containing the annual production of generators.
        """
        return self._get_europe_plot_data(index=1)

    def get_europe_plot_storage_installed_capacity(self) -> pd.DataFrame:
        """
        Retrieve the installed capacity of storages in each period. Values in MW.

        :return: A DataFrame containing the installed capacity of storages.
        """
        return self._get_europe_plot_data(index=2)

    def get_europe_plot_storage_installed_energy(self) -> pd.DataFrame:
        """
        Retrieve the installed energy of storages in each period. Values in GWh(?).

        :return: A DataFrame containing the installed capacity of storages.
        """
        return self._get_europe_plot_data(index=3)

    def get_europe_plot_storage_annual_discharge(self) -> pd.DataFrame:
        """
        Retrieve the expected annual discharge of storages in each period. Values in GWh.

        :return: A DataFrame containing the annual discharge of storages.
        """
        return self._get_europe_plot_data(index=4)
    
    @lru_cache(maxsize=None)
    def get_objective(self) -> float:
        """
        Retrieve the objective value of the model.

        :return: The objective value as a float.
        :raises ValueError: If unable to parse the objective value from the file.
        """
        with open(self.output_path / self.files.objective, "r") as file:
            data = file.read()
        try:
            return float(data.split(":")[1].strip())
        except (IndexError, ValueError):
            raise ValueError("Unable to parse objective value from file.")

    @lru_cache(maxsize=None)
    def get_curtailed_production(self) -> pd.DataFrame:
        """
        Retrieve the expected annual curtailment for each node and period.

        :return: A DataFrame containing the curtailed production data.
        """
        return pd.read_csv(self.output_path / self.files.curtailed_prod)

    @lru_cache(maxsize=None)
    def get_curtailed_operational(self) -> pd.DataFrame:
        """
        Retrieve the curtailment for each node, period, hour and RES technology.

        :return: A DataFrame containing the curtailed operational data.
        """
        return pd.read_csv(self.output_path / self.files.curtailed_operational)

    @lru_cache(maxsize=None)
    def get_generators_values(self) -> pd.DataFrame:
        """
        Retrieve values for generators in the nodes.

        :return: A DataFrame containing the generator values.
        """
        return pd.read_csv(self.output_path / self.files.gen)

    @lru_cache(maxsize=None)
    def get_storage_values(self) -> pd.DataFrame:
        """
        Retrieve values for storages in the nodes.

        :return: A DataFrame containing the storage values.
        """
        return pd.read_csv(self.output_path / self.files.stor)

    @lru_cache(maxsize=None)
    def get_transmission_values(self) -> pd.DataFrame:
        """
        Retrieve values of transmission lines between nodes.

        :return: A DataFrame containing the transmission values.
        """
        return pd.read_csv(self.output_path / self.files.transmision)

    def _slice_file_with_grep(self, file: Path, node: str | None = None) -> pd.DataFrame:
        """
        Slice the file contents based on the provided node using grep (for Unix-like systems).

        :param file: The path to the file to be sliced.
        :param node: The node to filter by. Defaults to None.
        :returns: A DataFrame containing the sliced data.
        """

        if node:
            if os.name == "posix":
                # Use grep to filter rows containing the node
                with open(file, "r") as f:
                    header = f.readline()
                result = subprocess.run(["grep", node, file], stdout=subprocess.PIPE)
                buffer = StringIO(header + result.stdout.decode())
                return pd.read_csv(buffer)
            else:
                df = pd.read_csv(file)
                return df.loc[df["Node"] == node]

        return pd.read_csv(file)

    @lru_cache(maxsize=None)
    def get_transmission_operational(self, node: str | None = None) -> pd.DataFrame:
        """
        Retrieve operational transmission data, optionally filtered by a specific node.

        :param node: The node to filter by. Defaults to None.
        :returns: A DataFrame containing the operational transmission data.
        """
        return self._slice_file_with_grep(file=self.output_path / self.files.transmision_operational, node=node)

    @lru_cache(maxsize=None)
    def get_node_operational_values(self, node: str | None = None) -> pd.DataFrame:
        """
        Retrieve operational values for a specific node.

        :param node: The node to filter by. Defaults to None.
        :returns: A DataFrame containing the operational values for the specified node.
        """
        return self._slice_file_with_grep(file=self.output_path / self.files.operational, node=node)


if __name__ == "__main__":
    result_dir = Path.cwd() / "Results/norway_analysis/ncc3000.0_na0.95_w0.0_wog0.0"
    output_dir = result_dir / "Output"

    client = EmpireOutputClient(output_path=output_dir)

    df_emission_and_energy = client.get_europe_summary_emission_and_energy()

    df = client.get_europe_plot_generator_annual_production()

    client.get_europe_plot_storage_annual_discharge()

    import time

    start = time.time()
    client.get_node_operational_values()
    print(f"All: {time.time() - start:.2f} [s]")

    start = time.time()
    df = client.get_node_operational_values("Austria")
    print(f"Selected node: {time.time() - start:.2f} [s]")
