from pathlib import Path

import plotly.express as px
import streamlit as st

from empire.core.config import EmpireConfiguration, read_config_file
from empire.input_client.client import EmpireInputClient
from empire.results.maps import plot_max_transmission_capacity, plot_nodes_and_lines, plot_transmission


def input(active_results: Path):
    st.title("Input")
    # active_results = Path.cwd()/"Results/basic_run/dataset_test"
    #### Input data
    input_client = EmpireInputClient(active_results / "Input/Xlsx")

    config_file = active_results / "Input/Xlsx/config.txt"
    config = read_config_file(config_file)
    empire_config = EmpireConfiguration.from_dict(config=config)

    inital_year = 2020
    leap_years_investment = empire_config.leap_years_investment

    n_periods = empire_config.n_periods
    periods_to_year_mapping = {
        i + 1: inital_year + i * leap_years_investment for i in range(20)
    }  # Quick fix in case there are fewer periods in the run than in the dataset

    st.markdown(f"How many periods: {n_periods}")

    st.sidebar.markdown("______________")
    st.sidebar.markdown("__Page filter:__")

    df_coords = input_client.sets.get_coordinates()
    df_coords_temp = df_coords.copy(deep=True)
    df_coords_temp.columns = [i.upper() for i in df_coords_temp.columns]
    st.map(df_coords_temp)

    ## Node
    st.header("Node data")

    df = input_client.nodes.get_electric_annual_demand()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig1 = px.line(
        df,
        x="Period",
        y="ElectricAdjustment in MWh per hour",
        color="Nodes",
        title="Annual Electric load",
        markers=True,
    )

    df = input_client.nodes.get_node_lost_load_cost()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.bar(
        df,
        x="Nodes",
        y="NodeLostLoadCost",
        # color="Period",  # This will differentiate bars by Period if there are multiple periods
        title="Value of Lost Load",
        labels={"NodeLostLoadCost": "Value of Lost Load"},
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.nodes.get_hydro_generators_max_annual_production()
    df.iloc[:, -1] = df.iloc[:, -1].div(1e6)
    df.sort_values(by="HydroGenMaxAnnualProduction in MWh per year", inplace=True, ascending=False)
    fig = px.bar(
        df,
        x="Nodes",
        y="HydroGenMaxAnnualProduction in MWh per year",
        title="Hydro Generators Max Annual Production",
        labels={"HydroGenMaxAnnualProduction in MWh per year": "Hydro Max Annual Production [TWh/year]"},
    )
    st.plotly_chart(fig)

    ## Generator
    st.header("Generator data")

    df = input_client.generator.get_capital_costs()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig1 = px.line(
        df,
        x="Period",
        y="generatorCapitalCost in euro per kW",
        color="GeneratorTechnology",
        title="Generator Capital Cost",
        markers=True,
    )

    df = input_client.generator.get_fixed_om_costs()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    y = "generatorFixedOMCost in euro per kW"
    if y not in df.columns:  # NB: Bug in excel sheet
        y = "generatorCapitalCost in euro per kW"

    fig2 = px.line(
        df,
        x="Period",
        y=y,
        color="GeneratorTechnology",
        title="Generator Fixed O&M Costs",
        markers=True,
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.generator.get_variable_om_costs()
    fig1 = px.bar(
        df,
        x="GeneratorTechnology",
        y="generatorVariableOMcosts in euro per MWh",
        title="Generator Variable O&M",
    )
    df = input_client.generator.get_fuel_costs()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.line(
        df,
        x="Period",
        y="generatorTypeFuelCost in euro per GJ",
        color="GeneratorTechnology",
        title="Generator Fuel Cost",
        markers=True,
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.generator.get_efficiency()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig1 = px.line(
        df,
        x="Period",
        y="generatorEfficiency",
        color="GeneratorTechnology",
        title="Generator Efficiency",
        markers=True,
    )
    df = input_client.generator.get_generator_type_availability()
    fig2 = px.bar(
        df,
        x="Generator",
        y="GeneratorTypeAvailability",
        title="Generator Availability",
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.generator.get_lifetime()
    fig1 = px.bar(
        df,
        x="GeneratorTechnology",
        y="generatorLifetime",
        title="Generator Lifetime",
    )
    df = input_client.generator.get_scale_factor_initial_capacity()
    fig2 = px.line(
        df,
        x="Period",
        y="generatorRetirementFactorInitialCap",
        color="GeneratorTechnology",
        title="Share of initial capacity that is retired in the period",
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    # df = input_client.generator.get_initial_capacity()
    # fig = px.bar(
    #     df,
    #     x="GeneratorTechnology",
    #     y="CO2Content_in_tCO2/GJ",
    #     title="Generator CO2 Content",
    # )
    # st.plotly_chart(fig)
    # df = input_client.generator.get_max_built_capacity()
    # fig = px.bar(
    #     df,
    #     x="GeneratorTechnology",
    #     y="generatoReferenceInitialCapacity in MW",
    #     color="Node",
    #     title=""
    # )
    # st.plotly_chart(fig)

    df = input_client.generator.get_ref_initial_capacity()
    fig1 = px.bar(
        df,
        x="GeneratorTechnology",
        y="generatoReferenceInitialCapacity in MW",
        color="Node",
        title="Initial Capacity",
        labels={"generatoReferenceInitialCapacity in MW": "Initial Capacity [MW]"},
    )
    df = input_client.generator.get_max_installed_capacity()
    num_types = df["Node"].nunique()
    bargap = 0.1 if num_types <= 3 else 0.3 / num_types
    fig2 = px.bar(
        df,
        x="GeneratorTechnology",
        y="generatorMaxInstallCapacity  in MW",
        color="Node",
        title="Max Installed Capacity",
    )
    fig2.update_layout(barmode="group", bargap=bargap)
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.generator.get_co2_content()
    fig1 = px.bar(
        df,
        x="GeneratorTechnology",
        y="CO2Content_in_tCO2/GJ",
        title="Generator CO2 Content",
    )
    df = input_client.generator.get_ccs_cost_ts_variable()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.bar(
        df,
        x="Period",
        y="CCS_TScost in euro per tCO2",
        title="CCS Cost",
        labels={"CCS_TScost in euro per tCO2": "CCS Cost [EUR/tCO2]"},
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.generator.get_ramp_rate()
    fig1 = px.bar(
        df,
        x="ThermalGenerators",
        y="RampRate",
        title="Ramp Rate of Thermal Generators from one Hour to the Next",
    )
    df = input_client.generator.get_ref_initial_capacity()
    fig2 = px.bar(
        df,
        x="GeneratorTechnology",
        y="generatoReferenceInitialCapacity in MW",
        color="Node",
        title="Initial capacity",
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    ## Sets
    st.header("Sets data")

    df_coords = input_client.sets.get_coordinates()
    df_coords.loc[:, "Location"] = df_coords["Location"].str.replace(" ", "")

    df_lines = input_client.sets.get_line_type_of_directional_lines()
    df_lines.loc[:, "FromNode"] = df_lines["FromNode"].str.replace(" ", "")
    df_lines.loc[:, "ToNode"] = df_lines["ToNode"].str.replace(" ", "")
    fig1 = plot_nodes_and_lines(df_coords, df_lines)
    df = input_client.sets.get_generators_of_node()
    df.sort_values(by="Node", ascending=True)
    fig2 = px.bar(
        df,
        x="Node",
        y="Generator",
        color="Generator",
        title="Generator Technology in Node",
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.sets.get_storage_of_nodes()
    df.sort_values(by="Node", ascending=True)
    fig1 = px.bar(
        df,
        x="Node",
        y="Storage",
        color="Storage",
        title="Storage Technology in Node",
    )
    st.plotly_chart(fig)

    ## Storage

    df = input_client.storage.get_energy_max_installed_capacity()
    fig1 = px.bar(
        df,
        x="Nodes",
        y="EnergyMaxInstalledCapacity",
        color="StorageTypes",
        title="Storage Max Installed Energy Capacity",
    )
    df = input_client.storage.get_power_max_installed_capacity()
    fig2 = px.bar(
        df,
        x="Nodes",
        y="PowerMaxInstalledCapacity",
        color="StorageTypes",
        title="Storage Max Installed Power Capacity",
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.storage.get_energy_max_built_capacity()
    fig1 = px.bar(
        df,
        x="Nodes",
        y="EnergyMaxBuiltCapacity",
        color="StorageTypes",
        title="Storage Max Built Energy Capacity",
    )
    df = input_client.storage.get_power_max_built_capacity()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.bar(
        df,
        x="Nodes",
        y="PowerMaxBuiltCapacity",
        color="StorageTypes",
        title="Storage Max Built Power Capacity",
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.storage.get_power_capital_cost()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig1 = px.line(
        df,
        x="Period",
        y="PowerCapitalCost in euro per kW",
        color="StorageTypes",
        title="Storage Power Capital Cost",
        markers=True,
    )
    df = input_client.storage.get_energy_capital_cost()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.line(
        df,
        x="Period",
        y="EnergyCapitalCost in euro per kWh",
        color="StorageTypes",
        title="Storage Energy Capital Cost",
        markers=True,
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = input_client.storage.get_initial_power_capacity()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig1 = px.line(
        df,
        x="Period",
        y="InitialPowerCapacity",
        color="Nodes",
        line_group="StorageTypes",
        title="Initial Power Capacity",
        markers=True,
    )
    df = input_client.storage.get_initial_energy_capacity()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.line(
        df,
        x="Period",
        y="EnergyInitialCapacity",
        color="Nodes",
        line_group="StorageTypes",
        title="Initial Energy Capacity",
        markers=True,
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    st.dataframe(input_client.storage.get_storage_initial_energy_level())
    st.dataframe(input_client.storage.get_lifetime())

    ## Transmission
    st.header("Transmission")

    df_init_capacity = input_client.transmission.get_initial_capacity()
    df_init_capacity.loc[:, "InterconnectorLinks"] = df_init_capacity["InterconnectorLinks"].str.replace(" ", "")
    df_init_capacity.loc[:, "ToNode"] = df_init_capacity["ToNode"].str.replace(" ", "")
    period = st.sidebar.selectbox("Select period: ", df_init_capacity["Period"].unique().tolist())
    df_init_capacity = df_init_capacity.query(f"Period=={period}")

    df_length = input_client.transmission.get_length()

    df_efficiency = input_client.transmission.get_line_efficiency()
    df_efficiency.loc[:, "FromNode"] = df_efficiency["FromNode"].str.replace(" ", "")
    df_efficiency.loc[:, "ToNode"] = df_efficiency["ToNode"].str.replace(" ", "")

    df_max_capacity = input_client.transmission.get_max_built_capacity()

    try:
        fig = plot_transmission(
            df_coords=df_coords,
            df_lines=df_lines,
            df_init_capacity=df_init_capacity,
            df_max_capacity=df_max_capacity,
            df_length=df_length,
            df_efficiency=df_efficiency,
        )
        fig.update_layout(title=f"Transmission grid, period: {period}")
        st.plotly_chart(fig)
    except KeyError as e:
        st.error(f"Error: {e}")

    df = input_client.transmission.get_type_capital_cost()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig1 = px.bar(
        df,
        x="Period",
        y="TypeCapitalCost in euro per MWkm",
        color="Type",
        title="Transmission Capital Cost",
    )
    fig1.update_layout(barmode="group")
    df = input_client.transmission.get_type_fixed_om_cost()
    df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
    fig2 = px.bar(
        df,
        x="Period",
        y="TypeFixedOMCost in euro per MW",
        color="Type",
        title="Transmission O&M Cost",
    )
    fig2.update_layout(barmode="group")
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    st.subheader("Max Install Capacity Raw")
    df_init_capacity = input_client.transmission.get_initial_capacity()
    df_init_capacity.loc[:, "InterconnectorLinks"] = df_init_capacity["InterconnectorLinks"].str.replace(" ", "")
    df_init_capacity.loc[:, "ToNode"] = df_init_capacity["ToNode"].str.replace(" ", "")
    df_init_capacity = df_init_capacity.query(f"Period=={period}")

    df_max_install_capacity = input_client.transmission.get_max_install_capacity_raw()
    df_max_capacity = input_client.transmission.get_max_built_capacity()

    fig = plot_max_transmission_capacity(
        df_coords=df_coords,
        df_lines=df_lines,
        df_max_capacity=df_max_install_capacity,
    )
    fig.update_layout(title=f"Max Transmission Capacity, period: {period}")

    st.plotly_chart(fig)

    # General data
    st.header("General data")

    if empire_config.use_emission_cap:
        st.markdown("The case uses the following CO2 cap:")

        df = input_client.general.get_co2_cap()
        df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
        fig1 = px.bar(
            df,
            x="Period",
            y="CO2Cap [in Mton CO2eq]",
            title="CO2 Cap",
        )
        st.plotly_chart(fig1)
    else:
        st.markdown("The case uses the following CO2 price:")

        df = input_client.general.get_co2_price()
        df.loc[:, "Period"] = df.loc[:, "Period"].replace(periods_to_year_mapping)
        fig1 = px.bar(
            df,
            x="Period",
            y="CO2price in euro per tCO2",
            title="CO2 Price",
        )

        st.plotly_chart(fig1)

    df = input_client.general.get_season_scale()
    fig1 = px.bar(
        df,
        x="Season",
        y="seasonScale",
        title="Seasonal scaling",
    )

    st.plotly_chart(fig1)
