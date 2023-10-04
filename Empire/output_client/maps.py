from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from mpl_toolkits.basemap import Basemap


def build_graph(coordinates, results, period):
    results_p = results[results["Period"] == period].reset_index(drop=True)
    G = nx.Graph()

    for _, row in coordinates.iterrows():
        G.add_node(row["Location"], pos=(row["Longitude"], row["Latitude"]))

    for _, row in results_p.iterrows():
        G.add_edge(
            row["BetweenNode"],
            row["AndNode"],
            weight=(row["transmisionInstalledCap_MW"] / 2500) + 0.6,
            label=row["transmisionInstalledCap_MW"],
        )

    return G


def plot_graph(G: nx.Graph) -> plt.Figure:
    """
    Plot the graph on a basemap and return the figure handle.

    Parameters:
    - G: nx.Graph : NetworkX graph to be plotted.

    Returns:
    - fig: matplotlib Figure object
    """
    fig = plt.figure(figsize=(10, 10))
    m = Basemap(
        projection="merc",
        llcrnrlat=35,
        urcrnrlat=72,
        llcrnrlon=-20,
        urcrnrlon=40,
        lat_ts=0,
        resolution="c",
    )
    m.drawcoastlines(linewidth=0.1)
    m.drawcountries(linewidth=1)
    m.etopo()

    pos = nx.get_node_attributes(G, "pos")
    for node, data in G.nodes(data=True):
        x, y = m(*data["pos"])
        m.plot(x, y, marker="o", markersize=3, markerfacecolor="black")

    for edge in G.edges(data=True):
        lon = [pos[edge[0]][0], pos[edge[1]][0]]
        lat = [pos[edge[0]][1], pos[edge[1]][1]]
        x, y = m(lon, lat)
        weight = edge[2].get("weight", 1)
        m.plot(
            x,
            y,
            marker="o",
            markersize=5,
            markerfacecolor="red",
            linestyle="-",
            color="blue",
            linewidth=weight,
        )

    return fig


def plot_results(results_path: Path, save_to_file: bool = False):
    """
    Plot results.

    :param results_path: Path to the csv file containing results data.
    """
    
    coordinates = pd.read_excel(results_path/"Input/Xlsx/Sets.xlsx", sheet_name="Coords")
    results = pd.read_csv(results_path/"Output/results_output_transmission.csv")

    plot_path = results_path / "Plots"
    plot_path.mkdir(parents=True, exist_ok=True)

    for period in results["Period"].unique():
        G = build_graph(coordinates, results, period)
        fig = plot_graph(G)
        plt.title(f"{period}")

        if save_to_file:
            plt.savefig(f"{period}.pdf")


if __name__ == "__main__":
    
    results_path = Path.cwd()/"Results/test_reg24_peak24_sce2_randomSGR_202310031437"
    plot_results(results_path=results_path)