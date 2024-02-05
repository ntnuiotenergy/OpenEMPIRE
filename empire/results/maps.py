from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def build_graph_with_results(coordinates, results, period):
    results_p = results[results["Period"] == period].reset_index(drop=True)
    G = nx.Graph()

    for _, row in coordinates.iterrows():
        G.add_node(row["Location"], pos=(row["Longitude"], row["Latitude"]))

    for _, row in results_p.iterrows():
        G.add_edge(
            row["BetweenNode"],
            row["AndNode"],
            weight=(row["transmissionInstalledCap_MW"] / 2500),
            label=row["transmissionInstalledCap_MW"],
        )

    return G


def build_graph_with_lines(coordinates, lines: pd.DataFrame):
    G = nx.Graph()

    for _, row in coordinates.iterrows():
        G.add_node(row["Location"], pos=(row["Longitude"], row["Latitude"]))

    for _, row in lines.iterrows():
        G.add_edge(row["NodeFrom"], row["NodeTo"], weight=1)

    return G


def plot_graph(G: nx.Graph) -> plt.Figure:
    """
    Plot the graph on a basemap and return the figure handle.

    Parameters:
    - G: nx.Graph : NetworkX graph to be plotted.

    Returns:
    - fig: matplotlib Figure object
    """
    from mpl_toolkits.basemap import Basemap

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

    coordinates = pd.read_excel(results_path / "Input/Xlsx/Sets.xlsx", sheet_name="Coords")
    results = pd.read_csv(results_path / "Output/results_output_transmission.csv")

    plot_path = results_path / "Plots"
    plot_path.mkdir(parents=True, exist_ok=True)

    for period in results["Period"].unique():
        G = build_graph_with_results(coordinates, results, period)
        plot_graph(G)
        plt.title(f"{period}")

        if save_to_file:
            plt.savefig(f"{period}.pdf")


def plot_nodes_and_lines(df_coords: pd.DataFrame, df_lines: pd.DataFrame) -> go.Figure:
    """
    Return a figure with a map of nodes and lines.

    :param df_coords: Dataframe containing coordinates of nodes.
    :param df_lines: Dataframe containing lines between nodes.
    :return: Plotly figure.
    """

    # Create a scatter plot for the cities
    fig = go.Figure(
        go.Scattergeo(
            lon=df_coords["Longitude"],
            lat=df_coords["Latitude"],
            text=df_coords["Location"],
            mode="markers+text",
            marker=dict(size=10, color="#1f78b4"),
            textfont=dict(size=10),
            textposition="bottom center",
            name="Nodes",
        )
    )

    color_node_type = {"HVAC_OverheadLine": "#32213A", "HVDC_Cable": "#2E86AB"}

    # Add lines connecting the nodes
    for _, row in df_lines.iterrows():
        from_lat = df_coords[df_coords["Location"] == row["FromNode"]]["Latitude"].values[0]
        from_lon = df_coords[df_coords["Location"] == row["FromNode"]]["Longitude"].values[0]
        to_lat = df_coords[df_coords["Location"] == row["ToNode"]]["Latitude"].values[0]
        to_lon = df_coords[df_coords["Location"] == row["ToNode"]]["Longitude"].values[0]

        fig.add_trace(
            go.Scattergeo(
                lon=[from_lon, to_lon],
                lat=[from_lat, to_lat],
                mode="lines",
                line=dict(width=0.2, color=color_node_type[row["LineType"]]),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=row["LineType"],
                legendgrouptitle={"text": row["LineType"]},
            )
        )
    # Update the map to zoom in on Europe and adjust the size
    fig.update_geos(
        lataxis_range=[40, 65],  # latitude range for Europe
        lonaxis_range=[-45, 20],  # longitude range for Europe
        showcoastlines=True,
        showcountries=True,
        showlakes=False,
        projection_type="orthographic",
        projection_rotation=dict(lon=15, lat=55),
    )
    fig.update_layout(
        width=900,  # Width in pixels
        height=600,  # Height in pixels
    )

    return fig


