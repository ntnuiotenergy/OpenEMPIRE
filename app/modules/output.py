from pathlib import Path

import plotly.express as px
import streamlit as st

from empire.output_client.client import EmpireOutputClient


def output(active_results: Path) -> None:
    st.title("Results")
    output_client = EmpireOutputClient(output_path=active_results / "Output")

    st.write(f"Objective value: {output_client.get_objective()/1e9:.2f} Billion")

    df = output_client.get_europe_plot_generator_annual_production()
    df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
    fig1 = px.bar(
        df,
        x="Period",
        y="Value",
        color="genExpectedAnnualProduction_GWh",
        title="Expected Annual Production",
        labels={"genExpectedAnnualProduction_GWh": "Technology", "Value": "Expected Annual Production [TWh]"},
    )

    df = output_client.get_europe_plot_generator_installed_capacity()
    df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
    fig2 = px.bar(
        df,
        x="Period",
        y="Value",
        color="genInstalledCap_MW",
        title="Installed Capacity",
        labels={"genInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = output_client.get_curtailed_production()
    df.loc[:, "ExpectedAnnualCurtailment_GWh"] = df.loc[:, "ExpectedAnnualCurtailment_GWh"] / 1e3
    fig1 = px.bar(
        df,
        x="RESGeneratorType",
        y="ExpectedAnnualCurtailment_GWh",
        color="Node",
        facet_col="Period",
        title="Expected Annual Curtailment",
        labels={"ExpectedAnnualCurtailment_GWh": "Expected Annual Curtailment [TWh]"},
        facet_col_wrap=False,
    )
    df = output_client.get_europe_plot_storage_installed_energy()
    df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
    fig2 = px.bar(
        df,
        x="Period",
        y="Value",
        color="storENInstalledCap_MW",
        title="Installed Energy Storage",
        labels={"storENInstalledCap_MW": "Technology", "Value": "Installed Storage [MWh?]"},
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    df = output_client.get_europe_plot_storage_annual_discharge()
    df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
    fig1 = px.bar(
        df,
        x="Period",
        y="Value",
        color="storExpectedAnnualDischarge_GWh",
        title="Expected Annual Storage Discharge",
        labels={"storExpectedAnnualDischarge_GWh": "Technology", "Value": "Expected Annual Storage Discharge [TWh]"},
    )
    df = output_client.get_europe_plot_storage_installed_capacity()
    df = (df.stack() / 1e3).to_frame(name="Value").reset_index()
    fig2 = px.bar(
        df,
        x="Period",
        y="Value",
        color="storPWInstalledCap_MW",
        title="Installed Storage Capacity",
        labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
    )
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1)
    col2.plotly_chart(fig2)

    # px.line(output_client.get_europe_summary_emission_and_energy().groupby("Period").mean())
