import cProfile
import pstats
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from empire.input_client.client import EmpireInputClient
from empire.output_client.client import EmpireOutputClient
from empire.results.maps import plot_built_transmission_capacity


def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats("cumulative")
        stats.dump_stats("profile_results.prof")
        return result

    return wrapper


# @st.cache_data
def get_europe_plot_generator_annual_production(_output_client):
    return _output_client.get_europe_plot_generator_annual_production()


# @st.cache_data
def get_europe_plot_generator_installed_capacity(_output_client):
    return _output_client.get_europe_plot_generator_installed_capacity()


# @st.cache_data
def get_curtailed_production(_output_client):
    return _output_client.get_curtailed_production()


# @st.cache_data
def get_europe_plot_storage_installed_energy(_output_client):
    return _output_client.get_europe_plot_storage_installed_energy()


# @st.cache_data
def get_europe_plot_storage_annual_discharge(_output_client):
    return _output_client.get_europe_plot_storage_annual_discharge()


# @st.cache_data
def get_europe_plot_storage_installed_capacity(_output_client):
    return _output_client.get_europe_plot_storage_installed_capacity()


# @st.cache_data
def get_europe_summary_emission_and_energy(_output_client):
    return _output_client.get_europe_summary_emission_and_energy()


# @profile_function
def output(active_results: Path) -> None:
    st.title("Results")
    output_client = EmpireOutputClient(output_path=active_results / "Output")
    input_client = EmpireInputClient(dataset_path=active_results / "Input/Xlsx")

    df = output_client.get_curtailed_production()
    st.sidebar.markdown("______________")
    st.sidebar.markdown("__Page filter:__")
    period = st.sidebar.select_slider("Select period: ", df["Period"].unique())

    st.header("Summary results")
    st.write(f"Objective value: {output_client.get_objective()/1e9:.2f} Billion")

    def plot_europe_plot_generator_annual_production():
        df = get_europe_plot_generator_annual_production(output_client)
        df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
        return px.bar(
            df,
            x="Period",
            y="Value",
            color="genExpectedAnnualProduction_GWh",
            title="Expected Annual Production",
            labels={"genExpectedAnnualProduction_GWh": "Technology", "Value": "Expected Annual Production [TWh]"},
        )

    def plot_europe_plot_generator_installed_capacity():
        df = get_europe_plot_generator_installed_capacity(output_client)
        df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
        return px.bar(
            df,
            x="Period",
            y="Value",
            color="genInstalledCap_MW",
            title="Installed Capacity",
            labels={"genInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_europe_plot_generator_annual_production())
    col2.plotly_chart(plot_europe_plot_generator_installed_capacity())

    def plot_curtailed_production():
        df = get_curtailed_production(output_client)
        df.loc[:, "ExpectedAnnualCurtailment_GWh"] = df.loc[:, "ExpectedAnnualCurtailment_GWh"] / 1e3
        fig = px.bar(
            df,
            x="RESGeneratorType",
            y="ExpectedAnnualCurtailment_GWh",
            color="Node",
            facet_col="Period",
            title="Expected Annual Curtailment",
            labels={"ExpectedAnnualCurtailment_GWh": "Expected Annual Curtailment [TWh]"},
            facet_col_wrap=False,
        )
        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_europe_plot_storage_installed_energy():
        df = get_europe_plot_storage_installed_energy(output_client)
        df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
        return px.bar(
            df,
            x="Period",
            y="Value",
            color="storENInstalledCap_MW",
            title="Installed Energy Storage",
            labels={"storENInstalledCap_MW": "Technology", "Value": "Installed Storage [MWh?]"},
        )

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_curtailed_production())
    col2.plotly_chart(plot_europe_plot_storage_installed_energy())

    def plot_europe_plot_storage_annual_discharge():
        df = get_europe_plot_storage_annual_discharge(output_client)
        df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
        return px.bar(
            df,
            x="Period",
            y="Value",
            color="storExpectedAnnualDischarge_GWh",
            title="Expected Annual Storage Discharge",
            labels={
                "storExpectedAnnualDischarge_GWh": "Technology",
                "Value": "Expected Annual Storage Discharge [TWh]",
            },
        )

    def plot_europe_plot_storage_installed_capacity():
        df = get_europe_plot_storage_installed_capacity(output_client)
        df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
        return px.bar(
            df,
            x="Period",
            y="Value",
            color="storPWInstalledCap_MW",
            title="Installed Storage Capacity",
            labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_europe_plot_storage_annual_discharge())
    col2.plotly_chart(plot_europe_plot_storage_installed_capacity())

    def plot_europe_summary_emission_and_energy():
        df = get_europe_summary_emission_and_energy(output_client)
        column_values = df.columns.to_list()[2:]
        selected_column = st.selectbox("Choose values: ", column_values)

        fig = px.bar(
            df,
            x="Scenario",
            y=selected_column,
            # color="GeneratorType",
            facet_col="Period",
            title="Emission and Energy Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )
        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))

        return fig

    st.plotly_chart(plot_europe_summary_emission_and_energy())

    st.header("Node results")

    def plot_transmission_values(col):
        df = output_client.get_transmission_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = np.unique(df[["BetweenNode", "AndNode"]].values.flatten())
        selected_nodes = col.multiselect(
            "Select nodes: ", nodes, default=[item for item in default_nodes if item in nodes]
        )
        df = df.query(f"BetweenNode in {selected_nodes} or AndNode in {selected_nodes}").copy(deep=True)

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values: ", column_values)

        df["From-To"] = df["BetweenNode"] + "-" + df["AndNode"]
        fig = px.bar(
            df,
            x="From-To",
            y=selected_column,
            facet_col="Period",
            title="Transmission Values",
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_transmission_values_line(col):
        df = output_client.get_transmission_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = np.unique(df[["BetweenNode", "AndNode"]].values.flatten())
        selected_nodes = col.multiselect(
            "Select nodes:   ", nodes, default=[item for item in default_nodes if item in nodes]
        )

        df = df.query(f"BetweenNode in {selected_nodes} or AndNode in {selected_nodes}").copy(deep=True)

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values:   ", column_values)

        df["From-To"] = df["BetweenNode"] + "-" + df["AndNode"]
        fig = px.line(
            df,
            x="Period",
            y=selected_column,
            color="From-To",
            title="Transmission Values",
        )

        return fig

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_transmission_values(col1))
    col2.plotly_chart(plot_transmission_values_line(col2))

    def plot_generator_values(col):
        df = output_client.get_generators_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = df["Node"].unique()
        selected_nodes = col.multiselect(
            "Select nodes: ", nodes, default=[item for item in default_nodes if item in nodes]
        )

        df = df.query(f"Node in {selected_nodes}")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values: ", column_values)

        fig = px.bar(
            df,
            x="Node",
            y=selected_column,
            color="GeneratorType",
            facet_col="Period",
            title="Generator Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_generator_values_line(col):
        df = output_client.get_generators_values()
        selected_generator_technology = col.selectbox("Select Generator Technology:  ", df["GeneratorType"].unique())
        df = df.query(f"GeneratorType in '{selected_generator_technology}'")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values:  ", column_values)

        fig = px.line(
            df,
            x="Period",
            y=selected_column,
            color="Node",
            title="Generator Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        return fig

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_generator_values(col1))
    col2.plotly_chart(plot_generator_values_line(col2))

    def plot_storage_values(col):
        df = output_client.get_storage_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = df["Node"].unique()
        selected_nodes = col.multiselect(
            "Select nodes:  ", nodes, default=[item for item in default_nodes if item in nodes]
        )
        df = df.query(f"Node in {selected_nodes}")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values: ", column_values)

        fig = px.bar(
            df,
            x="Node",
            y=selected_column,
            color="StorageType",
            facet_col="Period",
            title="Storage Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_storage_values_line(col):
        df = output_client.get_storage_values()
        selected_storage_technology = col.radio("Select Storage Technology:  ", df["StorageType"].unique())
        df = df.query(f"StorageType in '{selected_storage_technology}'")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values:  ", column_values)

        fig = px.line(
            df,
            x="Period",
            y=selected_column,
            color="Node",
            title="Storage Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_storage_values(col1))
    col2.plotly_chart(plot_storage_values_line(col2))

    def plot_node_operation_values(df, node, scenario, season, period):
        filtered_df = df.query(f"Scenario == '{scenario}' and Season == '{season}' and Period == '{period}'")

        columns = [i for i in df.columns if "_MW" in i and i not in ["AllGen_MW", "Net_load_MW"]]

        current_columns = list(set(columns).intersection(set(filtered_df.columns)))

        column_sums = filtered_df[current_columns].sum().abs()

        # Find columns where the sum is less than 0.1 MW
        columns_to_drop = column_sums[column_sums < 0.1].index
        filtered_columns = list(set(current_columns).difference(set(columns_to_drop.to_list() + ["Load_MW"])))

        # Melting the DataFrame to have a long-form DataFrame which is suitable for line plots in plotly
        melted_df = pd.melt(filtered_df, id_vars=["Hour"], value_vars=filtered_columns)

        # Calculate the sum of values for each variable
        sums = melted_df.groupby("variable")["value"].sum()

        # Sort variables based on their sums for a more readable area plot
        sorted_variables = sums.sort_values(ascending=False).index.tolist()

        # Sort the DataFrame based on the sorted order of variables
        melted_df["variable"] = pd.Categorical(melted_df["variable"], categories=sorted_variables, ordered=True)
        melted_df = melted_df.sort_values("variable")

        # Creating the line plot
        fig = px.area(
            melted_df,
            x="Hour",
            y="value",
            color="variable",
            title=f"Operational values for {node}, {scenario}, {period}",
        )
        fig.add_trace(go.Scatter(x=filtered_df["Hour"], y=-filtered_df["Load_MW"], name="Load_MW"))
        
        fig.update_layout(
            xaxis=dict(title="Hour", domain=[0.3,1]),
            yaxis=dict(title="Value (MW)"),
            yaxis2=dict(
                title="Energy Price [EUR/MWh]",
                side="left",
                overlaying="y",
                showgrid=False,  # Hides the secondary y-axis gridlines if desired
                # tickmode="auto",  # Ensures ticks are automatically generated
                anchor="free",
                position=0.15
            ),
        )
        fig.add_trace(
            go.Scatter(x=filtered_df["Hour"], y=filtered_df["Price_EURperMWh"], name="Energy Price", yaxis="y2")
        )

        return fig

    nodes = output_client.get_storage_values().Node.unique().tolist()

    node = st.selectbox("Select node: ", nodes, index=nodes.index("NO2") if "NO2" in nodes else 0)
    df = output_client.get_node_operational_values(node)

    scenario = st.selectbox("Select scenario: ", df["Scenario"].unique())
    season = st.selectbox("Select season: ", df["Season"].unique())

    def plot_transmission_flow(df, node, scenario, season, period):
        filtered_df = df.query(f"Scenario == '{scenario}' and Season == '{season}' and Period == '{period}'").copy(
            deep=True
        )

        filtered_df["From-To"] = filtered_df["FromNode"] + "-" + filtered_df["ToNode"]

        melted_df = pd.melt(filtered_df, id_vars=["Hour", "From-To"], value_vars=["TransmissionRecieved_MW"])

        filtered_lines = melted_df.groupby("From-To").sum()["value"] > 0.1
        melted_df = melted_df.loc[melted_df["From-To"].map(filtered_lines)]

        sums = melted_df.groupby("From-To")["value"].sum()

        # Sort variables based on their sums for a more readable area plot
        sorted_variables = sums.sort_values(ascending=False).index.tolist()

        # Sort the DataFrame based on the sorted order of variables
        melted_df["From-To"] = pd.Categorical(melted_df["From-To"], categories=sorted_variables, ordered=True)
        melted_df = melted_df.sort_values("From-To")

        return px.area(
            melted_df,
            x="Hour",
            y="value",
            color="From-To",
            title=f"Exchange for {node}, {scenario}, {season}, {period}",
        )

    df_operational_trans = output_client.get_transmission_operational(node)
    fig = plot_transmission_flow(df_operational_trans, node=node, scenario=scenario, season=season, period=period)

    col1, col2 = st.columns(2)
    col1.plotly_chart(plot_node_operation_values(df, node=node, scenario=scenario, season=season, period=period))
    col2.plotly_chart(fig)

    st.header("Transmission")

    df_built = output_client.get_transmission_values()
    df_built.loc[:, "BetweenNode"] = df_built["BetweenNode"].str.replace(" ", "")
    df_built.loc[:, "AndNode"] = df_built["AndNode"].str.replace(" ", "")
    df_built = df_built.query(f"Period=='{period}'")

    df_coords = input_client.sets.get_coordinates()
    df_coords.loc[:, "Location"] = df_coords["Location"].str.replace(" ", "")

    df_lines = input_client.sets.get_line_type_of_directional_lines()
    df_lines.loc[:, "FromNode"] = df_lines["FromNode"].str.replace(" ", "")
    df_lines.loc[:, "ToNode"] = df_lines["ToNode"].str.replace(" ", "")

    metric = st.selectbox("Select transmission metric: ", df_built.columns[3:].tolist())

    fig = plot_built_transmission_capacity(df_coords=df_coords, df_lines=df_lines, df_built=df_built, metric=metric)
    fig.update_layout(title=f"{metric} for {period}")
    st.plotly_chart(fig)

    st.header("Key Metrics")
    # Get and process the dataframe
    df = output_client.get_generators_values()

    df.loc[df["genExpectedAnnualProduction_GWh"] < 1, "genExpectedCapacityFactor"] = 0.0
    df_temp = df[["Node", "GeneratorType", "Period", "genExpectedAnnualProduction_GWh"]]
    df["TotalGeneration_GWh"] = df_temp.groupby(["Node", "Period"])["genExpectedAnnualProduction_GWh"].transform("sum")
    df["GenerationShare_Percent"] = (df["genExpectedAnnualProduction_GWh"] / df["TotalGeneration_GWh"]) * 100

    df_temp = df[["Node", "GeneratorType", "Period", "genInstalledCap_MW"]]
    df["TotalCapacity_MW"] = df_temp.groupby(["Node", "Period"])["genInstalledCap_MW"].transform("sum")
    df["CapacityShare_Percent"] = (df["genInstalledCap_MW"] / df["TotalGeneration_GWh"]) * 100

    # Select measure
    measures = [
        "genInvCap_MW",
        "genInstalledCap_MW",
        "genExpectedCapacityFactor",
        "DiscountedInvestmentCost_Euro",
        "genExpectedAnnualProduction_GWh",
        "GenerationShare_Percent",
        "CapacityShare_Percent",
    ]
    measure = st.selectbox(
        "Select measure: ",
        measures,
        index=measures.index("GenerationShare_Percent") if "GenerationShare_Percent" in measures else 0,
    )

    df_sum = df.query("Period == @period").pivot(index="Node", columns="GeneratorType", values=measure)

    # Select nodes and generators with defaults
    default_nodes = [
        "NO1",
        "NO2",
        "NO3",
        "NO4",
        "NO5",
        "Sweden",
        "Finland",
        "GreatBrit.",
        "France",
        "Italy",
        "Germany",
        "Poland",
        "SorligeNordsjoI",
        "SorligeNordsoII",
        "UtsiraNord",
    ]
    nodes = df_sum.index.to_list()
    selected_nodes = st.multiselect(
        "Select nodes: ", options=df_sum.index, default=[item for item in default_nodes if item in nodes]
    )
    selected_generators = st.multiselect("Select generators: ", options=df_sum.columns, default=df_sum.columns.tolist())

    # Process the dataframe and display it
    df_sum = (
        df_sum.loc[selected_nodes, selected_generators]
        .fillna(0.0)
        .loc[:, df_sum.sum(axis=0) > 1.0]
        .assign(Active_sum=lambda x: x.sum(axis=1))
        .T
    )

    st.markdown(f"{measure} for {period}:")
    st.dataframe(df_sum.style.format("{:.2f}").background_gradient(cmap="Blues"), height=40 * len(df_sum.index))


if __name__ == "__main__":
    active_results = Path(
        "/Users/martihj/mnt/Solstorm/OpenEMPIRE/Results/norway_analysis/ncc6000.0_na0.75_w0.0_wog0.0_pTrue"
    )
    active_results = Path(
        "/Users/martihj/gitsource/OpenEMPIRE/Results/norway_analysis/ncc6000.0_na0.75_w0.0_wog0.0_pTrue"
    )
    output_client = EmpireOutputClient(output_path=active_results / "Output")
    import pandas as pd

    df = output_client.get_node_operational_values()

    df[["Node", "Period", "Scenario", "Season", "Hour", "Price_EURperMWh"]]