def plot_transmission(
    df_coords: pd.DataFrame,
    df_lines: pd.DataFrame,
    df_init_capacity: pd.DataFrame,
    df_max_capacity: pd.DataFrame,
    df_length: pd.DataFrame,
    df_efficiency: pd.DataFrame,
) -> go.Figure:
    """
    Return a figure with a map of the transmission system.

    :param df_coords: Dataframe containing coordinates of nodes.
    :param df_lines: Dataframe containing lines between nodes.
    :return: Plotly figure.
    """
    # Create a scatter plot for the cities
    fig = go.Figure(
        go.Scattergeo(
            lon=df_coords["Longitude"],
            lat=df_coords["Latitude"],
            text=df_coords["Location"],
            mode="markers+text",
            marker=dict(size=10, color="#1f78b4"),
            textfont=dict(size=10),
            textposition="bottom center",
            name="Nodes",
        )
    )

    color_node_type = {"HVAC_OverheadLine": "#32213A", "HVDC_Cable": "#2E86AB"}

    # Add lines connecting the nodes
    for _, row in df_lines.iterrows():
        from_lat = df_coords[df_coords["Location"] == row["FromNode"]]["Latitude"].values[0]
        from_lon = df_coords[df_coords["Location"] == row["FromNode"]]["Longitude"].values[0]
        to_lat = df_coords[df_coords["Location"] == row["ToNode"]]["Latitude"].values[0]
        to_lon = df_coords[df_coords["Location"] == row["ToNode"]]["Longitude"].values[0]

        initial_capacity = df_init_capacity.query(
            f"InterconnectorLinks=='{row['FromNode']}' & ToNode=='{row['ToNode']}'"
        )["TransmissionInitialCapacity"]
        if not initial_capacity.empty:
            initial_capacity = initial_capacity.values[0]
        else:
            continue

        width = initial_capacity / 2000

        max_capacity = df_max_capacity.query(f"InterconnectorLinks=='{row['FromNode']}' & ToNode=='{row['ToNode']}'")[
            "TransmissionMaxBuiltCapacity in MW"
        ]
        if not max_capacity.empty:
            max_capacity = max_capacity.values[0]

        length = df_length.query(f"FromNode=='{row['FromNode']}' & ToNode=='{row['ToNode']}'")["Length in km"]
        if not length.empty:
            length = length.values[0]

        efficiency = df_efficiency.query(f"FromNode=='{row['FromNode']}' & ToNode=='{row['ToNode']}'")["lineEfficiency"]
        if not efficiency.empty:
            efficiency = efficiency.values[0]

        num_points = 10
        # Generate points along the line
        lons = np.linspace(from_lon, to_lon, num_points)
        lats = np.linspace(from_lat, to_lat, num_points)
        hover_text = f"Init: {initial_capacity:.0f}<br>Max: {max_capacity:.0f}<br>Length: {length}<br>Eff: {efficiency}"
        hover_texts = [hover_text] * num_points  # Repeat the hover text for each point

        fig.add_trace(
            go.Scattergeo(
                lon=lons,
                lat=lats,
                mode="lines",
                line=dict(width=0.0),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=f"{row['FromNode']}-{row['ToNode']}",
                hoverinfo="text",
                hovertext=hover_texts,
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scattergeo(
                lon=[from_lon, to_lon],
                lat=[from_lat, to_lat],
                mode="lines",
                line=dict(width=width, color=color_node_type[row["LineType"]]),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=f"{row['FromNode']}-{row['ToNode']}",
            )
        )

    # Update the map to zoom in on Europe and adjust the size
    fig.update_geos(
        lataxis_range=[40, 65],  # latitude range for Europe
        lonaxis_range=[-45, 20],  # longitude range for Europe
        showcoastlines=True,
        showcountries=True,
        showlakes=False,
        projection_type="orthographic",
        projection_rotation=dict(lon=15, lat=55),
    )
    fig.update_layout(
        width=900,  # Width in pixels
        height=600,  # Height in pixels
    )

    return fig


def plot_max_transmission_capacity(
    df_coords: pd.DataFrame,
    df_lines: pd.DataFrame,
    df_max_capacity: pd.DataFrame,
) -> go.Figure:
    """
    Return a figure with a map of max capacity of the transmission system.

    :param df_coords: Dataframe containing coordinates of nodes.
    :param df_lines: Dataframe containing lines between nodes.
    :return: Plotly figure.
    """
    # Create a scatter plot for the cities
    fig = go.Figure(
        go.Scattergeo(
            lon=df_coords["Longitude"],
            lat=df_coords["Latitude"],
            text=df_coords["Location"],
            mode="markers+text",
            marker=dict(size=10, color="#1f78b4"),
            textfont=dict(size=10),
            textposition="bottom center",
            name="Nodes",
        )
    )

    color_node_type = {"HVAC_OverheadLine": "#32213A", "HVDC_Cable": "#2E86AB"}

    # Add lines connecting the nodes
    for _, row in df_lines.iterrows():
        from_lat = df_coords[df_coords["Location"] == row["FromNode"]]["Latitude"].values[0]
        from_lon = df_coords[df_coords["Location"] == row["FromNode"]]["Longitude"].values[0]
        to_lat = df_coords[df_coords["Location"] == row["ToNode"]]["Latitude"].values[0]
        to_lon = df_coords[df_coords["Location"] == row["ToNode"]]["Longitude"].values[0]

        max_capacity = df_max_capacity.query(f"InterconnectorLinks=='{row['FromNode']}' & ToNode=='{row['ToNode']}'")[
            "MaxRawNotAdjustWithInitCap in MW"
        ]
        if not max_capacity.empty:
            max_capacity = max_capacity.values[0]
        else:
            continue

        width = max_capacity / 2000
        if width > 5:
            width = 5

        num_points = 10
        # Generate points along the line
        lons = np.linspace(from_lon, to_lon, num_points)
        lats = np.linspace(from_lat, to_lat, num_points)
        hover_text = f"Max capacity: {max_capacity:.0f}"
        hover_texts = [hover_text] * num_points  # Repeat the hover text for each point

        fig.add_trace(
            go.Scattergeo(
                lon=lons,
                lat=lats,
                mode="lines",
                line=dict(width=0.0),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=f"{row['FromNode']}-{row['ToNode']}",
                hoverinfo="text",
                hovertext=hover_texts,
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scattergeo(
                lon=[from_lon, to_lon],
                lat=[from_lat, to_lat],
                mode="lines",
                line=dict(width=width, color=color_node_type[row["LineType"]]),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=f"{row['FromNode']}-{row['ToNode']}",
            )
        )

    # Update the map to zoom in on Europe and adjust the size
    fig.update_geos(
        lataxis_range=[40, 65],  # latitude range for Europe
        lonaxis_range=[-45, 20],  # longitude range for Europe
        showcoastlines=True,
        showcountries=True,
        showlakes=False,
        projection_type="orthographic",
        projection_rotation=dict(lon=15, lat=55),
    )
    fig.update_layout(
        width=900,  # Width in pixels
        height=600,  # Height in pixels
    )

    return fig


def plot_built_transmission_capacity(
    df_coords: pd.DataFrame, df_lines: pd.DataFrame, df_built: pd.DataFrame, metric="transmissionInstalledCap_MW"
) -> go.Figure:
    """
    Return a figure with a map of max capacity of the transmission system.

    :param df_coords: Dataframe containing coordinates of nodes.
    :param df_lines: Dataframe containing lines between nodes.
    :return: Plotly figure.
    """
    # Create a scatter plot for the cities
    fig = go.Figure(
        go.Scattergeo(
            lon=df_coords["Longitude"],
            lat=df_coords["Latitude"],
            text=df_coords["Location"],
            mode="markers+text",
            marker=dict(size=10, color="#1f78b4"),
            textfont=dict(size=10),
            textposition="bottom center",
            name="Nodes",
        )
    )

    color_node_type = {"HVAC_OverheadLine": "#32213A", "HVDC_Cable": "#2E86AB"}

    # Add lines connecting the nodes
    for _, row in df_lines.iterrows():
        from_lat = df_coords[df_coords["Location"] == row["FromNode"]]["Latitude"].values[0]
        from_lon = df_coords[df_coords["Location"] == row["FromNode"]]["Longitude"].values[0]
        to_lat = df_coords[df_coords["Location"] == row["ToNode"]]["Latitude"].values[0]
        to_lon = df_coords[df_coords["Location"] == row["ToNode"]]["Longitude"].values[0]

        max_capacity = df_built.query(f"BetweenNode=='{row['FromNode']}' & AndNode=='{row['ToNode']}'")[metric]
        if not max_capacity.empty:
            max_capacity = max_capacity.values[0]
            if max_capacity < 1.0:
                continue
        else:
            continue

        width = max_capacity / 2000
        if width > 5:
            width = 5

        num_points = 10
        # Generate points along the line
        lons = np.linspace(from_lon, to_lon, num_points)
        lats = np.linspace(from_lat, to_lat, num_points)
        hover_text = f"Max capacity: {max_capacity:.0f}<br>{row['FromNode']}-{row['ToNode']}"
        hover_texts = [hover_text] * num_points  # Repeat the hover text for each point

        fig.add_trace(
            go.Scattergeo(
                lon=lons,
                lat=lats,
                mode="lines",
                line=dict(width=0.0),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=f"{row['FromNode']}-{row['ToNode']}",
                hoverinfo="text",
                hovertext=hover_texts,
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scattergeo(
                lon=[from_lon, to_lon],
                lat=[from_lat, to_lat],
                mode="lines",
                line=dict(width=width, color=color_node_type[row["LineType"]]),
                name=f"{row['FromNode']}-{row['ToNode']}",
                legendgroup=f"{row['FromNode']}-{row['ToNode']}",
            )
        )

    # Update the map to zoom in on Europe and adjust the size
    fig.update_geos(
        lataxis_range=[40, 65],  # latitude range for Europe
        lonaxis_range=[-45, 20],  # longitude range for Europe
        showcoastlines=True,
        showcountries=True,
        showlakes=False,
        projection_type="orthographic",
        projection_rotation=dict(lon=15, lat=55),
    )
    fig.update_layout(
        width=900,  # Width in pixels
        height=600,  # Height in pixels
    )

    return fig


if __name__ == "__main__":
    results_path = Path.cwd() / "Results/test_reg24_peak24_sce2_randomSGR_202310031437"
    plot_results(results_path=results_path)
