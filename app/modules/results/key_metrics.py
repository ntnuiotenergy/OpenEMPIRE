import pandas as pd
import streamlit as st


class KeyMetricsResults:
    def __init__(self, output_client, input_client, empire_config):
        self.output_client = output_client
        self.input_client = input_client
        self.empire_config = empire_config

    def generators(self, period):
        df = self.output_client.get_generators_values()
        df.loc[:, "genInvCap_MW"] /= 1e3
        df.loc[:, "genInstalledCap_MW"] /= 1e3

        df = df.rename(columns={"genInvCap_MW": "genInvCap_GW", "genInstalledCap_MW": "genInstalledCap_GW"})

        df.loc[df["genExpectedAnnualProduction_GWh"] < 1, "genExpectedCapacityFactor"] = 0.0
        df_temp = df[["Node", "GeneratorType", "Period", "genExpectedAnnualProduction_GWh"]]
        df["TotalGeneration_GWh"] = df_temp.groupby(["Node", "Period"])["genExpectedAnnualProduction_GWh"].transform(
            "sum"
        )
        df["GenerationShare_Percent"] = (df["genExpectedAnnualProduction_GWh"] / df["TotalGeneration_GWh"]) * 100

        df_temp = df[["Node", "GeneratorType", "Period", "genInstalledCap_GW"]]
        df["TotalCapacity_GW"] = df_temp.groupby(["Node", "Period"])["genInstalledCap_GW"].transform("sum")
        df["CapacityShare_Percent"] = (df["genInstalledCap_GW"] / df["TotalCapacity_GW"]) * 100

        # Select measure
        measures = [
            "genInvCap_GW",
            "genInstalledCap_GW",
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

        df_sum = df.query(f"Period == '{period}'").pivot(index="Node", columns="GeneratorType", values=measure)

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
            "Select nodes:       ", options=df_sum.index, default=[item for item in default_nodes if item in nodes]
        )
        selected_generators = st.multiselect(
            "Select generators: ", options=df_sum.columns, default=df_sum.columns.tolist()
        )

        # Process the dataframe and display it
        df_sum = (
            df_sum.loc[selected_nodes, selected_generators]
            .fillna(0.0)
            .loc[:, df_sum.sum(axis=0) > 1.0]
            .assign(Active_sum=lambda x: x.sum(axis=1))
            .T
        )

        return df_sum, measure, selected_nodes

    def average_power_prices(self, df, load_weighted: bool = True):
        if not load_weighted:
            avg_prices = df.groupby(["Node", "Period"])["Price_EURperMWh"].mean().to_frame().reset_index()
            avg_prices = avg_prices.pivot(columns="Node", index="Period")
            avg_prices.columns = avg_prices.columns.droplevel()

            return avg_prices

        else:
            df["PriceLoadWeighted"] = (df["Load_MW"] * df["Price_EURperMWh"]) / df.groupby(["Node", "Period"])[
                "Load_MW"
            ].transform("mean")

            # If NaN values (with zero load in node) fill the non-weighted price
            df.loc[:, "PriceLoadWeighted"] = df["PriceLoadWeighted"].fillna(df["Price_EURperMWh"])

            avg_weighted_price = df.groupby(["Node", "Period"])["PriceLoadWeighted"].mean().to_frame().reset_index()
            avg_weighted_price = avg_weighted_price.pivot(columns="Node", index="Period")

            df.drop(columns="PriceLoadWeighted")

            avg_weighted_price.columns = avg_weighted_price.columns.droplevel()

            return avg_weighted_price

    def total_flow(self, df):
        df_t = df.groupby(["Node", "Period"])[["FlowOut_MW", "FlowIn_MW"]].sum().reset_index()
        df_t["FlowTotal_MW"] = df_t["FlowOut_MW"] + df_t["FlowIn_MW"]
        return df_t.pivot(index="Period", columns="Node", values="FlowTotal_MW")

    def compute_discounted_marginal_cost(self) -> pd.DataFrame:
        """
        Compute the discounted marginal costs. If npv_discounted==True, this is the marginal cost in the objective
        function of Empire. Hence it can be used to verify which units are the marginal units and hence
        setting the electricity price in the different nodes (unless it is import/storage).

        :return: Dataframe
        """

        period_to_year_mapping = {}
        for i in range(self.empire_config.n_periods):
            year_from = 2020 + i * self.empire_config.leap_years_investment
            year_to = year_from + self.empire_config.leap_years_investment
            period_to_year_mapping[i + 1] = f"{year_from}-{year_to}"
        
        df_marginal_costs = pd.read_csv(self.output_client.output_path / "marginal_costs.csv")
        df_marginal_costs.loc[:, "Period"] = df_marginal_costs.loc[:, "Period"].replace(period_to_year_mapping)
        df_mc = df_marginal_costs.pivot(columns="Generator", index="Period", values="MarginalCost_EurperMWh")

        # Discount to PV
        discout_mapper = {
            period: (1 + self.empire_config.discount_rate) ** (-self.empire_config.leap_years_investment * i)
            for i, period in enumerate(df_mc.index.get_level_values("Period").unique().sort_values())
        }

        discounting = df_mc.index.get_level_values("Period").map(discout_mapper).values
        df_mc = df_mc.mul(discounting, axis=0)

        return df_mc
