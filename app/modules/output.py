import cProfile
import pstats
from pathlib import Path

import plotly.express as px
import streamlit as st

from app.modules.results.key_metrics import KeyMetricsResults
from app.modules.results.node import NodeResults
from app.modules.results.operational import OperationalResults
from empire.core.config import EmpireConfiguration, read_config_file
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


# active_results = Path("/Users/martihj/gitsource/OpenEMPIRE/Results/1_node_baseload/ncc_5000_co2_150_scale_1.0_shift-10")
# active_results = Path("/Users/martihj/gitsource/OpenEMPIRE/Results/norway_analysis/ncc3800.0_na0.95_w0.0_wog0.0_pTrue")


# @profile_function
def output(active_results: Path) -> None:
    st.title("Results")

    @st.cache_resource
    def get_output_client(active_results):
        return EmpireOutputClient(output_path=active_results / "Output")

    output_client = get_output_client(active_results)

    @st.cache_resource
    def get_input_client(active_results):
        return EmpireInputClient(dataset_path=active_results / "Input/Xlsx")

    input_client = get_input_client(active_results)

    # config_file = active_results / "Input/Xlsx/config.txt"
    config_file = Path.cwd() / "config/run.yaml"
    config = read_config_file(config_file)
    empire_config = EmpireConfiguration.from_dict(config=config)

    df = output_client.get_curtailed_production()
    st.sidebar.markdown("______________")
    st.sidebar.markdown("__Page filter:__")
    period = st.sidebar.select_slider("Select period: ", df["Period"].unique())

    #########################
    st.header("Summary results")
    #########################

    st.write(f"Objective value: {output_client.get_objective()/1e9:.2f} Billion")

    def plot_europe_plot_generator_annual_production():
        df = output_client.get_europe_plot_generator_annual_production()
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
        df = output_client.get_europe_plot_generator_installed_capacity()
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
        df = output_client.get_curtailed_production()
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
        df = output_client.get_europe_plot_storage_installed_energy()
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
        df = output_client.get_europe_plot_storage_annual_discharge()
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
        df = output_client.get_europe_plot_storage_installed_capacity()
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
        df = output_client.get_europe_summary_emission_and_energy()
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

    #########################
    st.header("Node results")
    #########################
    node_results = NodeResults(output_client=output_client)

    col1, col2 = st.columns(2)
    col1.plotly_chart(node_results.plot_accumulated_system_investments_in_transmission())
    col2.plotly_chart(node_results.plot_accumulated_system_investments_in_generation())

    col1, col2 = st.columns(2)
    col1.plotly_chart(node_results.plot_transmission_values(col1))
    col2.plotly_chart(node_results.plot_transmission_values_line(col2))

    col1, col2 = st.columns(2)
    col1.plotly_chart(node_results.plot_generator_values(col1))
    col2.plotly_chart(node_results.plot_generator_values_line(col2))

    col1, col2 = st.columns(2)
    col1.plotly_chart(node_results.plot_storage_values(col1))
    col2.plotly_chart(node_results.plot_storage_values_line(col2))

    node_results.visualize_built_capacity_in_nodes()

    ################################
    st.header("Operational results")
    ################################
    operational_results = OperationalResults(output_client=output_client, input_client=input_client)

    nodes = operational_results.get_nodes()
    node = st.selectbox("Select node: ", nodes, index=nodes.index("NO2") if "NO2" in nodes else 0)

    df_operational_node_all = output_client.get_node_operational_values()
    discount_prices = st.sidebar.toggle("Discount prices to present value", value=True)
    if not discount_prices:
        years_to_period_mapping = {
            f"{2020 + i*empire_config.leap_years_investment}-{2020+empire_config.leap_years_investment+i*empire_config.leap_years_investment}": i
            for i in range(empire_config.n_periods)
        }
        df_operational_node_all.loc[:, "Price_EURperMWh"] = df_operational_node_all.apply(
            lambda x: x["Price_EURperMWh"]
            * (1 + empire_config.discount_rate) ** (years_to_period_mapping[x["Period"]]),
            axis=1,
        )

    df_operational_node = df_operational_node_all.query(f"Node == '{node}'")

    scenario = st.selectbox("Select scenario: ", df_operational_node["Scenario"].unique())

    df_operational_trans = output_client.get_transmission_operational(node)

    col1, col2 = st.columns(2)
    col1.plotly_chart(
        operational_results.plot_node_operation_values(df_operational_node, node=node, scenario=scenario, period=period)
    )
    col2.plotly_chart(
        operational_results.plot_transmission_flow(df_operational_trans, node=node, scenario=scenario, period=period)
    )

    fig = operational_results.plot_duration_curve(df_operational_node, node, period)
    df_capture_rate = operational_results.get_capture_rate(df_operational_node, node, period)
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig)
    col2.dataframe(df_capture_rate.style.format("{:.2f}").background_gradient(cmap="Blues"))

    col1, col2 = st.columns(2)
    col1.plotly_chart(operational_results.plot_node_flow(df_operational_node, node))

    col2.plotly_chart(
        operational_results.plot_storage_operation_values(
            df_operational_node, node=node, scenario=scenario, period=period
        )
    )

    try:
        df_curtailed = output_client.get_curtailed_operational()
        st.plotly_chart(operational_results.plot_curtailment_operational(df_curtailed, node, scenario, period))
    except Exception as e:
        st.error(f"Exception: {e}")

    #########################
    st.header("Transmission")
    #########################

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

    ########################
    st.header("Key Metrics")
    ########################
    key_metrics_results = KeyMetricsResults(
        output_client=output_client, input_client=input_client, empire_config=empire_config
    )

    df_sum, measure, selected_nodes = key_metrics_results.generators(period)
    st.markdown(f"{measure} for {period}:")
    st.dataframe(df_sum.style.format("{:.2f}").background_gradient(cmap="Blues"), height=40 * len(df_sum.index))

    st.markdown("Mean electricity Prices")
    load_weighted = st.toggle("Load weighted prices", value=True)
    average_price_df = key_metrics_results.average_power_prices(df_operational_node_all, load_weighted=load_weighted)
    st.dataframe(average_price_df[selected_nodes].style.format("{:.2f}").background_gradient(cmap="Blues"))

    st.markdown("Import(+)/Export(-) [TWh/h]")
    flow_df = key_metrics_results.total_flow(df_operational_node_all) / 1e6
    st.dataframe(flow_df[selected_nodes].style.format("{:.2f}").background_gradient(cmap="Blues"))

    st.markdown("Marginal prices for generators")
    df_mc = key_metrics_results.compute_discounted_marginal_cost()
    st.dataframe(df_mc.style.format("{:.2f}").background_gradient(cmap="Blues"))

    st.markdown("Marginal prices for generators")
    df_mc = key_metrics_results.compute_discounted_marginal_cost()
    st.dataframe(df_mc.style.format("{:.2f}").background_gradient(cmap="Blues"))


if __name__ == "__main__":
    pass
